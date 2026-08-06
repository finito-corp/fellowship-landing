from __future__ import annotations

import functools
import http.server
import threading
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright


class LandingBrowserBehaviorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=root)
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(channel="chrome")
        cls.page = cls.browser.new_page(viewport={"width": 390, "height": 844})
        cls.page.goto(f"http://127.0.0.1:{cls.server.server_port}/index.html")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self) -> None:
        self.page.set_viewport_size({"width": 390, "height": 844})
        self.page.goto(f"http://127.0.0.1:{self.server.server_port}/index.html")

    def test_resizing_from_open_mobile_menu_releases_scroll_lock(self) -> None:
        menu_button = self.page.locator(".menu-button")
        menu_button.click()
        self.assertEqual(menu_button.get_attribute("aria-expanded"), "true")
        self.assertTrue(self.page.locator("body").evaluate("el => el.classList.contains('menu-open')"))

        self.page.set_viewport_size({"width": 900, "height": 844})
        self.page.wait_for_function("document.querySelector('.menu-button').getAttribute('aria-expanded') === 'false'")
        self.assertEqual(menu_button.get_attribute("aria-expanded"), "false")
        self.assertFalse(self.page.locator("body").evaluate("el => el.classList.contains('menu-open')"))

    def test_mobile_internal_menu_reveals_the_destination_below_the_fixed_header(self) -> None:
        self.page.locator(".menu-button").click()
        self.page.locator('.mobile-menu a[href="#history"]').click()
        self.page.wait_for_function("""() => {
            const heading = document.querySelector('#history-title').getBoundingClientRect();
            const header = document.querySelector('.site-header').getBoundingClientRect();
            return location.hash === '#history' && heading.top >= header.bottom && heading.top < innerHeight;
        }""")
        self.assertEqual(self.page.locator(".menu-button").get_attribute("aria-expanded"), "false")

    def test_faq_accordion_keeps_visual_and_accessibility_state_in_sync(self) -> None:
        questions = self.page.locator(".faq-question")
        answers = self.page.locator(".faq-answer")
        # FAQ 항목 수는 카피 변경에 따라 바뀐다. 정확한 개수는 test_static_release 가 고정하고,
        # 여기서는 "질문과 답변이 짝이 맞고 전부 접힌 채로 시작한다"만 확인한다.
        states = answers.evaluate_all("els => els.map(el => el.getAttribute('aria-hidden'))")
        self.assertEqual(len(states), questions.count())
        self.assertGreaterEqual(len(states), 2)
        self.assertEqual(states, ["true"] * len(states))

        questions.nth(0).click()
        self.assertEqual(questions.nth(0).get_attribute("aria-expanded"), "true")
        self.assertEqual(answers.nth(0).get_attribute("aria-hidden"), "false")
        questions.nth(1).click()
        self.assertEqual(questions.nth(0).get_attribute("aria-expanded"), "false")
        self.assertEqual(answers.nth(0).get_attribute("aria-hidden"), "true")
        self.assertEqual(questions.nth(1).get_attribute("aria-expanded"), "true")
        self.assertEqual(answers.nth(1).get_attribute("aria-hidden"), "false")

    def test_deadline_countdown_fills_in_and_keeps_the_written_deadline(self) -> None:
        count = self.page.locator(".deadline-count")
        self.page.set_viewport_size({"width": 1280, "height": 844})
        self.assertTrue(count.is_visible())
        self.assertIn("마감까지", count.inner_text())
        deadline = self.page.locator(".deadline-date")
        self.assertIn("8/10", deadline.inner_text())

        self.page.set_viewport_size({"width": 390, "height": 844})
        self.assertFalse(count.is_visible())
        self.assertIn("8/13 합격자 연락", deadline.inner_text())
        self.assertIn("본과정 합류 미보장", deadline.inner_text())

    def test_announcement_follows_the_same_deadline_as_the_hero(self) -> None:
        copy = self.page.locator(".announcement-copy")
        self.page.wait_for_function(
            "() => document.querySelector('.announcement-copy').textContent.includes('마감까지')"
        )
        self.assertIn("마감까지", copy.get_attribute("data-short"))
        self.assertIn("마감까지", self.page.locator(".announcement-inner").get_attribute("aria-label"))

    def test_past_cohort_numbers_settle_on_their_written_values(self) -> None:
        self.page.locator("#history").scroll_into_view_if_needed()
        self.page.wait_for_function(
            "() => [...document.querySelectorAll('[data-count-to]')]"
            ".every(el => el.textContent === el.dataset.countTo)"
        )
        self.assertIn("1기 50명, 2기 20명", self.page.locator(".stat-note").inner_text())

    def test_hero_title_splits_into_words_without_changing_its_text(self) -> None:
        title = self.page.locator("#hero-title")
        self.assertGreaterEqual(title.locator(".word").count(), 6)
        self.assertIn("계속 뭔가 하고 있는데,", title.inner_text())
        # 단어는 순차로 올라오므로 마지막 단어까지 끝난 뒤에 본다. 끝내 1이 안 되면 여기서 실패한다.
        self.page.wait_for_function(
            "() => [...document.querySelectorAll('#hero-title .word')]"
            ".every(el => getComputedStyle(el).opacity === '1')"
        )

    def test_side_guide_is_focusable_only_while_visibly_available(self) -> None:
        self.page.set_viewport_size({"width": 1280, "height": 800})
        guide = self.page.locator(".side-guide")
        self.assertEqual(guide.get_attribute("aria-hidden"), "true")
        self.assertTrue(guide.evaluate("el => el.inert"))

        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.35)")
        self.page.wait_for_function("document.querySelector('.side-guide').classList.contains('is-visible')")
        self.assertEqual(guide.get_attribute("aria-hidden"), "false")
        self.assertFalse(guide.evaluate("el => el.inert"))

        self.page.set_viewport_size({"width": 900, "height": 800})
        self.page.wait_for_function("document.querySelector('.side-guide').getAttribute('aria-hidden') === 'true'")
        self.assertEqual(guide.get_attribute("aria-hidden"), "true")
        self.assertTrue(guide.evaluate("el => el.inert"))

    def test_visible_links_and_buttons_meet_the_minimum_target_height(self) -> None:
        for width in (320, 390, 1280):
            self.page.set_viewport_size({"width": width, "height": 844})
            undersized = self.page.locator("a, button").evaluate_all("""elements => elements
                .filter(element => {
                    const style = getComputedStyle(element);
                    const rect = element.getBoundingClientRect();
                    return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0;
                })
                .filter(element => element.getBoundingClientRect().height < 44)
                .map(element => ({text: element.textContent.trim(), height: element.getBoundingClientRect().height}))""")
            self.assertEqual(undersized, [])

    def test_headings_fit_inside_narrow_viewports(self) -> None:
        for width in (320, 390):
            self.page.set_viewport_size({"width": width, "height": 844})
            clipped = self.page.locator("h1, h2").evaluate_all("""headings => headings.flatMap(heading => {
                const range = document.createRange();
                range.selectNodeContents(heading);
                return [...range.getClientRects()]
                    .filter(rect => rect.width > 0 && rect.height > 0)
                    .filter(rect => rect.left < -0.5 || rect.right > innerWidth + 0.5)
                    .map(rect => ({text: heading.textContent.trim(), left: rect.left, right: rect.right, width: innerWidth}));
            })""")
            self.assertEqual(clipped, [])
            self.assertEqual(
                self.page.evaluate("document.documentElement.scrollWidth"),
                self.page.evaluate("document.documentElement.clientWidth"),
            )

    def test_hero_type_scale_and_sentence_rhythm_are_restrained(self) -> None:
        for width, max_heading_size in ((320, 44), (390, 44), (1280, 68)):
            self.page.set_viewport_size({"width": width, "height": 844})
            heading_size = self.page.locator("#hero-title").evaluate(
                "el => parseFloat(getComputedStyle(el).fontSize)"
            )
            self.assertLessEqual(heading_size, max_heading_size)

            lines = self.page.locator(".hero-copy > span")
            self.assertEqual(lines.count(), 3)
            boxes = [lines.nth(index).bounding_box() for index in range(3)]
            self.assertTrue(all(box is not None for box in boxes))
            self.assertGreater(boxes[1]["y"], boxes[0]["y"] + boxes[0]["height"])
            self.assertGreater(boxes[2]["y"], boxes[1]["y"] + boxes[1]["height"])

    def test_application_link_stays_on_the_public_fellowship_site(self) -> None:
        self.page.locator('.hero-actions a[href="apply/"]').click()

        self.assertEqual(self.page.url, f"http://127.0.0.1:{self.server.server_port}/apply/")
        self.assertEqual(self.page.locator("h1").inner_text(), "위닝 펠로우십\n3기 지원서")
        self.assertEqual(self.page.locator("form").count(), 1)

    def test_application_link_preserves_supported_outreach_attribution(self) -> None:
        self.page.goto(
            f"http://127.0.0.1:{self.server.server_port}/index.html"
            "?utm_source=linkedin&utm_medium=organic_post&utm_campaign=wf3_202608&utm_content=main"
        )

        self.page.locator('.hero-actions a.button:not(.secondary)').click()

        self.assertIn("utm_source=linkedin", self.page.url)
        self.assertIn("utm_medium=organic_post", self.page.url)
        self.assertIn("utm_campaign=wf3_202608", self.page.url)
        self.assertIn("utm_content=main", self.page.url)

    def test_application_form_fits_supported_viewports(self) -> None:
        self.page.goto(f"http://127.0.0.1:{self.server.server_port}/apply/")
        self.assertEqual(self.page.locator('input[type="hidden"][name="contact_channel"][value="phone"]').count(), 1)
        self.assertEqual(self.page.locator('option[value="email"]').count(), 0)
        self.assertEqual(self.page.locator("fieldset").nth(1).locator("legend").inner_text(), "2. 도전 경험과 자기소개")
        self.assertIn("본과정 선발 전", self.page.locator(".lead").inner_text())
        self.assertIn("그 경험이 보여주는 나의 모습", self.page.locator("#challenge_self_intro").get_attribute("placeholder"))
        for width in (320, 390, 1280):
            self.page.set_viewport_size({"width": width, "height": 844})
            self.assertEqual(
                self.page.evaluate("document.documentElement.scrollWidth"),
                self.page.evaluate("document.documentElement.clientWidth"),
            )
            self.assertGreaterEqual(
                self.page.locator("#submit-button").evaluate(
                    "element => element.getBoundingClientRect().height"
                ),
                44,
            )

    def test_application_submission_carries_outreach_attribution(self) -> None:
        captured = {}

        def capture_submission(route) -> None:
            captured.update(route.request.post_data_json)
            route.fulfill(status=201, content_type="application/json", body='{"message":"ok"}')

        endpoint = "https://winning-fellowship-production.up.railway.app/api/fellowship/3/applications"
        self.page.route(endpoint, capture_submission)
        self.page.goto(
            f"http://127.0.0.1:{self.server.server_port}/apply/"
            "?utm_source=linkedin&utm_medium=organic_post&utm_campaign=wf3_202608&utm_content=main"
        )
        self.page.locator("#name").fill("테스트 지원자")
        self.page.locator("#age").fill("24")
        self.page.locator("#contact_value").fill("01012345678")
        self.page.locator("#eligibility_stage").select_option("대학4학년이상")
        self.page.locator("#challenge_self_intro").fill(
            "먼저 작은 프로젝트를 공개했고 반응이 예상과 달라 설명 순서와 다음 행동을 바꿨습니다."
        )
        self.page.locator("#why_now").fill(
            "미뤄 둔 포트폴리오 첫 페이지를 AI로 만들고 한 사람의 반응을 확인하겠습니다."
        )
        self.page.locator("#precourse_rhythm_plan").fill(
            "화요일과 목요일 저녁을 비우고 일정이 겹치면 토요일 오후로 옮기겠습니다."
        )
        self.page.locator('input[name="available_windows"]').nth(0).check()
        self.page.locator('input[name="available_windows"]').nth(1).check()
        self.page.locator('input[name="beta_commitment_confirmed"]').check()
        self.page.locator('input[name="core_commitment_confirmed"]').check()
        self.page.locator('input[name="contact_consent_confirmed"]').check()
        self.page.locator("#submit-button").click()
        self.page.wait_for_url("**/apply/complete/")

        self.assertEqual(captured["precourse_rhythm_plan"], "화요일과 목요일 저녁을 비우고 일정이 겹치면 토요일 오후로 옮기겠습니다.")
        self.assertEqual(captured["contact_channel"], "phone")
        self.assertEqual(captured["contact_value"], "01012345678")
        self.assertTrue(captured["core_commitment_confirmed"])
        self.assertEqual(captured["utm_source"], "linkedin")
        self.assertEqual(captured["utm_medium"], "organic_post")
        self.assertEqual(captured["utm_campaign"], "wf3_202608")
        self.assertEqual(captured["utm_content"], "main")
        self.assertNotIn("prior_ai_use_summary", captured)
        self.assertNotIn("personal_paid_ai_signal", captured)
        self.page.unroute(endpoint)

    def test_application_controls_have_accessible_focus_and_touch_targets(self) -> None:
        for path in ("apply/", "apply/complete/"):
            self.page.goto(f"http://127.0.0.1:{self.server.server_port}/{path}")
            undersized = self.page.locator("a, button").evaluate_all("""elements => elements
                .filter(element => {
                    const style = getComputedStyle(element);
                    const rect = element.getBoundingClientRect();
                    return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0;
                })
                .filter(element => element.getBoundingClientRect().height < 44)
                .map(element => ({text: element.textContent.trim(), height: element.getBoundingClientRect().height}))""")
            self.assertEqual(undersized, [])

        self.page.goto(f"http://127.0.0.1:{self.server.server_port}/apply/complete/?code=WF3-ABCDEF1234")
        self.assertEqual(self.page.locator("h1").inner_text(), "지원서 제출이 완료되었습니다.")
        self.assertEqual(self.page.get_by_text("접수 확인 코드").count(), 0)
        self.assertIn("합격자에게만", self.page.locator(".card p").inner_text())

        self.page.goto(f"http://127.0.0.1:{self.server.server_port}/apply/")
        self.page.locator("#name").focus()
        focus_style = self.page.locator("#name").evaluate("""element => {
            const style = getComputedStyle(element);
            return {color: style.outlineColor, style: style.outlineStyle, width: style.outlineWidth};
        }""")
        self.assertEqual(focus_style, {"color": "rgb(242, 189, 63)", "style": "solid", "width": "3px"})


if __name__ == "__main__":
    unittest.main()
