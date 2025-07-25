import base64
import json
from zhipuai import ZhipuAI
from config import API_KEY, MODEL_NAME
import re

def extract_json_simple(text):
    """
    从文本中提取第一个 { 到最后一个 } 之间的内容，并尝试解析成 JSON。
    如果失败则返回 None。
    """
    start = text.find('[')
    end = text.rfind(']')
    if start != -1 and end != -1 and end > start:
        json_str = text[start:end + 1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None
    return None



def call_ai(img_path, task_desc, history_messages=None):
    with open(img_path, 'rb') as f:
        img_base64 = base64.b64encode(f.read()).decode('utf-8')
    prompt = f"""
你是一个专业的 UI 自动化测试助手。请根据提供的用户界面截图（分辨率为 1280x720），分析并推理出完成【当前目标】所需的所有操作步骤。

🎯 当前目标：{task_desc}

📐 图像说明：
- 当前截图分辨率固定为 1280x720。
- **禁止对图像进行裁剪、缩放或增强处理**，必须基于原始截图进行坐标分析。
- 所有坐标必须为 **归一化坐标**（x 和 y 值在 0~1 范围内，保留小数点后 4 位），确保多平台一致性。

🔁 请返回一个操作步骤的 JSON 数组，按顺序依次执行。支持的操作类型如下：

- `"click"`：点击指定位置
- `"double_click"`：双击指定位置
- `"right_click"`：右键点击
- `"hover"`：鼠标悬停
- `"type"`：点击输入框后输入文字
- `"press_key"`：按下键盘按键，如 Enter、Tab 等
- `"swipe"`：鼠标拖动（支持起点和终点）
- `"scroll_to"`：页面滚动到指定位置
- `"wait"`：等待指定时间（毫秒）

📦 各操作的参数格式如下：

```json
[
  {{
    "action": "click" | "double_click" | "right_click" | "hover",
    "coordinate": {{ "x": 0.1234, "y": 0.5678 }}
  }},
  {{
    "action": "type",
    "coordinate": {{ "x": 0.2345, "y": 0.6789 }},
    "text": "示例输入内容"
  }},
  {{
    "action": "press_key",
    "key": "Enter"
  }},
  {{
    "action": "swipe",
    "coordinate": {{ "x1": 0.1234, "y1": 0.5678, "x2": 0.4321, "y2": 0.8765 }}
  }},
  {{
    "action": "scroll_to",
    "coordinate": {{ "x": 0.0, "y": 0.9 }}
  }},
  {{
    "action": "wait",
    "duration": 1500
  }}
]
````

⚠️ 请严格返回上述格式的 **纯 JSON 数组**，不要添加注释、解释或任何非 JSON 内容。

✅ 如果判断当前目标「{task_desc}」已完成，无需执行任何操作，请仅返回字符串："目标完成"
"""

    # 构造对话 messages 列表
    messages = history_messages[:] if history_messages else []
    messages.append({
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}},
            {"type": "text", "text": prompt}
        ]
    })
    client = ZhipuAI(api_key=API_KEY)
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages
    )

    content = response.choices[0].message.content.strip()

    if "目标完成" in content:
        return {"status": "done"}
    try:
        action_data = extract_json_simple(content)
        print(content)
        # action_data = json.loads(content)
        return {"status": "action", "data": action_data}
    except json.JSONDecodeError:
        return {"status": "error", "error": "Invalid JSON returned by AI", "raw": content}
