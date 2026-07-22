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
Created `tests/unit/test_local.py` which calls `SkillExtractor.extract_skills()` with a JavaScript description (`Wrote index.js using const arrow functions and async/await callbacks`) and a TypeScript description (`Built app.tsx and types.ts with strict TypeScript interfaces`). Running the script via `.venv\Scripts\python.exe` returned `[]` for the JS input (no skills detected) and `['React']` for the TS input (TypeScript undetected, only React matched via `.tsx` in the React indicator list). This confirms the core issue: language detection relies only on the `filename` parameter for `.js`/`.ts` extensions and never scans the text itself for in-line file extensions, language keywords, or the technology names "JavaScript" and "TypeScript".

**PLAN.md link:** https://github.com/ezhong08/pathreview/blob/fix/148-detect-javascript-typescript/PLAN.md

**Walkthrough video (recommended):** [link to your Loom video, ≤2 min — recommended, not graded]

**Blockers or open questions:**
The fix needs to modify `_detect_languages()` in `ingestion/parsers/skill_extractor.py` to scan the text body itself for `.js`/`.ts`/`.jsx`/`.tsx` file extension mentions, JS/TS-specific keywords (`const`, `let`, `export`, `require` without requiring a trailing space), and the literal words "JavaScript" and "TypeScript". Similarly, `_detect_tools()` needs to match Dockerfile patterns (`FROM`, `RUN`, `CMD`) and docker-compose keywords (`services:`, `version:`). The main uncertainty is whether importing JS/TS keywords from the `JS_TS_KEYWORDS` set (already defined) into the detection logic is sufficient, or if additional heuristics are needed to avoid false positives from Python code that also uses `import`, `async`, `await`, `class` — two of these (`import` and `def`/`class`) overlap with Python keywords.
