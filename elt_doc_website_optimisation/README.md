# ELT Doc Website Optimisation

Website optimisation assessment tool that evaluates websites across multiple dimensions:

- **Technical Review** - Performance, Security, Hosting/Infrastructure
- **UX & Navigation** - Navigation flow, Accessibility, Mobile friendliness
- **Content & Messaging** - Tone, CTAs, Outdated content
- **SEO Review** - On-page, Technical SEO (broken links, robots.txt, sitemap)
- **Plugin & Theme Audit** - WordPress plugins, theme analysis, admin API integration
- **Analytics & Tracking** - Google Analytics, Tag Manager, Cookie compliance
- **Visual Analysis** - Color contrast, font sizes, link styling
- **Multi-Page Crawl** - SEO across multiple pages (not just homepage)

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

### Run Assessment (Stage 1: Python)

Run the full website assessment and generate a Word report:

```bash
uv run elt-doc-website-optimisation run
```

This produces: `~/Downloads/website_optimisation_assessment.docx`

### Enhance Report (Stage 2: LLM)

Prepare the report for LLM-based enhancement:

```bash
uv run elt-doc-website-optimisation enhance ~/Downloads/website_optimisation_assessment.docx
```

This:
1. Extracts structured findings from the Python report
2. Creates an enhancement prompt (saved to `~/Downloads/enhancement_prompt.txt`)
3. The prompt includes all findings + instructions for LLM

**Next:** Submit the prompt file to your LLM API (Claude, GPT-4, etc.) to generate the final client-ready document.

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

---

## How It Works

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  HUMAN (You)                                                    │
│  - Provides specification (JPEG images)                        │
│  - Provides credentials (.yaml file)                           │
│  - Runs: uv run elt-doc-website-optimisation run               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PYTHON CODE (Deterministic - No LLM)                           │
│                                                                 │
│  Step 1: config_loader.py                                       │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ - Reads YAML config                                        │ │
│  │ - Loads credentials (username/password)                   │ │
│  │ - Parses requirement documents (sequence order)           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  Step 2: assessment.py (Orchestrator)                          │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ For each website:                                          │ │
│  │   → Call 9 analyzer modules                                │ │
│  │   → Collect findings                                       │ │
│  │   → Calculate score                                        │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  Step 3: Analyzer Modules (9 sections)                         │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ technical.py        → HTTP requests, headers              │ │
│  │ ux_navigation.py    → Playwright browser automation       │ │
│  │ content.py          → BeautifulSoup HTML parsing          │ │
│  │ seo.py              → BeautifulSoup HTML parsing          │ │
│  │ seo_technical.py    → HTTP requests (links, robots.txt)   │ │
│  │ wordpress.py        → HTTP requests (WP detection)        │ │
│  │ wordpress_admin.py  → HTTP POST login, scrape admin pages │ │
│  │ analytics.py        → BeautifulSoup HTML parsing          │ │
│  │ visual.py           → Color contrast, font sizes          │ │
│  │ crawler.py          → Multi-page site crawl               │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  Step 4: report/generator.py                                    │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ - Creates Word document (.docx)                           │ │
│  │ - Uses python-docx library                                │ │
│  │ - Inserts findings, screenshots, recommendations          │ │
│  │ - Generates Manual Review Checklist                       │ │
│  │ - SAVES to: ~/Downloads/website_optimisation_assessment…  │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  OUTPUT: Word Document                                          │
│  - Generated by PYTHON CODE (not LLM)                          │
│  - Deterministic: same input = same output                     │
│  - No AI/LLM used in report generation                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Two-Stage Workflow (Multi-Hop)

### Stage 1: Python Assessment (Deterministic)

```bash
uv run elt-doc-website-optimisation run
```

**What Python does:**
- ✅ Assesses all 6 specification sections
- ✅ Captures WordPress admin data (version, plugins)
- ✅ Detects Google Analytics
- ✅ Takes screenshots
- ✅ Generates findings with evidence
- ✅ Creates recommendations (template-based)

