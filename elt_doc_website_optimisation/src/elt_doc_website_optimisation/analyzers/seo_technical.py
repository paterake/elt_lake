"""SEO Technical analyzer - Broken links, redirects, robots.txt, sitemap."""

from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from ..models.assessment import Finding, Recommendation, SectionResult, Severity, Status


class SEOTechnicalAnalyzer:
    """Analyze technical SEO aspects - broken links, redirects, robots.txt."""

    def __init__(self, url: str, html: str = ""):
        self.url = url
        self.html = html
        self.parsed_url = urlparse(url)
        self.base_url = f"{self.parsed_url.scheme}://{self.parsed_url.netloc}"

    def analyze(self) -> SectionResult:
        """Run all technical SEO analysis checks."""
        result = SectionResult(name="Technical SEO")

        if not self.html:
            result.findings.append(Finding(
                section="SEO Review",
                subsection="Technical SEO",
                description="No HTML content to analyze",
                severity=Severity.MEDIUM,
                status=Status.NOT_CHECKED,
                url=self.url,
            ))
            return result

        # Broken links
        result.findings.extend(self._check_broken_links())
        result.recommendations.extend(self._recommend_broken_links())

        # Redirects
        result.findings.extend(self._check_redirects())
        result.recommendations.extend(self._recommend_redirects())

        # Robots.txt
        result.findings.extend(self._check_robots_txt())
        result.recommendations.extend(self._recommend_robots_txt())

        # Sitemap
        result.findings.extend(self._check_sitemap())
        result.recommendations.extend(self._recommend_sitemap())

        return result

    def _check_broken_links(self) -> list[Finding]:
        """Check for broken links on the page."""
        findings = []

        try:
            soup = BeautifulSoup(self.html, "lxml")
            links = soup.find_all("a", href=True)

            internal_links = []
            external_links = []
            broken_links = []

            for link in links[:30]:  # Check first 30 links to avoid timeout
                href = link.get("href", "")
                
                # Skip special links
                if href.startswith(("#", "tel:", "mailto:", "javascript:", "data:")):
                    continue

                # Determine if internal or external
                if href.startswith("http"):
                    if self.base_url not in href:
                        external_links.append(href)
                        continue
                else:
                    href = urljoin(self.url, href)
                
                internal_links.append(href)

            # Check internal links (with timeout)
            for link_url in internal_links[:15]:  # Limit to 15 internal links
                try:
                    response = httpx.head(link_url, timeout=5.0, follow_redirects=True)
                    if response.status_code >= 400:
                        broken_links.append((link_url, response.status_code))
                except Exception:
                    pass  # Skip on error

            # Report findings
            if broken_links:
                findings.append(Finding(
                    section="SEO Review",
                    subsection="Technical SEO",
                    description=f"{len(broken_links)} broken link(s) found",
                    severity=Severity.HIGH,
                    status=Status.FAIL,
                    evidence=f"Broken: {[bl[0] for bl in broken_links[:5]]}",
                    url=self.url,
                ))
            else:
                findings.append(Finding(
                    section="SEO Review",
                    subsection="Technical SEO",
                    description=f"No broken links found (checked {len(internal_links)} internal links)",
                    severity=Severity.LOW,
                    status=Status.PASS,
                    evidence=f"Checked {len(internal_links)} links",
                    url=self.url,
                ))

        except Exception as e:
            findings.append(Finding(
                section="SEO Review",
                subsection="Technical SEO",
                description=f"Error checking broken links: {str(e)}",
                severity=Severity.MEDIUM,
                status=Status.NOT_CHECKED,
                evidence=str(e),
                url=self.url,
            ))

        return findings

    def _check_redirects(self) -> list[Finding]:
        """Check redirect chains."""
        findings = []

        try:
            # Check main URL redirect chain
            session = httpx.Client()
            redirects = []
            
            try:
                response = session.get(
                    self.url,
                    timeout=10.0,
                    follow_redirects=False
                )
                
                redirect_count = 0
                current_url = self.url
                
                while response.status_code in [301, 302, 307, 308] and redirect_count < 5:
                    redirect_count += 1
                    location = response.headers.get("Location", "")
                    if location:
                        redirects.append((current_url, response.status_code, location))
                        current_url = urljoin(current_url, location)
                        response = session.get(
                            current_url,
                            timeout=10.0,
                            follow_redirects=False
                        )
                    else:
                        break

                if redirect_count > 2:
                    findings.append(Finding(
                        section="SEO Review",
                        subsection="Technical SEO",
                        description=f"Long redirect chain: {redirect_count} redirects",
                        severity=Severity.MEDIUM,
                        status=Status.WARNING,
                        evidence=f"Redirects: {redirect_count}",
                        url=self.url,
                    ))
                elif redirect_count > 0:
                    findings.append(Finding(
                        section="SEO Review",
                        subsection="Technical SEO",
                        description=f"{redirect_count} redirect(s) detected",
                        severity=Severity.LOW,
                        status=Status.PASS,
                        evidence=f"Redirects: {redirect_count}",
                        url=self.url,
                    ))
                else:
                    findings.append(Finding(
                        section="SEO Review",
                        subsection="Technical SEO",
                        description="No redirects detected",
                        severity=Severity.LOW,
                        status=Status.PASS,
                        evidence="Direct response",
                        url=self.url,
                    ))

            finally:
                session.close()

        except Exception as e:
            findings.append(Finding(
                section="SEO Review",
                subsection="Technical SEO",
                description=f"Error checking redirects: {str(e)}",
                severity=Severity.MEDIUM,
                status=Status.NOT_CHECKED,
                evidence=str(e),
                url=self.url,
            ))

        return findings

    def _check_robots_txt(self) -> list[Finding]:
        """Check robots.txt file."""
        findings = []

        try:
            robots_url = f"{self.base_url}/robots.txt"
            response = httpx.get(robots_url, timeout=5.0)

            if response.status_code == 200:
                findings.append(Finding(
                    section="SEO Review",
                    subsection="Technical SEO",
                    description="robots.txt file found",
                    severity=Severity.LOW,
                    status=Status.PASS,
                    evidence=f"URL: {robots_url}",
                    url=self.url,
                ))

                # Check for common issues
                content = response.text.lower()
                if "disallow: /" in content and "user-agent: *" in content:
                    findings.append(Finding(
                        section="SEO Review",
                        subsection="Technical SEO",
                        description="robots.txt may block all crawlers",
                        severity=Severity.HIGH,
                        status=Status.FAIL,
                        evidence="Disallow: / found",
                        url=self.url,
                    ))

                if "sitemap:" not in content:
                    findings.append(Finding(
                        section="SEO Review",
                        subsection="Technical SEO",
                        description="robots.txt does not reference sitemap",
                        severity=Severity.LOW,
                        status=Status.WARNING,
                        evidence="No sitemap reference",
                        url=self.url,
                    ))
            else:
                findings.append(Finding(
                    section="SEO Review",
                    subsection="Technical SEO",
                    description="robots.txt file not found",
                    severity=Severity.MEDIUM,
                    status=Status.WARNING,
                    evidence=f"Status: {response.status_code}",
                    url=self.url,
                ))

        except Exception as e:
            findings.append(Finding(
                section="SEO Review",
                subsection="Technical SEO",
                description=f"Error checking robots.txt: {str(e)}",
                severity=Severity.MEDIUM,
                status=Status.NOT_CHECKED,
                evidence=str(e),
                url=self.url,
            ))

        return findings

    def _check_sitemap(self) -> list[Finding]:
        """Check sitemap.xml file."""
        findings = []

        try:
            sitemap_url = f"{self.base_url}/sitemap.xml"
            response = httpx.get(sitemap_url, timeout=5.0)

            if response.status_code == 200:
                findings.append(Finding(
                    section="SEO Review",
                    subsection="Technical SEO",
                    description="sitemap.xml found at default location",
                    severity=Severity.LOW,
                    status=Status.PASS,
                    evidence=f"URL: {sitemap_url}",
                    url=self.url,
                ))
            else:
                # Try common alternatives
                alternatives = [
                    f"{self.base_url}/sitemap_index.xml",
                    f"{self.base_url}/sitemap/sitemap.xml",
                ]
                
                found = False
                for alt_url in alternatives:
                    try:
                        alt_response = httpx.get(alt_url, timeout=5.0)
                        if alt_response.status_code == 200:
                            findings.append(Finding(
                                section="SEO Review",
                                subsection="Technical SEO",
                                description=f"sitemap.xml found at alternative location",
                                severity=Severity.LOW,
                                status=Status.PASS,
                                evidence=f"URL: {alt_url}",
                                url=self.url,
                            ))
                            found = True
                            break
                    except Exception:
                        pass

                if not found:
                    findings.append(Finding(
                        section="SEO Review",
                        subsection="Technical SEO",
                        description="sitemap.xml not found",
                        severity=Severity.MEDIUM,
                        status=Status.WARNING,
                        evidence="No sitemap at common locations",
                        url=self.url,
                    ))

        except Exception as e:
            findings.append(Finding(
                section="SEO Review",
                subsection="Technical SEO",
                description=f"Error checking sitemap: {str(e)}",
                severity=Severity.MEDIUM,
                status=Status.NOT_CHECKED,
                evidence=str(e),
                url=self.url,
            ))

        return findings

    def _recommend_broken_links(self) -> list[Recommendation]:
        """Generate broken links recommendations."""
        return [
            Recommendation(
                section="SEO Review",
                subsection="Technical SEO",
                description="Fix or remove broken links to improve user experience and SEO",
                priority="high",
                effort="low",
            ),
            Recommendation(
                section="SEO Review",
                subsection="Technical SEO",
                description="Set up regular broken link monitoring (e.g., weekly crawl)",
                priority="medium",
                effort="low",
            ),
        ]

    def _recommend_redirects(self) -> list[Recommendation]:
        """Generate redirect recommendations."""
        return [
            Recommendation(
                section="SEO Review",
                subsection="Technical SEO",
                description="Minimize redirect chains to improve page load speed",
                priority="medium",
                effort="medium",
            ),
            Recommendation(
                section="SEO Review",
                subsection="Technical SEO",
                description="Use 301 redirects for permanent URL changes",
                priority="low",
                effort="low",
            ),
        ]

    def _recommend_robots_txt(self) -> list[Recommendation]:
        """Generate robots.txt recommendations."""
        return [
            Recommendation(
                section="SEO Review",
                subsection="Technical SEO",
                description="Ensure robots.txt allows search engine crawling of important pages",
                priority="high",
                effort="low",
            ),
            Recommendation(
                section="SEO Review",
                subsection="Technical SEO",
                description="Add sitemap reference to robots.txt",
                priority="low",
                effort="low",
            ),
        ]

    def _recommend_sitemap(self) -> list[Recommendation]:
        """Generate sitemap recommendations."""
        return [
            Recommendation(
                section="SEO Review",
                subsection="Technical SEO",
                description="Create and submit XML sitemap to Google Search Console",
                priority="high",
                effort="low",
            ),
            Recommendation(
                section="SEO Review",
                subsection="Technical SEO",
                description="Include all important pages in sitemap with lastmod dates",
                priority="medium",
                effort="medium",
            ),
        ]
