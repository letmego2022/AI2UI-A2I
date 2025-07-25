from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import os
from utils import generate_screenshot_name, ensure_dir
from ai_handler import call_ai
from global_operator import start_browser, get_operator, close_operator, is_browser_running, execute_in_browser_thread
import json
import traceback

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# 存储客户端SID的全局变量
client_sids = {}

@app.route('/')
def index():
    return render_template('index.html')

def start_browser_task(url, sid):
    """浏览器启动任务"""
    def emit_wrapper(event, data):
        try:
            socketio.emit(event, data, to=sid)
        except Exception as e:
            print(f"Emit error: {e}")
    
    try:
        success, message = start_browser(url)
        if success:
            emit_wrapper('browser_started', {'msg': message, 'url': url})
            
            # 获取初始截图
            operator = get_operator()
            if operator:
                screenshot_path = generate_screenshot_name("initial", suffix="_browser_start")
                operator.screenshot(screenshot_path)
                emit_wrapper('screenshot_update', {
                    'type': 'initial',
                    'img': screenshot_path,
                    'msg': '浏览器启动完成，初始页面截图'
                })
        else:
            emit_wrapper('browser_error', {'msg': message})
    except Exception as e:
        emit_wrapper('browser_error', {'msg': f'启动浏览器失败: {str(e)}'})

@socketio.on('start_browser')
def handle_start_browser(data):
    """启动浏览器"""
    # 保存客户端SID
    client_sids[request.sid] = request.sid
    
    url = data.get('url', '').strip()
    if not url:
        emit('browser_error', {'msg': 'URL不能为空'})
        return
    
    # 确保URL有协议
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    # 在浏览器线程中执行启动任务
    execute_in_browser_thread(start_browser_task, url, request.sid)

def run_task_logic(task_desc, sid):
    """任务执行逻辑 - 在浏览器线程中运行"""
    def emit_wrapper(event, data):
        try:
            socketio.emit(event, data, to=sid)
        except Exception as e:
            print(f"Emit error: {e}")

    if not task_desc:
        emit_wrapper('task_error', {'msg': '任务描述不能为空'})
        return

    emit_wrapper('task_start', {'msg': '开始执行任务...'})
    
    try:
        ensure_dir()
        operator = get_operator()
        if not operator:
            emit_wrapper('task_error', {'msg': '浏览器未启动'})
            return
            
        max_steps = 2
        messages = []

        for step_num in range(max_steps):
            emit_wrapper('step_start', {'step': step_num + 1})
            
            # 截图当前状态
            img_path = generate_screenshot_name(task_desc, suffix=f"_step{step_num+1}_input")
            operator.screenshot(img_path)
            
            emit_wrapper('screenshot_update', {
                'type': 'input',
                'step': step_num + 1,
                'img': img_path,
                'msg': f'步骤 {step_num + 1} 输入截图'
            })

            # 调用AI分析
            ai_result = call_ai(img_path, task_desc, messages)
            messages = [{
                "role": "assistant",
                "content": f"[步骤 {step_num + 1}] AI 返回：\n{ai_result}"
            }]

            if ai_result["status"] == "done":
                emit_wrapper('task_done', {'msg': '任务完成'})
                return

            elif ai_result["status"] == "action":
                actions = ai_result["data"]
                if isinstance(actions, list):
                    for substep_idx, action in enumerate(actions):
                        operator.execute_action(action)
                        sub_img_path = generate_screenshot_name(
                            task_desc, suffix=f"_step{step_num+1}_{substep_idx+1}"
                        )
                        operator.screenshot(sub_img_path)
                        emit_wrapper('screenshot_update', {
                            'type': 'action',
                            'step': step_num + 1,
                            'substep': substep_idx + 1,
                            'img': sub_img_path,
                            'msg': f'执行操作后截图'
                        })
                elif isinstance(actions, dict):
                    operator.execute_action(actions)
                    sub_img_path = generate_screenshot_name(
                        task_desc, suffix=f"_step{step_num+1}_1"
                    )
                    operator.screenshot(sub_img_path)
                    emit_wrapper('screenshot_update', {
                        'type': 'action',
                        'step': step_num + 1,
                        'substep': 1,
                        'img': sub_img_path,
                        'msg': f'执行操作后截图'
                    })
                else:
                    emit_wrapper('task_error', {'msg': '无法识别的操作数据格式'})
                    return

            elif ai_result["status"] == "error":
                emit_wrapper('task_error', {'msg': ai_result['error']})
                return

        else:
            emit_wrapper('task_warning', {'msg': '达到最大步骤数，任务可能未完成。'})

    except Exception as e:
        error_msg = f'执行出错: {str(e)}'
        print(f"Task error: {error_msg}\n{traceback.format_exc()}")
        emit_wrapper('task_error', {'msg': error_msg})

