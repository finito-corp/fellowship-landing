from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.validate_static_release import validate_site


class StaticReleaseValidationTests(unittest.TestCase):
    def test_missing_internal_asset_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text('<a href="/missing.html">broken</a>', encoding="utf-8")
            errors = validate_site(root)
            self.assertTrue(any("missing.html" in error for error in errors))

    def test_existing_internal_pages_and_fragments_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text(
                '<a href="/privacy.html">privacy</a><a href="#apply">apply</a><section id="apply"></section>',
                encoding="utf-8",
            )
            (root / "privacy.html").write_text("privacy", encoding="utf-8")
            self.assertEqual(validate_site(root), [])

    def test_publishable_landing_is_a_non_collecting_hold(self) -> None:
        root = Path(__file__).resolve().parents[1]
        index = (root / "index.html").read_text(encoding="utf-8")
        alternate = (root / "lime-light.html").read_text(encoding="utf-8")

        self.assertEqual(index, alternate)
        self.assertIn('data-collection-state="none"', index)
        self.assertIn("현재는 지원 정보를 받지 않습니다", index)
        self.assertNotIn("<form", index.lower())
        for retired_path_or_promise in (
            "forms.fillout.com",
            "docs.google.com/forms",
            "mailto:",
            "2기 합류 신청",
            "AI 살롱",
            "Career Track",
            "Global Track",
            "Life Track",
        ):
            self.assertNotIn(retired_path_or_promise, index)

    def test_policy_pages_state_that_the_hold_page_collects_no_applications(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for filename in ("privacy.html", "terms.html"):
            text = (root / filename).read_text(encoding="utf-8")
            self.assertIn("현재 이 페이지에서는 지원 정보를 수집하지 않습니다", text)
            self.assertNotIn("Fillout", text)
            self.assertNotIn("Career, Global, Life", text)

    def test_pull_request_validation_uses_the_non_collecting_contract(self) -> None:
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github/workflows/validate.yml").read_text(encoding="utf-8")

        self.assertIn("python -m unittest tests.test_static_release -v", workflow)
        for retired_assertion in ("2기 합류 신청", "forms.fillout.com", "winning_fellowship", "mailto:"):
            self.assertNotIn(retired_assertion, workflow)


if __name__ == "__main__":
    unittest.main()
