import time
import random
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException

from booking import constant as const
from booking.filters import BookingFiltration
from booking.report import BookingReport
from booking.pagenation import BookingPagenation


class Booking:
    """Main controller for Booking.com automation and high-speed data extraction."""

    def __init__(self, headless: bool = False, teardown: bool = True):
        self.headless = headless
        self.teardown = teardown
        self.driver = None

        self.place = ""
        self.date_checkin = ""
        self.date_checkout = ""
        self.adults = 2
        self.rooms = 1

    def __enter__(self):
        self.init_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown and self.driver:
            self.quit()

    def init_driver(self):
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument("--headless=new")

        chrome_options.page_load_strategy = "eager"
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        )
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--disable-sync")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(2)

        try:
            self.driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {
                    "source": """
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        });
                    """
                },
            )
        except Exception:
            pass

    def quit(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

    def dismiss_popups(self):
        try:
            cookie_buttons = self.driver.find_elements(By.CSS_SELECTOR, const.SELECTORS["cookie_banner_accept"])
            for btn in cookie_buttons:
                if btn.is_displayed():
                    btn.click()
                    time.sleep(0.3)
                    break
        except (NoSuchElementException, ElementClickInterceptedException):
            pass

        try:
            dismiss_buttons = self.driver.find_elements(By.CSS_SELECTOR, const.SELECTORS["sign_in_dismiss"])
            for btn in dismiss_buttons:
                if btn.is_displayed():
                    btn.click()
                    time.sleep(0.3)
                    break
        except (NoSuchElementException, ElementClickInterceptedException):
            pass

    def land_first_page(self):
        self.driver.get(const.BASE_URL)
        time.sleep(random.uniform(1.5, 2.5))
        self.dismiss_popups()

    def search_by_url(
        self,
        place: str,
        checkin: str,
        checkout: str,
        adults: int = 2,
        rooms: int = 1,
        offset: int = 0,
    ):
        self.place = place
        self.date_checkin = checkin
        self.date_checkout = checkout
        self.adults = adults
        self.rooms = rooms

        encoded_place = urllib.parse.quote_plus(place)
        url = const.SEARCH_URL_TEMPLATE.format(
            place=encoded_place,
            checkin=checkin,
            checkout=checkout,
            adults=adults,
            rooms=rooms,
            offset=offset,
        )
        self.driver.get(url)

        try:
            WebDriverWait(self.driver, 8).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, const.SELECTORS["property_card"]))
            )
            time.sleep(0.5)
        except TimeoutException:
            time.sleep(1.5)

        self.dismiss_popups()

    def navigate_to_offset(self, offset: int):
        self.search_by_url(
            place=self.place,
            checkin=self.date_checkin,
            checkout=self.date_checkout,
            adults=self.adults,
            rooms=self.rooms,
            offset=offset,
        )

    def get_total_count(self) -> int:
        pagination = BookingPagenation(next_pager=self.driver)
        return pagination.get_property_count()

    def select_place_to_go(self, place_to_go: str):
        self.place = place_to_go
        try:
            search_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, const.SELECTORS["destination_input"]))
            )
            search_field.clear()
            for char in place_to_go:
                search_field.send_keys(char)
                time.sleep(0.05)

            time.sleep(1.0)
            first_result = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, const.SELECTORS["destination_first_result"]))
            )
            first_result.click()
        except (NoSuchElementException, TimeoutException):
            pass

    def select_dates(self, checkin: str, checkout: str):
        self.date_checkin = checkin
        self.date_checkout = checkout

        try:
            date_toggle = self.driver.find_element(By.CSS_SELECTOR, const.SELECTORS["date_picker_toggle"])
            date_toggle.click()
            time.sleep(0.5)
        except Exception:
            pass

        try:
            checkin_sel = const.SELECTORS["date_cell"].format(date=checkin)
            checkin_elem = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, checkin_sel))
            )
            checkin_elem.click()
            time.sleep(0.3)

            checkout_sel = const.SELECTORS["date_cell"].format(date=checkout)
            checkout_elem = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, checkout_sel))
            )
            checkout_elem.click()
        except (NoSuchElementException, TimeoutException):
            pass

    def click_search(self):
        try:
            submit_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, const.SELECTORS["search_submit"]))
            )
            submit_btn.click()
            time.sleep(2)
            self.dismiss_popups()
        except Exception:
            pass

    def scroll_page(self, steps: int = 2, delay: float = 0.3):
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            time.sleep(delay)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(delay)
        except Exception:
            pass

    def apply_filtration(self, stars: list = None, sort_by_price: bool = False):
        filtration = BookingFiltration(driver=self.driver)
        if stars:
            filtration.apply_star_rating(*stars)
        if sort_by_price:
            filtration.sort_price()

    def report_results(self) -> list:
        self.scroll_page(steps=2, delay=0.3)
        report = BookingReport(report_driver=self.driver)
        return report.pull_deal_box_attributes(
            checkin=self.date_checkin,
            checkout=self.date_checkout,
            adult=self.adults,
            rooms=self.rooms,
            place=self.place,
        )

    def go_next_page(self) -> bool:
        pagination = BookingPagenation(next_pager=self.driver)
        success = pagination.go_next_page()
        if success:
            try:
                WebDriverWait(self.driver, 6).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, const.SELECTORS["property_card"]))
                )
                time.sleep(0.5)
            except TimeoutException:
                time.sleep(1.0)
            self.dismiss_popups()
        return success
