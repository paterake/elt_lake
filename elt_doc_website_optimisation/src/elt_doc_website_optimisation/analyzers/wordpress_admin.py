"""WordPress Admin API analyzer - Plugin versions, theme details, security checks."""

import re
from typing import Any

import httpx
from bs4 import BeautifulSoup

from ..models.assessment import Finding, Recommendation, SectionResult, Severity, Status


class WordPressAdminAnalyzer:
    """Analyze WordPress site via admin API (requires credentials)."""

    def __init__(self, url: str, credentials: Any = None):
        self.url = url
        self.credentials = credentials
        self.admin_url = self._find_admin_url()
        self.session = httpx.Client()
        self.is_logged_in = False
        self.wp_version = ""
        self.plugins: list[dict[str, Any]] = []
        self.theme_info: dict[str, str] = {}

    def _find_admin_url(self) -> str:
        """Find WordPress admin URL."""
        parsed = httpx.URL(self.url)
        return f"{parsed.scheme}://{parsed.netloc}/wp-admin/"

    def login(self) -> bool:
        """Attempt to login to WordPress admin."""
        if not self.credentials:
            return False

        try:
            # First, get the login page to extract nonce
            login_url = f"{self.url.rstrip('/')}/wp-login.php"
            
            response = self.session.get(login_url, timeout=10.0)
            if response.status_code != 200:
                return False

            # Extract nonce if present
            nonce_pattern = r'name="wp_nonce"\s+value="([^"]+)"'
            nonce_match = re.search(nonce_pattern, response.text)
            
            # Prepare login data
            login_data = {
                "log": self.credentials.username,
                "pwd": self.credentials.password,
                "wp-submit": "Log In",
                "redirect_to": f"{self.url.rstrip('/')}/wp-admin/",
                "testcookie": "1",
            }

            if nonce_match:
                login_data["wp_nonce"] = nonce_match.group(1)

            # Attempt login
            response = self.session.post(
                login_url,
                data=login_data,
                timeout=10.0,
                follow_redirects=True
            )

            # Check if login was successful
            if "wp-admin" in str(response.url) or "dashboard" in response.text.lower():
                self.is_logged_in = True
                return True

            return False

        except Exception as e:
            print(f"WordPress login failed: {e}")
            return False

    def fetch_wp_version(self) -> str:
        """Fetch WordPress version."""
        if not self.is_logged_in:
            return ""

        try:
            # Check dashboard for version
            dashboard_url = f"{self.url.rstrip('/')}/wp-admin/index.php"
            response = self.session.get(dashboard_url, timeout=10.0)
            
            # Look for version in HTML
            version_pattern = r'Version\s*([\d.]+)'
            match = re.search(version_pattern, response.text)
            if match:
                self.wp_version = match.group(1)
                return self.wp_version

            # Try REST API
            rest_url = f"{self.url.rstrip('/')}/wp-json/"
            try:
                rest_response = self.session.get(rest_url, timeout=5.0)
                if rest_response.status_code == 200:
                    data = rest_response.json()
                    if "generator" in data:
                        version_match = re.search(r'([\d.]+)', data["generator"])
                        if version_match:
                            self.wp_version = version_match.group(1)
            except Exception:
                pass

            return self.wp_version

        except Exception as e:
            print(f"Error fetching WP version: {e}")
            return ""

    def fetch_plugins(self) -> list[dict[str, Any]]:
        """Fetch installed plugins info."""
        if not self.is_logged_in:
            return []

        try:
            plugins_url = f"{self.url.rstrip('/')}/wp-admin/plugins.php"
            response = self.session.get(plugins_url, timeout=10.0)

            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, "lxml")
            plugins = []

            # Method 1: Find plugin rows by data-slug attribute
            plugin_rows = soup.find_all("tr", attrs={"data-slug": True})
            
            for row in plugin_rows:
                plugin_info = {
                    "name": "",
                    "version": "",
                    "slug": row.get("data-slug", ""),
                    "status": "active" if "active" in str(row.get("class", [])) else "inactive",
                }

                # Extract plugin name from plugin name element
                name_elem = row.find("div", class_="plugin-name")
                if name_elem:
                    plugin_info["name"] = name_elem.get_text(strip=True)
                else:
                    # Fallback: look for strong tag or link
                    strong_elem = row.find("strong")
                    if strong_elem:
                        plugin_info["name"] = strong_elem.get_text(strip=True)

                # Extract version
                version_elem = row.find("div", class_="plugin-version")
                if version_elem:
                    plugin_info["version"] = version_elem.get_text(strip=True)
                else:
                    # Fallback: look for version in row text
                    version_text = row.get_text()
                    version_match = re.search(r'Version\s*([\d.]+)', version_text)
                    if version_match:
                        plugin_info["version"] = version_match.group(1)

                if plugin_info["name"] or plugin_info["slug"]:
                    plugins.append(plugin_info)

            # Method 2: If no plugins found, try alternative approach
            if not plugins:
                # Look for plugin cards in responsive view
                plugin_cards = soup.find_all("div", class_=re.compile(r"plugin-card"))
                for card in plugin_cards[:20]:
                    plugin_info = {"name": "", "version": "", "slug": "", "status": "unknown"}
                    
                    name_elem = card.find("h3") or card.find("div", class_="plugin-name")
                    if name_elem:
                        plugin_info["name"] = name_elem.get_text(strip=True)
                    
                    version_elem = card.find("div", class_="plugin-version")
                    if version_elem:
                        plugin_info["version"] = version_elem.get_text(strip=True)
                    
                    if plugin_info["name"]:
                        plugins.append(plugin_info)

            self.plugins = plugins
            return plugins

        except Exception as e:
            print(f"Error fetching plugins: {e}")
            return []

    def analyze(self) -> SectionResult:
        """Run WordPress admin analysis."""
        result = SectionResult(name="WordPress Admin Audit")

        if not self.credentials:
            result.findings.append(Finding(
                section="Plugin & Theme Audit",
                subsection="Plugin Review",
                description="No WordPress credentials provided",
                severity=Severity.MEDIUM,
                status=Status.NOT_CHECKED,
                url=self.url,
            ))
            return result

        # Attempt login
        if not self.login():
            result.findings.append(Finding(
                section="Plugin & Theme Audit",
                subsection="Plugin Review",
                description="WordPress login failed - check credentials",
                severity=Severity.HIGH,
                status=Status.FAIL,
                evidence=f"Admin URL: {self.admin_url}",
                url=self.url,
            ))
            result.recommendations.append(Recommendation(
                section="Plugin & Theme Audit",
                subsection="Plugin Review",
                description="Verify WordPress admin credentials are correct",
                priority="high",
                effort="low",
            ))
            return result

        # Fetch WordPress version
        wp_version = self.fetch_wp_version()
        if wp_version:
            result.findings.append(Finding(
                section="Plugin & Theme Audit",
                subsection="Plugin Review",
                description=f"WordPress version: {wp_version}",
                severity=Severity.LOW,
                status=Status.PASS,
                evidence=f"Version: {wp_version}",
                url=self.url,
            ))

            # Check for outdated WordPress
            if wp_version.startswith(("4.", "5.0", "5.1", "5.2", "5.3", "5.4", "5.5", "5.6", "5.7", "5.8", "5.9")):
                result.findings.append(Finding(
                    section="Plugin & Theme Audit",
                    subsection="Plugin Review",
                    description=f"WordPress version {wp_version} may be outdated",
                    severity=Severity.MEDIUM,
                    status=Status.WARNING,
                    evidence=f"Current version: {wp_version}",
                    url=self.url,
                ))

        # Fetch plugins
        plugins = self.fetch_plugins()
        if plugins:
            active_plugins = [p for p in plugins if p.get("status") == "active"]
            inactive_plugins = [p for p in plugins if p.get("status") == "inactive"]

            result.findings.append(Finding(
                section="Plugin & Theme Audit",
                subsection="Plugin Review",
                description=f"Total plugins: {len(plugins)} (Active: {len(active_plugins)}, Inactive: {len(inactive_plugins)})",
                severity=Severity.LOW,
                status=Status.PASS,
                evidence=f"Plugins: {[p['name'] for p in plugins[:10]]}",
                url=self.url,
            ))

            # Check for plugins without versions (may be outdated)
            no_version = [p for p in plugins if not p.get("version")]
            if no_version:
                result.findings.append(Finding(
                    section="Plugin & Theme Audit",
                    subsection="Plugin Review",
                    description=f"{len(no_version)} plugin(s) without version info",
                    severity=Severity.LOW,
                    status=Status.WARNING,
                    evidence=f"No version: {[p['name'] for p in no_version[:5]]}",
                    url=self.url,
                ))

            # Check for inactive plugins
            if inactive_plugins:
                result.findings.append(Finding(
                    section="Plugin & Theme Audit",
                    subsection="Plugin Review",
                    description=f"{len(inactive_plugins)} inactive plugin(s) - consider removing",
                    severity=Severity.LOW,
                    status=Status.WARNING,
                    evidence=f"Inactive: {[p['name'] for p in inactive_plugins[:5]]}",
                    url=self.url,
                ))

        # Recommendations
        result.recommendations.extend(self._recommendations())

        return result

    def _recommendations(self) -> list[Recommendation]:
        """Generate WordPress admin recommendations."""
        recs = []

        if self.plugins:
            inactive = [p for p in self.plugins if p.get("status") == "inactive"]
            if inactive:
                recs.append(Recommendation(
                    section="Plugin & Theme Audit",
                    subsection="Plugin Review",
                    description=f"Remove {len(inactive)} inactive plugin(s) to reduce attack surface",
                    priority="medium",
                    effort="low",
                ))

        recs.append(Recommendation(
            section="Plugin & Theme Audit",
            subsection="Plugin Review",
            description="Enable auto-updates for WordPress core and trusted plugins",
            priority="medium",
            effort="low",
        ))

        recs.append(Recommendation(
            section="Plugin & Theme Audit",
            subsection="Plugin Review",
            description="Install a security plugin (e.g., Wordfence, Sucuri) for vulnerability scanning",
            priority="high",
            effort="low",
        ))

        return recs

    def close(self):
        """Close the session."""
        self.session.close()
