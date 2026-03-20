"""Analytics & Tracking analyzer."""

import re

from bs4 import BeautifulSoup

from ..models.assessment import Finding, Recommendation, SectionResult, Severity, Status


class AnalyticsAnalyzer:
    """Analyze analytics and tracking implementation."""

    def __init__(self, url: str, html: str = ""):
        self.url = url
        self.html = html

    def analyze(self) -> SectionResult:
        """Run analytics and tracking checks."""
        result = SectionResult(name="Analytics & Tracking")

        if not self.html:
            result.findings.append(Finding(
                section="Analytics & Tracking",
                subsection="General",
                description="No HTML content to analyze",
                severity=Severity.MEDIUM,
                status=Status.NOT_CHECKED,
                url=self.url,
            ))
            return result

        # Google Analytics
        result.findings.extend(self._check_google_analytics())
        result.recommendations.extend(self._recommend_analytics())

        # Google Tag Manager
        result.findings.extend(self._check_gtm())

        # Cookie banner
        result.findings.extend(self._check_cookie_banner())

        return result

    def _check_google_analytics(self) -> list[Finding]:
        """Check for Google Analytics installation."""
        findings = []

        try:
            soup = BeautifulSoup(self.html, "lxml")

            # Check for GA4 (gtag.js)
            gtag_scripts = soup.find_all("script", src=re.compile(r"googletagmanager\.com/gtag"))
            gtag_inline = soup.find_all("script", string=re.compile(r"gtag\('config'"))

            # Check for Universal Analytics (analytics.js) - deprecated but still common
            ua_scripts = soup.find_all("script", src=re.compile(r"google-analytics\.com/analytics\.js"))
            ua_inline = soup.find_all("script", string=re.compile(r"ga\('create'"))

            # Check for GA tracking IDs in HTML
            ga4_pattern = r"G-[A-Z0-9]{10}"
            ua_pattern = r"UA-\d+-\d+"

            ga4_ids = re.findall(ga4_pattern, self.html)
            ua_ids = re.findall(ua_pattern, self.html)

            if gtag_scripts or gtag_inline or ga4_ids:
                findings.append(Finding(
                    section="Analytics & Tracking",
                    subsection="Analytics",
                    description="Google Analytics 4 (GA4) detected",
                    severity=Severity.LOW,
                    status=Status.PASS,
                    evidence=f"GA4 IDs: {ga4_ids}" if ga4_ids else "GA4 gtag detected",
                    url=self.url,
                ))
            elif ua_scripts or ua_inline or ua_ids:
                findings.append(Finding(
                    section="Analytics & Tracking",
                    subsection="Analytics",
                    description="Universal Analytics detected (deprecated - migrate to GA4)",
                    severity=Severity.MEDIUM,
                    status=Status.WARNING,
                    evidence=f"UA IDs: {ua_ids}" if ua_ids else "UA analytics.js detected",
                    url=self.url,
                ))
            else:
                findings.append(Finding(
                    section="Analytics & Tracking",
                    subsection="Analytics",
                    description="No Google Analytics detected",
                    severity=Severity.MEDIUM,
                    status=Status.WARNING,
                    evidence="No GA code found",
                    url=self.url,
                ))

        except Exception as e:
            findings.append(Finding(
                section="Analytics & Tracking",
                subsection="Analytics",
                description=f"Error checking analytics: {str(e)}",
                severity=Severity.MEDIUM,
                status=Status.NOT_CHECKED,
                evidence=str(e),
                url=self.url,
            ))

        return findings

    def _check_gtm(self) -> list[Finding]:
        """Check for Google Tag Manager."""
        findings = []

        try:
            # GTM container ID pattern
            gtm_pattern = r"GTM-[A-Z0-9]+"
            gtm_matches = re.findall(gtm_pattern, self.html)

            # Check for GTM iframe (noscript)
            gtm_iframe = re.search(r"googletagmanager\.com/ns\.html\?id=(GTM-[A-Z0-9]+)", self.html)

            if gtm_matches or gtm_iframe:
                findings.append(Finding(
                    section="Analytics & Tracking",
                    subsection="Tag Manager",
                    description=f"Google Tag Manager detected: {gtm_matches}",
                    severity=Severity.LOW,
                    status=Status.PASS,
                    evidence=f"GTM IDs: {gtm_matches}",
                    url=self.url,
                ))

                # Check for proper placement (should be in head and body)
                head_pattern = r"<head>.*?GTM-[A-Z0-9]+.*?</head>"
                body_pattern = r"<body>.*?GTM-[A-Z0-9]+.*?</body>"

                has_head = bool(re.search(head_pattern, self.html, re.DOTALL | re.IGNORECASE))
                has_body = bool(re.search(body_pattern, self.html, re.DOTALL | re.IGNORECASE))

                if not has_head:
                    findings.append(Finding(
                        section="Analytics & Tracking",
                        subsection="Tag Manager",
                        description="GTM script may not be in <head> section",
                        severity=Severity.MEDIUM,
                        status=Status.WARNING,
                        evidence="GTM not found in head",
                        url=self.url,
                    ))

                if not has_body:
                    findings.append(Finding(
                        section="Analytics & Tracking",
                        subsection="Tag Manager",
                        description="GTM noscript iframe may not be in <body> section",
                        severity=Severity.LOW,
                        status=Status.WARNING,
                        evidence="GTM noscript not found in body",
                        url=self.url,
                    ))
            else:
                findings.append(Finding(
                    section="Analytics & Tracking",
                    subsection="Tag Manager",
                    description="Google Tag Manager not detected",
                    severity=Severity.LOW,
                    status=Status.PASS,
                    evidence="No GTM container found",
                    url=self.url,
                ))

        except Exception as e:
            findings.append(Finding(
                section="Analytics & Tracking",
                subsection="Tag Manager",
                description=f"Error checking GTM: {str(e)}",
                severity=Severity.MEDIUM,
                status=Status.NOT_CHECKED,
                evidence=str(e),
                url=self.url,
            ))

        return findings

    def _check_cookie_banner(self) -> list[Finding]:
        """Check for cookie consent banner."""
        findings = []

        try:
            soup = BeautifulSoup(self.html, "lxml")

            # Common cookie banner indicators
            cookie_indicators = [
                "cookie", "consent", "privacy", "gdpr", "accept cookies",
                "cookie policy", "manage preferences"
            ]

            text = soup.get_text(separator=" ", strip=True).lower()
            found_indicators = [ind for ind in cookie_indicators if ind in text]

            # Check for common cookie banner classes/IDs
            cookie_classes = [
                "cookie-banner", "cookie-consent", "cookie-notice",
                "gdpr-banner", "privacy-banner", "cc-banner"
            ]

            cookie_elements = []
            for class_name in cookie_classes:
                elements = soup.find_all(class_=re.compile(class_name, re.IGNORECASE))
                cookie_elements.extend(elements)

            if cookie_elements or len(found_indicators) >= 2:
                findings.append(Finding(
                    section="Analytics & Tracking",
                    subsection="Cookie Banner",
                    description="Cookie consent banner detected",
                    severity=Severity.LOW,
                    status=Status.PASS,
                    evidence=f"Indicators: {found_indicators}",
                    url=self.url,
                ))

                # Check for accept/reject buttons
                buttons = soup.find_all(["button", "a"])
                accept_buttons = [b for b in buttons if "accept" in b.get_text(strip=True).lower()]
                reject_buttons = [b for b in buttons if "reject" in b.get_text(strip=True).lower() 
                                 or "decline" in b.get_text(strip=True).lower()]

                if not reject_buttons:
                    findings.append(Finding(
                        section="Analytics & Tracking",
                        subsection="Cookie Banner",
                        description="Cookie banner may not have easy reject option (GDPR concern)",
                        severity=Severity.MEDIUM,
                        status=Status.WARNING,
                        evidence="No reject/decline button found",
                        url=self.url,
                    ))
            else:
                findings.append(Finding(
                    section="Analytics & Tracking",
                    subsection="Cookie Banner",
                    description="No cookie consent banner detected (GDPR compliance concern)",
                    severity=Severity.HIGH,
                    status=Status.FAIL,
                    evidence="No cookie banner indicators",
                    url=self.url,
                ))

        except Exception as e:
            findings.append(Finding(
                section="Analytics & Tracking",
                subsection="Cookie Banner",
                description=f"Error checking cookie banner: {str(e)}",
                severity=Severity.MEDIUM,
                status=Status.NOT_CHECKED,
                evidence=str(e),
                url=self.url,
            ))

        return findings

    def _recommend_analytics(self) -> list[Recommendation]:
        """Generate analytics recommendations."""
        return [
            Recommendation(
                section="Analytics & Tracking",
                subsection="Analytics",
                description="Ensure GA4 is properly configured with conversion events",
                priority="high",
                effort="medium",
            ),
            Recommendation(
                section="Analytics & Tracking",
                subsection="Analytics",
                description="Set up goals/events for key user actions (form submissions, calls, etc.)",
                priority="high",
                effort="medium",
            ),
            Recommendation(
                section="Analytics & Tracking",
                subsection="Analytics",
                description="Consider using Google Tag Manager for easier tracking management",
                priority="medium",
                effort="medium",
            ),
            Recommendation(
                section="Analytics & Tracking",
                subsection="Analytics",
                description="Review analytics data for tracking gaps or missing pages",
                priority="medium",
                effort="low",
            ),
            Recommendation(
                section="Analytics & Tracking",
                subsection="Analytics",
                description="Ensure cookie consent is integrated with analytics (consent mode)",
                priority="high",
                effort="medium",
            ),
        ]
