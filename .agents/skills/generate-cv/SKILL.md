---
name: generate-cv
description: >-
  Tailor and generate a publication-ready CV PDF from a Job Description (JD) using the master profile,
  matching tags against existing variants to reuse or creating a new variant with a companion README.md.
---

# Skill: Generate Tailored CV

Use this skill as the primary entrypoint when the user supplies a Job Description (JD), job URL, or target role title to produce a tailored CV PDF.

## Purpose & Scope
- Compare target JD tags against `cvs/registry.json`.
- If an existing CV variant matches the tags, reuse or present it directly to the user.
- If creating a new variant or updating one:
  1. Extract key focus areas from the JD (required technologies, domain emphasis, seniority level).
  2. Select and highlight relevant experiences/projects from `profile/profile.json`.
  3. Transform to `CvProfile` schema (via `export_to_cv_writer` on `profile-curator`).
  4. Compile native PDF using `render_cv` on `cv-writer`.
  5. Produce `cvs/<variant-slug>/README.md` explaining the rationale and focus points.
  6. Register the variant in `cvs/registry.json`.

## Available MCP Tools
- **`profile-curator`**:
  - `export_to_cv_writer`: Converts `CuratedProfile` into `CvProfile`. Returns envelope `{ "cv_profile": ... }`.
- **`cv-writer`**:
  - `get_cv_schema`: Inspect expected CV fields.
  - `get_template_info`: Star Rover styling rules, margins, color scheme.
  - `render_cv`: Compiles LuaLaTeX PDF from `{ "profile": <cv_profile>, "output_path": <dest_path> }`.

## Step-by-Step Procedure

### 1. Tag & Match Analysis
1. Analyze the JD provided by the user.
2. Extract:
   - Target Role (e.g. `Staff Backend Engineer`)
   - Company / Domain (e.g. `FinTech / Payments`)
   - Tags (e.g. `["backend", "rust", "distributed-systems", "high-throughput", "lead"]`)
3. Read `cvs/registry.json`.
4. Check if any existing entry has significant tag overlap (e.g. >= 70% match on core tags):
   - **If match found**: Inform the user: *"Found existing variant `cvs/<slug>` matching tags [tags]. Would you like to use this variant directly or create a specialized adaptation?"*

### 2. Tailor CV Profile Payload
1. Load `profile/profile.json`.
2. Generate base CV profile via `export_to_cv_writer` or curate specific experiences:
   - Prioritize bullet points and projects directly relevant to the JD requirements.
   - Adjust `summary` to reflect the candidate's alignment with the role.
   - Reorder skills so that JD-required technologies appear first.
3. Extract the inner `cv_profile` dictionary:
   ```json
   {
     "contact": { ... },
     "summary": "...",
     "skills": [ ... ],
     "experience": [ ... ],
     "projects": [ ... ],
     "education": [ ... ],
     "certifications": [ ... ]
   }
   ```

### 3. Generate Folder & Files
1. Create directory `cvs/<variant-slug>/`.
2. Save tailored JSON to `cvs/<variant-slug>/cv.json`.
3. Invoke `render_cv` on `cv-writer`:
   - `profile`: `<cv_profile object>`
   - `output_path`: `<workspace_root>/cvs/<variant-slug>/cv.pdf`
4. Confirm successful compilation (returns PDF size and status).

### 4. Create Companion `README.md`
Every generated variant MUST have `cvs/<variant-slug>/README.md` with:
```markdown
# CV: <Target Role Name> (<Variant Slug>)

- **Target Archetype / Role**: <Title>
- **Target Domain / Company**: <Domain or Company>
- **Generated Date**: <YYYY-MM-DD>
- **Tags**: `[tag1, tag2, tag3]`

## Purpose & Focus
<Brief explanation of why this variant was generated and what opportunity it targets.>

## Key Tailoring Decisions
- **Emphasized Projects**: Highlighted project X and Y because the JD emphasizes ...
- **Skill Ordering**: Moved ... to the primary category to match required qualifications.
- **Experience Highlights**: Rephrased achievements to showcase impact in ...

## Output Files
- [PDF Document](file:///home/ahndunn/Documents/cv/cvs/<variant-slug>/cv.pdf)
- [Source Payload](file:///home/ahndunn/Documents/cv/cvs/<variant-slug>/cv.json)
```

### 5. Update Registry
Add entry to `cvs/registry.json`:
```json
{
  "slug": "<variant-slug>",
  "role": "<Target Role>",
  "tags": ["tag1", "tag2"],
  "path": "cvs/<variant-slug>",
  "updated_at": "<ISO-timestamp>"
}
```
