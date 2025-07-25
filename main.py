from utils import generate_screenshot_name, ensure_dir
from ai_handler import call_ai
from ui_operator import UIOperator
import os

def main(task_desc):
    ensure_dir()
    operator = UIOperator()
    max_steps = 6
    messages = []  # 用于记录与 AI 的对话上下文

    for step_num in range(max_steps):
        # 初始截图用于 AI 判断
        img_path = generate_screenshot_name(task_desc, suffix=f"_step{step_num+1}_input")
        operator.screenshot(img_path)
        print(f"[步骤 {step_num + 1}] 已截图：{img_path}")

        ai_result = call_ai(img_path, task_desc, messages)
        print(f"[步骤 {step_num + 1}] AI 返回：\n{ai_result}")
        messages = [{
            "role": "assistant",
            "content": f"[步骤 {step_num + 1}] AI 返回：\n{ai_result}"
        }]

        if ai_result["status"] == "done":
            print(f"✅ 任务完成：{task_desc}")
            break

        elif ai_result["status"] == "action":
            actions = ai_result["data"]
            if isinstance(actions, list):
                for substep_idx, action in enumerate(actions):
                    print(f"👉 执行第 {substep_idx+1} 子步骤操作：{action}")
                    operator.execute_action(action)

                    # 对每个子步骤后截图
                    sub_img_path = generate_screenshot_name(
                        task_desc, suffix=f"_step{step_num+1}_{substep_idx+1}"
                    )
                    operator.screenshot(sub_img_path)
                    print(f"📸 已保存操作后截图：{sub_img_path}")

            elif isinstance(actions, dict):
                operator.execute_action(actions)
                sub_img_path = generate_screenshot_name(
                    task_desc, suffix=f"_step{step_num+1}_1"
                )
                operator.screenshot(sub_img_path)
                print(f"📸 已保存操作后截图：{sub_img_path}")

            else:
                print("[错误] 无法识别的操作数据格式：", actions)
                break

        elif ai_result["status"] == "error":
            print(f"❌ AI 解析失败：{ai_result['error']}")
            print(f"🔎 原始返回内容：{ai_result['raw']}")
            break

    else:
        print("⚠️ 已达到最大步骤数，任务可能未完成。")

    operator.close()

if __name__ == "__main__":
    main("使用 Lewis1:Lewis123! 登录")
