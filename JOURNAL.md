## Week 7 — Issue selection

**Issue link:** https://github.com/ascherj/pathreview/issues/148

**Issue title:** Skill extractor fails to detect JavaScript and TypeScript

**Tier:** [X] Tier 1 [ ] Tier 2 [ ] Tier 3

**Problem summary:**
*What the issue is:* The skill extractor
(`ingestion/parsers/skill_extractor.py`) is supposed to read a chunk of code or a
plain-English description of someone's work and report which technologies it sees.
It does this reliably for Python but is essentially blind to the JavaScript/
TypeScript family — text that clearly describes JS work returns nothing, and TS
samples only ever come back as "React".

*What is currently broken:* The `extract_skills()` entry point, via its
`_detect_languages()` helper, only looks at the passed-in `filename` for `.js`/`.ts`
extensions and never scans the text itself, its import/require pattern requires a
space after the keyword so `require('fs')` slips through, and it never recognizes
the literal words "JavaScript" or "TypeScript". As a result `.tsx`/`.ts` mentions
get picked up only incidentally by the React detector. A related DevOps gap: tool
detection matches the literal string "docker", which never appears in Dockerfile
(`FROM`/`RUN`) or docker-compose (`services:`/`version:`) content, so those go
undetected too.

*What a successful fix accomplishes:* Language and tool detection inspect the actual
text for family-specific signals — in-text file extensions, language keywords, and
the technology's own name — so JavaScript, TypeScript, and Docker are correctly
identified from realistic input. Concretely, the four failing tests
(`test_javascript_detection`, `test_text_with_typescript_files`,
`test_devops_tool_detection`, `test_docker_compose_detection`) pass without
regressing the Python and database detection that already works.

**Branch name:** fix/148-detect-javascript-typescript

**Setup confirmation:** [X] App runs locally at localhost:5173

**Cohort ledger:** [X] Issue added to cohort ledger
