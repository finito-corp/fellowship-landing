from __future__ import annotations

import tempfile
import unittest
import re
from html.parser import HTMLParser
from pathlib import Path

from scripts.validate_static_release import validate_site


APPLICATION_URL = "apply/"
VERIFIED_REVIEW_EXCERPTS = (
    "체력뿐 아니라 마음까지 단단해진 시간이었습니다. 다양한 러닝 코스를 뛰어보고 마지막에는 등산까지 해내면서, 서로 의지하며 끝까지 완주했던 과정 자체가 오래 기억에 남을 것 같아요.",
    "혼자 할 때는 흥미 없고 오래 하기 힘들었던 러닝을, 펠로우들과 다 같이 뛰니 힘들어도 어떻게든 뛰게 되고 시간도 빨리 가서 매우 즐거웠습니다.",
    "혼자였다면 겨울에 산 정상까지 오르는 걸 엄두도 내지 못했을 텐데, 여럿이서 으쌰으쌰 하는 분위기 덕분에 등산을 재밌게 할 수 있었어요! 운동 생활에 새로운 패러다임을 제시해준 활동이었습니다.",
    "정말 좋은 언니, 오빠를 만났고 팀 분위기가 펠로우십에서도 정말 최상위권이라고 생각합니다. 계획을 하나하나 실현해보는 경험이 좋았고, 연락도 빨리 보고 의견 반영도 잘 되어서 수다디 최고였습니다!",
    "평소에 일본어 공부를 해야겠다고 다짐만 하던 제가 어느새 한 달 연속으로 듀오링고를 해내고 있는 모습은 정말 놀라웠습니다. 팀원들이 매주 공유를 해줬기에 그 믿음을 져버릴 수 없어서 끝까지 달릴 수 있었습니다.",
    "마케팅에 대한 막연한 꿈만 가지고 있었는데, 무에서 유(팔로워 100명)를 만들어내며 성취감과 자신감을 얻었습니다. 루멘은 정말 가족 같은 분위기였고, 서로 매일 응원하며 힘을 얻었던 유일한 크루였습니다. 어떻게 표현해야 사람들의 관심을 끌 수 있는지 고민하는 시간이 되었어요.",
    "펠로우십하길 잘했다고 생각이 들 정도로 정말 재미있게 활동했습니다. 팀원들과의 결속력이 단단했기 때문에 지금까지 달려올 수 있었다고 생각합니다. 좋은 사람들과 재미있고 다양한 콘텐츠를 만들 수 있음에 감사하고 뿌듯합니다.",
    "팀원들의 조언과 레퍼런스 공유를 통해 각자의 제작 능력을 강화하고, 함께 성장을 이루어낸 모습이 눈에 보이면서 너무나도 기특했습니다. 브랜딩이라는 낯선 주제에서 좋은 동료들과 PA로 활동한 것은 어디서도 쉽게 얻지 못할 소중한 기회였습니다.",
)
VERIFIED_REVIEW_ATTRIBUTIONS = (
    "김○○ · Flow Crew",
    "오○○ · Flow Crew",
    "강○○ · Flow Crew",
    "전○○ · 수다디",
    "최○○ · 말랑말랑",
    "최○○ · 루멘",
    "김○○ · 노이즈",
    "김○○ · 루멘",
)


