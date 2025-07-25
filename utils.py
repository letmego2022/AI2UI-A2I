import uuid
import time
import os
import time
import hashlib

def generate_screenshot_name(task_desc, suffix=""):
    safe_name = hashlib.md5(task_desc.encode()).hexdigest()[:8]
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_name}_{timestamp}{suffix}.png"
    return os.path.join("static/screenshots", filename)

def ensure_dir(path="screenshots"):
    if not os.path.exists(path):
        os.makedirs(path)

def task_is_finished(latest_step_json):
    # 可扩展：AI 返回特定标记、或特定 UI 元素出现等
    return False
