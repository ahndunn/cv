---
trigger: always_on
---

# Rules for Profile Curation & CV Generation Repository

You are operating within an agent-skill-centric CV repository governed by two core MCP servers:
1. **`profile-curator`**: Iterative interview, profile enrichment, gap validation, question recommendation, and canonical profile export.
2. **`cv-writer`**: High-fidelity LuaLaTeX compilation and PDF generation using the modernized Star Rover template.

## Architectural Principles & Workflow Seam

1. **Single Source of Truth (`profile/profile.json`)**:
   - The master profile is the candidate's canonical career record (combining full history + forward-looking orientation).
   - Any modifications or conversational discoveries must be patched into `profile/profile.json` using `profile-curator` tools (`patch_profile` or updating the JSON structure) and tracked via Git commits.

2. **Decoupled CV Variants (`cvs/`)**:
   - Each job opportunity or archetype is stored in `cvs/<variant-slug>/`.
   - Before compiling a new CV, check `registry.json` to see if an existing CV variant matches the target Job Description (JD) tags (e.g. `[backend, distributed-systems, rust, senior]`).
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
   - When calling `export_to_cv_writer` on `profile-curator`, note that the tool returns an envelope containing `{"cv_profile": { ... }, "cv_writer_tool_call_sample": { ... }}`.
   - The `render_cv` tool of `cv-writer` requires the inner `cv_profile` object as its `profile` argument.
   - Always verify that the target directory exists before running `render_cv` with `output_path`.
