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
        cls.browser = cls.playwright.chromium.launch()
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

    def test_announcement_and_hero_do_not_invent_an_unconfirmed_deadline(self) -> None:
        announcement = self.page.locator(".announcement-inner")
        deadline = self.page.locator(".deadline-date")
        self.assertIn("3기 · 지원 안내", announcement.get_attribute("aria-label"))
        self.assertIn("2주 사전과정 후 본과정 합류 결정", deadline.inner_text())
        self.assertIn("확정 안내", deadline.inner_text())
        self.assertNotIn("8/14", self.page.content())
        self.assertNotIn("8/15", self.page.content())
        self.assertEqual(self.page.locator(".deadline-count").count(), 0)

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

    def test_side_guide_uses_folio_anchors_and_tracks_subchapters(self) -> None:
        self.page.set_viewport_size({"width": 1280, "height": 800})
        guide = self.page.locator("nav.side-guide")
        links = guide.locator(".side-link")
        self.assertEqual(guide.get_attribute("aria-label"), "페이지 섹션")
        self.assertEqual(links.count(), 8)
        self.assertEqual(
            links.evaluate_all("els => els.map(el => el.getAttribute('href'))"),
            ["#about", "#fit", "#core", "#beta", "#schedule", "#history", "#faq", "#apply"],
        )

        self.page.evaluate("document.getElementById('origin').scrollIntoView()")
        self.page.wait_for_function("document.querySelector('.side-link[aria-current=\"location\"]')?.hash === '#schedule'")
        self.assertEqual(guide.get_attribute("data-tone"), "light")

        self.page.evaluate("document.getElementById('reviews').scrollIntoView()")
        self.page.wait_for_function("document.querySelector('.side-link[aria-current=\"location\"]')?.hash === '#history'")
        self.assertEqual(guide.get_attribute("data-tone"), "dark")

        self.page.evaluate("document.getElementById('apply').scrollIntoView()")
        self.page.wait_for_function("document.querySelector('.side-link[aria-current=\"location\"]')?.hash === '#apply'")
        self.assertEqual(guide.get_attribute("data-tone"), "gold")
        self.assertEqual(guide.locator('.side-link[aria-current="location"]').count(), 1)
        self.assertEqual(guide.evaluate("el => el.style.getPropertyValue('--side-progress')"), "1")

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

            # P2 Hero는 압박→망설임→질문→전환의 4단계다.
            lines = self.page.locator(".hero-copy > span")
            self.assertEqual(lines.count(), 4)
            boxes = [lines.nth(index).bounding_box() for index in range(4)]
            self.assertTrue(all(box is not None for box in boxes))
            for previous, following in zip(boxes, boxes[1:]):
                self.assertGreater(following["y"], previous["y"] + previous["height"])

    def test_primary_hero_cta_is_fully_visible_on_a_short_desktop_viewport(self) -> None:
        self.page.set_viewport_size({"width": 1280, "height": 577})
        button = self.page.locator('.hero-actions a.button:not(.secondary)').first
        box = button.bounding_box()
        self.assertIsNotNone(box)
        self.assertGreaterEqual(box["y"], 0)
        self.assertLessEqual(box["y"] + box["height"], 577)

if __name__ == "__main__":
    unittest.main()
