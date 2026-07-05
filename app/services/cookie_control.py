import re

COOKIE_BUTTONS = [
    "Alle akzeptieren", "Alles akzeptieren", "Akzeptieren", "Einverstanden",
    "Zustimmen", "Ich stimme zu", "OK", "Okay", "Accept all", "Accept",
    "Agree", "I agree", "Allow all", "Auswahl akzeptieren", "Speichern",
    "Save choices",
]

COOKIE_SELECTORS = [
    "#onetrust-banner-sdk", "#onetrust-consent-sdk", ".onetrust-pc-dark-filter",
    ".cookie-banner", ".cookie-consent", ".cookie-notice", ".cc-window",
    ".cmpbox", ".qc-cmp2-container", ".fc-consent-root", "#didomi-host",
    "[id*='cookie']", "[class*='cookie']", "[id*='consent']",
    "[class*='consent']", "[id*='cmp']", "[class*='cmp']",
]

def add_consent_hints(page):
    try:
        page.add_init_script("""
            Object.defineProperty(navigator,'doNotTrack',{get:()=> '1'});
            window.localStorage.setItem('cookieconsent_status','allow');
            window.localStorage.setItem('cookiesAccepted','true');
            window.localStorage.setItem('cookieConsent','true');
            window.localStorage.setItem('consent','true');
        """)
    except Exception:
        pass

def click_cookie_buttons(page):
    for text in COOKIE_BUTTONS:
        try:
            locator = page.get_by_role("button", name=re.compile(rf"^{re.escape(text)}$", re.I))
            if locator.count() > 0:
                locator.first.click(timeout=1500)
                page.wait_for_timeout(800)
                return
        except Exception:
            pass

    for text in COOKIE_BUTTONS:
        try:
            locator = page.get_by_text(re.compile(re.escape(text), re.I), exact=False)
            if locator.count() > 0:
                locator.first.click(timeout=1500)
                page.wait_for_timeout(800)
                return
        except Exception:
            pass

def hide_cookie_elements(page):
    for selector in COOKIE_SELECTORS:
        try:
            page.locator(selector).evaluate_all("""
                (els)=>els.forEach(el=>{
                    el.style.setProperty('display','none','important');
                    el.style.setProperty('visibility','hidden','important');
                    el.style.setProperty('opacity','0','important');
                    el.style.setProperty('pointer-events','none','important');
                })
            """)
        except Exception:
            pass
    try:
        page.evaluate("()=>{document.body.style.overflow='auto';document.documentElement.style.overflow='auto';}")
    except Exception:
        pass
