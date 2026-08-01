## Week 7 — Issue selection

**Issue link:** https://github.com/ascherj/pathreview/issues/148

**Issue title:** Skill extractor fails to detect JavaScript and TypeScript

**Tier:** [X] Tier 1 [ ] Tier 2 [ ] Tier 3

**Problem summary:**
_What the issue is:_ The skill extractor
(`ingestion/parsers/skill_extractor.py`) is supposed to read a chunk of code or a
plain-English description of someone's work and report which technologies it sees.
It does this reliably for Python but is essentially blind to the JavaScript/
TypeScript family — text that clearly describes JS work returns nothing, and TS
samples only ever come back as "React".

_What is currently broken:_ The `extract_skills()` entry point, via its
`_detect_languages()` helper, only looks at the passed-in `filename` for `.js`/`.ts`
extensions and never scans the text itself, its import/require pattern requires a
space after the keyword so `require('fs')` slips through, and it never recognizes
the literal words "JavaScript" or "TypeScript". As a result `.tsx`/`.ts` mentions
get picked up only incidentally by the React detector. A related DevOps gap: tool
detection matches the literal string "docker", which never appears in Dockerfile
(`FROM`/`RUN`) or docker-compose (`services:`/`version:`) content, so those go
undetected too.

_What a successful fix accomplishes:_ Language and tool detection inspect the actual
text for family-specific signals — in-text file extensions, language keywords, and
the technology's own name — so JavaScript, TypeScript, and Docker are correctly
identified from realistic input. Concretely, the four failing tests
(`test_javascript_detection`, `test_text_with_typescript_files`,
`test_devops_tool_detection`, `test_docker_compose_detection`) pass without
regressing the Python and database detection that already works.

**Branch name:** fix/148-detect-javascript-typescript

**Setup confirmation:** [X] App runs locally at localhost:5173

**Cohort ledger:** [X] Issue added to cohort ledger

## Week 8 — Reproduction & solution planning

**Reproduction commit link:** https://github.com/ezhong08/pathreview/commit/6a4895095da11530763975ed1cab5ade463892a1

**Reproduction summary:**
Based on the issue created a local test file `test_local.py` which calls `SkillExtractor.extract_skills()` with a JavaScript description (`Wrote index.js using const arrow functions and async/await callbacks`) and a TypeScript description (`Built app.tsx and types.ts with strict TypeScript interfaces`). Running the script via `.venv\Scripts\python.exe` returned `[]` for the JS input (no skills detected) and `['React']` for the TS input (TypeScript undetected, only React matched via `.tsx` in the React indicator list). This confirms the core issue: language detection relies only on the `filename` parameter for `.js`/`.ts` extensions and never scans the text itself for in-line file extensions, language keywords, or the technology names "JavaScript" and "TypeScript".

**PLAN.md link:** https://github.com/ezhong08/pathreview/blob/fix/148-detect-javascript-typescript/PLAN.md

**Walkthrough video (recommended):** [link to your Loom video, ≤2 min — recommended, not graded]

**Blockers or open questions:**
The fix needs to modify `_detect_languages()` in `ingestion/parsers/skill_extractor.py` to scan the text body itself for `.js`/`.ts`/`.jsx`/`.tsx` file extension mentions, JS/TS-specific keywords (`const`, `let`, `export`, `require` without requiring a trailing space), and the literal words "JavaScript" and "TypeScript". Similarly, `_detect_tools()` needs to match Dockerfile patterns (`FROM`, `RUN`, `CMD`) and docker-compose keywords (`services:`, `version:`). The main uncertainty is whether importing JS/TS keywords from the `JS_TS_KEYWORDS` set (already defined) into the detection logic is sufficient, or if additional heuristics are needed to avoid false positives from Python code that also uses `import`, `async`, `await`, `class` — two of these (`import` and `def`/`class`) overlap with Python keywords.

## Week 9 — Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:**
Three sub-tasks from PLAN.md are done, all in `_detect_languages()` in `ingestion/parsers/skill_extractor.py`:

