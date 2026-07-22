"""
It failed in local to detect the TypeScript and JavaScript.
Output:
[]
['React']
"""

from ingestion.parsers.skill_extractor import SkillExtractor

e = SkillExtractor()
print(e.extract_skills('Wrote index.js using const arrow functions and async/await callbacks'))
# observed: []
print([d.name for d in e.extract_skills('Built app.tsx and types.ts with strict TypeScript interfaces')])
# observed: ['React']  (no TypeScript, no JavaScript)
