BASE_URL = "https://www.booking.com/"
SEARCH_URL_TEMPLATE = "https://www.booking.com/searchresults.html?ss={place}&checkin={checkin}&checkout={checkout}&group_adults={adults}&no_rooms={rooms}&group_children=0&offset={offset}"

CSV_FIELDNAMES = [
    "city_name",
    "property_name",
    "property_url",
    "property_image",
    "location",
    "distance",
    "property_price",
    "property_score",
    "review_count",
    "property_type",
    "checkin_date",
    "checkout_date",
    "number_of_adults",
    "number_of_rooms",
]

SELECTORS = {
    # Popups
    "cookie_banner_accept": 'button#onetrust-accept-btn-handler, button[id*="onetrust-accept"]',
    "sign_in_dismiss": 'button[aria-label*="Dismiss"], button[aria-label*="Bỏ qua"], button[aria-label*="Đóng"], button[aria-label*="Close"]',

    # Search Box (Home Page)
    "destination_input": 'input[name="ss"], input[data-testid="destination-input"]',
    "destination_first_result": 'ul[role="listbox"] li:first-child, [data-testid="autocomplete-results-options"] li:first-child, [data-testid="autocomplete-result"]',
    "date_picker_toggle": 'button[data-testid="date-display-field-start"], [data-testid="searchbox-dates-container"]',
    "date_cell": 'span[data-date="{date}"], td[data-date="{date}"]',
    "occupancy_config_toggle": 'button[data-testid="occupancy-config"]',
    "search_submit": 'button[type="submit"]',

    # Property Card Elements
    "property_card": 'div[data-testid="property-card"]',
    "property_title": '[data-testid="title"]',
    "property_link": 'a[data-testid="title-link"]',
    "property_image": 'img[data-testid="image"]',
    "property_address": '[data-testid="address"]',
    "property_distance": '[data-testid="distance"]',
    "property_price": '[data-testid="price-and-discounted-price"], [data-testid="price-for-x-nights"]',
    "property_score": '[data-testid="review-score"] [aria-hidden="true"], [data-testid="review-score"] div:first-child',
    "review_count": '[data-testid="review-score"] [class*="review-count"], [data-testid="review-score"] div:last-child',

    # Pagination
    "pagination_container": 'nav[aria-label*="Pagination"], [data-testid="pagination"]',
    "pagination_next_button": 'button[aria-label*="Next"], button[aria-label*="Trang sau"], [data-testid="pagination"] button:last-child',

    # Filters
    "filter_stars_group": '[data-filters-group="class"]',
    "filter_star_item": '[data-filters-item*="class:class={stars}"] input, [data-filters-item*="class:class={stars}"] label',
}
