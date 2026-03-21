"""Simple site crawler for multi-page analysis."""

from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from ..models.assessment import Finding, Recommendation, SectionResult, Severity, Status


class SiteCrawler:
    """Crawl multiple pages on the site for broader analysis."""

    def __init__(self, base_url: str, max_pages: int = 10):
        self.base_url = base_url
        self.max_pages = max_pages
        self.parsed_base = urlparse(base_url)
        self.visited: set[str] = set()
        self.to_visit: list[str] = [base_url]
        self.pages_data: list[dict] = []

    def _is_internal_url(self, url: str) -> bool:
        """Check if URL is on the same domain."""
        parsed = urlparse(url)
        return parsed.netloc == self.parsed_base.netloc

    def _normalize_url(self, url: str) -> str:
        """Normalize URL to absolute form."""
        if url.startswith(("http://", "https://")):
            return url
        return urljoin(self.base_url, url)

    def crawl(self) -> list[dict]:
        """Crawl up to max_pages."""
        while self.to_visit and len(self.visited) < self.max_pages:
            url = self.to_visit.pop(0)
            url = self._normalize_url(url)

            # Skip if already visited or external
            if url in self.visited or not self._is_internal_url(url):
                continue

            try:
                response = httpx.get(url, timeout=10.0, follow_redirects=True)
                if response.status_code != 200:
                    continue

                self.visited.add(url)

                # Parse page
                soup = BeautifulSoup(response.text, "lxml")
                
                page_data = {
                    "url": url,
                    "status": response.status_code,
                    "title": soup.find("title").get_text(strip=True) if soup.find("title") else "",
                    "h1": soup.find("h1").get_text(strip=True) if soup.find("h1") else "",
                    "word_count": len(soup.get_text().split()),
                    "links_count": len(soup.find_all("a", href=True)),
                    "images_count": len(soup.find_all("img")),
                }

                self.pages_data.append(page_data)

                # Extract links to visit
                for link in soup.find_all("a", href=True):
                    href = link.get("href", "")
                    if href and not href.startswith(("#", "tel:", "mailto:", "javascript:")):
                        full_url = self._normalize_url(href)
                        if full_url not in self.visited and full_url not in self.to_visit:
                            self.to_visit.append(full_url)

            except Exception as e:
                print(f"Error crawling {url}: {e}")
                continue

        return self.pages_data

    def analyze(self) -> SectionResult:
        """Analyze crawled pages."""
        result = SectionResult(name="Multi-Page Analysis")

        if not self.pages_data:
            self.crawl()

        if not self.pages_data:
            result.findings.append(Finding(
                section="SEO Review",
                subsection="Content SEO",
                description="Unable to crawl site",
                severity=Severity.MEDIUM,
                status=Status.NOT_CHECKED,
                url=self.base_url,
            ))
            return result

        # Analyze crawled pages
        result.findings.extend(self._check_duplicate_titles())
        result.findings.extend(self._check_missing_h1())
        result.findings.extend(self._check_thin_content())
        result.recommendations.extend(self._recommendations())

        return result

    def _check_duplicate_titles(self) -> list[Finding]:
        """Check for duplicate page titles."""
        findings = []

        titles = [p["title"] for p in self.pages_data if p["title"]]
        unique_titles = set(titles)

        if len(titles) > len(unique_titles):
            # Find duplicates
            seen = set()
            duplicates = []
            for title in titles:
                if title in seen:
                    duplicates.append(title)
                seen.add(title)

            findings.append(Finding(
                section="SEO Review",
                subsection="Content SEO",
                description=f"{len(duplicates)} duplicate title(s) found across {len(self.pages_data)} pages",
                severity=Severity.MEDIUM,
                status=Status.FAIL,
                evidence=f"Duplicates: {list(set(duplicates))[:3]}",
                url=self.base_url,
            ))
        else:
            findings.append(Finding(
                section="SEO Review",
                subsection="Content SEO",
                description=f"All {len(titles)} page titles are unique",
                severity=Severity.LOW,
                status=Status.PASS,
                evidence=f"Crawled {len(self.pages_data)} pages",
                url=self.base_url,
            ))

        return findings

    def _check_missing_h1(self) -> list[Finding]:
        """Check for pages missing H1 tags."""
        findings = []

        pages_without_h1 = [p for p in self.pages_data if not p["h1"]]

        if pages_without_h1:
            findings.append(Finding(
                section="SEO Review",
                subsection="Content SEO",
                description=f"{len(pages_without_h1)} page(s) missing H1 tag",
                severity=Severity.MEDIUM,
                status=Status.FAIL,
                evidence=f"Missing H1: {[p['url'] for p in pages_without_h1[:3]]}",
                url=self.base_url,
            ))
        else:
            findings.append(Finding(
                section="SEO Review",
                subsection="Content SEO",
                description=f"All {len(self.pages_data)} pages have H1 tags",
                severity=Severity.LOW,
                status=Status.PASS,
                evidence="All pages have H1",
                url=self.base_url,
            ))

        return findings

    def _check_thin_content(self) -> list[Finding]:
        """Check for pages with thin content."""
        findings = []

        thin_pages = [p for p in self.pages_data if p["word_count"] < 300]

        if thin_pages:
            findings.append(Finding(
                section="SEO Review",
                subsection="Content SEO",
                description=f"{len(thin_pages)} page(s) with thin content (<300 words)",
                severity=Severity.MEDIUM,
                status=Status.WARNING,
                evidence=f"Thin: {[p['url'] for p in thin_pages[:3]]}",
                url=self.base_url,
            ))
        else:
            findings.append(Finding(
                section="SEO Review",
                subsection="Content SEO",
                description=f"All pages have adequate content (300+ words)",
                severity=Severity.LOW,
                status=Status.PASS,
                evidence=f"Avg word count: {sum(p['word_count'] for p in self.pages_data) / len(self.pages_data):.0f}",
                url=self.base_url,
            ))

        return findings

    def _recommendations(self) -> list[Recommendation]:
        """Generate multi-page recommendations."""
        return [
            Recommendation(
                section="SEO Review",
                subsection="Content SEO",
                description="Ensure each page has a unique, descriptive title tag",
                priority="high",
                effort="medium",
            ),
            Recommendation(
                section="SEO Review",
                subsection="Content SEO",
                description="Add H1 heading to all pages",
                priority="high",
                effort="low",
            ),
            Recommendation(
                section="SEO Review",
                subsection="Content SEO",
                description="Expand thin content pages to 300+ words",
                priority="medium",
                effort="high",
            ),
        ]
