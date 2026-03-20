"""Content & Messaging analyzer - Tone, CTAs, Outdated content."""

import re
from datetime import datetime

from bs4 import BeautifulSoup

from ..models.assessment import Finding, Recommendation, SectionResult, Severity, Status


class ContentAnalyzer:
    """Analyze content and messaging aspects of a website."""

    def __init__(self, url: str, html: str = ""):
        self.url = url
        self.html = html

    def analyze(self) -> SectionResult:
        """Run all content and messaging analysis checks."""
        result = SectionResult(name="Content & Messaging")

        if not self.html:
            result.findings.append(Finding(
                section="Content & Messaging",
                subsection="General",
                description="No HTML content to analyze",
                severity=Severity.MEDIUM,
                status=Status.NOT_CHECKED,
                url=self.url,
            ))
            return result

        # Tone and clarity
        result.findings.extend(self._check_tone_clarity())
        result.recommendations.extend(self._recommend_tone())

        # Calls to action
        result.findings.extend(self._check_ctas())
        result.recommendations.extend(self._recommend_ctas())

        # Outdated content
        result.findings.extend(self._check_outdated_content())
        result.recommendations.extend(self._recommend_outdated())

        return result

    def _check_tone_clarity(self) -> list[Finding]:
        """Check tone and clarity of content."""
        findings = []

        try:
            soup = BeautifulSoup(self.html, "lxml")

            # Get text content
            text = soup.get_text(separator=" ", strip=True)
            words = text.split()
            word_count = len(words)

            # Check word count
            if word_count < 300:
                findings.append(Finding(
                    section="Content & Messaging",
                    subsection="Tone and clarity",
                    description=f"Low word count: {word_count} words (recommended: 300+)",
                    severity=Severity.MEDIUM,
                    status=Status.WARNING,
                    evidence=f"Word count: {word_count}",
                    url=self.url,
                ))
            elif word_count > 3000:
                findings.append(Finding(
                    section="Content & Messaging",
                    subsection="Tone and clarity",
                    description=f"High word count: {word_count} words - may be too text-heavy",
                    severity=Severity.LOW,
                    status=Status.WARNING,
                    evidence=f"Word count: {word_count}",
                    url=self.url,
                ))
            else:
                findings.append(Finding(
                    section="Content & Messaging",
                    subsection="Tone and clarity",
                    description=f"Appropriate word count: {word_count} words",
                    severity=Severity.LOW,
                    status=Status.PASS,
                    evidence=f"Word count: {word_count}",
                    url=self.url,
                ))

            # Check for paragraphs
            paragraphs = soup.find_all("p")
            if len(paragraphs) < 3:
                findings.append(Finding(
                    section="Content & Messaging",
                    subsection="Tone and clarity",
                    description=f"Few paragraphs: {len(paragraphs)} - content may be sparse",
                    severity=Severity.MEDIUM,
                    status=Status.WARNING,
                    evidence=f"Paragraph count: {len(paragraphs)}",
                    url=self.url,
                ))

            # Check for value proposition keywords
            value_keywords = ["we help", "our services", "solutions", "expertise", "professional"]
            text_lower = text.lower()
            found_keywords = [kw for kw in value_keywords if kw in text_lower]
            
            if not found_keywords:
                findings.append(Finding(
                    section="Content & Messaging",
                    subsection="Tone and clarity",
                    description="Value proposition may not be clear - few value-oriented keywords found",
                    severity=Severity.MEDIUM,
                    status=Status.WARNING,
                    evidence=f"Keywords found: {found_keywords}",
                    url=self.url,
                ))

        except Exception as e:
            findings.append(Finding(
                section="Content & Messaging",
                subsection="Tone and clarity",
                description=f"Error analyzing content: {str(e)}",
                severity=Severity.MEDIUM,
                status=Status.NOT_CHECKED,
                evidence=str(e),
                url=self.url,
            ))

        return findings

    def _check_ctas(self) -> list[Finding]:
        """Check calls to action."""
        findings = []

        try:
            soup = BeautifulSoup(self.html, "lxml")

            # Look for CTA elements
            cta_patterns = [
                r"contact\s*us",
                r"get\s*in\s*touch",
                r"request\s*a\s*quote",
                r"learn\s*more",
                r"sign\s*up",
                r"subscribe",
                r"download",
                r"book\s*(now|a|an)",
                r"call\s*(us|now)",
                r"email\s*us",
            ]

            text = soup.get_text(separator=" ", strip=True).lower()
            found_ctas = []

            for pattern in cta_patterns:
                if re.search(pattern, text):
                    found_ctas.append(pattern)

            # Check for buttons and links that might be CTAs
            buttons = soup.find_all(["button", "a"])
            cta_buttons = []
            for btn in buttons:
                btn_text = btn.get_text(strip=True).lower()
                if any(re.search(p, btn_text) for p in cta_patterns):
                    cta_buttons.append(btn_text)

            if not found_ctas and not cta_buttons:
                findings.append(Finding(
                    section="Content & Messaging",
                    subsection="Calls to action",
                    description="No clear calls to action found",
                    severity=Severity.HIGH,
                    status=Status.FAIL,
                    evidence="No CTAs detected",
                    url=self.url,
                ))
            elif len(found_ctas) < 2:
                findings.append(Finding(
                    section="Content & Messaging",
                    subsection="Calls to action",
                    description=f"Limited CTAs found: {len(found_ctas)}",
                    severity=Severity.MEDIUM,
                    status=Status.WARNING,
                    evidence=f"CTAs: {found_ctas}",
                    url=self.url,
                ))
            else:
                findings.append(Finding(
                    section="Content & Messaging",
                    subsection="Calls to action",
                    description=f"Good variety of CTAs: {len(found_ctas)}",
                    severity=Severity.LOW,
                    status=Status.PASS,
                    evidence=f"CTAs: {found_ctas}",
                    url=self.url,
                ))

        except Exception as e:
            findings.append(Finding(
                section="Content & Messaging",
                subsection="Calls to action",
                description=f"Error analyzing CTAs: {str(e)}",
                severity=Severity.MEDIUM,
                status=Status.NOT_CHECKED,
                evidence=str(e),
                url=self.url,
            ))

        return findings

    def _check_outdated_content(self) -> list[Finding]:
        """Check for outdated content."""
        findings = []

        try:
            soup = BeautifulSoup(self.html, "lxml")
            text = soup.get_text(separator=" ", strip=True)

            # Look for years in content
            current_year = datetime.now().year
            year_pattern = r"\b(20\d{2})\b"
            years_found = re.findall(year_pattern, text)

            if years_found:
                years = [int(y) for y in years_found]
                oldest_year = min(years)
                newest_year = max(years)

                # Check for old years
                if newest_year < current_year - 1:
                    findings.append(Finding(
                        section="Content & Messaging",
                        subsection="Outdated content",
                        description=f"Content may be outdated - most recent year: {newest_year}",
                        severity=Severity.MEDIUM,
                        status=Status.FAIL,
                        evidence=f"Years found: {set(years)}",
                        url=self.url,
                    ))
                elif oldest_year < current_year - 3:
                    findings.append(Finding(
                        section="Content & Messaging",
                        subsection="Outdated content",
                        description=f"Some content references old dates (from {oldest_year})",
                        severity=Severity.LOW,
                        status=Status.WARNING,
                        evidence=f"Years found: {set(years)}",
                        url=self.url,
                    ))
                else:
                    findings.append(Finding(
                        section="Content & Messaging",
                        subsection="Outdated content",
                        description="Content appears current",
                        severity=Severity.LOW,
                        status=Status.PASS,
                        evidence=f"Most recent year: {newest_year}",
                        url=self.url,
                    ))

            # Check for "copyright" year in footer
            copyright_pattern = r"copyright.*?(20\d{2})"
            copyright_matches = re.findall(copyright_pattern, text.lower())
            if copyright_matches:
                copyright_year = max(int(y) for y in copyright_matches)
                if copyright_year < current_year:
                    findings.append(Finding(
                        section="Content & Messaging",
                        subsection="Outdated content",
                        description=f"Copyright year not updated: {copyright_year}",
                        severity=Severity.LOW,
                        status=Status.WARNING,
                        evidence=f"Copyright year: {copyright_year}",
                        url=self.url,
                    ))

        except Exception as e:
            findings.append(Finding(
                section="Content & Messaging",
                subsection="Outdated content",
                description=f"Error checking for outdated content: {str(e)}",
                severity=Severity.MEDIUM,
                status=Status.NOT_CHECKED,
                evidence=str(e),
                url=self.url,
            ))

        return findings

    def _recommend_tone(self) -> list[Recommendation]:
        """Generate tone and clarity recommendations."""
        return [
            Recommendation(
                section="Content & Messaging",
                subsection="Tone and clarity",
                description="Ensure value proposition is clearly stated above the fold",
                priority="high",
                effort="medium",
            ),
            Recommendation(
                section="Content & Messaging",
                subsection="Tone and clarity",
                description="Use consistent tone and voice across all pages",
                priority="medium",
                effort="low",
            ),
            Recommendation(
                section="Content & Messaging",
                subsection="Tone and clarity",
                description="Break up large text blocks with headings, lists, and images",
                priority="medium",
                effort="low",
            ),
        ]

    def _recommend_ctas(self) -> list[Recommendation]:
        """Generate CTA recommendations."""
        return [
            Recommendation(
                section="Content & Messaging",
                subsection="Calls to action",
                description="Place primary CTA prominently above the fold",
                priority="high",
                effort="low",
            ),
            Recommendation(
                section="Content & Messaging",
                subsection="Calls to action",
                description="Use action-oriented, benefit-focused CTA copy",
                priority="medium",
                effort="low",
            ),
            Recommendation(
                section="Content & Messaging",
                subsection="Calls to action",
                description="Ensure every page has at least one clear CTA",
                priority="high",
                effort="medium",
            ),
        ]

    def _recommend_outdated(self) -> list[Recommendation]:
        """Generate outdated content recommendations."""
        return [
            Recommendation(
                section="Content & Messaging",
                subsection="Outdated content",
                description="Audit all pages for outdated dates, staff, and service information",
                priority="medium",
                effort="medium",
            ),
            Recommendation(
                section="Content & Messaging",
                subsection="Outdated content",
                description="Update copyright year in footer automatically",
                priority="low",
                effort="low",
            ),
            Recommendation(
                section="Content & Messaging",
                subsection="Outdated content",
                description="Review and archive or update old blog posts",
                priority="low",
                effort="medium",
            ),
        ]