**Output:** `~/Downloads/website_optimisation_assessment.docx`

---

### Stage 2: LLM Enhancement (Narrative Polish)

```bash
uv run elt-doc-website-optimisation enhance ~/Downloads/website_optimisation_assessment.docx
```

**What this does:**
1. Extracts structured findings from Python report
2. Creates enhancement prompt (`~/Downloads/enhancement_prompt.txt`)
3. Prompt includes all findings + instructions for LLM

**Next:** Submit the prompt to your LLM API (Claude, GPT-4, etc.)

**What LLM adds:**
- ✨ Executive Summary (narrative, 3-4 paragraphs)
- ✨ Requirements Traceability Matrix (proof all specs covered)
- ✨ Data Sources section (proof credentials used)
- ✨ Priority Action Plan (grouped by effort/impact)
- ✨ Professional tone and business context
- ✨ Connected insights across findings

**Output:** `~/Downloads/enhanced_report.docx`

---

### When to Use Each Stage

| Scenario | Stage 1 Only | Stage 1 + Stage 2 |
|----------|--------------|-------------------|
| Internal audit | ✅ Sufficient | Overkill |
| Technical team review | ✅ Fine | Nice-to-have |
| **Client delivery** | ⚠️ Functional | ✅ **Recommended** |
| Board/executive report | ❌ Too technical | ✅ **Required** |
| Premium consulting | ❌ Basic | ✅ **Expected** |

---

### Prompt Engineering

The enhancement prompt is stored in: `prompts/report_enhancement.txt`

