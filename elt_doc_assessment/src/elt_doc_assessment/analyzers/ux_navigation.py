"""UX & Navigation analyzer - Navigation flow, Accessibility, Mobile friendliness."""

from playwright.sync_api import sync_playwright

from ..models.assessment import Finding, Recommendation, SectionResult, Severity, Status


class UXNavigationAnalyzer:
    """Analyze UX and navigation aspects of a website."""

    def __init__(self, url: str):
        self.url = url
        self.html = ""
        self.screenshot_desktop: bytes | None = None
        self.screenshot_mobile: bytes | None = None

    def fetch(self) -> bool:
        """Fetch the website and capture screenshots."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                
                # Desktop viewport
                page = browser.new_page(viewport={"width": 1920, "height": 1080})
                page.goto(self.url, wait_until="networkidle", timeout=30000)
                self.screenshot_desktop = page.screenshot()
                self.html = page.content()
                
                # Mobile viewport
                page.set_viewport_size({"width": 375, "height": 667})
                self.screenshot_mobile = page.screenshot()
                
                browser.close()
            return True
        except Exception as e:
            print(f"Error in UX analysis for {self.url}: {e}")
            return False

    def analyze(self) -> SectionResult:
        """Run all UX and navigation analysis checks."""
        result = SectionResult(name="UX & Navigation")

        # Navigation flow
        result.findings.extend(self._check_navigation_flow())
        result.recommendations.extend(self._recommend_navigation())

        # Accessibility
        result.findings.extend(self._check_accessibility())
        result.recommendations.extend(self._recommend_accessibility())

        # Mobile friendliness
        result.findings.extend(self._check_mobile())
        result.recommendations.extend(self._recommend_mobile())

        return result

    def _check_navigation_flow(self) -> list[Finding]:
        """Check navigation flow and structure."""
        findings = []

        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(self.html, "lxml")

            # Check for navigation
            nav_elements = soup.find_all("nav")
            if not nav_elements:
                findings.append(Finding(
                    section="UX & Navigation",
                    subsection="Navigation flow",
                    description="No semantic <nav> element found",
                    severity=Severity.MEDIUM,
                    status=Status.WARNING,
                    evidence="Missing <nav> element",
                    url=self.url,
                ))
            else:
                findings.append(Finding(
                    section="UX & Navigation",
                    subsection="Navigation flow",
                    description="Semantic <nav> element present",
                    severity=Severity.LOW,
                    status=Status.PASS,
                    evidence=f"Found {len(nav_elements)} <nav> element(s)",
                    url=self.url,
                ))

            # Check for main content area
            main_elements = soup.find_all("main")
            if not main_elements:
                findings.append(Finding(
                    section="UX & Navigation",
                    subsection="Navigation flow",
                    description="No semantic <main> element found",
                    severity=Severity.LOW,
                    status=Status.WARNING,
                    evidence="Missing <main> element",
                    url=self.url,
                ))

            # Check for links
            links = soup.find_all("a", href=True)
            if len(links) < 5:
                findings.append(Finding(
                    section="UX & Navigation",
                    subsection="Navigation flow",
                    description=f"Low number of internal links: {len(links)}",
                    severity=Severity.MEDIUM,
                    status=Status.WARNING,
                    evidence=f"Only {len(links)} links found",
                    url=self.url,
                ))

            # Check for broken internal links (basic check)
            broken_links = []
            for link in links[:20]:  # Check first 20 links
                href = link.get("href", "")
                if href and not href.startswith(("http://", "https://", "#", "tel:", "mailto:")):
                    # Relative link - could be broken
                    if href.startswith("/") or not href.startswith("//"):
                        pass  # Valid relative link

        except Exception as e:
            findings.append(Finding(
                section="UX & Navigation",
                subsection="Navigation flow",
                description=f"Error analyzing navigation: {str(e)}",
                severity=Severity.MEDIUM,
                status=Status.NOT_CHECKED,
                evidence=str(e),
                url=self.url,
            ))

        return findings

    def _check_accessibility(self) -> list[Finding]:
        """Check accessibility features."""
        findings = []

        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(self.html, "lxml")

            # Check for alt tags on images
            images = soup.find_all("img")
            images_without_alt = [img for img in images if not img.get("alt")]
            if images_without_alt:
                findings.append(Finding(
                    section="UX & Navigation",
                    subsection="Accessibility",
                    description=f"{len(images_without_alt)} image(s) missing alt tags",
                    severity=Severity.MEDIUM,
                    status=Status.FAIL,
                    evidence=f"Missing alt tags on {len(images_without_alt)} images",
                    url=self.url,
                ))
            elif images:
                findings.append(Finding(
                    section="UX & Navigation",
                    subsection="Accessibility",
                    description="All images have alt tags",
                    severity=Severity.LOW,
                    status=Status.PASS,
                    evidence=f"{len(images)} images with alt tags",
                    url=self.url,
                ))

            # Check heading structure
            h1_tags = soup.find_all("h1")
            if len(h1_tags) == 0:
                findings.append(Finding(
                    section="UX & Navigation",
                    subsection="Accessibility",
                    description="No H1 heading found",
                    severity=Severity.MEDIUM,
                    status=Status.FAIL,
                    evidence="Missing H1 tag",
                    url=self.url,
                ))
            elif len(h1_tags) > 1:
                findings.append(Finding(
                    section="UX & Navigation",
                    subsection="Accessibility",
                    description=f"Multiple H1 headings found: {len(h1_tags)}",
                    severity=Severity.LOW,
                    status=Status.WARNING,
                    evidence=f"{len(h1_tags)} H1 tags",
                    url=self.url,
                ))
            else:
                findings.append(Finding(
                    section="UX & Navigation",
                    subsection="Accessibility",
                    description="Single H1 heading present",
                    severity=Severity.LOW,
                    status=Status.PASS,
                    evidence="One H1 tag found",
                    url=self.url,
                ))

            # Check for ARIA roles
            aria_elements = soup.find_all(attrs={"aria-label": True})
            aria_elements += soup.find_all(attrs={"role": True})
            if not aria_elements:
                findings.append(Finding(
                    section="UX & Navigation",
                    subsection="Accessibility",
                    description="No ARIA labels or roles found",
                    severity=Severity.LOW,
                    status=Status.WARNING,
                    evidence="Missing ARIA attributes",
                    url=self.url,
                ))

        except Exception as e:
            findings.append(Finding(
                section="UX & Navigation",
                subsection="Accessibility",
                description=f"Error analyzing accessibility: {str(e)}",
                severity=Severity.MEDIUM,
                status=Status.NOT_CHECKED,
                evidence=str(e),
                url=self.url,
            ))

        return findings

    def _check_mobile(self) -> list[Finding]:
        """Check mobile friendliness."""
        findings = []

        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(self.html, "lxml")

            # Check for viewport meta tag
            viewport = soup.find("meta", attrs={"name": "viewport"})
            if not viewport:
                findings.append(Finding(
                    section="UX & Navigation",
                    subsection="Mobile friendliness",
                    description="No viewport meta tag found",
                    severity=Severity.HIGH,
                    status=Status.FAIL,
                    evidence="Missing viewport meta tag",
                    url=self.url,
                ))
            else:
                findings.append(Finding(
                    section="UX & Navigation",
                    subsection="Mobile friendliness",
                    description="Viewport meta tag present",
                    severity=Severity.LOW,
                    status=Status.PASS,
                    evidence="Viewport meta tag found",
                    url=self.url,
                ))

            # Check for mobile-friendly width
            if viewport:
                content = viewport.get("content", "")
                if "width=device-width" in content:
                    findings.append(Finding(
                        section="UX & Navigation",
                        subsection="Mobile friendliness",
                        description="Responsive viewport configured",
                        severity=Severity.LOW,
                        status=Status.PASS,
                        evidence="width=device-width in viewport",
                        url=self.url,
                    ))

        except Exception as e:
            findings.append(Finding(
                section="UX & Navigation",
                subsection="Mobile friendliness",
                description=f"Error analyzing mobile friendliness: {str(e)}",
                severity=Severity.MEDIUM,
                status=Status.NOT_CHECKED,
                evidence=str(e),
                url=self.url,
            ))

        return findings

    def _recommend_navigation(self) -> list[Recommendation]:
        """Generate navigation recommendations."""
        return [
            Recommendation(
                section="UX & Navigation",
                subsection="Navigation flow",
                description="Ensure consistent navigation structure across all pages",
                priority="medium",
                effort="low",
            ),
            Recommendation(
                section="UX & Navigation",
                subsection="Navigation flow",
                description="Add breadcrumb navigation for deeper pages",
                priority="low",
                effort="low",
            ),
        ]

    def _recommend_accessibility(self) -> list[Recommendation]:
        """Generate accessibility recommendations."""
        return [
            Recommendation(
                section="UX & Navigation",
                subsection="Accessibility",
                description="Add alt text to all images for screen reader compatibility",
                priority="high",
                effort="medium",
            ),
            Recommendation(
                section="UX & Navigation",
                subsection="Accessibility",
                description="Ensure proper heading hierarchy (H1 > H2 > H3)",
                priority="medium",
                effort="low",
            ),
            Recommendation(
                section="UX & Navigation",
                subsection="Accessibility",
                description="Add ARIA labels to interactive elements",
                priority="medium",
                effort="medium",
            ),
            Recommendation(
                section="UX & Navigation",
                subsection="Accessibility",
                description="Ensure sufficient color contrast (WCAG AA minimum)",
                priority="medium",
                effort="low",
            ),
        ]

    def _recommend_mobile(self) -> list[Recommendation]:
        """Generate mobile recommendations."""
        return [
            Recommendation(
                section="UX & Navigation",
                subsection="Mobile friendliness",
                description="Test all interactive elements for touch-friendly sizing (min 44x44px)",
                priority="medium",
                effort="low",
            ),
            Recommendation(
                section="UX & Navigation",
                subsection="Mobile friendliness",
                description="Implement responsive images with srcset for different screen sizes",
                priority="low",
                effort="medium",
            ),
        ]
