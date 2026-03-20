"""SEO Review analyzer - On-page, Technical, Content SEO."""

import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from ..models.assessment import Finding, Recommendation, SectionResult, Severity, Status


class SEOAnalyzer:
    """Analyze SEO aspects of a website."""

    def __init__(self, url: str, html: str = ""):
        self.url = url
        self.html = html

    def analyze(self) -> SectionResult:
        """Run all SEO analysis checks."""
        result = SectionResult(name="SEO Review")

        if not self.html:
            result.findings.append(Finding(
                section="SEO Review",
                subsection="General",
                description="No HTML content to analyze",
                severity=Severity.MEDIUM,
                status=Status.NOT_CHECKED,
                url=self.url,
            ))
            return result

        # On-page SEO
        result.findings.extend(self._check_onpage_seo())
        result.recommendations.extend(self._recommend_onpage())

        # Technical SEO
        result.findings.extend(self._check_technical_seo())
        result.recommendations.extend(self._recommend_technical())

        # Content SEO
        result.findings.extend(self._check_content_seo())
        result.recommendations.extend(self._recommend_content())

        return result

    def _check_onpage_seo(self) -> list[Finding]:
        """Check on-page SEO elements."""
        findings = []

        try:
            soup = BeautifulSoup(self.html, "lxml")

            # Title tag
            title = soup.find("title")
            if not title:
                findings.append(Finding(
                    section="SEO Review",
                    subsection="On-page SEO",
                    description="Missing title tag",
                    severity=Severity.HIGH,
                    status=Status.FAIL,
                    evidence="No <title> tag",
                    url=self.url,
                ))
            else:
                title_text = title.get_text(strip=True)
                title_len = len(title_text)
                if title_len < 30:
                    findings.append(Finding(
                        section="SEO Review",
                        subsection="On-page SEO",
                        description=f"Title too short: {title_len} chars (recommended: 50-60)",
                        severity=Severity.MEDIUM,
                        status=Status.WARNING,
                        evidence=f"Title: {title_text[:50]}",
                        url=self.url,
                    ))
                elif title_len > 60:
                    findings.append(Finding(
                        section="SEO Review",
                        subsection="On-page SEO",
                        description=f"Title too long: {title_len} chars (recommended: 50-60)",
                        severity=Severity.MEDIUM,
                        status=Status.WARNING,
                        evidence=f"Title: {title_text[:50]}...",
                        url=self.url,
                    ))
                else:
                    findings.append(Finding(
                        section="SEO Review",
                        subsection="On-page SEO",
                        description=f"Good title length: {title_len} chars",
                        severity=Severity.LOW,
                        status=Status.PASS,
                        evidence=f"Title: {title_text[:50]}",
                        url=self.url,
                    ))

            # Meta description
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if not meta_desc:
                findings.append(Finding(
                    section="SEO Review",
                    subsection="On-page SEO",
                    description="Missing meta description",
                    severity=Severity.HIGH,
                    status=Status.FAIL,
                    evidence="No meta description",
                    url=self.url,
                ))
            else:
                desc_content = meta_desc.get("content", "")
                desc_len = len(desc_content)
                if desc_len < 120:
                    findings.append(Finding(
                        section="SEO Review",
                        subsection="On-page SEO",
                        description=f"Meta description too short: {desc_len} chars",
                        severity=Severity.MEDIUM,
                        status=Status.WARNING,
                        evidence=f"Description: {desc_content[:50]}",
                        url=self.url,
                    ))
                elif desc_len > 160:
                    findings.append(Finding(
                        section="SEO Review",
                        subsection="On-page SEO",
                        description=f"Meta description too long: {desc_len} chars",
                        severity=Severity.MEDIUM,
                        status=Status.WARNING,
                        evidence=f"Description: {desc_content[:50]}...",
                        url=self.url,
                    ))
                else:
                    findings.append(Finding(
                        section="SEO Review",
                        subsection="On-page SEO",
                        description=f"Good meta description length: {desc_len} chars",
                        severity=Severity.LOW,
                        status=Status.PASS,
                        evidence=f"Description: {desc_content[:50]}",
                        url=self.url,
                    ))

            # Heading structure
            h1_tags = soup.find_all("h1")
            h2_tags = soup.find_all("h2")
            
            if len(h1_tags) == 0:
                findings.append(Finding(
                    section="SEO Review",
                    subsection="On-page SEO",
                    description="Missing H1 heading",
                    severity=Severity.HIGH,
                    status=Status.FAIL,
                    evidence="No H1 tag",
                    url=self.url,
                ))
            elif len(h1_tags) > 1:
                findings.append(Finding(
                    section="SEO Review",
                    subsection="On-page SEO",
                    description=f"Multiple H1 headings: {len(h1_tags)}",
                    severity=Severity.MEDIUM,
                    status=Status.WARNING,
                    evidence=f"{len(h1_tags)} H1 tags",
                    url=self.url,
                ))
            else:
                findings.append(Finding(
                    section="SEO Review",
                    subsection="On-page SEO",
                    description="Single H1 heading present",
                    severity=Severity.LOW,
                    status=Status.PASS,
                    evidence="One H1 tag",
                    url=self.url,
                ))

            if len(h2_tags) == 0:
                findings.append(Finding(
                    section="SEO Review",
                    subsection="On-page SEO",
                    description="No H2 headings found",
                    severity=Severity.MEDIUM,
                    status=Status.WARNING,
                    evidence="No H2 tags",
                    url=self.url,
                ))

            # Image alt text
            images = soup.find_all("img")
            images_without_alt = [img for img in images if not img.get("alt")]
            if images_without_alt:
                findings.append(Finding(
                    section="SEO Review",
                    subsection="On-page SEO",
                    description=f"{len(images_without_alt)} image(s) missing alt text",
                    severity=Severity.MEDIUM,
                    status=Status.WARNING,
                    evidence=f"Missing alt on {len(images_without_alt)} images",
                    url=self.url,
                ))

            # URL structure
            parsed = urlparse(self.url)
            path = parsed.path
            if len(path) > 100:
                findings.append(Finding(
                    section="SEO Review",
                    subsection="On-page SEO",
                    description=f"URL path too long: {len(path)} chars",
                    severity=Severity.LOW,
                    status=Status.WARNING,
                    evidence=f"URL: {path[:50]}...",
                    url=self.url,
                ))
            if "_" in path:
                findings.append(Finding(
                    section="SEO Review",
                    subsection="On-page SEO",
                    description="URL contains underscores (use hyphens instead)",
                    severity=Severity.LOW,
                    status=Status.WARNING,
                    evidence=f"URL: {path}",
                    url=self.url,
                ))

        except Exception as e:
            findings.append(Finding(
                section="SEO Review",
                subsection="On-page SEO",
                description=f"Error analyzing on-page SEO: {str(e)}",
                severity=Severity.MEDIUM,
                status=Status.NOT_CHECKED,
                evidence=str(e),
                url=self.url,
            ))

        return findings

    def _check_technical_seo(self) -> list[Finding]:
        """Check technical SEO elements."""
        findings = []

        try:
            soup = BeautifulSoup(self.html, "lxml")

            # Robots meta
            robots_meta = soup.find("meta", attrs={"name": "robots"})
            if robots_meta:
                content = robots_meta.get("content", "").lower()
                if "noindex" in content:
                    findings.append(Finding(
                        section="SEO Review",
                        subsection="Technical SEO",
                        description="Page has noindex directive",
                        severity=Severity.HIGH,
                        status=Status.FAIL,
                        evidence="robots=noindex",
                        url=self.url,
                    ))

            # Canonical URL
            canonical = soup.find("link", attrs={"rel": "canonical"})
            if not canonical:
                findings.append(Finding(
                    section="SEO Review",
                    subsection="Technical SEO",
                    description="Missing canonical URL",
                    severity=Severity.MEDIUM,
                    status=Status.WARNING,
                    evidence="No canonical link",
                    url=self.url,
                ))
            else:
                findings.append(Finding(
                    section="SEO Review",
                    subsection="Technical SEO",
                    description="Canonical URL present",
                    severity=Severity.LOW,
                    status=Status.PASS,
                    evidence=f"Canonical: {canonical.get('href', '')}",
                    url=self.url,
                ))

            # Sitemap reference
            sitemap_links = soup.find_all("link", attrs={"rel": "sitemap"})
            if not sitemap_links:
                findings.append(Finding(
                    section="SEO Review",
                    subsection="Technical SEO",
                    description="No sitemap link in page",
                    severity=Severity.LOW,
                    status=Status.WARNING,
                    evidence="No sitemap link",
                    url=self.url,
                ))

            # Structured data (JSON-LD)
            json_ld_scripts = soup.find_all("script", type="application/ld+json")
            if not json_ld_scripts:
                findings.append(Finding(
                    section="SEO Review",
                    subsection="Technical SEO",
                    description="No structured data (JSON-LD) found",
                    severity=Severity.MEDIUM,
                    status=Status.WARNING,
                    evidence="No JSON-LD scripts",
                    url=self.url,
                ))
            else:
                findings.append(Finding(
                    section="SEO Review",
                    subsection="Technical SEO",
                    description=f"Structured data present: {len(json_ld_scripts)} schema(s)",
                    severity=Severity.LOW,
                    status=Status.PASS,
                    evidence=f"{len(json_ld_scripts)} JSON-LD scripts",
                    url=self.url,
                ))

            # Open Graph tags
            og_tags = soup.find_all("meta", attrs={"property": re.compile(r"^og:")})
            if not og_tags:
                findings.append(Finding(
                    section="SEO Review",
                    subsection="Technical SEO",
                    description="No Open Graph tags for social sharing",
                    severity=Severity.LOW,
                    status=Status.WARNING,
                    evidence="No og: tags",
                    url=self.url,
                ))

        except Exception as e:
            findings.append(Finding(
                section="SEO Review",
                subsection="Technical SEO",
                description=f"Error analyzing technical SEO: {str(e)}",
                severity=Severity.MEDIUM,
                status=Status.NOT_CHECKED,
                evidence=str(e),
                url=self.url,
            ))

        return findings

    def _check_content_seo(self) -> list[Finding]:
        """Check content SEO aspects."""
        findings = []

        try:
            soup = BeautifulSoup(self.html, "lxml")
            text = soup.get_text(separator=" ", strip=True).lower()
            words = text.split()

            # Word count for content depth
            if len(words) < 300:
                findings.append(Finding(
                    section="SEO Review",
                    subsection="Content SEO",
                    description=f"Thin content: {len(words)} words (recommended: 300+)",
                    severity=Severity.MEDIUM,
                    status=Status.WARNING,
                    evidence=f"Word count: {len(words)}",
                    url=self.url,
                ))

            # Keyword density (basic check)
            # Check if URL keywords appear in content
            parsed = urlparse(self.url)
            path_words = parsed.path.strip("/").split("/")
            path_keywords = []
            for path_word in path_words:
                path_keywords.extend(path_word.replace("-", " ").replace("_", " ").split())
            
            if path_keywords:
                found_keywords = [kw for kw in path_keywords if kw.lower() in text and len(kw) > 3]
                if not found_keywords:
                    findings.append(Finding(
                        section="SEO Review",
                        subsection="Content SEO",
                        description="URL keywords not found in page content",
                        severity=Severity.LOW,
                        status=Status.WARNING,
                        evidence=f"URL keywords: {path_keywords}",
                        url=self.url,
                    ))

        except Exception as e:
            findings.append(Finding(
                section="SEO Review",
                subsection="Content SEO",
                description=f"Error analyzing content SEO: {str(e)}",
                severity=Severity.MEDIUM,
                status=Status.NOT_CHECKED,
                evidence=str(e),
                url=self.url,
            ))

        return findings

    def _recommend_onpage(self) -> list[Recommendation]:
        """Generate on-page SEO recommendations."""
        return [
            Recommendation(
                section="SEO Review",
                subsection="On-page SEO",
                description="Write unique, compelling title tags (50-60 chars) with primary keyword",
                priority="high",
                effort="low",
            ),
            Recommendation(
                section="SEO Review",
                subsection="On-page SEO",
                description="Create meta descriptions that encourage clicks (120-160 chars)",
                priority="high",
                effort="low",
            ),
            Recommendation(
                section="SEO Review",
                subsection="On-page SEO",
                description="Use proper heading hierarchy (H1 > H2 > H3) with keywords",
                priority="medium",
                effort="low",
            ),
            Recommendation(
                section="SEO Review",
                subsection="On-page SEO",
                description="Add descriptive alt text to all images",
                priority="medium",
                effort="medium",
            ),
        ]

    def _recommend_technical(self) -> list[Recommendation]:
        """Generate technical SEO recommendations."""
        return [
            Recommendation(
                section="SEO Review",
                subsection="Technical SEO",
                description="Add canonical URLs to prevent duplicate content issues",
                priority="high",
                effort="low",
            ),
            Recommendation(
                section="SEO Review",
                subsection="Technical SEO",
                description="Implement structured data (Schema.org) for rich snippets",
                priority="medium",
                effort="medium",
            ),
            Recommendation(
                section="SEO Review",
                subsection="Technical SEO",
                description="Add Open Graph tags for better social media sharing",
                priority="low",
                effort="low",
            ),
            Recommendation(
                section="SEO Review",
                subsection="Technical SEO",
                description="Create and submit XML sitemap to search engines",
                priority="medium",
                effort="low",
            ),
        ]

    def _recommend_content(self) -> list[Recommendation]:
        """Generate content SEO recommendations."""
        return [
            Recommendation(
                section="SEO Review",
                subsection="Content SEO",
                description="Create comprehensive content (1000+ words) for key pages",
                priority="medium",
                effort="high",
            ),
            Recommendation(
                section="SEO Review",
                subsection="Content SEO",
                description="Identify and target relevant keywords naturally in content",
                priority="high",
                effort="medium",
            ),
            Recommendation(
                section="SEO Review",
                subsection="Content SEO",
                description="Create internal linking structure between related content",
                priority="medium",
                effort="medium",
            ),
        ]