**Key instructions to LLM:**
- Maintain factual accuracy (don't change findings)
- Add business context and narrative
- Create Requirements Traceability Matrix
- Document data sources used (WordPress, Analytics)
- Group recommendations by priority
- Professional, constructive tone

**You can customize** this prompt for your specific client needs.

### Requirements-Driven Architecture

The assessment framework was built directly from the **Specification Documents** (JPEG images in `~/Downloads`). Each section of the specification maps to a Python analyzer module:

| Specification Section | Python Module | Implementation |
|----------------------|---------------|----------------|
| **1. Technical Review** | `analyzers/technical.py` | Performance (response time), Security (HTTPS, headers), Hosting (server info) |
| **2. UX & Navigation** | `analyzers/ux_navigation.py` | Navigation flow (`<nav>` elements), Accessibility (alt tags, headings, ARIA), Mobile (viewport meta) |
| **3. Content & Messaging** | `analyzers/content.py` | Tone (word count, value keywords), CTAs (pattern matching), Outdated content (year detection) |
| **4. SEO Review** | `analyzers/seo.py` + `seo_technical.py` | On-page (title, meta, headings), Technical (broken links, robots.txt, sitemap, redirects) |
| **5. Plugin & Theme Audit** | `analyzers/wordpress.py` + `wordpress_admin.py` | WordPress detection, Plugin scanning, Theme ID, **Admin API login** for versions |
| **6. Analytics & Tracking** | `analyzers/analytics.py` | GA4/UA detection, GTM containers, Cookie banner compliance |

### Additional Capabilities (Beyond Spec)

| Feature | Python Module | Description |
|---------|---------------|-------------|
| Visual Analysis | `analyzers/visual.py` | Color contrast (WCAG), font sizes, link styling |
| Multi-Page Crawl | `analyzers/crawler.py` | Crawls 10 pages for duplicate titles, missing H1, thin content |
| WordPress Admin API | `analyzers/wordpress_admin.py` | Login with credentials, fetch WP version, plugin list with versions |
| Manual Review Checklist | `report/generator.py` | Generated section with credentials, checklist, notes area |

### Assessment Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│  1. Load Configuration (config_loader.py)                       │
│     - Parse websites (category: assess)                         │
│     - Parse information URLs (category: information)            │
│     - Load credentials for WordPress admin                      │
│     - Load requirement documents (sequence ordered)             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. For Each Website (assessment.py)                            │
│     ┌─────────────────────────────────────────────────────┐    │
│     │ [1] TechnicalAnalyzer.fetch()                       │    │
│     │     - HTTP request, measure response time           │    │
│     │     - Capture headers for security analysis         │    │
│     └─────────────────────────────────────────────────────┘    │
│     ┌─────────────────────────────────────────────────────┐    │
│     │ [2] UXNavigationAnalyzer.fetch()                    │    │
│     │     - Playwright browser automation                 │    │
│     │     - Screenshot: Desktop (1920×1080)               │    │
│     │     - Screenshot: Mobile (375×667)                  │    │
│     │     - Capture HTML for analysis                     │    │
│     └─────────────────────────────────────────────────────┘    │
│     ┌─────────────────────────────────────────────────────┐    │
│     │ [3-6] Analyzers (Content, SEO, WordPress, Analytics)│    │
│     │     - BeautifulSoup HTML parsing                    │    │
│     │     - Pattern matching for requirements             │    │
│     │     - Generate Findings (Pass/Warning/Fail)         │    │
│     │     - Generate Recommendations (priority/effort)    │    │
│     └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. Information URLs (Reference Only)                           │
│     - WordPress admin: Credentials available for manual login   │
│     - Google Analytics: Manual review (OAuth required)          │
│     - Not automated - logged for assessor reference             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. Generate Report (report/generator.py)                       │
│     - Title page with assessment name                           │
│     - Executive summary with severity counts                    │
│     - Per-website sections with:                                │
│       • Findings (status icons, severity colors)                │
│       • Screenshots (desktop + mobile)                          │
│       • Recommendations (priority indicators)                   │
│     - Overall recommendations section                           │
│     - Save to: ~/Downloads/website_optimisation_assessment.docx │
└─────────────────────────────────────────────────────────────────┘
```

### Requirement Capture Implementation

Each analyzer implements the specific checks from the specification:

**Example: Technical Review → Security (Specification 1.b)**

```python
# analyzers/technical.py - _check_security()

# Spec: "Check WordPress version + theme versions + plugin versions"
# Spec: "Review SSL configuration"
# Spec: "Note any publicly visible errors / security warnings"

if self.url.startswith("https://"):
    findings.append(Finding(..., status=Status.PASS, ...))
else:
    findings.append(Finding(..., status=Status.FAIL, ...))

# Check security headers
security_headers = [
    "Strict-Transport-Security",
    "X-Content-Type-Options",
    "X-Frame-Options",
    "Content-Security-Policy",
]
missing_headers = [h for h in security_headers if h not in self.headers]
```

**Example: SEO Review → On-page SEO (Specification 4.a)**

```python
# analyzers/seo.py - _check_onpage_seo()

# Spec: "Metadata (titles, descriptions)"
title = soup.find("title")
meta_desc = soup.find("meta", attrs={"name": "description"})

# Spec: "Heading structure"
h1_tags = soup.find_all("h1")
h2_tags = soup.find_all("h2")

# Spec: "Image alt text"
images_without_alt = [img for img in images if not img.get("alt")]
```

### Information URLs Usage

The `information` category URLs are **not automatically assessed** but are:

1. **Logged in preview** - Shown when running `uv run elt-doc-website-optimisation preview`
2. **Available for manual reference** - Assessor can manually check:
   - WordPress admin (`/wp-admin/`) for plugin/theme details
   - Google Analytics for traffic data and tracking verification
3. **Credentials provided** - WordPress login available in `.credentials/website_optimisation.yaml`

### Extending the Framework

To add new requirements:

1. **Update specification documents** in `~/Downloads`
2. **Add analyzer checks** in the appropriate module (or create new)
3. **Update config** if new URLs or credentials needed
4. **Re-run assessment** - new checks automatically included in report

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