- **Step 1 — In-text file extension detection.** The text body is now scanned with `re.finditer(r"\w+\.(js|jsx|ts|tsx)\b", text)`. The leading `\w+` avoids false-matching plain words ending in `.js`, and the trailing `\b` stops `.js` from swallowing `.jsx`. Matches are split into JavaScript (`.js`/`.jsx`) and TypeScript (`.ts`/`.tsx`) groups, each adding descriptive evidence, and the detected language is now chosen from these signals (plus the filename) rather than the filename alone — so `app.tsx`/`types.ts` in text correctly resolves to TypeScript.
- **Step 2 — Language name detection.** Case-insensitive checks for the literal words "javascript" and "typescript" in the text now trigger detection with their own evidence strings.
- **Step 3 — `require` pattern fix.** The import regex was changed from `r"\b(import|require)\s+"` to `r"\b(import|require)\s*\(?"`, so `require('fs')` with no trailing space now matches.

Test status: `test_javascript_detection` now passes, and the previously-passing Python/mixed-language tests still pass with no regressions (verified against the pre-change baseline).

**Next steps:**
Implement the remaining PLAN.md steps: step 4 (JS/TS keyword detection — using `const`/`let`/`var`/`export`/`function` with a ≥2 unique-keyword threshold, excluding keywords that overlap with Python) to make `test_text_with_typescript_files` pass, and step 5 (Docker detection in `_detect_tools()` — Dockerfile `FROM`/`RUN`/`CMD`/`EXPOSE`/`ENTRYPOINT` and docker-compose `version:`/`services:`/`build:`/`ports:` patterns) to make `test_devops_tool_detection` and `test_docker_compose_detection` pass. Then run the full suite and open the PR.

**Blockers:**
None. Note: `test_database_technology_detection` fails due to a pre-existing bug in the test itself (`skill_names = [s.name for s in skill_names]` references the variable before it is defined), unrelated to this fix.

---

### Check-in 2 (end of week)

**PR link:** [link to your submitted pull request]

**Branch:** fix/148-detect-javascript-typescript

**What you built:**
Taught `_detect_languages()` and `_detect_tools()` in `ingestion/parsers/skill_extractor.py` to inspect the text body itself instead of relying on the `filename` argument. Language detection now scans for in-text file extensions (`.js`/`.jsx`/`.ts`/`.tsx`), the literal words "JavaScript"/"TypeScript", JS-only keywords (`const`/`let`/`var`/`export`/`function` with a ≥2 unique-keyword threshold so Python-overlapping keywords don't false-trigger), and TypeScript-specific syntax (`interface`/`type`/`enum` declarations and typed annotations like `: string`); tool detection now recognizes Dockerfile instructions (`FROM`/`RUN`/`CMD`/`EXPOSE`/`ENTRYPOINT`) and docker-compose keys (`version:`/`services:`/`build:`/`ports:`) that never contain the literal word "docker". Along the way I tightened two regexes to kill false positives — the bare `import` pattern now requires JS-specific forms (`require(`, `import…from`, `import {`) so Python `import os` no longer reads as JavaScript, and the Python annotation pattern gained a `\b` so `id: string` no longer matches `str`.

**Tests added or updated:**
No new tests were needed — the fix is validated against the existing suite in `tests/unit/test_skill_extractor.py`, whose four previously-failing cases now pass: `test_javascript_detection` (JS from `require('fs')`), `test_text_with_typescript_files` (TS from `interface`/typed annotations), `test_devops_tool_detection` (Docker from Dockerfile `FROM`/`RUN`/`EXPOSE`), and `test_docker_compose_detection` (Docker from compose `version:`/`services:`). The Python and mixed-language tests continue to pass, confirming no regressions. `tests/unit/test_local.py` (the Week 8 reproduction script) now returns `['JavaScript']` and `['TypeScript', 'React']` for its two inputs instead of `[]` and `['React']`. One pre-existing failure remains untouched and out of scope: `test_database_technology_detection` references `skill_names` before it is assigned.

**Self-review confirmation:** [X] make check passes [X] make test-unit passes

**Draft PR feedback received from:** none
