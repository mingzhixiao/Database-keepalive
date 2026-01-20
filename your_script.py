import os
import time
from playwright.sync_api import sync_playwright

def run_auto_login_and_jump():
    # ================= 配置区域 =================
    # 1. 登录页面地址
    LOGIN_URL = "https://qinglong2.wzw77.top/"
    
    
    # 3. 账号信息
    USERNAME = os.getenv("MY_USERNAME")
    PASSWORD = os.getenv("MY_PASSWORD")
    
    # 4. 元素定位
    SELECTOR_USER = "input[id='username']"
    SELECTOR_PASS = "input[id='password']"
    
    # 5. 截图保存路径
    SCREENSHOT_PATH = "target_page_result.png"
    # ===========================================

    with sync_playwright() as p:
        print(">>> 正在启动浏览器...")
        # 调试模式 (headless=False)，正式运行时可改为 True
        browser = p.chromium.launch(headless=True, slow_mo=500) 
        
        # 创建上下文 (这会自动管理 Cookies)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            # --- 第一步：执行登录 ---
            print(f">>> [1/3] 正在访问登录页: {LOGIN_URL}")
            page.goto(LOGIN_URL)
            page.wait_for_load_state("networkidle")

            print(">>> 输入账号密码...")
            page.wait_for_selector(SELECTOR_USER, state="visible")
            page.fill(SELECTOR_USER, USERNAME)
            page.fill(SELECTOR_PASS, PASSWORD)

            print(">>> 提交登录...")
            # 使用回车键登录 (这是最稳妥的，避开找不到按钮的问题)
            page.focus(SELECTOR_PASS)
            try:
                # 等待登录跳转
                with page.expect_navigation(timeout=10000):
                    page.keyboard.press("Enter")
            except Exception as e:
                print(f"提示: 登录跳转检测超时 (如果已登录可忽略): {e}")

            # 登录后的缓冲，确保 Cookie 已写入
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000) 
            # 硬等待: 再多等3秒，确保一些动画或图表完全画好
            page.wait_for_timeout(3000) 

            # --- 第三步：截图 ---
            print(f">>> [3/3] 正在截图保存至: {SCREENSHOT_PATH}")
            # full_page=True 表示截取整个长网页
            page.screenshot(path=SCREENSHOT_PATH, full_page=True)
            
            print(f">>> ✅ 任务全部完成！截图已保存。")

        except Exception as e:
            print(f">>> ❌ 发生错误: {e}")
            # 如果出错，截取当前画面看看到底停在哪里了
            page.screenshot(path="error_debug.png")
            print(">>> 已保存错误截图: error_debug.png")
            
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    run_auto_login_and_jump()
