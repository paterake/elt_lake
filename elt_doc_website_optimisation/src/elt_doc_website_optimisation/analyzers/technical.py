"""Technical review analyzer - Performance, Security, Hosting/Infrastructure."""

import time
from typing import Any

import httpx
from bs4 import BeautifulSoup

from ..models.assessment import Finding, Recommendation, SectionResult, Severity, Status


class TechnicalAnalyzer:
    """Analyze technical aspects of a website."""

    def __init__(self, url: str):
        self.url = url
        self.html = ""
        self.headers: dict[str, str] = {}
        self.response_time_ms = 0
        self.status_code = 0

    def fetch(self) -> bool:
        """Fetch the website."""
        try:
            start = time.time()
            response = httpx.get(
                self.url,
                timeout=30.0,
                follow_redirects=True,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                },
            )
            self.response_time_ms = (time.time() - start) * 1000
            self.status_code = response.status_code
            self.headers = dict(response.headers)
            self.html = response.text
            return True
        except Exception as e:
            print(f"Error fetching {self.url}: {e}")
            return False

    def analyze(self) -> SectionResult:
        """Run all technical analysis checks."""
        result = SectionResult(name="Technical Review")

        # Performance
        result.findings.extend(self._check_performance())
        result.recommendations.extend(self._recommend_performance())

        # Security
        result.findings.extend(self._check_security())
        result.recommendations.extend(self._recommend_security())

        # Hosting & Infrastructure
        result.findings.extend(self._check_hosting())
        result.recommendations.extend(self._recommend_hosting())

        return result

    def _check_performance(self) -> list[Finding]:
        """Check page load performance."""
        findings = []

        # Response time check
        if self.response_time_ms > 3000:
            findings.append(Finding(
                section="Technical Review",
                subsection="Performance",
                description=f"Slow server response time: {self.response_time_ms:.0f}ms (>3s)",
                severity=Severity.HIGH,
                status=Status.FAIL,
                evidence=f"Response time: {self.response_time_ms:.0f}ms",
                url=self.url,
            ))
        elif self.response_time_ms > 1000:
            findings.append(Finding(
                section="Technical Review",
                subsection="Performance",
                description=f"Moderate server response time: {self.response_time_ms:.0f}ms",
                severity=Severity.MEDIUM,
                status=Status.WARNING,
                evidence=f"Response time: {self.response_time_ms:.0f}ms",
                url=self.url,
            ))
        else:
            findings.append(Finding(
                section="Technical Review",
                subsection="Performance",
                description=f"Good server response time: {self.response_time_ms:.0f}ms",
                severity=Severity.LOW,
                status=Status.PASS,
                evidence=f"Response time: {self.response_time_ms:.0f}ms",
                url=self.url,
            ))

        return findings

    def _check_security(self) -> list[Finding]:
        """Check security headers and SSL."""
        findings = []

        # Check HTTPS
        if self.url.startswith("https://"):
            findings.append(Finding(
                section="Technical Review",
                subsection="Security",
                description="HTTPS is enabled",
                severity=Severity.LOW,
                status=Status.PASS,
                evidence="URL uses HTTPS",
                url=self.url,
            ))
        else:
            findings.append(Finding(
                section="Technical Review",
                subsection="Security",
                description="Website does not use HTTPS",
                severity=Severity.CRITICAL,
                status=Status.FAIL,
                evidence="URL uses HTTP",
                url=self.url,
            ))

        # Check security headers
        security_headers = [
            "Strict-Transport-Security",
            "X-Content-Type-Options",
            "X-Frame-Options",
            "Content-Security-Policy",
        ]

        missing_headers = [h for h in security_headers if h not in self.headers]
        if missing_headers:
            findings.append(Finding(
                section="Technical Review",
                subsection="Security",
                description=f"Missing security headers: {', '.join(missing_headers)}",
                severity=Severity.MEDIUM,
                status=Status.WARNING,
                evidence=f"Missing: {missing_headers}",
                url=self.url,
            ))

        # Check server info disclosure
        if "Server" in self.headers:
            server = self.headers["Server"]
            if "apache" in server.lower() or "nginx" in server.lower():
                findings.append(Finding(
                    section="Technical Review",
                    subsection="Security",
                    description=f"Server version disclosed: {server}",
                    severity=Severity.LOW,
                    status=Status.WARNING,
                    evidence=f"Server header: {server}",
                    url=self.url,
                ))

        return findings

    def _check_hosting(self) -> list[Finding]:
        """Check hosting and infrastructure."""
        findings = []

        # Check response time as proxy for server performance
        if self.response_time_ms > 5000:
            findings.append(Finding(
                section="Technical Review",
                subsection="Hosting & Infrastructure",
                description="Very slow response time may indicate hosting issues",
                severity=Severity.MEDIUM,
                status=Status.WARNING,
                evidence=f"Response time: {self.response_time_ms:.0f}ms",
                url=self.url,
            ))

        # Check for common hosting indicators
        if "x-powered-by" in self.headers:
            powered_by = self.headers["x-powered-by"]
            findings.append(Finding(
                section="Technical Review",
                subsection="Hosting & Infrastructure",
                description=f"Technology stack disclosed: {powered_by}",
                severity=Severity.LOW,
                status=Status.PASS,
                evidence=f"X-Powered-By: {powered_by}",
                url=self.url,
            ))

        return findings

    def _recommend_performance(self) -> list[Recommendation]:
        """Generate performance recommendations."""
        recommendations = []

        if self.response_time_ms > 1000:
            recommendations.append(Recommendation(
                section="Technical Review",
                subsection="Performance",
                description="Implement server-side caching (Redis/Memcached) to improve response times",
                priority="high",
                effort="medium",
            ))
            recommendations.append(Recommendation(
                section="Technical Review",
                subsection="Performance",
                description="Enable gzip/brotli compression for text-based assets",
                priority="high",
                effort="low",
            ))
            recommendations.append(Recommendation(
                section="Technical Review",
                subsection="Performance",
                description="Consider using a CDN for static assets",
                priority="medium",
                effort="medium",
            ))

        return recommendations

    def _recommend_security(self) -> list[Recommendation]:
        """Generate security recommendations."""
        recommendations = []

        if not self.url.startswith("https://"):
            recommendations.append(Recommendation(
                section="Technical Review",
                subsection="Security",
                description="Install SSL certificate and enforce HTTPS across all pages",
                priority="high",
                effort="low",
            ))

        recommendations.append(Recommendation(
            section="Technical Review",
            subsection="Security",
            description="Add security headers: Strict-Transport-Security, X-Content-Type-Options, X-Frame-Options, Content-Security-Policy",
            priority="medium",
            effort="low",
        ))

        return recommendations

    def _recommend_hosting(self) -> list[Recommendation]:
        """Generate hosting recommendations."""
        recommendations = []

        if self.response_time_ms > 2000:
            recommendations.append(Recommendation(
                section="Technical Review",
                subsection="Hosting & Infrastructure",
                description="Consider upgrading hosting plan or optimizing database queries",
                priority="medium",
                effort="high",
            ))

        return recommendations
