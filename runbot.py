import os
import sys
import time
import math
import argparse

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from booking.booking import Booking
from booking import helpers
from booking import constant as const


def format_duration(seconds: float) -> str:
    seconds = int(max(0, seconds))
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{h:d}h {m:02d}m {s:02d}s" if h > 0 else f"{m:02d}m {s:02d}s"


def load_existing_urls(csv_file: str) -> set:
    if not os.path.exists(csv_file):
        return set()
    identifiers = set()
    try:
        import csv
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = (row.get("property_url") or "").split("?")[0].strip()
                if url:
                    identifiers.add(url)
                else:
                    name = row.get("property_name", "").strip().lower()
                    loc = row.get("location", "").strip().lower()
                    if name:
                        identifiers.add(f"{name}|{loc}")
    except Exception:
        pass
    return identifiers


def scrape_destination(
    bot: Booking,
    place: str,
    checkin: str,
    checkout: str,
    adults: int = 2,
    rooms: int = 1,
    max_pages: int = 0,
    nav_mode: str = "offset",
    delay: float = 0.8,
    resume: bool = True,
):
    sanitized_place = place.replace(" ", "_").lower()
    os.makedirs("scraped_data", exist_ok=True)
    csv_file = os.path.join("scraped_data", f"{sanitized_place}_booking.csv")
    json_file = os.path.join("scraped_data", f"{sanitized_place}_booking.json")

    seen_identifiers = set()
    all_results = []
    if resume and os.path.exists(csv_file):
        seen_identifiers = load_existing_urls(csv_file)
        if seen_identifiers:
            print(f"[*] Đã tải {len(seen_identifiers):,} bản ghi có sẵn từ {csv_file}")

    print(f"\n{'='*70}")
    print(f"[*] BẮT ĐẦU CÀO: {place.upper()}")
    print(f"[*] Ngày: {checkin} -> {checkout} | Khách: {adults} người, {rooms} phòng")
    print(f"[*] Phân trang: {nav_mode.upper()} | Giãn cách: {delay}s | Tệp: {csv_file}")
    print(f"{'='*70}\n")

    bot.search_by_url(
        place=place,
        checkin=checkin,
        checkout=checkout,
        adults=adults,
        rooms=rooms,
        offset=0,
    )

    total_found = bot.get_total_count()
    est_pages = math.ceil(total_found / 25) if total_found > 0 else 1
    accessible_pages = min(est_pages, 40)
    target_pages = min(accessible_pages, max_pages) if max_pages > 0 else accessible_pages

    print(f"[i] Tìm thấy ~{total_found:,} chỗ nghỉ. Kế hoạch cào: {target_pages} trang.\n")

    page_num = 0
    consecutive_empty = 0
    crawl_start_time = time.time()

    try:
        while True:
            page_num += 1

            if max_pages > 0 and page_num > max_pages:
                print(f"\n[*] Đạt giới hạn {max_pages} trang cấu hình.")
                break

            page_t0 = time.time()

            if page_num > 1:
                if nav_mode == "offset":
                    current_offset = (page_num - 1) * 25
                    bot.navigate_to_offset(current_offset)
                else:
                    if not bot.go_next_page():
                        print("\n[-] Hết nút chuyển trang tiếp theo.")
                        break

                if delay > 0:
                    time.sleep(delay)

            page_items = bot.report_results()

            if not page_items:
                consecutive_empty += 1
                if consecutive_empty >= 2:
                    print("[-] Không còn dữ liệu trên các trang tiếp theo.")
                    break
                continue

            new_unique_items = []
            for item in page_items:
                raw_url = item.get("property_url") or ""
                clean_url = raw_url.split("?")[0].strip() if raw_url else ""
                unique_key = clean_url if clean_url else f"{item.get('property_name', '').strip().lower()}|{item.get('location', '').strip().lower()}"

                if unique_key not in seen_identifiers:
                    seen_identifiers.add(unique_key)
                    new_unique_items.append(item)
                    all_results.append(item)

            if len(new_unique_items) == 0:
                consecutive_empty += 1
                if consecutive_empty >= 2 or page_num >= 40:
                    print(f"\n[-] Chạm ngưỡng giới hạn kết quả của Booking.com (lặp lại trang cũ). Hoàn tất!")
                    break
            else:
                consecutive_empty = 0

            if new_unique_items:
                helpers.save_to_csv(new_unique_items, csv_file, const.CSV_FIELDNAMES)
                helpers.save_to_json(all_results, json_file)

            page_duration = time.time() - page_t0
            elapsed_total = time.time() - crawl_start_time
            speed = len(all_results) / max(elapsed_total, 0.001)

            progress_pct = (page_num / target_pages * 100) if target_pages > 0 else 0
            remaining_pages = max(0, target_pages - page_num)
            eta_seconds = (remaining_pages * (elapsed_total / page_num)) if page_num > 0 else 0

            print(
                f"[Trang {page_num:02d}/{target_pages:02d} ({progress_pct:4.1f}%)] "
                f"+{len(new_unique_items):2d} mới (Tổng: {len(all_results):,}) | "
                f"{speed:4.1f} ks/s | "
                f"{page_duration:.2f}s | "
                f"ETA: {format_duration(eta_seconds)}",
                flush=True,
            )

            if len(page_items) < 15 and page_num > 1:
                break

    except KeyboardInterrupt:
        print("\n\n[!] Dừng bởi người dùng. Dữ liệu đã cào đã được lưu an toàn.")

    elapsed_total = time.time() - crawl_start_time
    print(f"\n{'='*70}")
    print(f"[OK] HOÀN TẤT CHO '{place}'")
    print(f"[+] Thu thập: {len(all_results):,} khách sạn ({page_num} trang)")
    print(f"[+] Thời gian: {format_duration(elapsed_total)} ({len(all_results)/max(elapsed_total, 0.001):.1f} ks/s)")
    print(f"[+] File CSV: {csv_file}")
    print(f"[+] File JSON: {json_file}")
    print(f"{'='*70}\n", flush=True)

    return all_results


