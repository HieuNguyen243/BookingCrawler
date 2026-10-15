# Booking.com Web Crawler (Selenium & CSS Selectors)

Chương trình tự động hóa thu thập dữ liệu khách sạn từ [Booking.com](https://www.booking.com/) sử dụng **Python**, **Selenium 4**, bộ **CSS Selector chuẩn hóa** (`data-testid`, `aria-label`) và cơ chế **Anti-bot Stealth** để kiểm tra và vượt qua các thử thách bảo vệ cơ bản của trang web.

---

## 🌟 Tính Năng Nổi Bật

- **Phương pháp CSS Selector chủ đạo**: Sử dụng các thuộc tính ổn định (`div[data-testid="property-card"]`, `[data-testid="title"]`, `[data-testid="price-and-discounted-price"]`,...) thay vì các CSS class ngẫu nhiên dễ đổi.
- **Vượt thử thách Anti-bot cơ bản (Stealth Mode)**:
  - Tắt các cờ nhận diện tự động (`--disable-blink-features=AutomationControlled`, `--disable-automation`).
  - Tiêm lệnh DevTools Protocol (CDP) xóa cờ `navigator.webdriver`.
  - Tự động phát hiện và đóng các popup/modal làm gián đoạn: Cookie banner (`#onetrust-accept-btn-handler`) và hộp thoại đăng nhập (`[aria-label*="Dismiss"]`).
- **Hỗ trợ 2 chế độ cào linh hoạt**:
  - `mode=url` (Khuyên dùng): Tạo URL tìm kiếm trực tiếp với các tham số, bỏ qua các bước nhập form phức tạp, tăng tốc độ và độ tin cậy.
  - `mode=interactive`: Mô phỏng tương tác gõ địa điểm, mở lịch chọn ngày, điều chỉnh số khách và bấm nút tìm kiếm.
- **Cuộn trang tự động (Lazy-load scrolling)**: Kích hoạt tải ảnh đầy đủ và các thẻ phòng tải chậm.
- **Xuất dữ liệu kép**: Tự động lưu ra cả 2 định dạng **CSV** và **JSON** trong thư mục `scraped_data/`.

---

## 📋 Trường Dữ Liệu Thu Thập

Mỗi khách sạn bao gồm các trường dữ liệu chi tiết:
- `city_name`: Tên thành phố / điểm đến
- `property_name`: Tên chỗ nghỉ / khách sạn
- `property_url`: Đường dẫn chi tiết trên Booking.com
- `property_image`: URL ảnh đại diện thumbnail
- `location`: Địa chỉ / vị trí
- `distance`: Khoảng cách tới trung tâm thành phố
- `property_price`: Giá phòng hiện hành (kèm đơn vị tiền tệ)
- `property_score`: Điểm đánh giá (vd: 9.2, 8.5)
- `review_count`: Số lượt khách hàng đánh giá
- `property_type`: Loại phòng / tiện ích đi kèm (đã chuẩn hóa định dạng dòng đơn)
- `checkin_date`: Ngày nhận phòng (YYYY-MM-DD)
- `checkout_date`: Ngày trả phòng (YYYY-MM-DD)
- `number_of_adults`: Số lượng người lớn
- `number_of_rooms`: Số lượng phòng

---

## 🚀 Cài Đặt & Khởi Chạy

### 1. Kích hoạt Môi trường ảo

```powershell
# Kích hoạt môi trường ảo Python 3.12 (.venv)
.\.venv\Scripts\Activate.ps1

# Cài đặt hoặc cập nhật thư viện
pip install -r requirements.txt
```

*(Lưu ý: Dự án sử dụng Selenium 4.x với **Selenium Manager**, trình duyệt Chrome sẽ tự động được tải đúng phiên bản tương thích mà không cần tải thủ công chromedriver.exe).*

---

### 2. Sử Dụng Lệnh `runbot.py`

#### A. Cào theo dòng lệnh (CLI):
```powershell
# Cào khách sạn tại Đà Nẵng (1 trang kết quả, chạy ngầm headless)
python runbot.py --destination "Da Nang" --pages 1 --headless

# Cào khách sạn tại Hà Nội có giao diện trình duyệt trực quan
python runbot.py --destination "Ha Noi" --pages 1

# Cào với ngày tùy chọn và số lượng khách
python runbot.py --destination "Nha Trang" --checkin 2026-11-10 --checkout 2026-11-15 --adults 2 --rooms 1
```

#### B. Cào hàng loạt theo tệp tham số CSV:
Cập nhật danh sách điểm đến trong `client_input/destination_param.csv`:
```csv
place,start_year,start_month,duration,adult,rooms
Da Nang,2026,11,1,2,1
Ha Noi,2026,11,1,2,1
Ho Chi Minh,2026,12,1,2,1
```
Sau đó chạy:
```powershell
python runbot.py
```

---

## 📁 Cấu Trúc Dự Án

```
booking.com_crawler/
├── .venv/                         # Môi trường ảo Python 3.12
├── booking/
│   ├── __init__.py
│   ├── constant.py                # Bảng registry CSS Selector & URL templates
│   ├── booking.py                 # Core scraper, stealth WebDriver, popup handling
│   ├── report.py                  # Module trích xuất thuộc tính khách sạn tốc độ cao
│   ├── pagenation.py              # Xử lý đếm kết quả & điều hướng trang
│   ├── filters.py                 # Lọc hạng sao và sắp xếp giá
│   └── helpers.py                 # Xử lý ngày tháng, làm sạch dữ liệu, lưu CSV/JSON
├── client_input/
│   └── destination_param.csv      # File cấu hình tham số cào hàng loạt
├── scraped_data/                  # Thư mục lưu trữ dữ liệu cào về (.csv, .json)
├── runbot.py                      # File thực thi chính với giao diện CLI
└── requirements.txt               # Danh sách thư viện phụ thuộc
```

---

## 🛡️ Khảo Sát Kỹ Thuật Bảo Mật & Anti-Bot

1. **Thử nghiệm HTTP Request thuần (`requests`/`curl`)**:
   - Booking.com phát hiện và trả về mã `HTTP 202` kèm mã thử thách AJAX JavaScript (PerimeterX / Kasada).
   - Kết luận: Không thể cào Booking.com bằng HTTP request đơn thuần mà không chạy JavaScript engine.

2. **Thử nghiệm Selenium mặc định**:
   - Dấu hiệu `window.navigator.webdriver = true` và các đối tượng tự động hóa bị phát hiện nếu không được cấu hình.
   - Khi phát hiện nghi vấn bot, Booking.com sẽ liên tục chèn modal đăng nhập, kiểm tra reCAPTCHA hoặc ẩn kết quả giá.

3. **Giải pháp đã kiểm nghiệm thành công**:
   - Tắt cờ `--disable-blink-features=AutomationControlled` và loại bỏ đối tượng `navigator.webdriver` qua Chrome DevTools Protocol (CDP).
   - Thiết lập User-Agent tiêu chuẩn của Google Chrome bản desktop.
   - Bổ sung hàm tự động tắt Cookie Banner và Sign-in popup bằng CSS Selector `aria-label*="Dismiss"`.
   - Kết quả: Thu thập 100% dữ liệu 25/25 khách sạn mỗi trang ổn định mà không bị chặn.
