---
name: "git-commit-push"
description: "Stage, commit, and push current repo changes. Invoke when user asks to git-commit-push or similar."
---

# Git Commit & Push (Auto Message)

## Purpose

Automatically stage, commit, and push changes in the current Git repository when the user explicitly asks you to do so (e.g. “git-commit-push”). The commit message should summarize the changes in a single concise line, maximum 50 characters.

## When to Use

- User says “git-commit-push”
- User says “commit and push the changes” or similar
- User clearly indicates they want you to create a commit and push to the current branch

Do **not** use this if the user has not explicitly requested a commit/push.

## Workflow

1. **Ensure you are at the workspace root**

   - Use the current Trae workspace root as the Git working directory.

2. **Check status**

   - Run:

     ```bash
     git status -sb
     ```

   - If the working tree is clean (no modified/added files), tell the user there is nothing to commit and stop.

3. **Review changes**

   - Run:

     ```bash
     git diff
     git diff --cached
     ```

   - Use these diffs to understand what changed (files, features, docs).

4. **Generate a commit message (max 50 chars)**

   - Summarize the changes in one short, imperative sentence.
   - Maximum 50 characters.
   - Present tense, no trailing period.
   - Examples:
     - `update SAD pipeline README`
     - `add orchestrated SAD to LeanIX skill`
     - `fix leanix inventory lookup`

5. **Stage changes**

   - Stage all relevant files (usually all modified/untracked files) with:

     ```bash
     git add -A
     ```

   - If the user previously indicated certain files should not be committed, respect that and avoid adding them.

6. **Commit**

   - Run:

     ```bash
     git commit -m "<COMMIT_MESSAGE>"
     ```

   - Replace `<COMMIT_MESSAGE>` with the generated message (<= 50 chars).

7. **Push to current branch**

   - Push the commit to the remote associated with the current branch:

     ```bash
     git push
     ```

   - If push fails (e.g. no upstream set or non-fast-forward), report the error to the user instead of retrying blindly.

8. **Report back**

   - Show the final `git status -sb` output.
   - Tell the user which branch was pushed and the commit summary.

## Notes

- Only perform these actions when explicitly asked to commit/push.
- Keep the commit message focused and under 50 characters so it is readable in `git log --oneline`.
