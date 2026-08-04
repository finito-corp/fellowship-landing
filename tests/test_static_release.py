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

    def test_publishable_landing_uses_only_the_server_verified_application_route(self) -> None:
        root = Path(__file__).resolve().parents[1]
        index = (root / "index.html").read_text(encoding="utf-8")
        alternate = (root / "lime-light.html").read_text(encoding="utf-8")

        self.assertEqual(index, alternate)
        self.assertIn('data-collection-state="server-verified"', index)
        self.assertIn('href="https://product-omrpipeline-production.up.railway.app/fellowship/3"', index)
        self.assertIn("정식 지원서로 3기 대기 명단을 받습니다.", index)
        self.assertNotIn("<form", index.lower())
        self.assertNotIn('aria-disabled="true"', index)
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

    def test_policy_pages_describe_the_live_application_scope_without_promising_selection(self) -> None:
        root = Path(__file__).resolve().parents[1]
        privacy = (root / "privacy.html").read_text(encoding="utf-8")
        terms = (root / "terms.html").read_text(encoding="utf-8")

        self.assertIn('data-collection-state="server-verified"', privacy)
        self.assertIn("3기 지원서에 필요한 정보만 받습니다", privacy)
        self.assertIn("2026-11-30", privacy)
        self.assertIn("송일현", privacy)
        self.assertNotIn("현재 이 페이지에서는 지원 정보를 수집하지 않습니다", privacy)
        self.assertIn('data-collection-state="server-verified"', terms)
        self.assertIn("지원이 곧 합류 확정은 아닙니다", terms)
        self.assertIn("조기 제출만으로 자동 선발하지 않습니다", terms)
        for text in (privacy, terms):
            self.assertNotIn("Fillout", text)
            self.assertNotIn("Career, Global, Life", text)

    def test_pull_request_validation_covers_the_live_route_contract(self) -> None:
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github/workflows/validate.yml").read_text(encoding="utf-8")

        self.assertIn("python -m unittest tests.test_static_release -v", workflow)
        self.assertIn("cmp index.html lime-light.html", workflow)

    def test_landing_uses_human_opening_copy_and_a_live_cta(self) -> None:
        root = Path(__file__).resolve().parents[1]
        primary = (root / "index.html").read_text(encoding="utf-8")

        self.assertIn("AI로 내 삶을 움직일", primary)
        self.assertNotIn("3기를 기다립니다.", primary)
        self.assertIn("3기 지원 접수 중", primary)
        self.assertIn("대기 명단 지원하기", primary)
        self.assertIn("2주 동안 직접 해 봅니다.", primary)
        self.assertIn("맞으면 12주를 더 갑니다.", primary)
        self.assertIn("AI를 잘 쓰는 사람보다", primary)
        self.assertIn("1·2기에서 배워, 3기는 이렇게 바꿨습니다.", primary)
        self.assertIn("1기 익명 후기", primary)
        self.assertIn("지원 전에 궁금할 만한 것", primary)
        self.assertIn("8/31–11/22", primary)
        self.assertEqual(primary.count("https://product-omrpipeline-production.up.railway.app/fellowship/3"), 3)
        for archive_asset in (
            "invite/photos/g2_kickoff.jpg",
            "invite/photos/ai3_handson.jpg",
            "invite/photos/g1_act_mountain.jpg",
            "invite/photos/g1_sudadi_group.jpg",
            "invite/photos/g1_graduation2.jpg",
        ):
            self.assertIn(archive_asset, primary)
        self.assertNotIn("8/4 OPEN 예정", primary)
        self.assertNotIn("HOW WE START", primary)
        self.assertNotIn("공개 지원폼과 운영 경로", primary)


if __name__ == "__main__":
    unittest.main()
