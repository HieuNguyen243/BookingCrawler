import re
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException


class BookingPagenation:
    """Handles pagination navigation on Booking.com search results."""

    def __init__(self, next_pager: WebDriver):
        self.driver = next_pager

    def get_property_count(self) -> int:
        """Reads total number of properties found for the search."""
        try:
            heading_elem = self.driver.find_element(
                By.CSS_SELECTOR, 'h1[aria-live="assertive"], [data-testid="results-list-subheading"], h1'
            )
            match = re.search(r"(\d[\d\s.,]*)\s*(?:chỗ nghỉ|properties|found|tìm thấy)", heading_elem.text, re.IGNORECASE)
            if match:
                raw_num = match.group(1).replace(",", "").replace(".", "").replace(" ", "")
                return int(raw_num)
        except Exception:
            pass
        return 25

    def go_next_page(self) -> bool:
        """Clicks the Next page button using CSS Selectors."""
        selectors = [
            'button[aria-label*="Next"]',
            'button[aria-label*="Trang sau"]',
            '[data-testid="pagination"] button:last-child',
            'nav[aria-label*="pagination"] button:last-child',
        ]

        for sel in selectors:
            try:
                buttons = self.driver.find_elements(By.CSS_SELECTOR, sel)
                for btn in buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                        time.sleep(0.3)
                        btn.click()
                        time.sleep(0.5)
                        return True
            except (NoSuchElementException, ElementClickInterceptedException):
                continue
            except Exception:
                continue

        return False
