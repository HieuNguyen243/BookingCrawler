import re
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from booking import constant as const


def _find_first(elem, css_selector: str):
    """Safely finds the first matching child element."""
    try:
        matches = elem.find_elements(By.CSS_SELECTOR, css_selector)
        return matches[0] if matches else None
    except Exception:
        return None


class BookingReport:
    """Parses hotel properties from search result cards."""

    def __init__(self, report_driver: WebDriver):
        self.driver = report_driver

    def pull_deal_boxes(self) -> list:
        try:
            return self.driver.find_elements(By.CSS_SELECTOR, const.SELECTORS["property_card"])
        except Exception:
            return []

    def parse_deal_box(self, deal_box, place: str, checkin: str, checkout: str, adult: int, rooms: int) -> dict:
        try:
            title_elem = _find_first(deal_box, const.SELECTORS["property_title"])
            property_name = title_elem.text.strip() if title_elem else "N/A"

            link_elem = _find_first(deal_box, const.SELECTORS["property_link"])
            property_url = link_elem.get_attribute("href") if link_elem else ""

            img_elem = _find_first(deal_box, const.SELECTORS["property_image"])
            property_image = img_elem.get_attribute("src") if img_elem else ""

            loc_elem = _find_first(deal_box, const.SELECTORS["property_address"])
            location = loc_elem.text.strip() if loc_elem else place

            dist_elem = _find_first(deal_box, const.SELECTORS["property_distance"])
            distance = dist_elem.text.strip() if dist_elem else ""

            price_elem = _find_first(deal_box, const.SELECTORS["property_price"])
            property_price = price_elem.text.strip() if price_elem else "N/A"

            property_score = "N/A"
            review_count = "N/A"
            score_container = _find_first(deal_box, '[data-testid="review-score"]')
            if score_container:
                score_text = score_container.text.strip()
                score_match = re.search(r"(\d+[.,]\d+|\d+)", score_text)
                if score_match:
                    property_score = score_match.group(1).replace(",", ".")
                rev_match = re.search(r"(\d[\d\s.,]*)\s*(?:đánh giá|reviews|nhận xét)", score_text, re.IGNORECASE)
                if rev_match:
                    review_count = rev_match.group(1).strip()

            type_elem = _find_first(deal_box, '[data-testid="recommended-units"], span[class*="property-type"]')
            property_type = re.sub(r"\s+", " ", type_elem.text).strip() if type_elem else "Hotel"

            return {
                "city_name": place,
                "property_name": property_name,
                "property_url": property_url,
                "property_image": property_image,
                "location": location,
                "distance": distance,
                "property_price": property_price,
                "property_score": property_score,
                "review_count": review_count,
                "property_type": property_type,
                "checkin_date": checkin,
                "checkout_date": checkout,
                "number_of_adults": adult,
                "number_of_rooms": rooms,
            }
        except StaleElementReferenceException:
            return None

    def pull_deal_box_attributes(
        self, checkin: str, checkout: str, adult: int, rooms: int, place: str
    ) -> list:
        js_extract_script = """
        return (function() {
            const cards = document.querySelectorAll('div[data-testid="property-card"]');
            const items = [];
            cards.forEach(card => {
                try {
                    const titleEl = card.querySelector('[data-testid="title"]');
                    if (!titleEl) return;
                    const property_name = titleEl.textContent.trim();
                    if (!property_name) return;

                    const linkEl = card.querySelector('a[data-testid="title-link"]');
                    const property_url = linkEl ? linkEl.href : '';

                    const imgEl = card.querySelector('img[data-testid="image"]');
                    const property_image = imgEl ? (imgEl.src || imgEl.getAttribute('data-src') || '') : '';

                    const locEl = card.querySelector('[data-testid="address"]');
                    const location = locEl ? locEl.textContent.trim() : '';

                    const distEl = card.querySelector('[data-testid="distance"]');
                    const distance = distEl ? distEl.textContent.trim() : '';

                    const priceEl = card.querySelector('[data-testid="price-and-discounted-price"], [data-testid="price-for-x-nights"]');
                    const property_price = priceEl ? priceEl.textContent.trim() : 'N/A';

                    let property_score = 'N/A';
                    let review_count = 'N/A';
                    const scoreContainer = card.querySelector('[data-testid="review-score"]');
                    if (scoreContainer) {
                        const text = scoreContainer.textContent.trim();
                        const scoreMatch = text.match(/(\\d+[.,]\\d+|\\d+)/);
                        if (scoreMatch) {
                            property_score = scoreMatch[1].replace(',', '.');
                        }
                        const revMatch = text.match(/(\\d[\\d\\s.,]*)\\s*(?:đánh giá|reviews|nhận xét)/i);
                        if (revMatch) {
                            review_count = revMatch[1].trim();
                        }
                    }

                    const typeEl = card.querySelector('[data-testid="recommended-units"], span[class*="property-type"]');
                    const property_type = typeEl ? typeEl.textContent.replace(/\\s+/g, ' ').trim() : 'Hotel';

                    items.push({
                        property_name,
                        property_url,
                        property_image,
                        location,
                        distance,
                        property_price,
                        property_score,
                        review_count,
                        property_type
                    });
                } catch (e) {}
            });
            return items;
        })();
        """

        try:
            raw_items = self.driver.execute_script(js_extract_script)
            if raw_items and len(raw_items) > 0:
                results = []
                for item in raw_items:
                    item["city_name"] = place
                    item["checkin_date"] = checkin
                    item["checkout_date"] = checkout
                    item["number_of_adults"] = adult
                    item["number_of_rooms"] = rooms
                    if not item.get("location"):
                        item["location"] = place
                    results.append(item)
                return results
        except Exception:
            pass

        # Fallback: Selenium DOM traversal
        prev_timeout = 2
        try:
            self.driver.implicitly_wait(0)
            deal_boxes = self.pull_deal_boxes()
            collection_list = []
            for box in deal_boxes:
                item = self.parse_deal_box(box, place, checkin, checkout, adult, rooms)
                if item and item.get("property_name") and item["property_name"] != "N/A":
                    collection_list.append(item)
            return collection_list
        finally:
            self.driver.implicitly_wait(prev_timeout)
