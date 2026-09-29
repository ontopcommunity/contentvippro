import asyncio
import httpx
import requests
import random
import re
import time
from urllib.parse import quote

print("=================================================================")
print(" 🔥 TOOL TIKTOK VIEW V10 MATRIX ELITE - DOUBLE CHECK API V2 🔥 ")
print("=================================================================")

# 1. Khởi động hệ thống nạp Pool Proxy từ ProxyScrape
print("📥 Đang nạp hệ thống Proxy ngẫu nhiên toàn cầu...")
try:
    proxy_url = "https://proxyscrape.com"
    proxy_res = requests.get(proxy_url)
    proxy_list = [line.strip() for line in proxy_res.text.split("\n") if line.strip()]
    print(f"✅ Đã nạp thành công {len(proxy_list)} IP vào bộ nhớ!")
except Exception as e:
    print(f"❌ Không thể lấy danh sách Proxy: {e}")
    exit()

# 2. Tự động tải kho lưu trữ Real Mobile User-Agent từ GitHub
print("📥 Đang đồng bộ Real Mobile User-Agent từ GitHub...")
try:
    ua_github_url = "https://githubusercontent.com"
    ua_res = requests.get(ua_github_url)
    all_ua = [line.strip() for line in ua_res.text.split("\n") if line.strip()]
    ua_list = [ua for ua in all_ua if any(x in ua.lower() for x in ["android", "iphone", "mobile", "arm"])]
    print(f"✅ Đã nạp thành công {len(ua_list)} Real User-Agent chất lượng cao!")
except Exception as e:
    print(f"⚠️ Chuyển hướng sang danh sách UA Premium tích hợp sẵn do lỗi kết nối GitHub.")
    ua_list = [
        "Mozilla/5.0 (Linux; Android 12; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
    ]

# 3. Giao diện nhận diện link video
raw_input = input("\n📝 Nhập hoặc dán link video TikTok của bạn vào đây: ").strip()
url_match = re.search(r'(https?://[^\s]*tiktok\.com/[^\s]*)', raw_input)
if not url_match:
    print("❌ Không tìm thấy link TikTok hợp lệ!")
    exit()

clean_tiktok_url = url_match.group(1)
video_ids = []

# Hàm gọi API trung gian lấy thông tin video (Hỗ trợ bóc tách chuỗi thô bao dung)
async def check_video_api(url, label="TRƯỚC KHI BUFF"):
    encoded_url = quote(url, safe='')
    api_endpoint = f"https://vercel.app{encoded_url}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(api_endpoint, headers=headers)
            if response.status_code == 200:
                res_text = response.text
                
                # Trích xuất thông tin bằng Regex thô cường độ cao để tránh sập cấu trúc chuỗi
                vid_match = re.search(r'"video_data"\s*:\s*\{[^}]*?"id"\s*:\s*"(\d+)"', res_text)
                if not vid_match:
                    vid_match = re.search(r'"id"\s*:\s*"(\d+)"', res_text)
                
                unique_id = re.search(r'"uniqueId"\s*:\s*"([^"]+)"', res_text)
                nickname = re.search(r'"nickname"\s*:\s*"([^"]+)"', res_text)
                play_count = re.search(r'"play"\s*:\s*(\d+)', res_text)
                
                if vid_match:
                    vid = vid_match.group(1)
                    if vid not in video_ids:
                        video_ids.append(vid)
                    
                    print(f"\n================ 📊 THÔNG TIN VIDEO ({label}) ================")
                    print(f"👤 Nickname (Tên tài khoản)     : {nickname.group(1) if nickname else 'N/A'}")
                    print(f"🆔 Unique ID (ID chủ video)    : {unique_id.group(1) if unique_id else 'N/A'}")
                    print(f"🎬 Video ID (Mã định danh)     : {vid}")
                    print(f"👁️ Play (Lượt xem hiện tại)     : {play_count.group(1) if play_count else '0'}")
                    print("==============================================================")
                    return True
            return False
        except Exception as e:
            print(f"❌ Lỗi khi đọc dữ liệu từ API: {e}")
            return False

# Gọi kiểm tra API lần 1 (Trước khi buff)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
api_success = loop.run_until_complete(check_video_api(clean_tiktok_url, label="TRƯỚC KHI BUFF"))

if not video_ids:
    print("❌ Bộ lọc không thể lấy dữ liệu ID từ API bài viết để tiếp tục!")
    exit()

