# CV & Profile Management Suite

An agent-skill-centric repository for maintaining a canonical, version-controlled career profile and generating tailored, high-converting CV PDFs compiled with LuaLaTeX using the Star Rover template.

## Architecture

This workspace integrates two Model Context Protocol (MCP) servers:
1. **`profile-curator`**: Iterative interview, incremental enrichment, completeness validation, and career orientation.
2. **`cv-writer`**: High-fidelity LuaLaTeX compilation and PDF rendering.

```
├── .agents/
│   ├── agents/
│   │   └── cv-suite-orchestrator.md     # Specialized career orchestrator agent
│   ├── rules/
│   │   └── cv_profile_workflow.md       # Rules linking curation, matching, and generation
│   └── skills/
│       ├── curate-profile/              # Entrypoint skill for interview & profile updates
│       │   └── SKILL.md
│       └── generate-cv/                 # Entrypoint skill for JD matching & CV compilation
│           └── SKILL.md
├── bin/                                 # Platform-specific MCP binaries (auto-managed)
│   ├── .versions.json
│   ├── cv-writer-mcp
│   └── profile-curator-mcp
├── cvs/                                 # Generated CV variants
│   ├── registry.json                    # Tag registry for JD reuse and matching
│   └── <variant-slug>/
│       ├── cv.json                      # Tailored CvProfile payload
│       ├── cv.pdf                       # Rendered PDF
│       └── README.md                    # Role context, tags, tailoring rationale
├── mcp_config.json                      # MCP configuration for IDE and agent runtimes
├── profile/
│   └── profile.json                     # Canonical Git-versioned master profile
└── scripts/
    ├── install_or_update_mcps.sh        # Pull / update platform binaries from releases
    └── check_updates.sh                 # Inspect local vs latest GitHub release versions
```

---

## Getting Started

### 1. Install or Update MCP Binaries
To automatically detect your OS/architecture and pull the latest binaries from GitHub:
```bash
./scripts/install_or_update_mcps.sh
```

To force re-download:
```bash
./scripts/install_or_update_mcps.sh --force
```

### 2. Check for Updates
To check if new versions exist without modifying your environment:
```bash
./scripts/check_updates.sh
```

### 3. Regenerate CV PDFs (Without AI Agent)
When `cv-writer` is updated or when adjusting template/styling rules, you can directly recompile any `cv.pdf` from its `cv.json`:
```bash
# Recompile a specific variant
./scripts/regenerate_cvs.sh cvs/general-ai-engineer

# Recompile all existing variants under cvs/
./scripts/regenerate_cvs.sh --all
```


---

## Agent Usage & Workflows

### 1. Curating Your Master Profile
Use the **`curate-profile`** skill:
- Review completeness and missing metrics with `validate_profile`.
- Answer targeted questions recommended by `recommend_next_questions`.
- Incremental updates are saved to `profile/profile.json` and tracked in Git.

### 2. Generating a Tailored CV from a Job Description (JD)
Use the **`generate-cv`** skill:
- Paste a Job Description or target role requirements.
- The agent extracts core tags and searches `cvs/registry.json`.
- If a matching variant exists, it can be reused or refined.
- When generating a new variant, the agent compiles `cv.pdf` via `cv-writer`, stores the tailored payload `cv.json`, writes a companion `README.md`, and updates `cvs/registry.json`.
