from typing import Tuple
from playwright.sync_api import PlaywrightContextManager, TimeoutError as PlaywrightTimeoutError

class Playwright():


    def __init__(self, p_ctx: PlaywrightContextManager, image_path: str):
        self.image_path = image_path
        self.browser = p_ctx.chromium.launch(headless=False)
        self.page = self.browser.new_page(color_scheme="dark")
        self.page.set_viewport_size({"width": 430, "height": 932})
        self.i = 0


    def screenshot(self, selector: str):
        self.page.locator(selector).first.screenshot(path=f"{self.image_path}/img{self.i}.png")
        self.i += 1
    

    def screenshot_between(self, selectors: Tuple[str, str], alt_selector: str = None):
        sel1, sel2 = selectors
        root_locator = self.page.locator(sel1).first
        root_locator.scroll_into_view_if_needed()
        root_bbox = root_locator.bounding_box()

        try:
            next_reply_ypos = self.page.locator(sel2).first.bounding_box()["y"]
        except PlaywrightTimeoutError as exc:
            if alt_selector:
                self.page.locator(alt_selector).first.click()
                next_reply_ypos = self.page.locator(sel2).first.bounding_box()["y"]
            raise exc

        self.page.screenshot(
            path=f"{self.image_path}/img{self.i}.png",
            clip={**root_bbox, "height": next_reply_ypos - root_bbox["y"]}
        )
        self.i += 1
    