def main():
    parser = argparse.ArgumentParser(
        description="Booking.com High-Speed Exhaustive Scraper"
    )
    parser.add_argument(
        "--destination", "--destinations", "--place", "--places",
        nargs="*",
        default=None,
        help="Một hoặc nhiều thành phố (ví dụ: --destinations 'Da Nang' 'Ha Noi' hoặc 'Da Nang, Ha Noi')",
    )
    parser.add_argument("--checkin", type=str, default=None, help="Ngày nhận phòng (YYYY-MM-DD)")
    parser.add_argument("--checkout", type=str, default=None, help="Ngày trả phòng (YYYY-MM-DD)")
    parser.add_argument("--adults", type=int, default=2, help="Số người lớn (mặc định: 2)")
    parser.add_argument("--rooms", type=int, default=1, help="Số phòng (mặc định: 1)")
    parser.add_argument("--pages", type=int, default=0, help="Số trang tối đa (0 = vét cạn tất cả)")
    parser.add_argument(
        "--nav",
        choices=["offset", "click"],
        default="offset",
        help="Phương thức phân trang: 'offset' (khuyến nghị) hoặc 'click'",
    )
    parser.add_argument("--delay", type=float, default=0.8, help="Thời gian giãn cách giữa các trang (giây, mặc định: 0.8s)")
    parser.add_argument("--headless", action="store_true", help="Chạy ẩn trình duyệt không mở giao diện")
    parser.add_argument("--no-resume", action="store_true", help="Không đọc lại dữ liệu cũ, ghi đè file mới")
    parser.add_argument("--csv", type=str, default="client_input/destination_param.csv", help="Đường dẫn file CSV danh sách tham số đầu vào")

    args = parser.parse_args()

    targets = []
    raw_destinations = []
    if args.destination:
        for item in args.destination:
            for part in str(item).split(","):
                clean_part = part.strip()
                if clean_part:
                    raw_destinations.append(clean_part)

    if raw_destinations:
        checkin, checkout = args.checkin, args.checkout
        if not checkin or not checkout:
            checkin, checkout = helpers.generate_default_dates(days_ahead=7, duration_days=3)
        for place in raw_destinations:
            targets.append({
                "place": place,
                "checkin": checkin,
                "checkout": checkout,
                "adult": args.adults,
                "rooms": args.rooms,
            })
    else:
        csv_rows = helpers.get_csv_data(args.csv)
        if not csv_rows:
            c_in, c_out = helpers.generate_default_dates(days_ahead=7, duration_days=3)
            targets.append({
                "place": "Da Nang",
                "checkin": c_in,
                "checkout": c_out,
                "adult": 2,
                "rooms": 1,
            })
        else:
            for row in csv_rows:
                date_ranges = helpers.construct_date_range(
                    start_year=int(row.get("start_year", 2026)),
                    start_month=int(row.get("start_month", 11)),
                    duration=int(row.get("duration", 1)),
                    place=row.get("place", "Da Nang"),
                    adult=int(row.get("adult", 2)),
                    rooms=int(row.get("rooms", 1)),
                )
                targets.extend(date_ranges)

    target_names = [t['place'] for t in targets]
    print(f"\n{'='*70}")
    print(f"[*] DANH SÁCH ĐỊA ĐIỂM ({len(targets)}): {', '.join(target_names)}")
    print(f"[*] Headless: {args.headless} | Phân trang: {args.nav.upper()} | Giãn cách: {args.delay}s")
    print(f"{'='*70}\n")

    with Booking(headless=args.headless, teardown=True) as bot:
        for idx, target in enumerate(targets, 1):
            print(f"\n{'#'*70}")
            print(f"### [{idx}/{len(targets)}] {target['place'].upper()}")
            print(f"{'#'*70}")
            try:
                scrape_destination(
                    bot=bot,
                    place=target["place"],
                    checkin=target["checkin"],
                    checkout=target["checkout"],
                    adults=int(target.get("adult", 2)),
                    rooms=int(target.get("rooms", 1)),
                    max_pages=args.pages,
                    nav_mode=args.nav,
                    delay=args.delay,
                    resume=not args.no_resume,
                )
                time.sleep(2)
            except Exception as e:
                print(f"[!] Lỗi khi cào dữ liệu cho {target.get('place')}: {e}")


if __name__ == "__main__":
    main()
