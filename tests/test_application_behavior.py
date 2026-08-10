from __future__ import annotations

import functools
import http.server
import threading
import unittest
from pathlib import Path

from playwright.sync_api import Route, sync_playwright


class ApplicationBehaviorTests(unittest.TestCase):
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

    @classmethod
    def tearDownClass(cls) -> None:
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self) -> None:
        self.page.goto(f"http://127.0.0.1:{self.server.server_port}/apply/")

    def _fill_valid_application(self) -> None:
        self.page.locator("#name").fill("테스트 지원자")
        self.page.locator("#age").fill("24")
        self.page.locator("#contact_value").fill("01012345678")
        self.page.locator("#eligibility_stage").select_option("기타")
        self.page.locator("#challenge_self_intro").fill(
            "작은 프로젝트를 공개했고 반응이 예상과 달라 설명 순서와 다음 행동을 바꿨습니다."
        )
        self.page.locator("#why_now").fill(
            "포트폴리오 첫 페이지를 AI로 만들고 한 사람의 반응을 확인한 뒤 방향을 수정하겠습니다."
        )
        self.page.locator("#precourse_rhythm_plan").fill(
            "화요일과 목요일 저녁을 비우고 일정이 겹치면 토요일 오후로 옮기겠습니다."
        )
        self.page.locator('input[name="available_windows"]').nth(0).check()
        self.page.locator('input[name="available_windows"]').nth(1).check()
        self.page.locator('input[name="beta_commitment_confirmed"]').check()
        self.page.locator('input[name="core_commitment_confirmed"]').check()
        self.page.locator('input[name="contact_consent_confirmed"]').check()

    def test_invalid_submission_focuses_summary_and_preserves_valid_values(self) -> None:
        self.page.locator("#name").fill("테스트 지원자")

        self.page.locator("#submit-button").click()

        self.assertTrue(self.page.locator("#error-summary").is_visible())
        self.assertEqual(self.page.evaluate("document.activeElement.id"), "error-summary")
        self.assertEqual(self.page.locator("#name").input_value(), "테스트 지원자")
        self.assertEqual(self.page.locator("#age").get_attribute("aria-invalid"), "true")
        self.assertEqual(self.page.locator("#available-windows").get_attribute("aria-invalid"), "true")
        self.assertTrue(self.page.locator("#available-windows-error").is_visible())

    def test_landing_application_link_preserves_supported_attribution(self) -> None:
        self.page.goto(
            f"http://127.0.0.1:{self.server.server_port}/index.html"
            "?utm_source=linkedin&utm_medium=organic_post&utm_campaign=wf3_202608&utm_content=main"
        )

        self.page.locator(".hero-actions a.button:not(.secondary)").first.click()

        self.assertEqual(self.page.locator("h1").inner_text(), "위닝 펠로우십\n3기 지원서")
        self.assertIn("utm_source=linkedin", self.page.url)
        self.assertIn("utm_medium=organic_post", self.page.url)
        self.assertIn("utm_campaign=wf3_202608", self.page.url)
        self.assertIn("utm_content=main", self.page.url)

    def test_review_allows_editing_and_defers_the_network_request(self) -> None:
        submissions: list[dict[str, str | int | bool | list[str] | None]] = []

        def capture_submission(route: Route) -> None:
            submissions.append(route.request.post_data_json)
            route.fulfill(status=201, content_type="application/json", body='{"message":"ok"}')

        endpoint = "https://winning-fellowship-production.up.railway.app/api/fellowship/3/applications"
        self.page.route(endpoint, capture_submission)
        self.page.goto(
            f"http://127.0.0.1:{self.server.server_port}/apply/"
            "?utm_source=linkedin&utm_medium=organic_post&utm_campaign=wf3_202608&utm_content=main"
        )
        self._fill_valid_application()

        self.page.locator("#submit-button").click()

        self.assertEqual(submissions, [])
        self.assertTrue(self.page.locator("#review-panel").is_visible())
        self.assertFalse(self.page.locator("#form-fields").is_visible())
        self.assertEqual(self.page.evaluate("document.activeElement.id"), "review-title")
        self.assertEqual(self.page.locator("#review-name").inner_text(), "테스트 지원자")

        self.page.locator("#review-edit-button").click()

        self.assertTrue(self.page.locator("#form-fields").is_visible())
        self.assertEqual(self.page.locator("#name").input_value(), "테스트 지원자")

        self.page.locator("#submit-button").click()
        self.page.locator("#final-submit-button").click()
        self.page.wait_for_url("**/apply/complete/")

        self.assertEqual(len(submissions), 1)
        self.assertEqual(submissions[0]["contact_channel"], "phone")
        self.assertEqual(submissions[0]["contact_value"], "01012345678")
        self.assertEqual(submissions[0]["eligibility_stage"], "기타")
        self.assertEqual(submissions[0]["utm_source"], "linkedin")
        self.assertEqual(submissions[0]["utm_medium"], "organic_post")
        self.assertEqual(submissions[0]["utm_campaign"], "wf3_202608")
        self.assertEqual(submissions[0]["utm_content"], "main")
        self.assertNotIn("prior_ai_use_summary", submissions[0])
        self.assertNotIn("personal_paid_ai_signal", submissions[0])
        self.page.unroute(endpoint)

    def test_application_and_completion_fit_supported_viewports(self) -> None:
        for width in (320, 390, 1280):
            self.page.set_viewport_size({"width": width, "height": 844})
            self.assertEqual(
                self.page.evaluate("document.documentElement.scrollWidth"),
                self.page.evaluate("document.documentElement.clientWidth"),
            )
            self.assertGreaterEqual(
                self.page.locator("#submit-button").evaluate("element => element.getBoundingClientRect().height"),
                44,
            )

        self.page.locator("#name").focus()
        focus_style = self.page.locator("#name").evaluate("""element => {
            const style = getComputedStyle(element);
            return {color: style.outlineColor, style: style.outlineStyle, width: style.outlineWidth};
        }""")
        self.assertEqual(focus_style, {"color": "rgb(242, 189, 63)", "style": "solid", "width": "3px"})

        self.page.goto(f"http://127.0.0.1:{self.server.server_port}/apply/complete/?code=WF3-ABCDEF1234")
        self.assertEqual(self.page.get_by_text("접수 확인 코드").count(), 0)
        self.assertEqual(self.page.locator('a[href="mailto:winningfellowship25@gmail.com"]').count(), 1)


if __name__ == "__main__":
    unittest.main()
