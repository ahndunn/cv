---
name: curate-profile
description: >-
  Iteratively interview the candidate, create or update the canonical master profile (profile/profile.json),
  validate completeness, identify career orientation, and version changes with Git.
---

# Skill: Curate Candidate Profile

Use this skill as the primary entrypoint when the user wants to build, enrich, or audit their comprehensive career profile.

## Purpose & Scope
- Initialize or load `profile/profile.json` (canonical `CuratedProfile`).
- Conduct structured conversational interviews using `profile-curator` recommendations.
- Incrementally patch profile sections (`background`, `career_orientation`, `contact`).
- Commit updates into Git to maintain a version-controlled career record.

## Available MCP Tools (`profile-curator`)
- `get_profile_schema`: Inspect fields for `CuratedProfile` and `ProfilePatch`.
- `create_empty_profile`: Generate initial template structure.
- `get_sample_profile`: View a full reference example.
- `validate_profile`: Analyze profile completeness, missing contact info, missing metrics/dates.
- `recommend_next_questions`: Suggest tailored questions based on current profile gaps.
- `patch_profile`: Apply additions, updates, or removals to an in-memory profile and view clean diffs.

## Standard Execution Procedure

### Step 1: Check or Initialize Profile
1. Check if `profile/profile.json` exists in the repository.
2. If it does not exist:
   - Call `create_empty_profile` or populate basic fields from the user.
   - Save to `profile/profile.json`.
3. If it exists:
   - Load the JSON content into memory.

### Step 2: Validate & Discover Gaps
1. Call `validate_profile` with the current profile JSON.
2. Call `recommend_next_questions` to understand high-value missing details (e.g., quantifiable metrics, target roles, preferred stack, certifications).

### Step 3: Conversational Interview
1. Ask the candidate targeted, concise questions (1-3 questions at a time).
2. As the user provides their answers, structure the input into a `ProfilePatch`.
3. Call `patch_profile` with `{ "current_profile": <profile>, "patch": <patch> }`.
4. Save the updated profile back to `profile/profile.json`.

### Step 4: Version Control Commit
1. After significant enrichments, inform the user and suggest or execute a Git commit:
   ```bash
   git add profile/profile.json
   git commit -m "feat(profile): update experience and career orientation"
   ```
