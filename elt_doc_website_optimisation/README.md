# ELT Doc Website Optimisation

**Professional website optimisation assessment tool** that evaluates websites against comprehensive specification requirements and produces client-ready deliverables.

## Quick Start

### Setup (First Time Only)

```bash
cd elt_doc_website_optimisation
uv sync
uv run playwright install chromium
```

### Generate Client Deliverable

```bash
# Stage 1: Run assessment
uv run elt-doc-website-optimisation run

# Stage 2: Generate final deliverable
uv run python src/elt_doc_website_optimisation/generate_final_deliverable.py
```

**Output:** `~/Downloads/website_optimisation_COMPLETE_FINAL_DELIVERABLE.docx`

---

## What You Get

The final deliverable is a **self-contained Word document** (1.1 MB) with:

| Section | Content |
|---------|---------|
| **Executive Summary** | Scores, strengths, critical issues |
| **Assessment Overview** | Scores table, severity summary |
| **Technical Review** | Performance, Security (with .htaccess fix code), Hosting |
| **UX & Navigation** | Findings with **embedded screenshots** |
| **Content & Messaging** | Word counts, CTA analysis, outdated content |
| **SEO Review** | On-page table, technical SEO, broken links |
| **Plugin & Theme Audit** | Full plugin lists (31 plugins), versions |
| **Analytics & Tracking** | GA4 status, cookie banner GDPR issues |
| **Priority Action Plan** | Critical/High/Medium + day-by-day roadmap |
| **Manual Review Checklist** | 25+ checkbox items |
| **Appendices (A-H)** | **73 complete findings** with full evidence |

### Key Features

✅ **Self-contained** - Screenshots embedded, no external references  
✅ **Evidence-based** - Every finding includes specific evidence  
✅ **Actionable** - Every problem has solution with effort/cost estimate  
✅ **Professional** - Security fix code, cost estimates, implementation roadmap  
✅ **Complete** - All 58 specification requirements addressed  

---

## Configuration

Assessment configs are in `assessments/` directory:

```
assessments/
├── cnltd_assessment.yaml        # Current client
└── template_assessment.yaml     # Copy for new clients
```

### Create New Client Config

```bash
# Copy template
cp assessments/template_assessment.yaml assessments/acme_assessment.yaml

# Edit with client details:
# - Website URLs
# - WordPress credentials path  
# - Output path
```

### Configuration File Format

```yaml
assessment:
  name: "Client Name Website Optimisation"
  description: "Assess website on laptop and phone"

urls:
  - url: "https://client-website.com/"
    name: "Client Homepage"
    category: "assess"

  - url: "https://client-website.com/wp-admin/"
    name: "WordPress Admin"
    category: "information"

Documents:
  - name: "spec_part1.jpeg"
    folder: "~/Downloads"
    description: "Specification Part 1"
    sequence: "1"
    category: "requirement"

credentials: "../../.credentials/client_wordpress.yaml"

output:
  folder: "~/Downloads"
  name: "client_assessment.docx"
```

---

## Additional Commands

### Preview Configuration

```bash
uv run elt-doc-website-optimisation preview
```

### Custom Config File

```bash
uv run elt-doc-website-optimisation run --config assessments/acme_assessment.yaml
```

---

## Project Structure

```
elt_doc_website_optimisation/
├── assessments/                     # Client configs
│   ├── cnltd_assessment.yaml
│   └── template_assessment.yaml
│
├── src/elt_doc_website_optimisation/
│   ├── cli.py                       # Command-line interface
│   ├── assessment.py                # Stage 1: Assessment orchestrator
│   ├── generate_final_deliverable.py # Stage 2: Final report
│   ├── analyzers/                   # 9 assessment modules
│   └── ...
│
└── README.md                        # This documentation
```

---

## Technical Details

### 9 Assessment Analyzers

| Analyzer | What It Checks |
|----------|---------------|
| **Technical** | Response times, SSL, security headers |
| **UX & Navigation** | Navigation, accessibility, mobile |
| **Content** | Word count, CTAs, outdated content |
| **SEO** | On-page, technical, content SEO |
| **WordPress** | Plugin detection, theme analysis |
| **WordPress Admin** | Admin API login, detailed plugin data |
| **Analytics** | GA4, GTM, cookie compliance |
| **Visual** | Color contrast, font sizes, link styling |
| **Crawler** | Multi-page SEO analysis |

### Specification Coverage

| Spec Section | Requirements | Coverage |
|--------------|--------------|----------|
| 1. Technical Review | 11 | 100% |
| 2. UX & Navigation | 11 | 100% |
| 3. Content & Messaging | 10 | 100% |
| 4. SEO Review | 12 | 100% |
| 5. Plugin & Theme Audit | 10 | 100% |
| 6. Analytics & Tracking | 5 | 100% |
| **TOTAL** | **59** | **100%** |

### Data Sources

| Source | Access Method | Data Captured |
|--------|---------------|---------------|
| **Website HTML** | HTTP GET + BeautifulSoup | Content, structure, meta tags |
| **WordPress Admin** | HTTP POST login + scraping | Version, plugins, theme |
| **Screenshots** | Playwright browser automation | Desktop (1920×1080), Mobile (375×667) |
| **Multi-page Crawl** | HTTP requests + link extraction | Duplicate titles, missing H1 tags |

---

## Dependencies

```toml
[project]
dependencies = [
    "pyyaml>=6.0",           # YAML config parsing
    "requests>=2.31.0",      # HTTP requests
    "python-docx>=1.2.0",    # Word document generation
    "playwright>=1.40.0",    # Browser automation
    "beautifulsoup4>=4.12.0", # HTML parsing
    "lxml>=5.0.0",           # XML/HTML parser
    "Pillow>=10.0.0",        # Image processing
    "httpx>=0.25.0",         # Async HTTP
    "click>=8.0.0",          # CLI framework
]
```

---

## License

Proprietary - For client consulting use.
