import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from app.services.cookie_control import add_consent_hints, click_cookie_buttons, hide_cookie_elements

def hide_custom_selectors(page, ignore_selectors: str):
    for selector in [x.strip() for x in ignore_selectors.split(",") if x.strip()]:
        try:
            page.locator(selector).evaluate_all(
                '''
                (els)=>els.forEach(el=>{
                    el.style.setProperty('display','none','important');
                    el.style.setProperty('visibility','hidden','important');
                    el.style.setProperty('opacity','0','important');
                    el.style.setProperty('pointer-events','none','important');
                })
                '''
            )
        except Exception:
            pass

def capture_screenshot(url: str, output_path: Path, viewport_width: int, viewport_height: int, wait_seconds: int, ignore_selectors: str, cookie_mode: str = "auto") -> tuple[int, int]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": viewport_width, "height": viewport_height},
            device_scale_factor=1,
            ignore_https_errors=True,
            locale="de-DE",
            timezone_id="Europe/Berlin",
            extra_http_headers={"Accept-Language": "de-DE,de;q=0.9,en;q=0.7"},
        )
        page = context.new_page()

        if cookie_mode != "off":
            add_consent_hints(page)

        response = page.goto(url, wait_until="domcontentloaded", timeout=60000)
        http_status = response.status if response else 0

        page.wait_for_timeout(1500)

        if cookie_mode in ("auto", "click"):
            click_cookie_buttons(page)
        if cookie_mode in ("auto", "hide"):
            hide_cookie_elements(page)

        hide_custom_selectors(page, ignore_selectors)

        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass

        if wait_seconds > 0:
            time.sleep(wait_seconds)

        if cookie_mode in ("auto", "click"):
            click_cookie_buttons(page)
        if cookie_mode in ("auto", "hide"):
            hide_cookie_elements(page)

        hide_custom_selectors(page, ignore_selectors)

        page.screenshot(path=str(output_path), full_page=True)
        browser.close()

    return http_status, int((time.perf_counter() - start) * 1000)
