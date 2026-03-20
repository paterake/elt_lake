"""WordPress analyzer - Plugin & Theme audit."""

import re
from typing import Any

import httpx
from bs4 import BeautifulSoup

from ..models.assessment import Finding, Recommendation, SectionResult, Severity, Status


class WordPressAnalyzer:
    """Analyze WordPress-specific aspects (requires admin access for full audit)."""

    def __init__(self, url: str, credentials: Any = None):
        self.url = url
        self.credentials = credentials
        self.html = ""
        self.is_wordpress = False
        self.wp_version = ""
        self.theme_name = ""
        self.plugins: list[dict[str, str]] = []

    def detect_wordpress(self) -> bool:
        """Detect if the site is WordPress."""
        try:
            response = httpx.get(
                self.url,
                timeout=10.0,
                follow_redirects=True,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                },
            )
            self.html = response.text

            # Check for WordPress indicators
            indicators = [
                "wp-content",
                "wp-includes",
                "wp-json",
                "WordPress",
            ]

            for indicator in indicators:
                if indicator in self.html:
                    self.is_wordpress = True
                    break

            return self.is_wordpress
        except Exception as e:
            print(f"Error detecting WordPress: {e}")
            return False

    def analyze(self) -> SectionResult:
        """Run WordPress analysis checks."""
        result = SectionResult(name="Plugin & Theme Audit")

        if not self.is_wordpress:
            result.findings.append(Finding(
                section="Plugin & Theme Audit",
                subsection="General",
                description="Website does not appear to be WordPress",
                severity=Severity.LOW,
                status=Status.PASS,
                url=self.url,
            ))
            return result

        # Plugin Review
        result.findings.extend(self._check_plugins())
        result.recommendations.extend(self._recommend_plugins())

        # Theme Review
        result.findings.extend(self._check_theme())
        result.recommendations.extend(self._recommend_theme())

        # General WordPress recommendations
        result.recommendations.extend(self._recommend_general())

        return result

    def _check_plugins(self) -> list[Finding]:
        """Check for WordPress plugins."""
        findings = []

        # Try to detect plugins from HTML
        plugin_patterns = [
            (r"/wp-content/plugins/([^/]+)/", "Plugin detected in path"),
            (r'wp-content/plugins/([^/]+)/', "Plugin in content"),
        ]

        detected_plugins = set()
        for pattern, description in plugin_patterns:
            matches = re.findall(pattern, self.html)
            for match in matches:
                if match not in detected_plugins:
                    detected_plugins.add(match)

        if detected_plugins:
            findings.append(Finding(
                section="Plugin & Theme Audit",
                subsection="Plugin Review",
                description=f"Detected {len(detected_plugins)} plugin(s): {', '.join(list(detected_plugins)[:10])}",
                severity=Severity.LOW,
                status=Status.PASS,
                evidence=f"Plugins: {list(detected_plugins)[:10]}",
                url=self.url,
            ))

            # Check for common problematic plugins
            problematic_plugins = [
                "revslider",  # Known vulnerabilities
                "showcase-idx",
                "wp-database-backup",
            ]

            found_problematic = [p for p in problematic_plugins if p in detected_plugins]
            if found_problematic:
                findings.append(Finding(
                    section="Plugin & Theme Audit",
                    subsection="Plugin Review",
                    description=f"Potentially vulnerable plugins: {', '.join(found_problematic)}",
                    severity=Severity.HIGH,
                    status=Status.FAIL,
                    evidence=f"Vulnerable: {found_problematic}",
                    url=self.url,
                ))
        else:
            findings.append(Finding(
                section="Plugin & Theme Audit",
                subsection="Plugin Review",
                description="No plugins detected from public HTML (may require admin access)",
                severity=Severity.LOW,
                status=Status.WARNING,
                evidence="No plugin paths found",
                url=self.url,
            ))

        # Note about admin access
        if self.credentials:
            findings.append(Finding(
                section="Plugin & Theme Audit",
                subsection="Plugin Review",
                description="Credentials available - full plugin audit requires WordPress admin API access",
                severity=Severity.LOW,
                status=Status.NOT_CHECKED,
                evidence="Credentials provided but API access not implemented",
                url=self.url,
            ))
        else:
            findings.append(Finding(
                section="Plugin & Theme Audit",
                subsection="Plugin Review",
                description="No WordPress credentials provided - limited plugin analysis",
                severity=Severity.MEDIUM,
                status=Status.WARNING,
                evidence="No credentials",
                url=self.url,
            ))

        return findings

    def _check_theme(self) -> list[Finding]:
        """Check WordPress theme."""
        findings = []

        # Try to detect theme from HTML
        theme_pattern = r"/wp-content/themes/([^/]+)/"
        theme_matches = re.findall(theme_pattern, self.html)

        if theme_matches:
            theme_name = theme_matches[0]
            self.theme_name = theme_name
            findings.append(Finding(
                section="Plugin & Theme Audit",
                subsection="Theme Review",
                description=f"Theme detected: {theme_name}",
                severity=Severity.LOW,
                status=Status.PASS,
                evidence=f"Theme: {theme_name}",
                url=self.url,
            ))

            # Check for common themes
            premium_themes = [
                "divi", "avada", "enfold", "x-theme", "betheme",
                "bridge", "total", "uncode", "kalium"
            ]

            if theme_name.lower() in premium_themes:
                findings.append(Finding(
                    section="Plugin & Theme Audit",
                    subsection="Theme Review",
                    description=f"Premium theme detected ({theme_name}) - may be bloated",
                    severity=Severity.LOW,
                    status=Status.WARNING,
                    evidence=f"Premium theme: {theme_name}",
                    url=self.url,
                ))

            # Check for default themes (outdated)
            default_themes = ["twentyten", "twentyeleven", "twentytwelve", 
                            "twentythirteen", "twentyfourteen", "twentyfifteen"]
            if theme_name.lower() in default_themes:
                findings.append(Finding(
                    section="Plugin & Theme Audit",
                    subsection="Theme Review",
                    description=f"Default WordPress theme detected ({theme_name}) - consider custom theme",
                    severity=Severity.LOW,
                    status=Status.WARNING,
                    evidence=f"Default theme: {theme_name}",
                    url=self.url,
                ))
        else:
            findings.append(Finding(
                section="Plugin & Theme Audit",
                subsection="Theme Review",
                description="Theme not detected from public HTML",
                severity=Severity.LOW,
                status=Status.WARNING,
                evidence="No theme path found",
                url=self.url,
            ))

        return findings

    def _recommend_plugins(self) -> list[Recommendation]:
        """Generate plugin recommendations."""
        return [
            Recommendation(
                section="Plugin & Theme Audit",
                subsection="Plugin Review",
                description="Audit all plugins - remove unused, unnecessary, or duplicated functionality",
                priority="high",
                effort="medium",
            ),
            Recommendation(
                section="Plugin & Theme Audit",
                subsection="Plugin Review",
                description="Ensure all plugins are actively maintained and updated",
                priority="high",
                effort="low",
            ),
            Recommendation(
                section="Plugin & Theme Audit",
                subsection="Plugin Review",
                description="Replace plugins with known vulnerabilities with secure alternatives",
                priority="high",
                effort="medium",
            ),
            Recommendation(
                section="Plugin & Theme Audit",
                subsection="Plugin Review",
                description="Document all custom code and plugin configurations",
                priority="medium",
                effort="low",
            ),
        ]

    def _recommend_theme(self) -> list[Recommendation]:
        """Generate theme recommendations."""
        return [
            Recommendation(
                section="Plugin & Theme Audit",
                subsection="Theme Review",
                description="Verify theme is actively supported and receives security updates",
                priority="high",
                effort="low",
            ),
            Recommendation(
                section="Plugin & Theme Audit",
                subsection="Theme Review",
                description="Consider lightweight theme if current theme is bloated",
                priority="medium",
                effort="high",
            ),
            Recommendation(
                section="Plugin & Theme Audit",
                subsection="Theme Review",
                description="Document any custom theme modifications or child theme usage",
                priority="medium",
                effort="low",
            ),
        ]

    def _recommend_general(self) -> list[Recommendation]:
        """Generate general WordPress recommendations."""
        return [
            Recommendation(
                section="Plugin & Theme Audit",
                subsection="Recommendations",
                description="Remove inactive plugins and themes",
                priority="medium",
                effort="low",
            ),
            Recommendation(
                section="Plugin & Theme Audit",
                subsection="Recommendations",
                description="Replace plugins with overlapping functionality",
                priority="medium",
                effort="medium",
            ),
            Recommendation(
                section="Plugin & Theme Audit",
                subsection="Recommendations",
                description="Update WordPress core, themes, and plugins to latest versions",
                priority="high",
                effort="low",
            ),
            Recommendation(
                section="Plugin & Theme Audit",
                subsection="Recommendations",
                description="Implement regular backup and update schedule",
                priority="high",
                effort="low",
            ),
        ]
