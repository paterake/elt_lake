"""Screenshot capture for websites."""

from pathlib import Path

from playwright.sync_api import sync_playwright


class ScreenshotCapture:
    """Capture screenshots of websites at different viewports."""

    VIEWPORTS = {
        "desktop": {"width": 1920, "height": 1080},
        "mobile": {"width": 375, "height": 667},
        "tablet": {"width": 768, "height": 1024},
    }

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def capture(self, url: str, name: str = "website") -> dict[str, Path]:
        """Capture screenshots at all viewports."""
        screenshots = {}

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                page.goto(url, wait_until="networkidle", timeout=30000)

                for viewport_name, viewport_size in self.VIEWPORTS.items():
                    page.set_viewport_size(viewport_size)
                    
                    # Wait for any animations to settle
                    page.wait_for_timeout(1000)
                    
                    screenshot_path = self.output_dir / f"{name}_{viewport_name}.png"
                    page.screenshot(path=str(screenshot_path), full_page=True)
                    screenshots[viewport_name] = screenshot_path

                browser.close()

        except Exception as e:
            print(f"Error capturing screenshots for {url}: {e}")

        return screenshots

    def capture_single(self, url: str, name: str, viewport: str = "desktop") -> Path | None:
        """Capture a single screenshot at specified viewport."""
        if viewport not in self.VIEWPORTS:
            print(f"Unknown viewport: {viewport}")
            return None

        viewport_size = self.VIEWPORTS[viewport]

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport=viewport_size)

                page.goto(url, wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(1000)

                screenshot_path = self.output_dir / f"{name}_{viewport}.png"
                page.screenshot(path=str(screenshot_path), full_page=True)

                browser.close()
                return screenshot_path

        except Exception as e:
            print(f"Error capturing screenshot for {url}: {e}")
            return None
