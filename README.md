# CV & Profile Management Suite

An agent-skill-centric repository for maintaining a canonical, version-controlled career profile and generating tailored, high-converting CV PDFs compiled with LuaLaTeX using the Star Rover template.

## Architecture

This workspace integrates two **agent-first, stateless CLI tools**:
1. **`profile-curator`**: Iterative interview guide, incremental enrichment, completeness validation, STAR interview story vault, and profile export.
2. **`cv-writer`**: High-fidelity LuaLaTeX compilation, profile diffs/changelogs, and PDF rendering using the modern Star Rover template.

```
├── .agents/
│   ├── agents/
│   │   └── cv-suite-orchestrator.md     # Specialized career orchestrator agent
│   ├── rules/
│   │   └── cv_profile_workflow.md       # Workflow seam between curation and compilation
│   └── skills/
│       ├── curate-profile/              # Interview & profile curation skill
│       │   └── SKILL.md
│       └── generate-cv/                 # JD matching & CV compilation skill
│           └── SKILL.md
├── bin/                                 # Stateless CLI binaries (auto-managed)
│   ├── .versions.json
│   ├── cv-writer
│   └── profile-curator
├── cvs/                                 # Generated CV variants
│   ├── registry.json                    # Tag registry for JD reuse and matching
│   └── <variant-slug>/
│       ├── cv.json                      # Tailored CvProfile payload
│       ├── cv.pdf                       # Rendered PDF
│       └── README.md                    # Role context, tags, tailoring rationale
├── mcp_config.json                      # Optional legacy MCP configuration (fallback)
├── profile/
│   └── profile.json                     # Canonical Git-versioned master profile
└── scripts/
    ├── install_or_update_tools.sh       # Pull / update CLI binaries from GitHub releases
    ├── check_updates.sh                 # Inspect local vs latest GitHub release versions
    ├── render_cv.py                     # Python runner calling cv-writer CLI
    └── regenerate_cvs.sh                # Convenient shell wrapper to recompile CVs
```

---

## Getting Started

### 1. Install or Update CLI Binaries
To automatically detect your OS/architecture and pull the latest release binaries:
```bash
./scripts/install_or_update_tools.sh
```

To force re-download:
```bash
./scripts/install_or_update_tools.sh --force
```

### 2. Check for Updates
To check if new versions exist without modifying your environment:
```bash
./scripts/check_updates.sh
```

### 3. Regenerate CV PDFs (Without AI Agent)
You can directly recompile any `cv.pdf` from its `cv.json`:
```bash
# Recompile a specific variant
./scripts/regenerate_cvs.sh cvs/general-ai-engineer

# Recompile all existing variants under cvs/
./scripts/regenerate_cvs.sh --all
```

Or invoke `cv-writer` directly:
```bash
./bin/cv-writer compile -p cvs/general-ai-engineer/cv.json -o cvs/general-ai-engineer/cv.pdf
```

---

## Agent Usage & Workflows

### 1. Curating Your Master Profile
Use the **`curate-profile`** skill:
- Review completeness and missing metrics with `./bin/profile-curator validate --state profile/profile.json`.
- Answer targeted questions recommended by `./bin/profile-curator guide --state profile/profile.json`.
- Incrementally patch updates via `./bin/profile-curator patch` into `profile/profile.json` and track with Git commits.

### 2. Generating a Tailored CV from a Job Description (JD)
Use the **`generate-cv`** skill:
- Paste a Job Description or target role requirements.
- The agent extracts core tags and searches `cvs/registry.json`.
- If a matching variant exists, it can be reused or refined.
- When generating a new variant:
  1. Base profile data is exported via `./bin/profile-curator export --state profile/profile.json | jq '.cv_profile'`.
  2. The agent tailors experiences, metrics, and skill ordering in `cvs/<variant-slug>/cv.json`.
  3. The PDF is compiled with `./bin/cv-writer compile -p cvs/<variant-slug>/cv.json -o cvs/<variant-slug>/cv.pdf --changelog-dir cvs/<variant-slug>/changelogs/`.
  4. The companion `README.md` and `cvs/registry.json` are created/updated.
