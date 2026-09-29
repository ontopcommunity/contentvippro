import time
import random
import requests
from playwright.sync_api import sync_playwright

print("=================================================================")
print(" 🚀 TOOL TIKTOK VIEW - PROXYSCRAPE FREE API V2 (MAX POOL ALL) ")
print("=================================================================")

# 1. Tự động gọi API của ProxyScrape để lấy danh sách IP miễn phí toàn cầu (Không cần tài khoản)
print("📥 Đang tải danh sách Proxy miễn phí từ ProxyScrape API v4...")
try:
    # Gọi API lấy định dạng HTTP proxy, tốc độ phản hồi dưới 10s, từ tất cả quốc gia
    api_url = "https://proxyscrape.com"
    response = requests.get(api_url)
    
    # Tách danh sách thành từng dòng IP:Port
    proxy_list = [line.strip() for line in response.text.split("\n") if line.strip()]
    print(f"✅ Tải thành công {len(proxy_list)} Proxy toàn cầu vào bộ nhớ đệm!")
except Exception as e:
    print(f"❌ Không thể kết nối với API ProxyScrape: {e}")
    exit()

# 2. Giao diện nhập liệu tương tác
video_url = input("\n🔗 Dán link video TikTok cần cày view: ").strip()
if "tiktok.com" not in video_url:
    print("Link không hợp lệ! Vui lòng dán đúng link video TikTok.")
    exit()

try:
    total_views = int(input("🔢 Nhập TỔNG SỐ LƯỢNG VIEW muốn chạy: "))
    if total_views <= 0:
        raise ValueError
except ValueError:
    print("Vui lòng nhập một số nguyên dương!")
    exit()

print(f"\n[HỆ THỐNG] Bắt đầu kích hoạt cày {total_views} view không cần đăng nhập...")

# 3. Vòng lặp tự động chạy view bằng Proxy xoay vòng liên tục
for idx in range(1, total_views + 1):
    # Bốc ngẫu nhiên 1 IP trong cụm pool toàn thế giới vừa tải về
    selected_proxy = random.choice(proxy_list)
    print(f"\n[Lượt {idx}/{total_views}] 🌐 Proxy ngẫu nhiên: {selected_proxy}")
    
    proxy_config = {"server": f"http://{selected_proxy}"}
    
    with sync_playwright() as p:
        try:
            # Chạy trình duyệt sạch, không headless để video load chuẩn nhất
            browser = p.chromium.launch(headless=False, proxy=proxy_config)
            
            # Khởi tạo một phiên ẩn danh hoàn toàn, không lưu dấu vết, bỏ qua lỗi SSL nếu có
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()
            
            # Tạo kích thước màn hình ngẫu nhiên một chút để tránh bị quét thiết bị ảo
            width = random.choice([1024, 1280, 1366])
            height = random.choice([768, 720, 1080])
            page.set_viewport_size({"width": width, "height": height})
            
            print("   -> Đang mở trang video TikTok (Chế độ khách)...")
            page.goto(video_url, timeout=45000) # Đặt thời gian chờ 45s đề phòng proxy miễn phí tải chậm
            
            # Thời gian cày view ngẫu nhiên (từ 12 đến 25 giây)
            watch_time = random.uniform(12, 25)
            print(f"   -> Đang phát video... Giữ màn hình {watch_time:.1f} giây")
            time.sleep(watch_time)
            
            browser.close()
            print("   -> Hoàn thành 1 lượt view! Đóng trình duyệt.")
            
            # Nghỉ ngắn giữa các lượt mở trình duyệt từ 1 đến 3 giây
            time.sleep(random.uniform(1, 3))
            
        except Exception as e:
            # Do là proxy miễn phí nên sẽ có tỉ lệ một số IP bị chết hoặc kết nối quá chậm
            print(f"   ❌ Lượt thứ {idx} bỏ qua (Proxy phản hồi chậm hoặc bị TikTok chặn mạng).")
            try:
                browser.close()
            except:
                pass
            continue

print("\n================ TẤT CẢ LƯỢT CHẠY ĐÃ KẾT THÚC ================")
    