def contrast_ratio(foreground: str, background: str) -> float:
    def luminance(hex_color: str) -> float:
        channels = [int(hex_color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
        linear = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4 for channel in channels]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

    lighter, darker = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


class LandingContractParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.application_hrefs: list[str] = []
        self.faq_controls: list[str] = []
        self.faq_regions: dict[str, str | None] = {}
        self.image_count = 0
        self.form_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "a" and attributes.get("href") == APPLICATION_URL:
            self.application_hrefs.append(APPLICATION_URL)
        elif tag == "img":
            self.image_count += 1
        elif tag == "form":
            self.form_count += 1

        classes = set((attributes.get("class") or "").split())
        if tag == "button" and "faq-question" in classes:
            control = attributes.get("aria-controls")
            if control:
                self.faq_controls.append(control)
        elif tag == "div" and "faq-answer" in classes:
            region_id = attributes.get("id")
            if region_id:
                self.faq_regions[region_id] = attributes.get("aria-hidden")


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
        self.assertIn('href="apply/"', index)
        self.assertNotIn('href="https://product-omrpipeline-production.up.railway.app', index)
        self.assertIn("지원서 제출 후 내부 심의를 진행하며", index)
        self.assertIn("2주 프리과정 합격자에게만 8월 13일까지 연락드립니다", index)
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
        self.assertIn("2027-02-28", privacy)
        self.assertIn("송일현", privacy)
        self.assertIn("동의하지 않으면 3기 지원서를 제출할 수 없습니다", privacy)
        self.assertIn("내부 심의 후 2주 프리과정 합격자에게만", privacy)
        self.assertIn("winningfellowship25@gmail.com", privacy)
        self.assertNotIn("현재 이 페이지에서는 지원 정보를 수집하지 않습니다", privacy)
        self.assertIn('data-collection-state="server-verified"', terms)
        self.assertIn("지원서 제출 후 내부 심의를 진행합니다", terms)
        self.assertIn("2주 프리과정 합격자에게만 8월 13일까지 개별 연락드립니다", terms)
        self.assertIn("불합격자에게는 별도 연락을 드리지 않습니다", terms)
        self.assertNotIn("조기 제출", terms)
        for text in (privacy, terms):
            self.assertNotIn("Fillout", text)
            self.assertNotIn("Career, Global, Life", text)

    def test_pull_request_validation_covers_the_live_route_contract(self) -> None:
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github/workflows/validate.yml").read_text(encoding="utf-8")
        pages_workflow = (root / ".github/workflows/pages.yml").read_text(encoding="utf-8")

        self.assertIn("python -m unittest tests.test_static_release -v", workflow)
        self.assertIn("cmp index.html lime-light.html", workflow)
        self.assertIn("cp -R main/assets _site/assets", pages_workflow)
        self.assertIn('cp -R preview/assets "${target}/assets"', pages_workflow)
        self.assertNotIn("main/invite", pages_workflow)
        self.assertNotIn("preview/invite", pages_workflow)

    def test_public_application_page_is_direct_and_keeps_backend_internal(self) -> None:
        root = Path(__file__).resolve().parents[1]
        application = (root / "apply" / "index.html").read_text(encoding="utf-8")
        completion = (root / "apply" / "complete" / "index.html").read_text(encoding="utf-8")

        self.assertIn('id="application-form"', application)
        self.assertIn('name="age"', application)
        self.assertIn('name="challenge_self_intro"', application)
        self.assertIn('name="why_now"', application)
        self.assertIn('name="precourse_rhythm_plan"', application)
        self.assertIn('name="available_windows"', application)
        self.assertIn('id="submit-button"', application)
        self.assertIn('name="eligibility_stage"', application)
        self.assertNotIn("actual_term_or_regular_rhythm_starts_on", application)
        self.assertNotIn("학기 또는 정규 일정 시작일", application)
        self.assertIn('min="20"', application)
        self.assertNotIn("만 나이) ", application)
        for stage in ("대학3학년", "대학4학년이상", "졸업생"):
            self.assertIn(f'<option value="{stage}">', application)
        for ineligible_stage in ("대학1학년", "대학2학년"):
            self.assertNotIn(f'<option value="{ineligible_stage}">', application)
        self.assertIn("대학 3학년 이상·졸업생", application)
        self.assertIn("내부 심의를 거쳐 합격자에게만 연락드립니다", application)
        self.assertIn("불합격자에게는 별도 연락을 드리지 않습니다", application)
        self.assertNotIn("대기 명단", application)
        self.assertNotIn('href="https://product-omrpipeline-production.up.railway.app', application)
        self.assertNotIn(
            "https://product-omrpipeline-production.up.railway.app/api/fellowship/3/applications",
            application,
        )
        self.assertIn(
            "https://winning-fellowship-production.up.railway.app/api/fellowship/3/applications",
            application,
        )
        self.assertNotIn("application_code", application)
        self.assertNotIn("접수 확인 코드", completion)
        self.assertNotIn("URLSearchParams", completion)
        self.assertIn("지원서 제출이 완료되었습니다", completion)
        self.assertNotIn('name="prior_ai_use_summary"', application)
        self.assertNotIn('name="personal_paid_ai_signal"', application)
        self.assertIn("2주 프리과정", application)
        self.assertIn("3개월 본과정", application)
        for attribution_field in ("utm_source", "utm_medium", "utm_campaign", "utm_content"):
            self.assertIn(attribution_field, application)

    def test_landing_uses_human_opening_copy_and_a_live_cta(self) -> None:
        root = Path(__file__).resolve().parents[1]
        primary = (root / "index.html").read_text(encoding="utf-8")
        contract = LandingContractParser()
        contract.feed(primary)

        self.assertIn("미뤄 둔 일 하나를,", primary)
        self.assertIn("2주 안에 먼저 움직여 봅니다.", primary)
        self.assertNotIn("3기를 기다립니다.", primary)
        self.assertIn("2주 프리과정", primary)
        self.assertIn("3개월 본과정", primary)
        self.assertNotIn("2주 베타", primary)
        self.assertIn("수능 다음에서 시작한 질문은,", primary)
        self.assertIn("1기 · 발견과 시작", primary)
        self.assertIn("2기 · 집중과 확장", primary)
        self.assertIn("3기 · 다음 장", primary)
        self.assertIn("지금, 이런 ", primary)
        self.assertIn("선택 앞에 있다면.", primary)
        self.assertIn("스스로 선택하고 움직여 본 몇 달은,", primary)
        self.assertNotIn("30년 뒤를 약속하지는 않습니다.", primary)
        self.assertIn("대학 3학년 이상·졸업생", primary)
        self.assertNotIn("대학 재학생·졸업생", primary)
        self.assertNotIn("대학 3학년 이후", primary)
        for retired_hedge in (
            "3기는 1·2기의 실패를 고친 상품이 아닙니다.",
            "아래 문장은 1기 홈페이지에 공개된 익명 후기 원문입니다",
            "취업을 보장하거나",
            "잘 쓴 지원서만으로 서로를 판단하지 않습니다.",
            "성공한 척하지 않습니다.",
            "바쁜 시기에는 범위를 줄이거나 잠시 멈출 수 있습니다.",
            "잠수하지 않고",
            "주식 학습",
            "지원서에 쓰면 안 되는 정보가 있나요?",
        ):
            self.assertNotIn(retired_hedge, primary)
        self.assertIn("먼저 합류한 사람들이,", primary)
        # 마감 카운트다운은 JS 가 채우고, 스크립트가 없어도 마감 시각은 글로 남아야 한다.
        self.assertIn('data-deadline="2026-08-10T23:59:59+09:00"', primary)
        self.assertIn("8/10(월) 23:59 지원 마감", primary)
        # 후기와 3기 사이의 인지 단절을 메우는 문단
        # 상단 공지도 같은 마감 시각을 따라간다. 좁은 화면 문구는 CSS 하드코딩이 아니라 속성에서 읽는다.
        self.assertIn("content: attr(data-short)", primary)
        self.assertIn('data-short="3기 모집 · 8/4–8/10"', primary)
        # 지난 두 기수 규모. 값은 마크업에 적혀 있고 JS 는 0부터 올리기만 한다.
        self.assertIn('data-count-to="70"', primary)
        self.assertIn('data-count-to="3"', primary)
        self.assertIn("1·2기를 거쳐 간 펠로우", primary)
        self.assertIn("1기 50명, 2기 20명이 함께했습니다.", primary)
        self.assertIn("이 소감들에 AI 이야기는 없습니다.", primary)
        self.assertIn("바뀌는 것은 도구지 방식이 아닙니다.", primary)
        # 제목 텍스트는 마크업에 그대로 있어야 한다. 단어 분리는 런타임에만 일어난다.
        self.assertNotIn('class="word"', primary)
        self.assertIn("교육 관련 AI를 직접 만들었습니다", primary)
        self.assertIn("온라인으로도, 직접 만나서도 진행합니다", primary)
        self.assertIn("8/31–11/22", primary)
        self.assertGreaterEqual(len(contract.application_hrefs), 4)
        self.assertEqual(contract.image_count, 0)
        self.assertEqual(contract.form_count, 0)
        self.assertNotIn("og:image", primary.lower())
        self.assertNotIn("invite/photos", primary)
        self.assertNotIn("cdn.jsdelivr.net", primary)
        self.assertIn('url("assets/PretendardVariable.woff2")', primary)
        self.assertTrue((root / "assets" / "PretendardVariable.woff2").is_file())
        self.assertTrue((root / "assets" / "Pretendard-LICENSE.txt").is_file())
        self.assertNotIn("1기 익명 후기", primary)
        self.assertEqual(primary.count("<footer>"), 2 * len(VERIFIED_REVIEW_ATTRIBUTIONS))
        for review in VERIFIED_REVIEW_EXCERPTS:
            self.assertEqual(primary.count(review), 2)
        for attribution in VERIFIED_REVIEW_ATTRIBUTIONS:
            self.assertEqual(primary.count(attribution), 2)
        self.assertIn("prefers-reduced-motion", primary)
        self.assertNotIn("8/4 OPEN 예정", primary)
        self.assertNotIn("HOW WE START", primary)
        self.assertNotIn("공개 지원폼과 운영 경로", primary)

    def test_story_order_and_intake_language_match_the_public_contract(self) -> None:
        root = Path(__file__).resolve().parents[1]
        primary = (root / "index.html").read_text(encoding="utf-8")
        hero = primary[primary.index('<section class="hero"') : primary.index('</section>', primary.index('<section class="hero"'))]

        ordered_ids = ('id="about"', 'id="history"', 'id="reviews"', 'id="fit"', 'id="beta"', 'id="core"', 'id="schedule"', 'id="faq"', 'id="apply"')
        positions = [primary.index(section_id) for section_id in ordered_ids]
        self.assertEqual(positions, sorted(positions))
        self.assertNotIn("대기 명단", primary)
        self.assertNotIn("14주", hero)
        self.assertNotIn("12주", hero)
        self.assertNotIn("약 3개월", hero)
        self.assertIn("내부 심의를 거쳐 2주 프리과정 참가자를 먼저 선발하며", primary)
        self.assertIn("2주 프리과정 종료 후 운영진이 3개월 본과정 참가자를 최종 선발합니다", primary)
        self.assertIn("const ATTRIBUTION_KEYS", primary)

    def test_small_accent_text_meets_aa_contrast_on_light_sections(self) -> None:
        root = Path(__file__).resolve().parents[1]
        primary = (root / "index.html").read_text(encoding="utf-8")
        tokens = dict(re.findall(r"--([a-z-]+):\s*(#[0-9a-fA-F]{6})", primary))

        self.assertGreaterEqual(contrast_ratio(tokens["gold-deep"], tokens["paper"]), 4.5)
        self.assertGreaterEqual(contrast_ratio(tokens["text-boundary"], tokens["ink"]), 4.5)
        self.assertGreaterEqual(contrast_ratio(tokens["gold-meta"], tokens["gold"]), 4.5)

    def test_faq_starts_collapsed_for_sighted_and_assistive_technology_users(self) -> None:
        root = Path(__file__).resolve().parents[1]
        primary = (root / "index.html").read_text(encoding="utf-8")
        contract = LandingContractParser()
        contract.feed(primary)

        self.assertEqual(len(contract.faq_controls), 5)
        self.assertEqual(set(contract.faq_controls), set(contract.faq_regions))
        self.assertTrue(all(contract.faq_regions[control] == "true" for control in contract.faq_controls))


if __name__ == "__main__":
    unittest.main()
