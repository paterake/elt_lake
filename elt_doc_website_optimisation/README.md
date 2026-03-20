# ELT Doc Website Optimisation

Website optimisation assessment tool that evaluates websites across multiple dimensions:

- **Technical Review** - Performance, Security, Hosting/Infrastructure
- **UX & Navigation** - Navigation flow, Accessibility, Mobile friendliness
- **Content & Messaging** - Tone, CTAs, Outdated content
- **SEO Review** - On-page, Technical, Content SEO
- **Plugin & Theme Audit** - WordPress plugins and theme analysis
- **Analytics & Tracking** - Google Analytics, Tag Manager, Cookie compliance

## Setup

```bash
cd elt_doc_website_optimisation
uv sync
```

## Usage

### Preview Configuration

View the current assessment configuration:

```bash
uv run elt-doc-website-optimisation preview
```

### Run Assessment

Run the full website assessment and generate a Word report:

```bash
uv run elt-doc-website-optimisation run
```

### Custom Config File

Specify a different configuration file:

```bash
uv run elt-doc-website-optimisation run --config /path/to/config.yaml
uv run elt-doc-website-optimisation preview --config /path/to/config.yaml
```

## Configuration

Edit `config/website_optimisation.yaml` to configure:

- **Websites to assess** - URLs with category `assess`
- **Information URLs** - Reference URLs (e.g., WordPress admin, Analytics)
- **Requirements** - Specification documents in `~/Downloads`
- **Credentials** - Path to credentials YAML file
- **Output** - Where to save the generated report

### Example Configuration

```yaml
assessment:
  name: "Website Optimisation"
  description: "Assess websites on laptop and phone"

urls:
  - url: "https://example.com/"
    name: "Example Site"
    category: "assess"

  - url: "https://example.com/wp-admin/"
    name: "WordPress Admin"
    category: "information"

Documents:
  - name: "spec_part1.jpeg"
    folder: "~/Downloads"
    description: "Specification Part 1"
    sequence: "1"
    category: "requirement"

credentials: "../../.credentials/website_optimisation.yaml"

output:
  folder: "~/Downloads"
  name: "assessment_report.docx"
```

## Output

The assessment generates a Word document (`*.docx`) containing:

- Executive summary with overall scores
- Detailed findings per website
- Screenshots (desktop and mobile viewports)
- Prioritised recommendations
- Next steps

## Project Structure

```
elt_doc_website_optimisation/
├── config/
│   └── website_optimisation.yaml    # Assessment configuration
├── src/elt_doc_website_optimisation/
│   ├── cli.py                       # Command-line interface
│   ├── config_loader.py             # YAML config parser
│   ├── assessment.py                # Main orchestrator
│   ├── screenshot.py                # Playwright screenshots
│   ├── models/                      # Data models
│   ├── analyzers/                   # Analysis modules
│   │   ├── technical.py
│   │   ├── ux_navigation.py
│   │   ├── content.py
│   │   ├── seo.py
│   │   ├── wordpress.py
│   │   └── analytics.py
│   └── report/
│       └── generator.py             # Word document generator
└── tests/
```
