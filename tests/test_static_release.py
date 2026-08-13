from __future__ import annotations

import re
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

from scripts.validate_static_release import validate_site


class LandingContractParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.application_hrefs: list[str] = []
        self.faq_controls: list[str] = []
        self.faq_regions: dict[str, str | None] = {}
        self.form_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "a" and values.get("href") == "apply/":
            self.application_hrefs.append("apply/")
        if tag == "form":
            self.form_count += 1
        classes = set((values.get("class") or "").split())
        if tag == "button" and "faq-question" in classes and values.get("aria-controls"):
            self.faq_controls.append(str(values["aria-controls"]))
        if tag == "div" and "faq-answer" in classes and values.get("id"):
            self.faq_regions[str(values["id"])] = values.get("aria-hidden")


class StaticReleaseValidationTests(unittest.TestCase):
    def test_static_references_are_valid(self) -> None:
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(validate_site(root), [])
        with tempfile.TemporaryDirectory() as tmp:
            malformed = Path(tmp)
            (malformed / "index.html").write_text('<a href="missing.html">missing</a>', encoding="utf-8")
            self.assertTrue(validate_site(malformed))

    def test_landing_mirrors_and_uses_one_internal_application_route(self) -> None:
        root = Path(__file__).resolve().parents[1]
        index = (root / "index.html").read_text(encoding="utf-8")
        self.assertEqual(index, (root / "lime-light.html").read_text(encoding="utf-8"))
        self.assertIn('data-collection-state="server-verified"', index)
        self.assertNotIn("<form", index.lower())
        self.assertNotIn("forms.fillout.com", index)
        self.assertIn("hostedPreview", index)
        self.assertIn("target.searchParams.set('preview', '1')", index)
        parsed = LandingContractParser()
        parsed.feed(index)
        self.assertGreaterEqual(len(parsed.application_hrefs), 4)
        self.assertEqual(parsed.form_count, 0)

    def test_p2_message_chain_and_factual_contract_are_present(self) -> None:
        root = Path(__file__).resolve().parents[1]
        index = (root / "index.html").read_text(encoding="utf-8")
        required = (
            "AI를 안 쓰면 뒤처질 것 같습니다.",
            "해보고 싶은 일 하나를 현실에서 직접 해봅니다.",
            "해보고 싶은데 아직 못 해 본 일이 있다",
            "AI로 더 잘해 보고 싶은 일",
            "나만의 도전",
            "여러 번의 실제 시도",
            "현실 반응",
            "동료 리뷰",
            "나에게 맞는 다음 한 걸음",
            "20살 이상 · 대학 여부 무관",
            "2주 사전과정 + 3개월 본과정",
            "최소 5명 · 최대 10명",
            "격주 90분",
            "자동 합류가 아닙니다.",
            "해보고 싶은 일을 실제로 해볼 수 있게 돕습니다.",
            "Claude Code·Codex 같은 고성능 CLI AI 작업 도구 구독료 지원",
            "Claude Code를 처음 쓰는 사람을 위한 시작 영상·실습 자료",
            "AI 작업 세션",
        )
        for phrase in required:
            self.assertIn(phrase, index)
        prohibited = (
            "8/14", "8/15", "8/17", "8/30", "8/31", "11/22",
            "전액 고연승T 연구실 지원", "구독 한 가지", "구독 1개",
            "Codex Max", "무제한", "상시 멘토링",
        )
        for phrase in prohibited:
            self.assertNotIn(phrase, index)

    def test_p2_application_completion_and_guidance_are_aligned(self) -> None:
        root = Path(__file__).resolve().parents[1]
        application = (root / "apply/index.html").read_text(encoding="utf-8")
        completion = (root / "apply/complete/index.html").read_text(encoding="utf-8")
        terms = (root / "terms.html").read_text(encoding="utf-8")
        privacy = (root / "privacy.html").read_text(encoding="utf-8")
        for field in ("challenge_self_intro", "why_now", "precourse_rhythm_plan", "available_windows"):
            self.assertIn(field, application)
        for phrase in (
            "지금 해보고 싶은 일", "첫 행동과 현실 반응", "2주 사전과정",
            "본과정 합류가 결정될 경우", "previewMode",
        ):
            self.assertIn(phrase, application)
        self.assertNotIn("도전 경험과 자기소개", application)
        self.assertNotIn("미선정자에게는 별도 연락", application)
        self.assertIn("본과정 합류를 뜻하지 않습니다.", completion)
        self.assertIn("다음 과정 안내", completion)
        self.assertIn("최소 5명·최대 10명", terms)
        self.assertIn("해보고 싶은 일을 실제로 해볼 수 있게 돕습니다.", terms)
        self.assertIn("다음 과정 안내", privacy)
        for page in (terms, privacy):
            self.assertNotIn("8월 15일", page)
            self.assertNotIn("구독 1개", page)

    def test_faq_starts_collapsed_and_has_matching_regions(self) -> None:
        root = Path(__file__).resolve().parents[1]
        parsed = LandingContractParser()
        parsed.feed((root / "index.html").read_text(encoding="utf-8"))
        self.assertEqual(len(parsed.faq_controls), 5)
        self.assertEqual(set(parsed.faq_controls), set(parsed.faq_regions))
        self.assertTrue(all(value == "true" for value in parsed.faq_regions.values()))

    def test_accent_has_light_section_contrast(self) -> None:
        root = Path(__file__).resolve().parents[1]
        source = (root / "index.html").read_text(encoding="utf-8")
        tokens = dict(re.findall(r"--([a-z-]+):\s*(#[0-9a-fA-F]{6})", source))
        self.assertEqual(tokens["gold-deep"], "#8f5f00")
        self.assertEqual(tokens["paper"], "#f7f5ef")


if __name__ == "__main__":
    unittest.main()