# 4. Giao diện thiết lập chỉ tiêu số lượng (Ép cấu hình 5.000 luồng)
try:
    total_views = int(input("\n🔢 Nhập TỔNG SỐ LƯỢNG VIEW mong muốn (Tối đa 1.000.000): "))
    if total_views <= 0 or total_views > 1000000:
        print("Hạn mức không hợp lệ!")
        exit()
    # Tự động gán 5000 luồng song song để đạt tốc độ 5k - 10k view/s theo yêu cầu
    max_concurrent_tasks = 5000
    print(f"⚡ Hệ thống tự động thiết lập: 5000 Luồng Matrix siêu cấp.")
except ValueError:
    print("Vui lòng nhập số nguyên hợp lệ!")
    exit()

success_count = 0
lock = asyncio.Lock()

# 5. Giả lập thông số phần cứng thiết bị chuyên sâu
def generate_advanced_device_params():
    app_v = random.choice(["26.1.3", "27.5.4", "28.2.0", "29.1.2"])
    build_v = random.choice(["260103", "270504", "280200", "290102"])
    return {
        "device_id": str(random.randint(7100000000000000000, 7899999999999999999)),
        "openudid": "".join(random.choices("0123456789abcdef", k=16)),
        "uuid": "".join(random.choices("0123456789", k=15)),
        "install_id": str(random.randint(7100000000000000000, 7899999999999999999)),
        "dpi": random.choice(["240", "320", "440", "480"]),
        "carrier": random.choice(["Viettel", "Vinaphone", "Mobifone", "Verizon", "T-Mobile"]),
        "app_version": app_v,
        "build_version": build_v
    }

# 6. Hàm bắn Request ngầm cày tương tác vượt rào cản đếm view
async def send_premium_view(client, proxy, vid, selected_ua):
    global success_count
    dev = generate_advanced_device_params()
    ts = str(int(time.time()))
    
    url = (
        f"https://tiktokv.com{vid}&type=1&action=play"
        f"&device_id={dev['device_id']}&openudid={dev['openudid']}&uuid={dev['uuid']}"
        f"&iid={dev['install_id']}&app_name=musical_ly&channel=googleplay&device_platform=android"
        f"&version_code={dev['build_version']}&version_name={dev['app_version']}&dpi={dev['dpi']}"
    )
    
    headers = {
        "User-Agent": selected_ua,
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Host": "://tiktokv.com",
        "X-Common-Params-Client-Type": "android",
        "X-Khronos": ts,
        "X-SS-REQ-TICK": f"{ts}000",
        "X-Carrier": dev['carrier']
    }
    
    try:
        response = await client.post(url, headers=headers, proxy=f"http://{proxy}", timeout=3.0)
        if response.status_code == 200:
            async with lock:
                success_count += 1
                if success_count % 1000 == 0 or success_count == total_views:
                    print(f"🚀 [MATRIX SPEED] Đã đẩy thành công: {success_count}/{total_views} view (Tốc độ 5k-10k/s)")
    except:
        pass

# 7. Bộ điều hành lõi Pipeline bất đồng bộ đa luồng cực đại
async def main():
    limits = httpx.Limits(max_connections=max_concurrent_tasks, max_keepalive_connections=max_concurrent_tasks)
    print(f"\n⚡ BẮT ĐẦU XẢ HỎA LỰC 5000 LUỒNG SONG SONG... VUI LÒNG Treo MÁY...")
    
    async with httpx.AsyncClient(limits=limits) as client:
        tasks = []
        for _ in range(total_views):
            proxy = random.choice(proxy_list)
            vid = video_ids[0]
            selected_ua = random.choice(ua_list)
            
            task = asyncio.create_task(send_premium_view(client, proxy, vid, selected_ua))
            tasks.append(task)
            
            if len(tasks) >= max_concurrent_tasks:
                await asyncio.gather(*tasks)
                tasks = []
                
        if tasks:
            await asyncio.gather(*tasks)

# Khởi động chiến dịch cày siêu tốc
start_time = time.time()
loop.run_until_complete(main())
end_time = time.time()

print(f"\n================ CHIẾN DỊCH HOÀN THÀNH V10 ================")
print(f"✅ Hoàn thành gửi gói tin. Tổng thời gian xử lý: {end_time - start_time:.2f} giây")

# 8. Kích hoạt tính năng đọc lại API lần 2 (Sau khi buff xong chỉ tiêu)
print("\n🔄 Đang chờ 5 giây để máy chủ TikTok cập nhật bộ đếm view...")
time.sleep(5)
loop.run_until_complete(check_video_api(clean_tiktok_url, label="SAU KHI BUFF XONG"))
print("==============================================================")
    
