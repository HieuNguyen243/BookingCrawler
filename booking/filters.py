import time
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException


class BookingFiltration:
    """Applies filters (star ratings, sorting) to search results."""

    def __init__(self, driver: WebDriver):
        self.driver = driver

    def apply_star_rating(self, *star_values):
        for star in star_values:
            selector = f'[data-filters-item*="class:class={star}"] input, [data-filters-item*="class:class={star}"] label'
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    if elem.is_displayed():
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                        time.sleep(0.3)
                        elem.click()
                        time.sleep(1.0)
                        break
            except (NoSuchElementException, ElementClickInterceptedException):
                pass

    def sort_price(self):
        selectors = [
            'button[data-testid="sorters-dropdown-trigger"]',
            'li[data-id="price"] button',
            'button[data-id="price"]',
        ]
        for sel in selectors:
            try:
                elem = self.driver.find_element(By.CSS_SELECTOR, sel)
                if elem.is_displayed():
                    elem.click()
                    time.sleep(1.0)
                    return
            except NoSuchElementException:
                continue
