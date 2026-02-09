# Adding a Claude Code Skill

Reference guide for creating and installing Claude Code skills.

## How Skills Work

When you start a conversation, Claude Code automatically scans for skills in:

1. `~/.claude-code/skills/` (global - available across all projects)
2. `./.claude-code/skills/` (project-level - available only in that project)

Each skill lives in its own subdirectory and **must** contain a file named exactly `SKILL.md` (all caps). Claude reads all discovered `SKILL.md` files before responding and uses them when your request matches the skill's purpose.

## Prerequisites

Some skills include Python scripts that depend on third-party packages. Install any required packages before first use.

For the **leanix-from-sad** skill:

```bash
pip3 install python-docx
```

`python-docx` is needed to parse `.docx` SAD documents.

> **Tip:** Check the skill's `SKILL.md` and any `.py` files for `import` statements to identify dependencies.


## Installation Options

### Option A: Project-Level Skill (current preference)

Keeps the skill under source control alongside the project. Only available when working within this project.

```bash
# From the project root
mkdir -p .claude-code/skills/<skill-name>

# Copy or create the skill file (must be named SKILL.md)
cp my-skill.md .claude-code/skills/<skill-name>/SKILL.md

# Copy any supporting files the skill needs
cp helper_script.py .claude-code/skills/<skill-name>/
```

Resulting structure:

```
<project-root>/
├── .claude-code/
│   └── skills/
│       └── <skill-name>/
│           ├── SKILL.md
│           └── [optional supporting files]
└── [project files]
```

### Option B: Global Skill

Available across all projects. Lives outside any single repo so it is **not** under project source control by default.

```bash
mkdir -p ~/.claude-code/skills/<skill-name>

cp my-skill.md ~/.claude-code/skills/<skill-name>/SKILL.md
cp helper_script.py ~/.claude-code/skills/<skill-name>/
```

Resulting structure:

```
~/.claude-code/
└── skills/
    └── <skill-name>/
        ├── SKILL.md
        └── [optional supporting files]
```

> **Note:** If you want global skills under version control you could symlink `~/.claude-code/skills/` to a tracked directory, or manage it as its own repo.

## Creating the SKILL.md File

The `SKILL.md` file should describe:

- **Purpose** - what the skill does
- **Trigger patterns** - what kinds of requests should activate it
- **Instructions** - step-by-step directions for Claude to follow
- **Templates / examples** - any output formats, code patterns, or reference material

Keep it focused and specific. Claude will follow the instructions literally, so be explicit about expected inputs, outputs, and constraints.

## Multiple Skills

You can have any number of skills installed. Claude loads all of them:

```
.claude-code/skills/
├── skill-one/
│   └── SKILL.md
├── skill-two/
│   └── SKILL.md
└── skill-three/
    └── SKILL.md
```

## Verifying Installation

Start Claude Code and ask:

```
"What skills do you have available?"
```

Claude will list all discovered skills and their purposes.

## Updating a Skill

Edit the `SKILL.md` file directly. Claude picks up changes on the next conversation - no restart required.

## Sharing Skills with a Team

For project-level skills, they are already shared via the repo. For global skills:

```bash
# Package
cd ~/.claude-code/skills
tar -czf <skill-name>.tar.gz <skill-name>/

# Recipient extracts to their own skills directory
cd ~/.claude-code/skills
tar -xzf <skill-name>.tar.gz
```
