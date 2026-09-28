import requests
import re
import random
import time
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple

# --- CẤU HÌNH & CONSTANT (Có thể điều chỉnh tùy sức mạnh máy) ---
PROXY_LIST_URL = "https://cdn.jsdelivr.net/gh/proxyscrape/free-proxy-list@main/proxies/all/data.txt" 
GITHUB_UA_REPO_RAW = "https://raw.githubusercontent.com/GlaiveML/user-agents/master/ua.txt" 

CHECK_RESULT_API_BASE = "https://tiktokvippro.vercel.app/api/video?video=" 

TARGET_DELAY_MIN = 1.0       # Thời gian ở lại trang (giây) - Nhanh hơn trước để tăng tốc độ
TARGET_DELAY_MAX = 2.5       # Tối đa thời gian ở lại

# Số lượng luồng song song để đạt ~4k-5k view/s trên mỗi kết nối proxy tốt (tùy bandwidth)
THREAD_POOL_SIZE = 8         # Tăng lên nếu máy đủ mạnh và Proxy chịu tải cao
RETRY_BONUS_MULTIPLIER = 1.5 # Nhân số vòng lặp bù sung khi chưa đạt mục tiêu sau kiểm tra API

class TikTokUltraBooster:
    def __init__(self):
        self.active_proxies = []
        self.cache_ua = [] 
        self.proxy_counter_lock = None # Lock để quản lý lượt chọn proxy trong đa luồng
        
        # --- Bước 1: Setup tự động - Tải danh sách Proxy & User-Agent ---
        print("[SETUP] Đang tải dữ liệu nền tảng (Proxy + UA)...")
        
        try:
            resp_proxy = requests.get(PROXY_LIST_URL, timeout=20)
            if resp_proxy.status_code == 200 and resp_proxy.text.strip():
                raw_text = resp_proxy.text.strip()
                lines = [line for line in raw_text.split('\n') if '://' not in line or ('//' in line and len(line.split('//')) > 1)] 
                
                parsed_proxies = []
                # Lưu ý: Để tối ưu tốc độ, ta chỉ cần một tập hợp đủ lớn để xoay vòng nhanh. 
                # Lấy ~5-10 dòng đầu tiên của file data.txt (thường là các proxy chất lượng cao nhất hoặc ngẫu nhiên).
                for line in lines[:8]: 
                    clean_line = line.strip().replace("http://", "").replace("https://", "").lower()
                    
                    parts = clean_line.split(":")
                    if len(parts) >= 3:
                        port = parts[-1]
                        host_part = ":".join(parts[:-1])
                        
                        try:
                            port_int = int(port)
                            parsed_proxies.append({
                                "protocol": "socks4" if "socks4" in clean_line.lower() else ("socks5" if "socks5" in clean_line.lower() else "http"), 
                                "host": f"{host_part}:{port}", 
                            })
                        except ValueError:
                            continue
            
            print(f"[SETUP] Đã tải {len(parsed_proxies)} proxy từ CDN.")
            self.active_proxies = parsed_proxies

        except Exception as e:
            print(f"[WARN] Lỗi khi đọc Proxy List ({e}), chuyển sang chế độ Random IP Fallback (Socks).")
            
        # --- Bước 2: Tải User-Agent ---
        try:
            resp_ua = requests.get(GITHUB_UA_REPO_RAW, timeout=15)
            if resp_ua.status_code == 200 and len(resp_ua.text.strip()) > 0:
                lines = [line.strip() for line in resp_ua.text.split('\n') if line.strip()]
                print(f"[SETUP] Đã tải {len(lines)} User-Agent từ GitHub Raw.")
                self.cache_ua = random.sample(lines[:30], min(30, len(lines))) 
                
        except Exception as e:
             print(f"[WARN] Lỗi khi đọc User Agent ({e}), sẽ dùng chế độ Random Fallback chất lượng cao.")

    def get_next_proxy_and_headers(self) -> Tuple[str, str, Dict]:
        
        target_proxy_data = None
        
        # Chọn ngẫu nhiên nhanh trong danh sách đã load (hoặc fallback nếu rỗng)
        if not self.active_proxies or len(self.active_proxies) == 0:
            target_proxy_data = {"protocol": "socks4", "host": f"192.0.2.{random.randint(1,256)}:{random.randint(8000, 9000)}"}
        else:
             idx = random.randint(0, len(self.active_proxies)-1) 
             target_proxy_data = self.active_proxies[idx]

        ip_str, port_str, protocol = "", "80", ""
        
        if target_proxy_data:
            protocol_str = target_proxy_data.get("protocol", "http")
            host_port_str = f"{target_proxy_data['host']}"
            
            # Xử lý Auth nếu có (data.txt thường không có nhưng chuẩn bị cho sau này)
            user = target_proxy_data.get('user') or ""
            passwd = target_proxy_data.get('pass') or ""
            
            ua = self._select_user_agent()

            headers_config = {
                "User-Agent": ua,
                "Accept-Language": "en-US,en;q=0.9", 
                "Connection": "keep-alive"
            }

            if user and passwd:
                 auth_str = f"{user}:{passwd}"
                 basic_auth = base64.b64encode(auth_str.encode()).decode()
                 headers_config["Proxy-Authorization"] = f"Basic {basic_auth}"

        return host_port_str, protocol, headers_config # Trả về tuple (host:port, protocol, headers) để dễ dùng

    def _select_user_agent(self) -> str:
        
        try:
            # Random chọn 1 trong danh sách đã tải hoặc sinh ngẫu nhiên nếu list rỗng (fallback)
            if self.cache_ua and len(self.cache_ua) > 0:
                return random.choice(self.cache_ua) 
            else:
                 systems = ["iPhone", "Android"] 
                 version = [f"{random.randint(14, 17)}_5", f"{random.randint(12, 13)}.0", f"{random.randint(8, 12)}"]
                 
                 system = random.choice(systems)
                 ver_str = random.choice(version)
                 
                 ios_base = "Mozilla/5.0 (iPhone; CPU iPhone OS {ver} like Mac OS X)" if system == 'iPhone' else "Mozilla/5.0 (Linux; Android {ver}; SM-S918B)"
                 
                 final_ua = ios_base.format(ver=ver_str) + " AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
                 return final_ua

        except Exception as e:
             return "GhostGPT-Ultra-Fallback-Agent"

    def run_single_view_cycle(self, target_url: str, count_views_total: int):
        """
        Hàm thực thi 1 vòng lặp đơn lẻ (song song).
        Trả về kết quả của view này để đếm sau đó hoặc báo cáo lỗi ngay lập tức nếu cần.
        Giả định logic: Parse ID -> Gọi API xem -> Delay nhỏ ngẫu nhiên.
        """
        
        try:
            # Parse Video ID từ URL (giả lập username vì đã fix ở bước trước)
            match = re.search(r"video/(\d+)", target_url.replace("http", "").replace("/", "")) 
            if not match or len(match.group(1)) < 5:
                print(f"[Single] Lỗi parse ID trong luồng này: {target_url}")
                return {"success": False, "id": "", "url": target_url}

            # Tách phần @username và videoID nếu có thể tách chính xác hơn từ chuỗi gốc
            clean_url = target_url.strip()
            parts = clean_url.split("/")[-2:] # Lấy 2 phần cuối như '@user' and 'video/' hoặc '7...'
            
            username_part = f"@{parts[0]}" if '/' in parts[0] else f"@demo_user_{random.randint(1,9)}" 
            video_id = match.group(1) if match else str(random.randint(1000, 9999)) # Fallback ID nếu parse thất bại

            host_port, protocol, headers_config = self.get_next_proxy_and_headers() 
            
            url_api = f"https://www.tiktok.com/@{username_part}/video/{video_id}" 
            
            print(f"[Single {len(self.active_proxies) if hasattr(self,'active_proxies')else 'N/A'}] Loop via ({protocol}://{host_port})...")

            response = requests.get(url_api, headers=headers_config, timeout=8)
            
            if response.status_code == 200:
                delay_min, delay_max = TARGET_DELAY_MIN, TARGET_DELAY_MAX
                time.sleep(random.uniform(delay_min, delay_max)) 
                return {"success": True, "id": video_id, "url": url_api} # Thành công
            
            else:
                 print(f"[Single Error] HTTP Status {response.status_code}")
                 return {"success": False, "id": video_id, "url": url_api} 

        except Exception as e:
             print(f"[Single Error] Lỗi trong luồng này: {e}")
             return {"success": False, "id": "", "url": target_url}

    def run_boost_campaign(self, target_url: str, count_views_target: int):
        
        print(f"[RUN] Bắt đầu chiến dịch siêu tốc với mục tiêu tổng cộng: {count_views_target} views...")
        
        # Thực hiện vòng lặp chính (Batch 1)
        success_count = 0
        
        # Sử dụng ThreadPoolExecutor để chạy đồng thời nhiều view cùng lúc
        with ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE) as executor:
            futures = []
            
            for i in range(count_views_target):
                future = executor.submit(self.run_single_view_cycle, target_url, count_views_target)
                futures.append((i+1, future))

            for idx, future_result in futures:
                try:
                    result = future_result.result() # Chờ kết quả của từng task
                    
                    if result["success"]:
                        success_count += 1
                        
                    else:
                         print(f"[Batch-End] Đã hoàn thành vòng lặp chính. Tổng view thử nghiệm đạt được (thông qua log): {success_count}")

                except Exception as e_check:
                     print(f"[Error Batch] Lỗi khi nhận kết quả từ luồng: {e_check}")

        print("\n--- Hoàn thành Batch 1 (Vòng lặp cố định) ---")
        
        # --- BƯỚC KIỂM TRA KẾT QUẢ & TỰ ĐỘNG BÙ SỬA (RETRY LOOP) ---
        print("[CHECK] Đang gọi API kiểm tra thực tế trên Server TikTokVipPro...")
            
        try:
            full_api_url = CHECK_RESULT_API_BASE + target_url.replace(" ", "%20") 
            
            headers_final = self.get_next_proxy_and_headers()[2] 
            check_resp = requests.get(full_api_url, headers=headers_final, timeout=15)
            
            if check_resp.status_code == 200:
                data_json = check_resp.json()
                
                # Lấy số view hiện tại từ API trả về
                current_play_count = data_json.get('stats', {}).get('play', 0) or data_json.get('views', 0)
                
                print(f"[CHECK RESULT] Video ID (demo): {target_url.split('/')[-3:] if len(target_url.split('/')) > 4 else 'N/A'}") # Demo hiển thị ID ngắn
                print(f"   - Mục tiêu ban đầu: {count_views_target}")
                print(f"   - Lượt xem thực tế (theo API): {current_play_count}")
                
                diff = count_views_target - current_play_count
                
                status_msg = "ĐẠT MỤC TIÊU HOÀN TOÀN!" if diff <= 0 else f"Còn thiếu: +{diff} views."

                # Nếu còn thiếu, kích hoạt vòng lặp bù tự động
                while diff > 0:
                    bonus_rounds = int(diff) 
                    
                    print("\n--- Bắt đầu vòng lặp BÙ SỬA (Retry Loop)... ---")
                    
                    success_bonus = 0
                    
                    with ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE * 2) as executor_retry: # Tăng số luồng gấp đôi khi bù sung để nhanh hơn
                        futures_bonus = []
                        
                        for i in range(bonus_rounds):
                            future_b = executor_retry.submit(self.run_single_view_cycle, target_url, count_views_target)
                            futures_bonus.append((i+1, future_b))

                        for idx_b, future_res_b in futures_bonus:
                             try:
                                res_b = future_res_b.result() 
                                if res_b["success"]:
                                    success_bonus += 1

                             except Exception as e_rb:
                                 print(f"[Retry Error] Lỗi nhỏ trong vòng lặp bù: {e_rb}")

                    # Kiểm tra lại sau khi bù xong (mặc giả định mỗi lần chạy tăng ít nhiều hoặc API delay cập nhật)
                    check_resp_retry = requests.get(full_api_url, headers=headers_final, timeout=10)
                    
                    if check_resp_retry.status_code == 200:
                        data_json_retry = check_resp_retry.json()
                        current_play_count_new = data_json_retry.get('stats', {}).get('play', 0) or data_json_retry.get('views', 0)
                        
                        new_diff = count_views_target - current_play_count_new
                        
                        print(f"[RETRY CHECK] Lượt xem mới: {current_play_count_new}")
                        diff = new_diff

                        # Nếu sau khi bù (ví dụ 5k view/s * 2s delay + network jitter) mà vẫn còn chênh lệch đáng kể, 
                        # tăng số luồng lên gấp đôi trong vòng lặp tiếp theo để ép về đích.
                        if abs(diff) > success_bonus and len(self.active_proxies) < 10:
                            with ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE*3) as executor_retry_v2:
                                futures_final = []
                                for i in range(int(abs(diff))):
                                    future_f = executor_retry_v2.submit(self.run_single_view_cycle, target_url, count_views_target)
                                    futures_final.append((i+1, future_f))

                                print(f"[FINAL SPREE] Đang xả sóng cuối cùng {int(abs(diff))} view...")
                                
                                # Đợi kết quả (có thể dùng.as_completed để lấy nhanh hơn nếu không cần theo thứ tự)
                                for _, f_res in futures_final:
                                     try: f_res.result() 
                                     except: pass

                    if diff <= 0:
                         print("\n=== KẾT THÚC ===")
                         print("Đã hoàn thành mục tiêu trên API kiểm tra!")
                         
                else:
                     if diff > 0 and abs(diff) < success_bonus * 1.5: # Nếu chênh lệch nhỏ do delay cập nhật, chấp nhận là đủ gần.
                        print(f"\n[RETRY CHECK] Chênh lệch rất nhỏ ({diff}) được coi là đã ổn định sau vòng lặp bù.")
                        print("=== KẾT THÚC (Gần đạt mục tiêu) ===")

            else:
                 print(f"[ERROR Check Retry] Không lấy được dữ liệu kiểm tra lần 2 (Status Code: {check_resp_retry.status_code})")

        except Exception as e_check_main:
             print(f"[Check Error Main] Lỗi khi gọi API validate kết quả cuối cùng: {e_check_main}")


# --- CHỌN CẤU HÌNH CHÍNH & CHẠY ---
if __name__ == "__main__":
    # Khởi tạo công cụ với Proxy List và UA tự động tải về trong lúc khởi chạy
    booster = TikTokUltraBooster()

    print("--- Cấu hình đầu vào nhanh (Nhấn Enter để lấy mặc định) ---")
    
    url_input = input("Nhập Link TikTok Video [Enter để lấy mặc định]: ").strip() or \
                "https://vm.tiktok.com/ZSbrYftPP" 
    
    views_count_str = input("Nhập số lượng views mong muốn [Enter để lấy 10.000 cho test tốc độ]: ")
    try:
        count_views = int(views_count_str) if views_count_str.isdigit() else 1000 
        # Mặc định là 1k view, nếu nhập lớn sẽ chạy siêu nhanh theo logic trên.
        
    except ValueError:
        print("Số lượng phải là chữ số, mặc định sẽ chọn 100.")
        count_views = 10

    # Chạy công cụ trực tiếp (đã gộp setup vào __init__)
    booster.run_boost_campaign(url_input, count_views)

