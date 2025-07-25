# global_operator.py (优化后完整代码)
from ui_operator import UIOperator
import threading
import queue
import time
import logging

# --- 配置日志 ---
# 设置日志级别为 INFO，格式包含时间、级别和消息
# 你可以根据需要调整级别（如 DEBUG 获取更详细信息）或格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
# --- 配置日志结束 ---


class BrowserManager:
    def __init__(self):
        self.operator = None
        # 使用 RLock 以增强安全性，允许同一线程多次获取锁
        self.lock = threading.RLock()
        self.current_url = None

    def start_browser(self, url):
        """启动浏览器并访问指定URL"""
        logger.info(f"Attempting to start browser for URL: {url}")
        with self.lock:
            # 确保在创建新实例前，旧实例已被尽可能关闭和清理
            self._internal_close() # 调用内部健壮的关闭方法
            try:
                # 创建新的浏览器实例
                # 注意：传递 target_url=None, 然后调用 navigate_to(url) 是合理的
                # 如果 UIOperator 构造函数可以直接接受 URL 并导航，也可以考虑直接传入
                self.operator = UIOperator(target_url=None, headless=True)
                logger.debug("UIOperator instance created.")
                self.operator.navigate_to(url)
                logger.debug(f"Navigated to {url}")
                self.current_url = url
                logger.info("Browser started successfully.")
                return True, "浏览器启动成功"
            except Exception as e:
                # 记录详细错误
                error_msg = f"启动浏览器失败: {str(e)}"
                logger.error(error_msg, exc_info=True) # exc_info=True 记录堆栈跟踪
                # 确保失败时清理状态
                self._internal_close() # 再次尝试清理，确保状态干净
                return False, error_msg

    def get_operator(self):
        """获取当前浏览器操作器"""
        with self.lock:
            logger.debug(f"get_operator called. Operator exists: {self.operator is not None}")
            return self.operator

    def _internal_close(self):
        """内部方法：健壮地关闭浏览器并清理状态。
           此方法应在已持有 self.lock 的情况下被调用。
        """
        logger.debug("Internal close initiated.")
        if self.operator:
            try:
                logger.debug("Attempting to close UIOperator...")
                # 尝试正常关闭
                self.operator.close()
                logger.debug("UIOperator closed successfully (or close() returned).")
            except Exception as e:
                # 捕获所有异常，记录但不中断流程，确保状态被清理
                logger.warning(f"Exception occurred during operator.close(): {e}", exc_info=True)
                # 如果问题持续，需要检查 UIOperator 的具体实现，
                # 看是否需要更细致的资源清理（如 page, context）。
            finally:
                # *** 关键点：无论 close() 成功与否，都必须清理引用 ***
                self.operator = None
                self.current_url = None
                logger.debug("Operator reference and current_url cleared.")
        else:
            logger.debug("No operator to close.")

    def close_operator(self):
        """关闭浏览器"""
        logger.info("Close operator requested.")
        with self.lock:
            # 调用内部健壮的关闭方法
            self._internal_close()
        logger.info("Close operator completed.")

    def is_browser_running(self):
        """检查浏览器是否正在运行"""
        with self.lock:
            # 简单检查 operator 实例是否存在
            running = self.operator is not None
            logger.debug(f"Is browser running? {running}")
            return running


# 全局浏览器管理器
browser_manager = BrowserManager()

# 全局任务队列和工作线程
task_queue = queue.Queue()
browser_thread = None  # 显式初始化为 None
browser_thread_running = False


