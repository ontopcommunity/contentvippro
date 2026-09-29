import asyncio
import httpx
import requests
import random
import re

print("=================================================================")
print(" 🚀 TOOL TIKTOK VIEW - ASYNC MULTI-THREADING REQ (SUPER SPEED) ")
print("=================================================================")

# 1. Tự động cào Pool Proxy miễn phí từ ProxyScrape Toàn Cầu
print("📥 Đang nạp Pool Proxy từ ProxyScrape API v4...")
try:
    api_url = "https://proxyscrape.com"
    response = requests.get(api_url)
    proxy_list = [line.strip() for line in response.text.split("\n") if line.strip()]
    print(f"✅ Đã nạp thành công {len(proxy_list)} IP vào bệ phóng!")
except Exception as e:
    print(f"❌ Không thể lấy danh sách Proxy: {e}")
    exit()

# 2. Nhập thông tin cấu hình tốc độ
video_url = input("\n🔗 Dán link video TikTok cần cày view: ").strip()
try:
    video_id = re.search(r'/video/(\d+)', video_url).group(1)
    print(f"🎯 Phát hiện Video ID: {video_id}")
except:
    print("❌ Link video không đúng định dạng chuẩn của TikTok!")
    exit()

try:
    total_views = int(input("🔢 Nhập TỔNG SỐ LƯỢNG VIEW mong muốn (Ví dụ: 50000): "))
    max_concurrent_tasks = int(input("⚡ Nhập SỐ LUỒNG CHẠY SONG SONG (Khuyên dùng: 500 - 2000 tùy cấu hình máy): "))
except ValueError:
    print("Vui lòng nhập số nguyên hợp lệ!")
    exit()

success_count = 0
lock = asyncio.Lock()

# 3. Định nghĩa hàm gửi gói tin View siêu tốc bất đồng bộ
async def send_view_request(client, proxy):
    global success_count
    # Giả lập Header giống như ứng dụng TikTok thật gửi tín hiệu về Server
    headers = {
        "User-Agent": "com.zhiliaoapp.musically/2022403040 (Linux; U; Android 10; bst_pro_x86_64)",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Host": "://tiktokv.com"
    }
    
    # Endpoint gửi gói tin log thống kê lượt xem của hệ thống TikTok
    url = f"https://://tiktokv.com/aweme/v1/aweme/stats/?aweme_id={video_id}&type=1&action=play"
    
    try:
        # Gửi request ẩn danh cực nhanh qua Proxy xoay vòng
        response = await client.post(url, headers=headers, proxy=f"http://{proxy}", timeout=3.0)
        
        if response.status_code == 200:
            async with lock:
                success_count += 1
                if success_count % 100 == 0: # Cứ 100 view thì in ra màn hình một lần để tránh nghẽn log
                    print(f"🚀 Tốc lực: Đã bắn thành công {success_count} lượt xem...")
    except:
        pass # Bỏ qua các proxy lỗi/chậm để nhường luồng cho IP khác bắn tiếp

# 4. Trình quản lý điều phối hàng vạn luồng chạy cùng một lúc
async def main():
    global success_count
    limits = httpx.Limits(max_connections=max_concurrent_tasks, max_keepalive_connections=max_concurrent_tasks)
    
    print("\n[HỆ THỐNG] Đang kích hoạt chế độ tàn sát... Nhấn Ctrl+C để dừng.")
    
    async with httpx.AsyncClient(limits=limits) as client:
        tasks = []
        for _ in range(total_views):
            # Chọn ngẫu nhiên 1 IP trong danh sách để gửi gói tin
            proxy = random.choice(proxy_list)
            task = asyncio.create_task(send_view_request(client, proxy))
            tasks.append(task)
            
            # Kiểm tra kiểm soát số luồng tối đa chạy cùng một thời điểm tránh treo CPU mạng nhà
            if len(tasks) >= max_concurrent_tasks:
                await asyncio.gather(*tasks)
                tasks = []
                
        if tasks:
            await asyncio.gather(*tasks)

# Kích hoạt bệ phóng Async
asyncio.run(main())
print(f"\n================ CHIẾN DỊCH KẾT THÚC. TỔNG VIEW ĐÃ GỬI: {success_count} ================")
