"""Visual analyzer - Basic color contrast and layout checks."""

import re
from typing import Any, Dict, List, Tuple

from bs4 import BeautifulSoup

from ..models.assessment import Finding, Recommendation, SectionResult, Severity, Status


class VisualAnalyzer:
    """Analyze visual aspects - colors, contrast (basic)."""

    def __init__(self, url: str, html: str = ""):
        self.url = url
        self.html = html

    def analyze(self) -> SectionResult:
        """Run visual analysis checks."""
        result = SectionResult(name="Visual Analysis")

        if not self.html:
            result.findings.append(Finding(
                section="Visual Analysis",
                subsection="General",
                description="No HTML content to analyze",
                severity=Severity.MEDIUM,
                status=Status.NOT_CHECKED,
                url=self.url,
            ))
            return result

        # Color contrast (inline styles)
        result.findings.extend(self._check_inline_colors())
        result.recommendations.extend(self._recommend_colors())

        # Font sizes
        result.findings.extend(self._check_font_sizes())
        result.recommendations.extend(self._recommend_fonts())

        # Link styling
        result.findings.extend(self._check_link_styling())

        return result

    def _parse_color(self, color_str: str) -> Tuple[int, int, int] | None:
        """Parse color string to RGB tuple."""
        if not color_str:
            return None

        # Hex color
        hex_match = re.match(r'^#([0-9a-f]{6})$', color_str.lower())
        if hex_match:
            hex_val = hex_match.group(1)
            return (
                int(hex_val[0:2], 16),
                int(hex_val[2:4], 16),
                int(hex_val[4:6], 16)
            )

        # RGB color
        rgb_match = re.match(r'rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', color_str.lower())
        if rgb_match:
            return (
                int(rgb_match.group(1)),
                int(rgb_match.group(2)),
                int(rgb_match.group(3))
            )

        return None

    def _calculate_luminance(self, rgb: Tuple[int, int, int]) -> float:
        """Calculate relative luminance of a color."""
        def adjust(c):
            c = c / 255.0
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

        r, g, b = rgb
        return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)

    def _contrast_ratio(self, rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]) -> float:
        """Calculate contrast ratio between two colors."""
        l1 = self._calculate_luminance(rgb1)
        l2 = self._calculate_luminance(rgb2)

        lighter = max(l1, l2)
        darker = min(l1, l2)

        return (lighter + 0.05) / (darker + 0.05)

    def _check_inline_colors(self) -> list[Finding]:
        """Check inline color styles for potential contrast issues."""
        findings = []

        try:
            soup = BeautifulSoup(self.html, "lxml")
            
            elements_with_colors = []
            contrast_issues = []

            # Find elements with inline color styles
            for elem in soup.find_all(style=True):
                style = elem.get("style", "")
                
                # Extract color and background-color
                color_match = re.search(r'color\s*:\s*([^;]+)', style)
                bg_match = re.search(r'background(?:-color)?\s*:\s*([^;]+)', style)

                if color_match and bg_match:
                    fg_color = self._parse_color(color_match.group(1).strip())
                    bg_color = self._parse_color(bg_match.group(1).strip())

                    if fg_color and bg_color:
                        ratio = self._contrast_ratio(fg_color, bg_color)
                        elements_with_colors.append({
                            "tag": elem.name,
                            "ratio": ratio,
                            "text": elem.get_text(strip=True)[:50]
                        })

                        # WCAG AA requires 4.5:1 for normal text
                        if ratio < 4.5:
                            contrast_issues.append({
                                "tag": elem.name,
                                "ratio": ratio,
                                "text": elem.get_text(strip=True)[:50]
                            })

            if contrast_issues:
                findings.append(Finding(
                    section="Visual Analysis",
                    subsection="Accessibility",
                    description=f"{len(contrast_issues)} element(s) with potential contrast issues",
                    severity=Severity.MEDIUM,
                    status=Status.WARNING,
                    evidence=f"Issues: {[f'{ci['ratio']:.2f}' for ci in contrast_issues[:5]]}",
                    url=self.url,
                ))
            elif elements_with_colors:
                findings.append(Finding(
                    section="Visual Analysis",
                    subsection="Accessibility",
                    description=f"{len(elements_with_colors)} element(s) with inline colors - all pass contrast",
                    severity=Severity.LOW,
                    status=Status.PASS,
                    evidence=f"Checked {len(elements_with_colors)} elements",
                    url=self.url,
                ))
            else:
                findings.append(Finding(
                    section="Visual Analysis",
                    subsection="Accessibility",
                    description="No inline color styles found (colors likely in CSS)",
                    severity=Severity.LOW,
                    status=Status.PASS,
                    evidence="Colors defined in external stylesheets",
                    url=self.url,
                ))

        except Exception as e:
            findings.append(Finding(
                section="Visual Analysis",
                subsection="Accessibility",
                description=f"Error checking colors: {str(e)}",
                severity=Severity.MEDIUM,
                status=Status.NOT_CHECKED,
                evidence=str(e),
                url=self.url,
            ))

        return findings

    def _check_font_sizes(self) -> list[Finding]:
        """Check font sizes for readability."""
        findings = []

        try:
            soup = BeautifulSoup(self.html, "lxml")
            
            small_fonts = []
            
            for elem in soup.find_all(style=True):
                style = elem.get("style", "")
                font_size_match = re.search(r'font-size\s*:\s*([^;]+)', style)
                
                if font_size_match:
                    size_str = font_size_match.group(1).strip().lower()
                    
                    # Check for small sizes
                    if any(size_str.startswith(x) for x in ["10px", "11px", "12px", "9px", "8px"]):
                        small_fonts.append({
                            "tag": elem.name,
                            "size": size_str,
                            "text": elem.get_text(strip=True)[:30]
                        })

            if small_fonts:
                findings.append(Finding(
                    section="Visual Analysis",
                    subsection="Readability",
                    description=f"{len(small_fonts)} element(s) with small font sizes",
                    severity=Severity.LOW,
                    status=Status.WARNING,
                    evidence=f"Small fonts: {small_fonts[:3]}",
                    url=self.url,
                ))
            else:
                findings.append(Finding(
                    section="Visual Analysis",
                    subsection="Readability",
                    description="No small font sizes detected in inline styles",
                    severity=Severity.LOW,
                    status=Status.PASS,
                    evidence="Font sizes appear adequate",
                    url=self.url,
                ))

        except Exception as e:
            findings.append(Finding(
                section="Visual Analysis",
                subsection="Readability",
                description=f"Error checking font sizes: {str(e)}",
                severity=Severity.MEDIUM,
                status=Status.NOT_CHECKED,
                evidence=str(e),
                url=self.url,
            ))

        return findings

    def _check_link_styling(self) -> list[Finding]:
        """Check if links are visually distinguishable."""
        findings = []

        try:
            soup = BeautifulSoup(self.html, "lxml")
            
            links = soup.find_all("a", href=True)[:20]
            underlined_links = 0
            colored_links = 0

            for link in links:
                style = link.get("style", "")
                
                if "underline" in style.lower():
                    underlined_links += 1
                if "color" in style.lower():
                    colored_links += 1

            # If no links have visual styling, flag it
            if underlined_links == 0 and colored_links == 0:
                findings.append(Finding(
                    section="Visual Analysis",
                    subsection="Accessibility",
                    description="Links may not be visually distinguishable (no inline underline/color)",
                    severity=Severity.LOW,
                    status=Status.WARNING,
                    evidence="Check CSS for link styling",
                    url=self.url,
                ))
            else:
                findings.append(Finding(
                    section="Visual Analysis",
                    subsection="Accessibility",
                    description=f"Links have visual styling ({underlined_links} underlined, {colored_links} colored)",
                    severity=Severity.LOW,
                    status=Status.PASS,
                    evidence="Links appear distinguishable",
                    url=self.url,
                ))

        except Exception as e:
            findings.append(Finding(
                section="Visual Analysis",
                subsection="Accessibility",
                description=f"Error checking link styling: {str(e)}",
                severity=Severity.MEDIUM,
                status=Status.NOT_CHECKED,
                evidence=str(e),
                url=self.url,
            ))

        return findings

    def _recommend_colors(self) -> list[Recommendation]:
        """Generate color recommendations."""
        return [
            Recommendation(
                section="Visual Analysis",
                subsection="Accessibility",
                description="Ensure all text has minimum 4.5:1 contrast ratio (WCAG AA)",
                priority="high",
                effort="medium",
            ),
            Recommendation(
                section="Visual Analysis",
                subsection="Accessibility",
                description="Use online contrast checker for main brand colors",
                priority="medium",
                effort="low",
            ),
        ]

    def _recommend_fonts(self) -> list[Recommendation]:
        """Generate font recommendations."""
        return [
            Recommendation(
                section="Visual Analysis",
                subsection="Readability",
                description="Use minimum 16px font size for body text",
                priority="medium",
                effort="low",
            ),
            Recommendation(
                section="Visual Analysis",
                subsection="Readability",
                description="Ensure buttons have minimum 14px font for readability",
                priority="low",
                effort="low",
            ),
        ]