def browser_worker():
    """浏览器操作工作线程"""
    global browser_thread_running
    logger.info("Browser worker thread started.")
    while browser_thread_running:
        try:
            # 使用 timeout 避免无限期阻塞，以便能响应 browser_thread_running 状态变化
            task = task_queue.get(timeout=1)
            if task is None:  # 停止信号
                logger.info("Stop signal received in browser worker.")
                task_queue.task_done()
                break
            func, args, kwargs, callback = task
            try:
                logger.debug(f"Executing task: {func.__name__ if hasattr(func, '__name__') else 'lambda/anonymous'}")
                result = func(*args, **kwargs)
                if callback:
                    logger.debug("Calling success callback.")
                    callback(result, None)
            except Exception as e:
                logger.error(f"Error executing task: {e}", exc_info=True)
                if callback:
                    logger.debug("Calling error callback.")
                    callback(None, e)
            finally:
                task_queue.task_done()
                logger.debug("Task done.")
        except queue.Empty:
            # 队列超时，继续循环检查 browser_thread_running
            continue
        except Exception as e:
            logger.critical(f"Unexpected error in browser worker thread: {e}", exc_info=True)
            try:
                task_queue.task_done()
            except ValueError:
                # task_done() called too many times, ignore
                pass
    logger.info("Browser worker thread stopped.")


def start_browser_thread():
    """启动浏览器工作线程"""
    global browser_thread, browser_thread_running
    # *** 关键修复 ***
    # 检查线程是否真的可以启动：
    # 1. 标志位为 False
    # 2. 线程引用为 None (从未启动或已清理)
    # 3. 线程引用不为 None 但线程已死 (异常退出)
    # 只要满足以上任一条件，就认为需要/可以启动新线程
    if not browser_thread_running or browser_thread is None or not browser_thread.is_alive():
        logger.info("Starting browser worker thread.")
        browser_thread_running = True
        # 总是创建一个新的 Thread 对象，确保状态干净
        browser_thread = threading.Thread(target=browser_worker, daemon=True)
        browser_thread.start()
        logger.debug(f"New browser thread started. Thread ID: {browser_thread.ident}")
    else:
        logger.debug("Browser worker thread is already running.")


def stop_browser_thread():
    """停止浏览器工作线程"""
    global browser_thread, browser_thread_running
    if browser_thread_running:
        logger.info("Stopping browser worker thread.")
        browser_thread_running = False
        task_queue.put(None)  # 发送停止信号
        if browser_thread:
            logger.debug(f"Joining browser thread (ID: {browser_thread.ident})...")
            browser_thread.join(timeout=5) # 等待线程结束，最多等待5秒
            if browser_thread.is_alive():
                logger.warning("Browser worker thread did not stop gracefully within timeout.")
            else:
                logger.info("Browser worker thread joined successfully.")
            # *** 关键修复点：清理线程引用 ***
            # 这是允许 start_browser_thread 在下次需要时创建一个全新线程的关键
            browser_thread = None
            logger.debug("Browser thread reference cleared.")
    else:
        logger.debug("Browser worker thread was not running or already stopped.")


def execute_in_browser_thread(func, *args, callback=None, **kwargs):
    """在浏览器线程中执行任务"""
    logger.debug(f"execute_in_browser_thread called for function: {getattr(func, '__name__', 'unknown')}")
    # 确保浏览器线程正在运行
    start_browser_thread() # 这个函数现在能正确处理重启
    # 将任务放入队列
    task_queue.put((func, args, kwargs, callback))
    logger.debug("Task put into queue.")


# --- 全局函数接口 ---
# 这些函数是外部调用的主要入口，它们内部会调用 browser_manager 的方法

def start_browser(url):
    """全局函数接口：启动浏览器"""
    logger.info(f"Global start_browser() called with URL: {url}")
    return browser_manager.start_browser(url)


def get_operator():
    """全局函数接口：获取浏览器操作器"""
    # logger.debug("Global get_operator() called.") # 调用频繁，可按需开启
    return browser_manager.get_operator()


def close_operator():
    """全局函数接口：关闭浏览器"""
    logger.info("Global close_operator() called.")
    browser_manager.close_operator()


def is_browser_running():
    """全局函数接口：检查浏览器是否运行"""
    # logger.debug("Global is_browser_running() called.") # 调用频繁，可按需开启
    return browser_manager.is_browser_running()

# --- 全局函数接口结束 ---
