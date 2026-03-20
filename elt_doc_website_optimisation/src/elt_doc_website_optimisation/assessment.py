"""Main assessment orchestrator."""

import tempfile
from pathlib import Path

from elt_doc_website_optimisation.config_loader import load_config
from elt_doc_website_optimisation.models.assessment import (
    AssessmentConfig,
    AssessmentResult,
    Finding,
    Recommendation,
    SectionResult,
    Severity,
    Status,
)
from elt_doc_website_optimisation.screenshot import ScreenshotCapture
from elt_doc_website_optimisation.analyzers.analytics import AnalyticsAnalyzer
from elt_doc_website_optimisation.analyzers.content import ContentAnalyzer
from elt_doc_website_optimisation.analyzers.seo import SEOAnalyzer
from elt_doc_website_optimisation.analyzers.technical import TechnicalAnalyzer
from elt_doc_website_optimisation.analyzers.ux_navigation import UXNavigationAnalyzer
from elt_doc_website_optimisation.analyzers.wordpress import WordPressAnalyzer
from elt_doc_website_optimisation.report.generator import ReportGenerator


class AssessmentOrchestrator:
    """Orchestrate the full website assessment."""

    def __init__(self, config_path: Path):
        self.config = load_config(config_path)
        self.results: list[AssessmentResult] = []

    def run(self) -> Path:
        """Run the full assessment and generate report."""
        print(f"Starting assessment: {self.config.name}")
        print(f"Websites to assess: {len(self.config.websites)}")
        print(f"Output: {self.config.output_path}")
        print()

        # Create temp directory for screenshots
        with tempfile.TemporaryDirectory() as temp_dir:
            screenshots_dir = Path(temp_dir) / "screenshots"
            screenshots_dir.mkdir(parents=True, exist_ok=True)

            for website in self.config.websites:
                print(f"\n{'='*60}")
                print(f"Assessing: {website.name}")
                print(f"URL: {website.url}")
                print(f"{'='*60}")

                result = self._assess_website(website, screenshots_dir)
                self.results.append(result)

            # Generate report
            print("\n" + "="*60)
            print("Generating report...")
            print("="*60)

            report_generator = ReportGenerator(self.config)
            output_path = report_generator.generate(self.results, screenshots_dir)

            print(f"\n✓ Report generated: {output_path}")
            return output_path

    def _assess_website(self, website, screenshots_dir: Path) -> AssessmentResult:
        """Assess a single website."""
        result = AssessmentResult(
            website_url=website.url,
            website_name=website.name,
        )

        # 1. Technical Review
        print("\n[1/6] Technical Review...")
        technical = TechnicalAnalyzer(website.url)
        if technical.fetch():
            result.sections["Technical Review"] = technical.analyze()
        else:
            result.sections["Technical Review"] = SectionResult(
                name="Technical Review",
                findings=[Finding(
                    section="Technical Review",
                    subsection="General",
                    description="Failed to fetch website",
                    severity=Severity.HIGH,
                    status=Status.FAIL,
                    url=website.url,
                )],
            )

        # 2. UX & Navigation (includes screenshots)
        print("[2/6] UX & Navigation...")
        ux = UXNavigationAnalyzer(website.url)
        if ux.fetch():
            ux_result = ux.analyze()
            
            # Save screenshots
            if ux.screenshot_desktop:
                desktop_path = screenshots_dir / f"{website.name}_desktop.png"
                desktop_path.write_bytes(ux.screenshot_desktop)
                ux_result.screenshots.append(desktop_path)
            
            if ux.screenshot_mobile:
                mobile_path = screenshots_dir / f"{website.name}_mobile.png"
                mobile_path.write_bytes(ux.screenshot_mobile)
                ux_result.screenshots.append(mobile_path)
            
            result.sections["UX & Navigation"] = ux_result
        else:
            result.sections["UX & Navigation"] = SectionResult(name="UX & Navigation")

        # 3. Content & Messaging
        print("[3/6] Content & Messaging...")
        content = ContentAnalyzer(website.url, ux.html if hasattr(ux, 'html') else "")
        result.sections["Content & Messaging"] = content.analyze()

        # 4. SEO Review
        print("[4/6] SEO Review...")
        seo = SEOAnalyzer(website.url, ux.html if hasattr(ux, 'html') else "")
        result.sections["SEO Review"] = seo.analyze()

        # 5. Plugin & Theme Audit (WordPress)
        print("[5/6] Plugin & Theme Audit...")
        wordpress = WordPressAnalyzer(website.url, self.config.credentials)
        if wordpress.detect_wordpress():
            result.sections["Plugin & Theme Audit"] = wordpress.analyze()
        else:
            result.sections["Plugin & Theme Audit"] = SectionResult(
                name="Plugin & Theme Audit",
                findings=[Finding(
                    section="Plugin & Theme Audit",
                    subsection="General",
                    description="Website is not WordPress-based",
                    severity=Severity.LOW,
                    status=Status.PASS,
                    url=website.url,
                )],
            )

        # 6. Analytics & Tracking
        print("[6/6] Analytics & Tracking...")
        analytics = AnalyticsAnalyzer(website.url, ux.html if hasattr(ux, 'html') else "")
        result.sections["Analytics & Tracking"] = analytics.analyze()

        # Calculate overall score
        result.overall_score = self._calculate_score(result)
        result.summary = self._generate_summary(result)

        print(f"\nOverall Score: {result.overall_score:.1f}/100")

        return result

    def _calculate_score(self, result: AssessmentResult) -> float:
        """Calculate overall score based on findings."""
        total_points = 0
        earned_points = 0

        for section in result.sections.values():
            for finding in section.findings:
                total_points += 1
                
                # Severity weight
                if finding.severity == Severity.CRITICAL:
                    sev_weight = 0
                elif finding.severity == Severity.HIGH:
                    sev_weight = 0.25
                elif finding.severity == Severity.MEDIUM:
                    sev_weight = 0.5
                else:  # LOW
                    sev_weight = 1.0
                
                # Status weight
                if finding.status == Status.PASS:
                    status_weight = 1.0
                elif finding.status == Status.WARNING:
                    status_weight = 0.5
                elif finding.status == Status.FAIL:
                    status_weight = 0
                else:  # NOT_CHECKED
                    status_weight = 0.5
                
                earned_points += sev_weight * status_weight

        if total_points == 0:
            return 0.0

        return (earned_points / total_points) * 100

    def _generate_summary(self, result: AssessmentResult) -> str:
        """Generate summary text for the assessment."""
        critical_count = 0
        high_count = 0

        for section in result.sections.values():
            for finding in section.findings:
                if finding.severity == Severity.CRITICAL:
                    critical_count += 1
                elif finding.severity == Severity.HIGH:
                    high_count += 1

        if critical_count > 0:
            return f"Critical issues found: {critical_count}. Immediate attention required."
        elif high_count > 0:
            return f"High-priority issues found: {high_count}. Address soon."
        else:
            return "No critical or high-priority issues found. Focus on continuous improvement."
