---
trigger: always_on
---

# Rules for Profile Curation & CV Generation Repository

You are operating within an agent-skill-centric CV repository powered by two agent-first stateless CLI tools:
1. **`profile-curator`**: Iterative interview, readiness guide, profile enrichment, gap validation, and canonical profile export.
2. **`cv-writer`**: High-fidelity LuaLaTeX compilation, tailoring diff tracking, and PDF generation using the modernized Star Rover template.

Binary locations: `./bin/profile-curator` and `./bin/cv-writer` (or in `$PATH`).

## Architectural Principles & Workflow Seam

1. **Single Source of Truth (`profile/profile.json`)**:
   - The master profile is the candidate's canonical career record (combining full history + forward-looking orientation).
   - Any modifications or conversational discoveries are patched into `profile/profile.json` using `profile-curator patch` (or editing JSON) and tracked via Git commits.
   - Recommended interview workflow:
     ```bash
     ./bin/profile-curator guide --state profile/profile.json
     ./bin/profile-curator patch --state profile/profile.json --patch-json '{"..."}' --message "..."
     ./bin/profile-curator validate --state profile/profile.json
     ```

2. **Decoupled CV Variants (`cvs/`)**:
   - Each job opportunity or archetype is stored in `cvs/<variant-slug>/`.
   - Before compiling a new CV, check `cvs/registry.json` to see if an existing CV variant matches the target Job Description (JD) tags (e.g. `[backend, distributed-systems, rust, senior]`).
   - If tags match and the role is compatible, reuse or adapt the existing variant.

3. **Mandatory Companion `README.md`**:
   - Every CV folder in `cvs/<variant-slug>/` MUST contain:
     - `cv.json`: The specific `CvProfile` payload tailored for the role.
     - `cv.pdf`: The compiled PDF binary output.
     - `README.md`: A short companion document explaining:
       - Target Role & Archetype (e.g., Senior Backend Engineer - FinTech).
       - Matching Tags.
       - Key tailored focal points (why specific projects/skills were highlighted over others).
       - JD context or requirements it addresses.

4. **Integration Seam Between Tools**:
   - `profile-curator export --state profile/profile.json` outputs `{ "cv_profile": { ... } }`.
   - `cv-writer compile --profile <path> --output <path>` accepts either direct `CvProfile` JSON or STDIN (`-`).
   - When piping from `profile-curator export`:
     ```bash
     ./bin/profile-curator export --state profile/profile.json | jq '.cv_profile' | ./bin/cv-writer compile -p - -o cvs/<slug>/cv.pdf
     ```
   - When compiling from `cvs/<variant-slug>/cv.json` (which contains `CvProfile` directly):
     ```bash
     ./bin/cv-writer compile -p cvs/<slug>/cv.json -o cvs/<slug>/cv.pdf --changelog-dir cvs/<slug>/changelogs/
     ```
   - Always verify that the target directory exists before running compilation.
