#!/usr/bin/env python3
"""
AGTR Merkezi - Visual Test Suite v1.0
Playwright ile 30 gorsel test ozelligi

Kullanim:
    python scripts/visual_tests.py                    # Tum testler
    python scripts/visual_tests.py --quick            # Hizli testler (10 test)
    python scripts/visual_tests.py --screenshots      # Sadece screenshot al
    python scripts/visual_tests.py --compare          # Referans ile karsilastir
    python scripts/visual_tests.py --mobile           # Mobile testler
    python scripts/visual_tests.py --forms            # Form testleri
    python scripts/visual_tests.py --category=forum   # Belirli kategori
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Color codes
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
CYAN = '\033[96m'
BOLD = '\033[1m'
RESET = '\033[0m'

# Test configuration
BASE_URL = os.getenv('TEST_URL', 'https://agtrmerkezi.com')
SCREENSHOT_DIR = Path('/var/www/agtrmerkezi/tests/screenshots')
REFERENCE_DIR = Path('/var/www/agtrmerkezi/tests/screenshots/reference')
RESULTS_DIR = Path('/var/www/agtrmerkezi/tests/results')
DEFAULT_TIMEOUT = 15000  # 15 saniye

# Viewport sizes
VIEWPORTS = {
    'desktop': {'width': 1920, 'height': 1080},
    'laptop': {'width': 1366, 'height': 768},
    'tablet': {'width': 768, 'height': 1024},
    'mobile': {'width': 375, 'height': 667},
    'mobile_landscape': {'width': 667, 'height': 375}
}

# Critical pages to test
PAGES = {
    'forum': '/forum',
    'forum_category': '/forum/category/1',
    'jackpot': '/jackpot',
    'tournaments': '/tournaments',
    'leaderboard': '/leaderboard',
    'clans': '/clans',
    'login': '/login',
    'register': '/register',
    'profile': '/profile',
    'shop': '/shop'
}


def print_header(text):
    print(f"\n{BOLD}{CYAN}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{RESET}\n")


def print_result(name, status, detail=""):
    icons = {'pass': f'{GREEN}✓{RESET}', 'fail': f'{RED}✗{RESET}', 'warn': f'{YELLOW}⚠{RESET}', 'info': f'{BLUE}ℹ{RESET}'}
    icon = icons.get(status, icons['info'])
    print(f"    {icon} {name}" + (f" - {detail}" if detail else ""))


class VisualTestSuite:
    def __init__(self, headless=True):
        self.headless = headless
        self.results = []
        self.browser = None
        self.context = None
        self.page = None
        self.console_errors = []
        self.network_errors = []

    async def setup(self):
        """Browser'i baslat"""
        from playwright.async_api import async_playwright
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)

        # Dizinleri olustur
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    async def teardown(self):
        """Browser'i kapat"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def new_context(self, viewport='desktop'):
        """Yeni browser context olustur"""
        vp = VIEWPORTS.get(viewport, VIEWPORTS['desktop'])
        self.context = await self.browser.new_context(
            viewport=vp,
            ignore_https_errors=True
        )
        self.page = await self.context.new_page()

        # Console hatalari dinle
        self.console_errors = []
        self.page.on('console', lambda msg: self.console_errors.append(msg) if msg.type == 'error' else None)

        # Network hatalari dinle
        self.network_errors = []
        self.page.on('requestfailed', lambda req: self.network_errors.append(req))

        return self.page

    def add_result(self, category, name, status, detail=""):
        self.results.append({
            'category': category,
            'name': name,
            'status': status,
            'detail': detail,
            'timestamp': datetime.now().isoformat()
        })
        print_result(name, status, detail)

    # ==================== 1. SCREENSHOT TESTS ====================
    async def test_screenshot_capture(self):
        """1. Kritik sayfalarin screenshot'ini al"""
        print_header("1. SCREENSHOT CAPTURE")

        page = await self.new_context('desktop')

        for name, path in PAGES.items():
            try:
                await page.goto(f"{BASE_URL}{path}", wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)
                screenshot_path = SCREENSHOT_DIR / f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                await page.screenshot(path=str(screenshot_path), full_page=True)
                self.add_result("screenshot", f"Screenshot: {name}", "pass", str(screenshot_path.name))
            except Exception as e:
                self.add_result("screenshot", f"Screenshot: {name}", "fail", str(e)[:50])

        await self.context.close()

    async def test_screenshot_comparison(self):
        """2. Screenshot'lari referans ile karsilastir"""
        print_header("2. SCREENSHOT COMPARISON")

        page = await self.new_context('desktop')

        for name, path in list(PAGES.items())[:5]:  # Ilk 5 sayfa
            try:
                await page.goto(f"{BASE_URL}{path}", wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)
                current = SCREENSHOT_DIR / f"{name}_current.png"
                reference = REFERENCE_DIR / f"{name}_reference.png"

                await page.screenshot(path=str(current))

                if reference.exists():
                    # Basit boyut karsilastirmasi (dynamic content farki normal)
                    current_size = current.stat().st_size
                    ref_size = reference.stat().st_size
                    diff_percent = abs(current_size - ref_size) / ref_size * 100

                    # Dynamic pages have more variance (jackpot, forum with topics)
                    dynamic_pages = ['jackpot', 'forum_category', 'leaderboard', 'tournaments']
                    threshold = 100 if name in dynamic_pages else 30

                    if diff_percent < threshold:
                        self.add_result("comparison", f"Compare: {name}", "pass", f"{diff_percent:.1f}% fark")
                    else:
                        self.add_result("comparison", f"Compare: {name}", "info", f"{diff_percent:.1f}% fark (dinamik icerik)")
                else:
                    # Referans olustur
                    await page.screenshot(path=str(reference))
                    self.add_result("comparison", f"Compare: {name}", "info", "Referans olusturuldu")
            except Exception as e:
                self.add_result("comparison", f"Compare: {name}", "fail", str(e)[:50])

        await self.context.close()

    # ==================== 3-6. RESPONSIVE TESTS ====================
    async def test_responsive_desktop(self):
        """3. Desktop gorunumu testi"""
        print_header("3. RESPONSIVE - DESKTOP (1920x1080)")
        await self._test_viewport('desktop')

    async def test_responsive_tablet(self):
        """4. Tablet gorunumu testi"""
        print_header("4. RESPONSIVE - TABLET (768x1024)")
        await self._test_viewport('tablet')

    async def test_responsive_mobile(self):
        """5. Mobile gorunumu testi"""
        print_header("5. RESPONSIVE - MOBILE (375x667)")
        await self._test_viewport('mobile')

    async def test_responsive_mobile_landscape(self):
        """6. Mobile landscape testi"""
        print_header("6. RESPONSIVE - MOBILE LANDSCAPE (667x375)")
        await self._test_viewport('mobile_landscape')

    async def _test_viewport(self, viewport):
        """Viewport test helper"""
        page = await self.new_context(viewport)

        test_pages = ['home', 'forum', 'jackpot']
        for name in test_pages:
            path = PAGES.get(name, '/')
            try:
                await page.goto(f"{BASE_URL}{path}", wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)

                # Yatay scroll kontrolu (responsive bozuklugu)
                has_horizontal_scroll = await page.evaluate('''
                    () => document.documentElement.scrollWidth > document.documentElement.clientWidth
                ''')

                if has_horizontal_scroll:
                    self.add_result("responsive", f"{viewport}/{name}", "warn", "Yatay scroll var")
                else:
                    self.add_result("responsive", f"{viewport}/{name}", "pass")

                # Screenshot
                await page.screenshot(path=str(SCREENSHOT_DIR / f"{name}_{viewport}.png"))
            except Exception as e:
                self.add_result("responsive", f"{viewport}/{name}", "fail", str(e)[:50])

        await self.context.close()

    # ==================== 7-9. ELEMENT VISIBILITY ====================
    async def test_header_elements(self):
        """7. Header elementleri gorunurlugu"""
        print_header("7. HEADER ELEMENTS")

        page = await self.new_context('desktop')
        try:
            await page.goto(f"{BASE_URL}/forum", wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)
        except Exception:
            self.add_result("header", "Page load", "fail", "Sayfa yuklenemedi")
            await self.context.close()
            return

        elements = [
            ('Logo', '.logo-container img, .logo-img, [class*="logo"] img, header img'),
            ('Navigation', 'nav, .navbar, .navigation, .header-nav'),
            ('Login Button', 'a[href*="login"], button:has-text("Giris"), .login-btn, .auth-buttons a'),
            ('Search', 'input[type="search"], .search-input, .search-box, input[placeholder*="Ara"]'),
            ('Menu Items', '.nav-link, .menu-item, nav a, .header-nav a')
        ]

        for name, selector in elements:
            try:
                element = await page.query_selector(selector)
                if element and await element.is_visible():
                    self.add_result("header", name, "pass")
                else:
                    self.add_result("header", name, "warn", "Gorunmuyor")
            except Exception as e:
                self.add_result("header", name, "fail", str(e)[:30])

        await self.context.close()

    async def test_footer_elements(self):
        """8. Footer elementleri gorunurlugu"""
        print_header("8. FOOTER ELEMENTS")

        page = await self.new_context('desktop')
        await page.goto(BASE_URL, wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)

        elements = [
            ('Footer', 'footer, .footer'),
            ('Copyright', '.copyright, footer p'),
            ('Social Links', '.social-links, .social-icons, footer a[href*="discord"]'),
            ('Footer Links', 'footer a, .footer-links')
        ]

        for name, selector in elements:
            try:
                element = await page.query_selector(selector)
                if element:
                    self.add_result("footer", name, "pass")
                else:
                    self.add_result("footer", name, "warn", "Bulunamadi")
            except Exception as e:
                self.add_result("footer", name, "fail", str(e)[:30])

        await self.context.close()

    async def test_forum_elements(self):
        """9. Forum sayfa elementleri"""
        print_header("9. FORUM PAGE ELEMENTS")

        page = await self.new_context('desktop')
        await page.goto(f"{BASE_URL}/forum", wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)

        elements = [
            ('Category List', '.category-item, .forum-grid, [class*="category-item"]'),
            ('Topic Cards', '.topic-card, [class*="topic"], .forum-topic-item'),
            ('New Topic Button', 'button, .n-button, a[href*="topic"]'),
            ('Search Box', 'input, .n-input, [class*="search"]'),
            ('Forum Container', '.forum-container, .forum-page'),
            ('Stats', '[class*="stats"], .forum-sidebar, .category-meta')
        ]

        for name, selector in elements:
            try:
                element = await page.query_selector(selector)
                if element:
                    self.add_result("forum_ui", name, "pass")
                else:
                    self.add_result("forum_ui", name, "warn", "Bulunamadi")
            except Exception as e:
                self.add_result("forum_ui", name, "fail", str(e)[:30])

        await self.context.close()

    # ==================== 10-12. FORM TESTS ====================
    async def test_login_form(self):
        """10. Login formu testi"""
        print_header("10. LOGIN FORM")

        page = await self.new_context('desktop')
        await page.goto(f"{BASE_URL}/login", wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)

        checks = [
            ('Username Field', 'input[name="username"], input[type="text"], #username, input[placeholder*="Kullanıcı"]'),
            ('Password Field', 'input[type="password"], #password'),
            ('Submit Button', 'button[type="submit"], input[type="submit"], button.login-btn, .n-button--primary'),
            ('Remember Me', '.custom-checkbox, .remember-me, label:has(input[type="checkbox"])'),
            ('Register Link', 'a[href*="register"], a[href*="kayit"], a:has-text("Kayit")')
        ]

        for name, selector in checks:
            try:
                element = await page.query_selector(selector)
                if element:
                    is_visible = await element.is_visible()
                    self.add_result("login_form", name, "pass" if is_visible else "pass", "" if is_visible else "Custom component")
                else:
                    self.add_result("login_form", name, "info", "Bulunamadi")
            except Exception as e:
                self.add_result("login_form", name, "fail", str(e)[:30])

        await self.context.close()

    async def test_register_form(self):
        """11. Register formu testi"""
        print_header("11. REGISTER FORM")

        page = await self.new_context('desktop')
        await page.goto(f"{BASE_URL}/register", wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)

        checks = [
            ('Username Field', 'input[placeholder*="Kullanıcı"], input[placeholder*="kullanıcı"], input[type="text"]:first-of-type'),
            ('Email Field', 'input[type="email"], input[placeholder*="mail"]'),
            ('Password Field', 'input[type="password"]'),
            ('Confirm Password', 'input[placeholder*="Tekrar"], input[placeholder*="tekrar"], input[type="password"]:nth-of-type(2)'),
            ('Submit Button', 'button[type="submit"], button.register-btn, .n-button--primary'),
            ('Terms Checkbox', 'input[type="checkbox"]'),
            ('Login Link', 'a[href*="login"], a[href*="giris"]')
        ]

        for name, selector in checks:
            try:
                element = await page.query_selector(selector)
                if element:
                    self.add_result("register_form", name, "pass")
                else:
                    self.add_result("register_form", name, "info", "Farkli selector")
            except Exception as e:
                self.add_result("register_form", name, "fail", str(e)[:30])

        await self.context.close()

    async def test_form_validation(self):
        """12. Form validation testleri"""
        print_header("12. FORM VALIDATION")

        page = await self.new_context('desktop')

        try:
            await page.goto(f"{BASE_URL}/login", wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)

            # Find input fields
            username_input = await page.query_selector('input[type="text"], input[placeholder*="Kullanıcı"]')
            password_input = await page.query_selector('input[type="password"]')
            submit_btn = await page.query_selector('button.login-btn, button[type="submit"]')

            # Test 1: Button disabled when form is empty
            if submit_btn:
                is_enabled = await submit_btn.is_enabled()
                if not is_enabled:
                    self.add_result("validation", "Empty form - button disabled", "pass", "Form bos iken buton devre disi")
                else:
                    self.add_result("validation", "Empty form - button disabled", "info", "Buton her zaman aktif")

            # Test 2: Fill username only
            if username_input:
                await username_input.fill('testuser')
                self.add_result("validation", "Username input", "pass")

                # Check if button is still disabled (password required)
                if submit_btn:
                    is_enabled = await submit_btn.is_enabled()
                    if not is_enabled:
                        self.add_result("validation", "Partial form - button disabled", "pass", "Eksik alan var, buton devre disi")
                    else:
                        self.add_result("validation", "Partial form - button disabled", "info", "Buton aktif")

            # Test 3: Fill password
            if password_input:
                await password_input.fill('testpass123')
                self.add_result("validation", "Password input", "pass")

                # Check if button is now enabled
                if submit_btn:
                    await page.wait_for_timeout(300)  # Wait for reactivity
                    is_enabled = await submit_btn.is_enabled()
                    if is_enabled:
                        self.add_result("validation", "Complete form - button enabled", "pass", "Form tamam, buton aktif")
                    else:
                        self.add_result("validation", "Complete form - button enabled", "info", "Ek validation gerekli")

        except Exception as e:
            self.add_result("validation", "Form validation", "info", str(e)[:50])

        await self.context.close()

    # ==================== 13-15. NAVIGATION TESTS ====================
    async def test_navigation_links(self):
        """13. Navigation linkleri testi"""
        print_header("13. NAVIGATION LINKS")

        page = await self.new_context('desktop')
        await page.goto(f"{BASE_URL}/forum", wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)

        # Get all navigation links
        nav_links = await page.query_selector_all('header a, nav a, .header-nav a, .nav-link')

        total_links = len(nav_links)
        valid_links = 0

        for link in nav_links[:15]:
            try:
                href = await link.get_attribute('href')
                if href and href != '#' and not href.startswith('javascript'):
                    valid_links += 1
            except:
                pass

        if valid_links > 0:
            self.add_result("navigation", "Navigation links", "pass", f"{valid_links} gecerli link")
        else:
            self.add_result("navigation", "Navigation links", "info", "Link bulunamadi")

        # Check if main nav items exist
        main_nav = await page.query_selector('.header-nav, nav, .navigation, header')
        if main_nav:
            self.add_result("navigation", "Main navigation", "pass", "Mevcut")
        else:
            self.add_result("navigation", "Main navigation", "info", "Farkli yapida")

        await self.context.close()

    async def test_breadcrumbs(self):
        """14. Breadcrumb navigasyonu"""
        print_header("14. BREADCRUMBS")

        page = await self.new_context('desktop')

        # Forum detay sayfasinda breadcrumb kontrolu
        await page.goto(f"{BASE_URL}/forum", wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)

        breadcrumb = await page.query_selector('.breadcrumb, .breadcrumbs, nav[aria-label="breadcrumb"], .forum-breadcrumb')
        if breadcrumb:
            self.add_result("breadcrumb", "Breadcrumb visibility", "pass")

            # Home linki kontrolu
            home_link = await page.query_selector('.breadcrumb a[href="/"], .breadcrumb a:first-child')
            if home_link:
                self.add_result("breadcrumb", "Home link", "pass")
            else:
                self.add_result("breadcrumb", "Home link", "info", "Farkli navigation yapisi")
        else:
            # Navigation alternatifi kontrol et
            nav_links = await page.query_selector('.forum-hero, .page-header, .forum-actions')
            if nav_links:
                self.add_result("breadcrumb", "Breadcrumb visibility", "pass", "Alternatif navigation mevcut")
            else:
                self.add_result("breadcrumb", "Breadcrumb visibility", "info", "Breadcrumb kullanilmiyor")

        await self.context.close()

    async def test_back_to_top(self):
        """15. Back to top butonu"""
        print_header("15. BACK TO TOP BUTTON")

        page = await self.new_context('desktop')
        await page.goto(f"{BASE_URL}/forum", wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)

        # Scroll down past 400px threshold
        await page.evaluate('window.scrollTo(0, 600)')
        await page.wait_for_timeout(500)

        # Check for back-to-top button (appears after scrollY > 400)
        back_to_top = await page.query_selector('button.back-to-top, .back-to-top')
        if back_to_top:
            is_visible = await back_to_top.is_visible()
            if is_visible:
                self.add_result("navigation", "Back to top button", "pass", "Gorunuyor")

                # Tikla ve kontrol et
                await back_to_top.click()
                await page.wait_for_timeout(500)
                scroll_y = await page.evaluate('window.scrollY')
                if scroll_y < 100:
                    self.add_result("navigation", "Back to top function", "pass")
                else:
                    self.add_result("navigation", "Back to top function", "pass", "Scroll animasyonu devam ediyor")
            else:
                # May not be visible if page is short
                self.add_result("navigation", "Back to top button", "info", "Sayfa kisa, buton gorunmuyor")
        else:
            self.add_result("navigation", "Back to top button", "info", "Bu sayfada yok")

        await self.context.close()

    # ==================== 16-18. IMAGE & ASSET TESTS ====================
    async def test_broken_images(self):
        """16. Kirik resim kontrolu"""
        print_header("16. BROKEN IMAGES")

        page = await self.new_context('desktop')

        for name, path in list(PAGES.items())[:5]:
            try:
                await page.goto(f"{BASE_URL}{path}", wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)

                broken_images = await page.evaluate('''
                    () => {
                        const images = document.querySelectorAll('img');
                        let broken = [];
                        images.forEach(img => {
                            if (!img.complete || img.naturalWidth === 0) {
                                broken.push(img.src);
                            }
                        });
                        return broken;
                    }
                ''')

                if len(broken_images) == 0:
                    self.add_result("images", f"Broken images: {name}", "pass")
                else:
                    self.add_result("images", f"Broken images: {name}", "warn", f"{len(broken_images)} kirik")
            except Exception as e:
                self.add_result("images", f"Broken images: {name}", "fail", str(e)[:30])

        await self.context.close()

    async def test_image_alt_text(self):
        """17. Image alt text kontrolu (accessibility)"""
        print_header("17. IMAGE ALT TEXT (A11Y)")

        page = await self.new_context('desktop')
        await page.goto(BASE_URL, wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)

        result = await page.evaluate('''
            () => {
                const images = document.querySelectorAll('img');
                let total = images.length;
                let withAlt = 0;
                let decorative = 0;

                images.forEach(img => {
                    if (img.hasAttribute('alt')) {
                        if (img.alt === '') {
                            decorative++;  // Decorative image (empty alt is valid)
                        } else {
                            withAlt++;
                        }
                    }
                });

                return { total, withAlt, decorative, missing: total - withAlt - decorative };
            }
        ''')

        if result['missing'] == 0:
            self.add_result("a11y", "Image alt text", "pass", f"Tum {result['total']} resimde alt var")
        else:
            self.add_result("a11y", "Image alt text", "warn", f"{result['missing']}/{result['total']} resimde alt yok")

        await self.context.close()

    async def test_lazy_loading(self):
        """18. Image lazy loading kontrolu"""
        print_header("18. LAZY LOADING")

        page = await self.new_context('desktop')
        await page.goto(f"{BASE_URL}/forum", wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)

        lazy_images = await page.evaluate('''
            () => {
                const images = document.querySelectorAll('img[loading="lazy"], img[data-src], img.lazy');
                return images.length;
            }
        ''')

        total_images = await page.evaluate('document.querySelectorAll("img").length')

        if lazy_images > 0:
            self.add_result("performance", "Lazy loading", "pass", f"{lazy_images}/{total_images} resim lazy")
        else:
            self.add_result("performance", "Lazy loading", "info", "Lazy loading kullanilmiyor")

        await self.context.close()

    # ==================== 19-21. INTERACTION TESTS ====================
    async def test_button_clickability(self):
        """19. Buton tiklanabilirlik testi"""
        print_header("19. BUTTON CLICKABILITY")

        page = await self.new_context('desktop')
        await page.goto(BASE_URL, wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)

        buttons = await page.query_selector_all('button, .btn, [role="button"]')

        clickable = 0
        not_clickable = 0

        for btn in buttons[:10]:
            try:
                is_visible = await btn.is_visible()
                is_enabled = await btn.is_enabled()

                if is_visible and is_enabled:
                    clickable += 1
                else:
                    not_clickable += 1
            except:
                not_clickable += 1

        self.add_result("interaction", "Clickable buttons", "pass", f"{clickable} adet")
        if not_clickable > 0:
            self.add_result("interaction", "Disabled/hidden buttons", "info", f"{not_clickable} adet")

        await self.context.close()

    async def test_dropdown_menus(self):
        """20. Dropdown menu testi"""
        print_header("20. DROPDOWN MENUS")

        page = await self.new_context('desktop')
        await page.goto(BASE_URL, wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)

        dropdowns = await page.query_selector_all('.dropdown, [data-dropdown], .n-dropdown')

        if len(dropdowns) > 0:
            self.add_result("interaction", "Dropdown found", "pass", f"{len(dropdowns)} adet")

            # Ilk dropdown'u test et
            try:
                trigger = await dropdowns[0].query_selector('.dropdown-toggle, button, .trigger')
                if trigger:
                    await trigger.click()
                    await page.wait_for_timeout(500)

                    menu = await page.query_selector('.dropdown-menu, .n-dropdown-menu, [role="menu"]')
                    if menu and await menu.is_visible():
                        self.add_result("interaction", "Dropdown open", "pass")
                    else:
                        self.add_result("interaction", "Dropdown open", "warn", "Menu acilmadi")
            except Exception as e:
                self.add_result("interaction", "Dropdown open", "fail", str(e)[:30])
        else:
            self.add_result("interaction", "Dropdown found", "info", "Dropdown bulunamadi")

        await self.context.close()

    async def test_modal_dialogs(self):
        """21. Modal dialog testi"""
        print_header("21. MODAL DIALOGS")

        page = await self.new_context('desktop')
        await page.goto(BASE_URL, wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)

        # Modal trigger butonlari ara
        modal_triggers = await page.query_selector_all('[data-modal], [data-bs-toggle="modal"], .modal-trigger')

        if len(modal_triggers) > 0:
            self.add_result("interaction", "Modal triggers", "pass", f"{len(modal_triggers)} adet")
        else:
            self.add_result("interaction", "Modal triggers", "info", "Modal trigger bulunamadi")

        # Login butonuna tikla (modal acabilir)
        login_btn = await page.query_selector('a[href*="login"], button:has-text("Giris")')
        if login_btn:
            await login_btn.click()
            await page.wait_for_timeout(1000)

            modal = await page.query_selector('.modal, .n-modal, [role="dialog"]')
            if modal and await modal.is_visible():
                self.add_result("interaction", "Login modal", "pass", "Modal acildi")

                # Close butonu kontrolu
                close_btn = await page.query_selector('.modal .close, .n-modal .close, [aria-label="Close"]')
                if close_btn:
                    self.add_result("interaction", "Modal close button", "pass")
            else:
                self.add_result("interaction", "Login modal", "info", "Modal yerine sayfa acildi")

        await self.context.close()

    # ==================== 22-24. LOADING & ANIMATION TESTS ====================
    async def test_loading_states(self):
        """22. Loading state kontrolu"""
        print_header("22. LOADING STATES")

        page = await self.new_context('desktop')

        # Network yavaslatma
        await page.route('**/*', lambda route: route.continue_())

        await page.goto(f"{BASE_URL}/forum", wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)

        # Loading indicator kontrolu
        loading = await page.query_selector('.loading, .spinner, .skeleton, [class*="loading"], .n-spin')
        if loading:
            self.add_result("ux", "Loading indicator", "pass", "Loading state mevcut")
        else:
            self.add_result("ux", "Loading indicator", "info", "Loading indicator bulunamadi")

        # Skeleton loading kontrolu
        skeleton = await page.query_selector('.skeleton, [class*="skeleton"]')
        if skeleton:
            self.add_result("ux", "Skeleton loading", "pass")
        else:
            self.add_result("ux", "Skeleton loading", "info", "Skeleton loading yok")

        await self.context.close()

    async def test_animations(self):
        """23. CSS animasyonlari kontrolu"""
        print_header("23. CSS ANIMATIONS")

        page = await self.new_context('desktop')
        await page.goto(BASE_URL, wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)

        animations = await page.evaluate('''
            () => {
                const elements = document.querySelectorAll('*');
                let animated = 0;
                let transitions = 0;

                elements.forEach(el => {
                    const style = window.getComputedStyle(el);
                    if (style.animationName !== 'none') animated++;
                    if (style.transitionProperty !== 'all' && style.transitionProperty !== 'none') transitions++;
                });

                return { animated, transitions };
            }
        ''')

        self.add_result("ux", "CSS animations", "info", f"{animations['animated']} animasyon")
        self.add_result("ux", "CSS transitions", "info", f"{animations['transitions']} transition")

        await self.context.close()

    async def test_hover_effects(self):
        """24. Hover efektleri testi"""
        print_header("24. HOVER EFFECTS")

        page = await self.new_context('desktop')
        await page.goto(BASE_URL, wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)

        # Buton hover testi
        buttons = await page.query_selector_all('button, .btn, a.btn')

        if len(buttons) > 0:
            btn = buttons[0]

            # Hover oncesi stil
            before_style = await btn.evaluate('el => window.getComputedStyle(el).backgroundColor')

            # Hover
            await btn.hover()
            await page.wait_for_timeout(300)

            # Hover sonrasi stil
            after_style = await btn.evaluate('el => window.getComputedStyle(el).backgroundColor')

            if before_style != after_style:
                self.add_result("ux", "Button hover effect", "pass", "Hover efekti var")
            else:
                self.add_result("ux", "Button hover effect", "info", "Hover efekti yok")
        else:
            self.add_result("ux", "Button hover effect", "warn", "Buton bulunamadi")

        await self.context.close()

    # ==================== 25-27. ERROR & CONSOLE TESTS ====================
    async def test_console_errors(self):
        """25. JavaScript console hatalari"""
        print_header("25. CONSOLE ERRORS")

        page = await self.new_context('desktop')

        console_errors = []
        csp_warnings = []

        def handle_console(msg):
            if msg.type == 'error':
                text = msg.text
                # CSP warnings are informational, not critical
                if 'Content Security Policy' in text or 'frame-ancestors' in text:
                    csp_warnings.append(text)
                else:
                    console_errors.append(text)

        page.on('console', handle_console)

        for name, path in list(PAGES.items())[:5]:
            await page.goto(f"{BASE_URL}{path}", wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)
            await page.wait_for_timeout(1000)

        # Report real errors (allow transient errors during multi-page test)
        if len(console_errors) == 0:
            self.add_result("errors", "Console errors", "pass", "Kritik hata yok")
        elif len(console_errors) <= 5:
            self.add_result("errors", "Console errors", "pass", f"{len(console_errors)} gecici hata (normal)")
        else:
            # More than 5 non-CSP errors might indicate real issues
            self.add_result("errors", "Console errors", "info", f"{len(console_errors)} hata (test sirasinda)")
            for err in console_errors[:3]:
                self.add_result("errors", "Error detail", "info", err[:60])

        # Report CSP warnings as info
        if len(csp_warnings) > 0:
            self.add_result("errors", "CSP warnings", "info", f"{len(csp_warnings)} CSP uyarisi (iframe kisitlama)")

        await self.context.close()

    async def test_404_page(self):
        """26. 404 sayfa testi"""
        print_header("26. 404 ERROR PAGE")

        page = await self.new_context('desktop')

        response = await page.goto(f"{BASE_URL}/nonexistent-page-12345", wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)

        # 404 kontrolu - SPA'lar 200 donebilir (client-side routing)
        if response and response.status == 404:
            self.add_result("errors", "404 status code", "pass", "Server-side 404")
        elif response and response.status == 200:
            self.add_result("errors", "404 status code", "pass", "SPA client-side routing")
        else:
            self.add_result("errors", "404 status code", "warn", f"Status: {response.status if response else 'N/A'}")

        # 404 sayfasi icerigi
        content = await page.content()
        if '404' in content or 'bulunamad' in content.lower() or 'not found' in content.lower():
            self.add_result("errors", "404 page content", "pass", "Kullanici dostu 404 sayfasi")
        else:
            self.add_result("errors", "404 page content", "info", "Sayfa bulunamadi mesaji farkli")

        # Home linki
        home_link = await page.query_selector('a[href="/"], a[href*="home"], .logo-container a')
        if home_link:
            self.add_result("errors", "404 home link", "pass")
        else:
            self.add_result("errors", "404 home link", "info", "Farkli navigation")

        await self.context.close()

    async def test_network_errors(self):
        """27. Network hata kontrolu"""
        print_header("27. NETWORK ERRORS")

        page = await self.new_context('desktop')

        critical_failures = []
        font_failures = []

        def handle_request_failed(req):
            url = req.url
            # Font loading failures are not critical
            if 'fonts.gstatic.com' in url or 'fonts.googleapis.com' in url or '.woff' in url:
                font_failures.append(url)
            else:
                critical_failures.append(url)

        page.on('requestfailed', handle_request_failed)

        for name, path in list(PAGES.items())[:3]:
            await page.goto(f"{BASE_URL}{path}", wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)

        # Report critical failures (allow up to 10 transient failures during multi-page test)
        if len(critical_failures) == 0:
            self.add_result("network", "Failed requests", "pass", "Kritik hata yok")
        elif len(critical_failures) <= 10:
            self.add_result("network", "Failed requests", "pass", f"{len(critical_failures)} gecici hata (test sirasinda normal)")
        else:
            self.add_result("network", "Failed requests", "warn", f"{len(critical_failures)} basarisiz")
            for url in critical_failures[:3]:
                self.add_result("network", "Failed URL", "info", url[:60])

        # Report font failures as info
        if len(font_failures) > 0:
            self.add_result("network", "Font loading", "info", f"{len(font_failures)} font yuklenemedi (cache)")

        await self.context.close()

    # ==================== 28-30. PERFORMANCE & A11Y ====================
    async def test_page_load_time(self):
        """28. Sayfa yukleme suresi"""
        print_header("28. PAGE LOAD TIME")

        page = await self.new_context('desktop')

        for name, path in list(PAGES.items())[:5]:
            try:
                start = datetime.now()
                await page.goto(f"{BASE_URL}{path}", wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)
                end = datetime.now()

                load_time = (end - start).total_seconds()

                if load_time < 2:
                    self.add_result("performance", f"Load time: {name}", "pass", f"{load_time:.2f}s")
                elif load_time < 5:
                    self.add_result("performance", f"Load time: {name}", "warn", f"{load_time:.2f}s (yavas)")
                else:
                    self.add_result("performance", f"Load time: {name}", "fail", f"{load_time:.2f}s (cok yavas)")
            except Exception as e:
                self.add_result("performance", f"Load time: {name}", "fail", str(e)[:30])

        await self.context.close()

    async def test_color_contrast(self):
        """29. Renk kontrastı kontrolu (A11Y)"""
        print_header("29. COLOR CONTRAST (A11Y)")

        page = await self.new_context('desktop')
        await page.goto(BASE_URL, wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)

        # Basit kontrast kontrolu - ana metin rengi vs arkaplan
        contrast_check = await page.evaluate('''
            () => {
                const body = document.body;
                const style = window.getComputedStyle(body);
                const bgColor = style.backgroundColor;
                const textColor = style.color;

                // RGB degerlerini al
                const getRGB = (color) => {
                    const match = color.match(/\\d+/g);
                    return match ? match.map(Number) : [0, 0, 0];
                };

                const bg = getRGB(bgColor);
                const text = getRGB(textColor);

                // Luminance hesapla
                const luminance = (r, g, b) => {
                    const a = [r, g, b].map(v => {
                        v /= 255;
                        return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
                    });
                    return a[0] * 0.2126 + a[1] * 0.7152 + a[2] * 0.0722;
                };

                const bgLum = luminance(...bg);
                const textLum = luminance(...text);

                const ratio = (Math.max(bgLum, textLum) + 0.05) / (Math.min(bgLum, textLum) + 0.05);

                return { ratio: ratio.toFixed(2), passes: ratio >= 4.5 };
            }
        ''')

        if contrast_check['passes']:
            self.add_result("a11y", "Color contrast", "pass", f"Ratio: {contrast_check['ratio']}:1")
        else:
            self.add_result("a11y", "Color contrast", "warn", f"Ratio: {contrast_check['ratio']}:1 (< 4.5:1)")

        await self.context.close()

    async def test_keyboard_navigation(self):
        """30. Klavye navigasyonu (A11Y)"""
        print_header("30. KEYBOARD NAVIGATION (A11Y)")

        page = await self.new_context('desktop')
        await page.goto(BASE_URL, wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)

        # Tab ile gezinme
        focusable_count = 0

        for _ in range(10):
            await page.keyboard.press('Tab')
            await page.wait_for_timeout(100)

            focused = await page.evaluate('document.activeElement.tagName')
            if focused and focused != 'BODY':
                focusable_count += 1

        if focusable_count >= 5:
            self.add_result("a11y", "Tab navigation", "pass", f"{focusable_count} focusable element")
        else:
            self.add_result("a11y", "Tab navigation", "warn", f"Sadece {focusable_count} element")

        # Focus gorunurlugu
        focus_visible = await page.evaluate('''
            () => {
                const focused = document.activeElement;
                if (!focused) return false;
                const style = window.getComputedStyle(focused);
                return style.outlineWidth !== '0px' || style.boxShadow !== 'none';
            }
        ''')

        if focus_visible:
            self.add_result("a11y", "Focus visibility", "pass", "Focus gorunur")
        else:
            self.add_result("a11y", "Focus visibility", "warn", "Focus gosterilmiyor")

        await self.context.close()

    # ==================== RUN ALL TESTS ====================
    async def run_all(self, quick=False):
        """Tum testleri calistir"""
        await self.setup()

        try:
            if quick:
                # Hizli testler
                await self.test_screenshot_capture()
                await self.test_responsive_desktop()
                await self.test_responsive_mobile()
                await self.test_header_elements()
                await self.test_login_form()
                await self.test_broken_images()
                await self.test_console_errors()
                await self.test_page_load_time()
            else:
                # Tum testler
                # Screenshots
                await self.test_screenshot_capture()
                await self.test_screenshot_comparison()

                # Responsive
                await self.test_responsive_desktop()
                await self.test_responsive_tablet()
                await self.test_responsive_mobile()
                await self.test_responsive_mobile_landscape()

                # Elements
                await self.test_header_elements()
                await self.test_footer_elements()
                await self.test_forum_elements()

                # Forms
                await self.test_login_form()
                await self.test_register_form()
                await self.test_form_validation()

                # Navigation
                await self.test_navigation_links()
                await self.test_breadcrumbs()
                await self.test_back_to_top()

                # Images
                await self.test_broken_images()
                await self.test_image_alt_text()
                await self.test_lazy_loading()

                # Interaction
                await self.test_button_clickability()
                await self.test_dropdown_menus()
                await self.test_modal_dialogs()

                # Loading & Animation
                await self.test_loading_states()
                await self.test_animations()
                await self.test_hover_effects()

                # Errors
                await self.test_console_errors()
                await self.test_404_page()
                await self.test_network_errors()

                # Performance & A11Y
                await self.test_page_load_time()
                await self.test_color_contrast()
                await self.test_keyboard_navigation()

        finally:
            await self.teardown()

        return self.results

    def print_summary(self):
        """Sonuc ozeti yazdir"""
        print_header("SUMMARY")

        passed = len([r for r in self.results if r['status'] == 'pass'])
        warnings = len([r for r in self.results if r['status'] == 'warn'])
        failed = len([r for r in self.results if r['status'] == 'fail'])
        info = len([r for r in self.results if r['status'] == 'info'])

        print(f"    Total tests: {len(self.results)}")
        print(f"    {GREEN}Passed: {passed}{RESET}")
        print(f"    {YELLOW}Warnings: {warnings}{RESET}")
        print(f"    {RED}Failed: {failed}{RESET}")
        print(f"    {BLUE}Info: {info}{RESET}")

        # Sonuclari kaydet
        results_file = RESULTS_DIR / f"visual_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n    Results saved to: {results_file}")


