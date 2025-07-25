from playwright.sync_api import sync_playwright
from config import TARGET_URL

class UIOperator:
    def __init__(self, target_url=TARGET_URL, headless=True):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        # 关键改动在这里：设置 viewport 和 device_scale_factor
        self.page = self.browser.new_page(
            viewport={"width": 1280, "height": 720},
            device_scale_factor=1  # 强制设置为 1
        )
        if target_url:
            self.page.goto(target_url)
            self.page.wait_for_timeout(1000)

    def navigate_to(self, url):
        """导航到指定URL"""
        if not url:
            raise ValueError("URL不能为空")
        self.page.goto(url)
        self.page.wait_for_timeout(1000)

    def screenshot(self, path):
        self.page.wait_for_load_state("networkidle")  # 等待网络静止
        self.page.wait_for_timeout(500)               # 额外等待动画结束
        self.page.screenshot(path=path, full_page=False)

    def highlight_point(self, x, y, duration=1500):
        js = f"""
        const dot = document.createElement("div");
        dot.style.cssText = `
            position: fixed;
            left: {x - 3}px;
            top: {y - 3}px;
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: red;
            z-index: 99999;
            pointer-events: none;
        `;

        const label = document.createElement("div");
        label.textContent = "({x},{y})";
        label.style.cssText = `
            position: fixed;
            left: {x + 8}px;
            top: {y - 6}px;
            font-size: 10px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 1px 4px;
            border-radius: 3px;
            z-index: 99999;
            pointer-events: none;
        `;

        document.body.append(dot);
        document.body.append(label);

        setTimeout(() => {{
            requestAnimationFrame(() => {{
                dot.remove();
                label.remove();
            }});
        }}, {duration});
        """
        self.page.evaluate(js)

    def norm_to_pixel(self, x_norm, y_norm):
        width, height = 1280, 720
        return int(x_norm * width), int(y_norm * height)
    
    def execute_action(self, action_json):
        if not isinstance(action_json, dict):
            print("[错误] execute_action 参数不是字典类型:", action_json)
            return

        action = action_json.get("action")
        coordinate = action_json.get("coordinate", {})

        def resolve_xy(coordinate_dict, keys=("x", "y")):
            x_norm = coordinate_dict.get(keys[0])
            y_norm = coordinate_dict.get(keys[1])
            if isinstance(x_norm, float) and isinstance(y_norm, float):
                return self.norm_to_pixel(x_norm, y_norm)
            return x_norm, y_norm  # 若非归一化，按原样处理

        try:
            if action == "click":
                if "x" in coordinate and "y" in coordinate:
                    x, y = resolve_xy(coordinate)
                elif "click" in coordinate:
                    x, y = resolve_xy(coordinate["click"])
                else:
                    print("[错误] click 操作缺少坐标:", coordinate)
                    return

                print(f"[操作] 点击坐标: ({x}, {y})")
                self.highlight_point(x, y)
                self.page.mouse.click(x, y)

            elif action == "type":
                if "x" in coordinate and "y" in coordinate:
                    x, y = resolve_xy(coordinate)
                elif "type" in coordinate:
                    x, y = resolve_xy(coordinate["type"])
                else:
                    print("[错误] type 操作缺少坐标:", coordinate)
                    return

                text = action_json.get("text", "")
                if not text:
                    print("[错误] type 操作缺少 text 字段")
                    return

                print(f"[操作] 输入坐标: ({x}, {y}), 文字: {text}")
                self.highlight_point(x, y)
                self.page.mouse.click(x, y)
                self.page.keyboard.type(text)

            elif action == "swipe":
                if all(k in coordinate for k in ("x1", "y1", "x2", "y2")):
                    x1, y1 = resolve_xy(coordinate, ("x1", "y1"))
                    x2, y2 = resolve_xy(coordinate, ("x2", "y2"))
                elif "swipe" in coordinate:
                    swipe = coordinate["swipe"]
                    x1, y1 = resolve_xy(swipe, ("x1", "y1"))
                    x2, y2 = resolve_xy(swipe, ("x2", "y2"))
                else:
                    print("[错误] swipe 操作缺少完整坐标:", coordinate)
                    return

                print(f"[操作] 滑动坐标: ({x1}, {y1}) -> ({x2}, {y2})")
                self.highlight_point(x1, y1)
                self.page.mouse.move(x1, y1)
                self.page.mouse.down()
                self.page.wait_for_timeout(100)
                drag_steps = max(5, min(50, int(500 / 20)))
                print(f"[调试] 拖拽将使用 {drag_steps} 个步骤")
                self.page.mouse.move(x2, y2, steps=drag_steps)
                self.page.wait_for_timeout(100)
                self.page.mouse.up()

            elif action == "hover":
                x, y = resolve_xy(coordinate)
                print(f"[操作] 鼠标悬停坐标: ({x}, {y})")
                self.highlight_point(x, y)
                self.page.mouse.move(x, y)

            elif action == "double_click":
                x, y = resolve_xy(coordinate)
                print(f"[操作] 双击坐标: ({x}, {y})")
                self.highlight_point(x, y)
                self.page.mouse.dblclick(x, y)

            elif action == "right_click":
                x, y = resolve_xy(coordinate)
                print(f"[操作] 右键点击坐标: ({x}, {y})")
                self.highlight_point(x, y)
                self.page.mouse.click(x, y, button="right")

            elif action == "press_key":
                key = action_json.get("key")
                if not key:
                    print("[错误] press_key 操作缺少 key 字段")
                    return
                print(f"[操作] 按键: {key}")
                self.page.keyboard.press(key)

            elif action == "wait":
                duration = action_json.get("duration", 1000)
                print(f"[操作] 等待 {duration} 毫秒")
                self.page.wait_for_timeout(duration)

            elif action == "scroll_to":
                x, y = resolve_xy(coordinate)
                print(f"[操作] 页面滚动到: ({x}, {y})")
                js_scroll = f"window.scrollTo({x}, {y});"
                self.page.evaluate(js_scroll)

            else:
                print(f"[错误] 未知 action 类型: {action}")
                return

            self.page.wait_for_timeout(1200)

        except Exception as e:
            print("[异常] 执行操作时出错:", e)

    def close(self):
        self.browser.close()
        self.playwright.stop()