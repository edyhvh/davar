# Remote

---

name:remote
agent: ask
description: Analyze recent commits + file changes by running git commands, detect target branch, and generate a ready-to-copy gh pr create --web command with semantic title and detailed bullet-point body

---

You are allowed — and expected — to run the following git commands yourself to gather accurate, up-to-date information:

- git status
- git branch -vv
- git log --oneline --graph --decorate -n 15 (or more if needed)
- git remote show origin
- git rev-parse --abbrev-ref --symbolic-full-name @{u} (to detect upstream tracking branch)
- Any other git commands that help you understand recent commits, changed files, and the target base branch

Use these outputs to:

1. Identify the current branch
2. Determine which remote branch it tracks / diverged from (usually origin/main or origin/master) → this will be your --base
3. Understand the commit messages since divergence
4. Examine the actual file changes/diffs to describe WHAT was implemented/modified/added/fixed/refactored/etc.

Then generate **ONLY** the complete `gh pr create` command ready to copy-paste, strictly following these rules:

- Always use `gh pr create --web` (opens the browser for final review/creation — safest option)
- Include `--base <target-branch>` using the actual base branch you determined from git (most commonly main or master)
- Do NOT use `--fill`
- Title must be semantic in conventional commits style: `<type>: <concise summary>`  
  (valid types: feat, fix, chore, refactor, docs, style, test, build, ci, perf, revert, etc.)
- Body: Markdown bullet points (3–8 maximum), each one describing the implemented changes with detail — based **exclusively** on commit messages AND the actual file diffs/changes (what was added, modified, removed, fixed, refactored, etc. in which files)
- Output **ONLY** the bash code block with the full command
- After the command, add this exact note:  
  "Run this AFTER `git push` if you haven't pushed yet. Review/edit in the browser before submitting."

If it appears the branch hasn't been pushed yet (no upstream or git status shows it), include this reminder at the beginning of the body (before the command):  
"First run: git push origin HEAD"

NEVER execute any gh commands yourself — only generate the command string for the user to run.
NEVER output any git command output or explanations — output ONLY the final gh pr create command block + the exact note.
