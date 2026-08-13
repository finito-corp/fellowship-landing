from __future__ import annotations

import unittest
from html.parser import HTMLParser
from pathlib import Path


class ApplicationContractParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.elements: dict[str, dict[str, str | None]] = {}
        self.skip_targets: list[str] = []
        self.mailto_links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        element_id = attributes.get("id")
        if element_id:
            self.elements[element_id] = {"tag": tag, **attributes}

        classes = set((attributes.get("class") or "").split())
        href = attributes.get("href")
        if tag == "a" and "skip-link" in classes and href:
            self.skip_targets.append(href)
        if tag == "a" and href and href.startswith("mailto:"):
            self.mailto_links.append(href)


class ApplicationUxStaticTests(unittest.TestCase):
    def test_landing_and_application_expose_main_skip_targets(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for relative_path in ("index.html", "lime-light.html", "apply/index.html"):
            parser = ApplicationContractParser()
            parser.feed((root / relative_path).read_text(encoding="utf-8"))

            self.assertIn("#main-content", parser.skip_targets)
            self.assertEqual(parser.elements["main-content"]["tag"], "main")

    def test_application_declares_error_and_direct_submit_state(self) -> None:
        root = Path(__file__).resolve().parents[1]
        parser = ApplicationContractParser()
        parser.feed((root / "apply" / "index.html").read_text(encoding="utf-8"))

        error_summary = parser.elements["error-summary"]
        result = parser.elements["result"]
        submit_button = parser.elements["submit-button"]
        self.assertEqual(error_summary["role"], "alert")
        self.assertEqual(error_summary["tabindex"], "-1")
        self.assertIn("hidden", error_summary)
        self.assertEqual(result["role"], "status")
        self.assertEqual(result["aria-live"], "polite")
        self.assertEqual(submit_button["type"], "submit")
        self.assertNotIn("review-panel", parser.elements)
        self.assertNotIn("final-submit-button", parser.elements)
        self.assertEqual(parser.elements["available-windows"]["aria-describedby"], "available-windows-help available-windows-error")

    def test_completion_exposes_the_correction_channel(self) -> None:
        root = Path(__file__).resolve().parents[1]
        parser = ApplicationContractParser()
        parser.feed((root / "apply" / "complete" / "index.html").read_text(encoding="utf-8"))

        self.assertEqual(parser.mailto_links, ["mailto:irs8@finito.me"])


if __name__ == "__main__":
    unittest.main()
