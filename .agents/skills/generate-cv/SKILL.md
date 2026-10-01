---
name: generate-cv
description: >-
  Tailor and generate a publication-ready CV PDF from a Job Description (JD) using the master profile,
  matching tags against existing variants to reuse or creating a new variant with a companion README.md using cv-writer CLI.
---

# Skill: Generate Tailored CV

Use this skill as the primary entrypoint when the user supplies a Job Description (JD), job URL, or target role title to produce a tailored CV PDF.

## Purpose & Scope
- Compare target JD tags against `cvs/registry.json`.
- If an existing CV variant matches the tags, reuse or present it directly to the user.
- If creating a new variant or updating one:
  1. Extract key focus areas from the JD (required technologies, domain emphasis, seniority level).
  2. Select and highlight relevant experiences/projects from `profile/profile.json`.
  3. Transform to base `CvProfile` schema via `./bin/profile-curator export --state profile/profile.json` or customize directly.
  4. Compile native PDF using `./bin/cv-writer compile`.
  5. Produce `cvs/<variant-slug>/README.md` explaining the rationale and focus points.
  6. Register the variant in `cvs/registry.json`.

## Available CLI Tools
Binaries: `./bin/cv-writer` and `./bin/profile-curator`

- **`cv-writer compile -p <profile.json> -o <output.pdf> [--changelog-dir <dir>] [--emit-tex] [--dry-run]`**:
  Compiles a `CvProfile` JSON (or STDIN via `-p -`) into a LuaLaTeX PDF.
- **`cv-writer schema`**: Outputs canonical `CvProfile` JSON Schema.
- **`cv-writer sample`**: Outputs realistic reference JSON profile.
- **`cv-writer template-info`**: Outputs typography, margins, color palette.
- **`profile-curator export --state profile/profile.json`**:
  Exports curated profile into `{ "cv_profile": <CvProfile> }`.

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
1. Load `profile/profile.json` or export base CV data:
   ```bash
   ./bin/profile-curator export --state profile/profile.json | jq '.cv_profile' > cvs/<variant-slug>/cv.json
   ```
2. Tailor `cvs/<variant-slug>/cv.json`:
   - Prioritize bullet points and projects directly relevant to the JD requirements.
   - Adjust `summary` to reflect candidate alignment with the specific role.
   - Reorder skills so JD-required technologies appear first.

### 3. Compile PDF via `cv-writer`
1. Ensure destination directory exists:
   ```bash
   mkdir -p cvs/<variant-slug>
   ```
2. Compile the PDF:
   ```bash
   ./bin/cv-writer compile \
     -p cvs/<variant-slug>/cv.json \
     -o cvs/<variant-slug>/cv.pdf \
     --changelog-dir cvs/<variant-slug>/changelogs/
   ```
3. Check exit code:
   - `0`: Success (PDF compiled atomically).
   - `1`: I/O error.
   - `2`: Schema validation error.
   - `3`: LuaLaTeX engine error.

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
