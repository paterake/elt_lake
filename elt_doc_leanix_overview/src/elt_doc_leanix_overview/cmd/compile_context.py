#!/usr/bin/env python3
"""
Compile a full LLM prompt by combining:
1. The Master Prompt (Instructions)
2. The Reference Overview Template (Structure)
3. All Individual Integration XMLs (Input)
"""
import sys
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Compile Overview LLM Prompt')
    script_dir = Path(__file__).parent
    default_prompt = script_dir.parent / 'prompts' / 'consolidate_overview.md'

    # Find the templates directory
    project_root = script_dir.parent.parent.parent.parent
    if not (project_root / 'pyproject.toml').exists():
        project_root = script_dir.parent.parent.parent
    template_path = project_root / 'elt_doc_leanix_overview' / 'templates' / 'integration_overview.xml'
    if not template_path.exists():
        template_path = project_root / 'templates' / 'integration_overview.xml'

    parser.add_argument('xml_dir', help='Directory containing individual integration XML files')
    parser.add_argument('--prompt', default=str(default_prompt), help='Path to master prompt file')
    parser.add_argument('--template', default=str(template_path), help='Path to reference overview template')
    parser.add_argument('--existing', help='Path to existing overview XML (for updates)')
    args = parser.parse_args()

    prompt_path = Path(args.prompt)
    xml_dir = Path(args.xml_dir)
    template_path = Path(args.template)

    if not prompt_path.exists():
        print(f"Error: Prompt file {prompt_path} not found", file=sys.stderr)
        sys.exit(1)

    if not xml_dir.is_dir():
        print(f"Error: {xml_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    print(f"Compiling overview prompt from {xml_dir}...", file=sys.stderr)

    # Read master prompt
    with open(prompt_path, 'r', encoding='utf-8') as f:
        master_prompt = f.read()

    # Read reference template
    template_text = "Reference template not found."
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            template_text = f.read()

    # Read all individual integration XMLs
    xml_files = sorted(xml_dir.glob('*.xml'))
    if not xml_files:
        print(f"Error: No XML files found in {xml_dir}", file=sys.stderr)
        sys.exit(1)

    # Skip any file that looks like an overview (contains wide Workday box)
    integration_xmls = []
    for xf in xml_files:
        content = xf.read_text(encoding='utf-8')
        # Simple heuristic: overview has a very wide Workday box (width >= 800)
        if 'width="1440"' in content or 'width="1600"' in content or 'width="1920"' in content:
            print(f"  Skipping overview file: {xf.name}", file=sys.stderr)
            continue
        integration_xmls.append((xf.name, content))

    if not integration_xmls:
        print(f"Error: No individual integration XMLs found (all appear to be overviews)", file=sys.stderr)
        sys.exit(1)

    print(f"  Found {len(integration_xmls)} integration XML files", file=sys.stderr)

    # Read existing overview if updating
    existing_text = ""
    if args.existing:
        existing_path = Path(args.existing)
        if existing_path.exists():
            with open(existing_path, 'r', encoding='utf-8') as f:
                existing_text = f.read()
            print(f"  Including existing overview for update: {existing_path.name}", file=sys.stderr)

    # Assemble
    integration_sections = []
    for name, content in integration_xmls:
        integration_sections.append(f"### {name}\n\n```xml\n{content}\n```")

    integrations_text = "\n\n".join(integration_sections)

    full_output = f"""{master_prompt}

---

## CONTEXT DATA

### Reference Overview Template
The following XML is a reference for the overview structure and layout. Use it as a structural guide.

```xml
{template_text}
```

---

## INPUT DATA

### Individual Integration XML Files ({len(integration_xmls)} files)

{integrations_text}
"""

    if existing_text:
        full_output += f"""
---

### Existing Overview XML (Update Mode)
The following is the existing overview XML. Preserve its content and add new integrations.

```xml
{existing_text}
```
"""

    # Output to stdout
    print(full_output)


if __name__ == '__main__':
    main()