@socketio.on('run_task')
def handle_run_task(data):
    """执行AI任务"""
    # 保存客户端SID
    client_sids[request.sid] = request.sid
    
    task_desc = data.get('task')
    if not task_desc:
        emit('task_error', {'msg': '任务描述不能为空'})
        return

    # 检查浏览器是否运行
    if not is_browser_running():
        emit('task_error', {'msg': '请先启动浏览器'})
        return

    # 在浏览器线程中执行任务
    execute_in_browser_thread(run_task_logic, task_desc, request.sid)

# --- 在文件顶部，import 部分之后，添加一个用于关闭浏览器任务的辅助函数 ---

def close_browser_task(sid):
    """在浏览器线程中执行的实际关闭浏览器任务"""
    def emit_wrapper(event, data):
        try:
            # 使用 to=sid 确保消息发送给正确的客户端
            socketio.emit(event, data, to=sid)
        except Exception as e:
            # 使用 app logger 记录 emit 错误
            app.logger.error(f"Emit error in close_browser_task to SID {sid}: {e}")

    try:
        # 调用全局的 close_operator 函数，它会在线程安全的环境中操作 BrowserManager
        # 这会调用 browser_manager.close_operator()，从而安全地关闭 Playwright 资源
        close_operator()
        emit_wrapper('browser_closed', {'msg': '浏览器已关闭'})
        # 注意：在工作线程中无法直接修改主线程的 client_sids 字典
        # 我们将在主线程的 handle_close_browser 中处理这个清理
    except Exception as e:
        error_msg = f'关闭浏览器时出错: {str(e)}'
        app.logger.error(f"Error in close_browser_task: {error_msg}", exc_info=True) # 记录堆栈
        emit_wrapper('browser_error', {'msg': error_msg})


# --- 修改 handle_close_browser 函数 ---

@socketio.on('close_browser')
def handle_close_browser():
    """关闭浏览器 - 通过工作线程执行"""
    sid = request.sid
    try:
        # 1. 在主线程中，先清理客户端SID
        # 这样可以立即反映在UI状态上，即使关闭过程需要时间
        if sid in client_sids:
            del client_sids[sid]
            app.logger.info(f"Client SID {sid} removed from client_sids.")

        # 2. 调度实际的关闭任务到浏览器线程
        # 将 sid 传递给任务函数，以便它可以在完成后 emit 消息
        execute_in_browser_thread(close_browser_task, sid)
        
        # 注意：主线程在此处立即返回，不会等待工作线程完成
        # 关闭成功的确认将由 close_browser_task 通过 emit 发送
        
    except Exception as e:
        # 如果调度任务本身失败（虽然不太可能），也要通知客户端
        error_msg = f"调度关闭浏览器任务时出错: {str(e)}"
        app.logger.error(error_msg, exc_info=True)
        emit('browser_error', {'msg': error_msg}) # 通知发起关闭请求的客户端


@socketio.on('get_browser_status')
def handle_get_browser_status():
    """获取浏览器状态"""
    try:
        if is_browser_running():
            emit('browser_status', {'status': '浏览器运行中', 'type': 'success'})
        else:
            emit('browser_status', {'status': '浏览器未启动', 'type': 'secondary'})
    except Exception as e:
        emit('browser_status', {'status': f'状态检查失败: {str(e)}', 'type': 'danger'})

# 连接管理
@socketio.on('connect')
def handle_connect():
    print(f'客户端 {request.sid} 已连接')
    client_sids[request.sid] = request.sid
    handle_get_browser_status()

@socketio.on('disconnect')
def handle_disconnect():
    print(f'客户端 {request.sid} 已断开连接')
    if request.sid in client_sids:
        del client_sids[request.sid]

if __name__ == '__main__':
    try:
        socketio.run(app, debug=False, port=5088, host='0.0.0.0')
    except KeyboardInterrupt:
        print("正在关闭应用...")
        close_operator()
        from global_operator import stop_browser_thread
        stop_browser_thread()