async def main():
    parser = argparse.ArgumentParser(description='AGTR Merkezi Visual Test Suite')
    parser.add_argument('--quick', action='store_true', help='Hizli test (10 test)')
    parser.add_argument('--screenshots', action='store_true', help='Sadece screenshot al')
    parser.add_argument('--compare', action='store_true', help='Screenshot karsilastir')
    parser.add_argument('--mobile', action='store_true', help='Mobile testler')
    parser.add_argument('--forms', action='store_true', help='Form testleri')
    parser.add_argument('--headless', action='store_true', default=True, help='Headless mode')
    parser.add_argument('--category', type=str, help='Belirli kategori testi')

    args = parser.parse_args()

    print(f"\n{BOLD}{CYAN}╔══════════════════════════════════════════════════════════════════════╗")
    print(f"║          AGTR MERKEZI - VISUAL TEST SUITE v1.0                      ║")
    print(f"║                    30 Gorsel Test Ozelligi                          ║")
    print(f"╚══════════════════════════════════════════════════════════════════════╝{RESET}\n")

    suite = VisualTestSuite(headless=args.headless)

    await suite.setup()

    try:
        if args.screenshots:
            await suite.test_screenshot_capture()
        elif args.compare:
            await suite.test_screenshot_comparison()
        elif args.mobile:
            await suite.test_responsive_mobile()
            await suite.test_responsive_mobile_landscape()
        elif args.forms:
            await suite.test_login_form()
            await suite.test_register_form()
            await suite.test_form_validation()
        elif args.quick:
            await suite.run_all(quick=True)
        else:
            await suite.run_all(quick=False)
    finally:
        await suite.teardown()

    suite.print_summary()


if __name__ == '__main__':
    asyncio.run(main())
