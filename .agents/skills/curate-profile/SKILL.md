---
name: curate-profile
description: >-
  Iteratively interview the candidate, create or update the canonical master profile (profile/profile.json),
  validate completeness, identify career orientation, and version changes with Git using the profile-curator CLI.
---

# Skill: Curate Candidate Profile

Use this skill as the primary entrypoint when the user wants to build, enrich, or audit their comprehensive career profile.

## Purpose & Scope
- Initialize or load `profile/profile.json` (canonical `CuratedProfile`).
- Conduct structured conversational interviews using `profile-curator guide` recommendations.
- Incrementally patch profile sections (`background`, `career_orientation`, `contact`, `stories`) using `profile-curator patch`.
- Commit updates into Git to maintain a version-controlled career record.

## Available CLI Commands (`profile-curator`)
Binary path: `./bin/profile-curator`

- `profile-curator guide --state profile/profile.json [--json]`: Analyze completeness score, detect missing fields, and suggest prioritized conversational interview questions.
- `profile-curator patch --state profile/profile.json --patch-json '<JSON>' [--changelog-dir ./history] [--message "Rationale"]`: Incrementally patch profile fields, atomically save state, and emit audit diffs.
- `profile-curator validate --state profile/profile.json`: Validate profile completeness score (0-100), highlight critical gaps, and check section coverage.
- `profile-curator history --changelog-dir ./history`: Review past interview session changelogs and narratives.
- `profile-curator schema [--type profile|patch|cv_writer|all]`: Dump canonical schemas for reference.
- `profile-curator init --state profile/profile.json [--sample]`: Initialize a fresh profile scaffold.

## Standard Execution Procedure

### Step 1: Check or Initialize Profile
1. Check if `profile/profile.json` exists in the repository.
2. If it does not exist:
   ```bash
   ./bin/profile-curator init --state profile/profile.json
   ```
3. If it exists, inspect readiness:
   ```bash
   ./bin/profile-curator validate --state profile/profile.json
   ```

### Step 2: Validate & Discover Gaps
1. Run guide command to get conversational questions:
   ```bash
   ./bin/profile-curator guide --state profile/profile.json
   ```
2. Note missing high-value details: quantifiable metrics, target roles, preferred stack, STAR stories, certifications.

### Step 3: Conversational Interview
1. Ask the candidate targeted, concise questions (1-3 questions at a time).
2. As the user provides answers, patch them incrementally:
   ```bash
   ./bin/profile-curator patch \
     --state profile/profile.json \
     --patch-json '{"contact": {"name": "..."}, "career_orientation": {"add_target_roles": ["..."]}}' \
     --message "Added candidate target roles"
   ```
   Or for STAR stories:
   ```bash
   ./bin/profile-curator patch \
     --state profile/profile.json \
     --patch-json '{"add_stories": [{"id": "...", "title": "...", "situation": "...", "task": "...", "action": "...", "result": "...", "tags": [...]}]}' \
     --message "Recorded STAR experience story"
   ```

### Step 4: Version Control Commit
1. After significant enrichments, commit the changes:
   ```bash
   git add profile/profile.json
   git commit -m "feat(profile): update experience and career orientation"
   ```
