# Remote

---

name:remote
agent: ask
description: Analyze recent commits and generate a ready-to-copy gh pr create --web command with semantic title and concise bullet-point body

---

Analyze the recent git commits on the current branch (since the last push or divergence from remote/main).

Generate **ONLY** the complete `gh pr create` command ready to copy-paste, strictly following these rules:

- Always use `gh pr create --web` (opens the browser for final review/creation — safest option)
- Do NOT use `--fill`
- Title must be semantic in conventional commits style: `<type>: <concise summary>`  
  (valid types: feat, fix, chore, refactor, docs, style, test, build, ci, perf, revert, etc.)
- Body: Markdown bullet points (3–8 maximum), each one short and on a single line, based **ONLY** on actual commit messages and changes
- Base the title and bullets **exclusively** on real git commit messages / diff
- Output **ONLY** the bash code block with the full command
- After the command, add this exact note:  
  "Run this AFTER `git push` if you haven't pushed yet. Review/edit in the browser before submitting."

If the branch hasn't been pushed yet, include a reminder at the beginning of the body (before the command):  
"First run: git push origin HEAD"

NEVER execute any git or gh commands yourself. Only output the command string.
