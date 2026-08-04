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
        self.assertEqual(answers.evaluate_all("els => els.map(el => el.getAttribute('aria-hidden'))"), ["true"] * 6)

        questions.nth(0).click()
        self.assertEqual(questions.nth(0).get_attribute("aria-expanded"), "true")
        self.assertEqual(answers.nth(0).get_attribute("aria-hidden"), "false")
        questions.nth(1).click()
        self.assertEqual(questions.nth(0).get_attribute("aria-expanded"), "false")
        self.assertEqual(answers.nth(0).get_attribute("aria-hidden"), "true")
        self.assertEqual(questions.nth(1).get_attribute("aria-expanded"), "true")
        self.assertEqual(answers.nth(1).get_attribute("aria-hidden"), "false")

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
            self.assertEqual(lines.count(), 2)
            first = lines.nth(0).bounding_box()
            second = lines.nth(1).bounding_box()
            self.assertIsNotNone(first)
            self.assertIsNotNone(second)
            self.assertGreater(second["y"], first["y"] + first["height"])

    def test_application_link_stays_on_the_public_fellowship_site(self) -> None:
        self.page.locator('.hero-actions a[href="apply/"]').click()

        self.assertEqual(self.page.url, f"http://127.0.0.1:{self.server.server_port}/apply/")
        self.assertEqual(self.page.locator("h1").inner_text(), "위닝 펠로우십\n3기 지원서")
        self.assertEqual(self.page.locator("form").count(), 1)

    def test_application_form_fits_supported_viewports(self) -> None:
        self.page.goto(f"http://127.0.0.1:{self.server.server_port}/apply/")
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

        self.page.goto(f"http://127.0.0.1:{self.server.server_port}/apply/")
        self.page.locator("#name").focus()
        focus_style = self.page.locator("#name").evaluate("""element => {
            const style = getComputedStyle(element);
            return {color: style.outlineColor, style: style.outlineStyle, width: style.outlineWidth};
        }""")
        self.assertEqual(focus_style, {"color": "rgb(242, 189, 63)", "style": "solid", "width": "3px"})


if __name__ == "__main__":
    unittest.main()
