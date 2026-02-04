#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 Jarvis AI Agent - 自动化引擎
 版本: 1.0.0
 功能: 提供文件操作、应用程序控制、网页操作等自动化能力
"""

import os
import sys
import time
import json
import logging
import shutil
import threading
import subprocess
from typing import Dict, List, Optional, Any, Tuple, Callable
from pathlib import Path
from datetime import datetime
import aiohttp
import asyncio
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)


class FileOperations:
    """文件操作管理器"""
    
    def __init__(self, default_download_path: str = "~/Downloads"):
        """
        初始化文件操作管理器
        
        Args:
            default_download_path: 默认下载路径
        """
        self.download_path = os.path.expanduser(default_download_path)
        self.ensure_directory(self.download_path)
    
    def ensure_directory(self, path: str):
        """确保目录存在"""
        Path(path).mkdir(parents=True, exist_ok=True)
    
    def download_file(
        self, 
        url: str, 
        save_path: str = None,
        filename: str = None
    ) -> str:
        """
        下载文件
        
        Args:
            url: 文件URL
            save_path: 保存路径
            filename: 文件名
            
        Returns:
            下载的文件路径
        """
        save_path = save_path or self.download_path
        self.ensure_directory(save_path)
        
        try:
            # 获取文件名
            if not filename:
                filename = self._extract_filename(url)
            
            filepath = os.path.join(save_path, filename)
            
            # 下载文件
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            filepath = loop.run_until_complete(
                self._async_download_file(url, filepath)
            )
            loop.close()
            
            logger.info(f"文件已下载: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"文件下载失败: {e}")
            raise
    
    async def _async_download_file(self, url: str, filepath: str) -> str:
        """
        异步下载文件
        
        Args:
            url: 文件URL
            filepath: 保存路径
            
        Returns:
            下载的文件路径
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    with open(filepath, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                    return filepath
                else:
                    raise Exception(f"下载失败: HTTP {response.status}")
    
    def _extract_filename(self, url: str) -> str:
        """从URL提取文件名"""
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        
        if not filename or filename == '':
            filename = f"download_{int(time.time())}"
        
        return filename
    
    def organize_files(
        self, 
        source_dir: str, 
        target_dir: str,
        classification: Dict = None
    ):
        """
        整理文件
        
        Args:
            source_dir: 源目录
            target_dir: 目标目录
            classification: 分类规则
        """
        source_dir = os.path.expanduser(source_dir)
        target_dir = os.path.expanduser(target_dir)
        
        self.ensure_directory(target_dir)
        
        try:
            # 获取源目录所有文件
            files = self._get_files(source_dir)
            
            # 根据分类规则整理
            for file_path in files:
                category = self._determine_category(file_path, classification)
                if category:
                    self._move_file(file_path, target_dir, category)
            
            logger.info(f"文件整理完成: {source_dir} -> {target_dir}")
            
        except Exception as e:
            logger.error(f"文件整理失败: {e}")
            raise
    
    def _get_files(self, directory: str) -> List[str]:
        """获取目录下所有文件"""
        files = []
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(root, filename)
                files.append(filepath)
        return files
    
    def _determine_category(
        self, 
        file_path: str, 
        classification: Dict = None
    ) -> Optional[str]:
        """
        确定文件分类
        
        Args:
            file_path: 文件路径
            classification: 分类规则
            
        Returns:
            分类名称
        """
        ext = Path(file_path).suffix.lower()
        
        # 默认分类规则
        default_categories = {
            '.pdf': 'Documents',
            '.doc': 'Documents',
            '.docx': 'Documents',
            '.txt': 'Documents',
            '.md': 'Documents',
            '.jpg': 'Images',
            '.jpeg': 'Images',
            '.png': 'Images',
            '.gif': 'Images',
            '.mp4': 'Videos',
            '.avi': 'Videos',
            '.mov': 'Videos',
            '.mp3': 'Audio',
            '.wav': 'Audio',
            '.py': 'Code',
            '.js': 'Code',
            '.html': 'Code',
            '.css': 'Code',
            '.zip': 'Archives',
            '.rar': 'Archives',
            '.tar': 'Archives'
        }
        
        if classification and 'custom_rules' in classification:
            # 使用自定义规则
            for rule in classification['custom_rules']:
                if rule.get('extension') == ext:
                    return rule.get('category')
        
        return default_categories.get(ext, 'Others')
    
    def _move_file(self, file_path: str, target_dir: str, category: str):
        """
        移动文件到分类目录
        
        Args:
            file_path: 源文件路径
            target_dir: 目标目录
            category: 分类名称
        """
        category_dir = os.path.join(target_dir, category)
        self.ensure_directory(category_dir)
        
        filename = os.path.basename(file_path)
        new_path = os.path.join(category_dir, filename)
        
        # 如果文件已存在，添加序号
        if os.path.exists(new_path):
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(new_path):
                new_filename = f"{base}_{counter}{ext}"
                new_path = os.path.join(category_dir, new_filename)
                counter += 1
        
        shutil.move(file_path, new_path)
    
    def rename_file(self, file_path: str, new_name: str) -> str:
        """
        重命名文件
        
        Args:
            file_path: 原始文件路径
            new_name: 新名称
            
        Returns:
            新文件路径
        """
        directory = os.path.dirname(file_path)
        new_path = os.path.join(directory, new_name)
        
        os.rename(file_path, new_path)
        
        logger.info(f"文件已重命名: {file_path} -> {new_path}")
        return new_path
    
    def create_backup(self, file_path: str) -> str:
        """
        创建文件备份
        
        Args:
            file_path: 文件路径
            
        Returns:
            备份文件路径
        """
        if os.path.exists(file_path):
            backup_path = f"{file_path}.backup_{int(time.time())}"
            shutil.copy2(file_path, backup_path)
            logger.info(f"备份已创建: {backup_path}")
            return backup_path
        return None
    
    def delete_file(self, file_path: str):
        """
        删除文件
        
        Args:
            file_path: 文件路径
        """
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"文件已删除: {file_path}")
    
    def search_files(
        self, 
        directory: str, 
        pattern: str = "*",
        recursive: bool = True
    ) -> List[str]:
        """
        搜索文件
        
        Args:
            directory: 搜索目录
            pattern: 文件名模式
            recursive: 是否递归搜索
            
        Returns:
            匹配的文件列表
        """
        directory = os.path.expanduser(directory)
        
        if recursive:
            files = Path(directory).rglob(pattern)
        else:
            files = Path(directory).glob(pattern)
        
        return [str(f) for f in files if f.is_file()]


class ApplicationController:
    """应用程序控制器"""
    
    def __init__(self):
        """初始化应用程序控制器"""
        self.running_apps: Dict[str, Dict] = {}
    
    def open_application(self, app_name: str) -> bool:
        """
        打开应用程序
        
        Args:
            app_name: 应用程序名称
            
        Returns:
            是否成功
        """
        try:
            # 使用AppleScript打开应用
            script = f'tell application "{app_name}" to activate'
            subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                check=True
            )
            
            logger.info(f"已打开应用: {app_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"打开应用失败: {app_name}, {e}")
            return False
    
    def close_application(self, app_name: str) -> bool:
        """
        关闭应用程序
        
        Args:
            app_name: 应用程序名称
            
        Returns:
            是否成功
        """
        try:
            script = f'tell application "{app_name}" to quit'
            subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                check=True
            )
            
            logger.info(f"已关闭应用: {app_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"关闭应用失败: {app_name}, {e}")
            return False
    
    def is_app_running(self, app_name: str) -> bool:
        """
        检查应用是否正在运行
        
        Args:
            app_name: 应用程序名称
            
        Returns:
            是否正在运行
        """
        try:
            script = f'tell application "System Events" to (name of processes) contains "{app_name}"'
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True
            )
            
            return result.stdout.strip().lower() == 'true'
            
        except Exception as e:
            logger.error(f"检查应用状态失败: {app_name}, {e}")
            return False
    
    def get_running_apps(self) -> List[str]:
        """获取正在运行的应用列表"""
        try:
            script = 'tell application "System Events" to name of every process'
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True
            )
            
            apps = result.stdout.strip().split(', ')
            return [app for app in apps if app]
            
        except Exception as e:
            logger.error(f"获取运行应用列表失败: {e}")
            return []
    
    def send_keystrokes(self, keys: str):
        """
        发送按键
        
        Args:
            keys: 按键字符串
        """
        try:
            # 使用AppleScript发送按键
            script = f'tell application "System Events" to keystroke "{keys}"'
            subprocess.run(
                ['osascript', '-e', script],
                capture_output=True
            )
            
            logger.info(f"已发送按键: {keys}")
            
        except Exception as e:
            logger.error(f"发送按键失败: {e}")
    
    def press_special_key(self, key: str):
        """
        按下特殊键
        
        Args:
            key: 键名（如 'return', 'escape', 'delete' 等）
        """
        try:
            script = f'tell application "System Events" to key code {self._get_key_code(key)}'
            subprocess.run(
                ['osascript', '-e', script],
                capture_output=True
            )
            
            logger.info(f"已按下特殊键: {key}")
            
        except Exception as e:
            logger.error(f"按键失败: {e}")
    
    def _get_key_code(self, key: str) -> int:
        """获取键码"""
        key_codes = {
            'return': 36,
            'escape': 53,
            'delete': 51,
            'backspace': 117,
            'tab': 48,
            'space': 49,
            'up': 126,
            'down': 125,
            'left': 123,
            'right': 124,
            'home': 115,
            'end': 119,
            'page_up': 116,
            'page_down': 121
        }
        return key_codes.get(key.lower(), 36)
    
    def execute_menu_command(
        self, 
        app_name: str, 
        menu_path: List[str]
    ) -> bool:
        """
        执行菜单命令
        
        Args:
            app_name: 应用程序名称
            menu_path: 菜单路径（如 ['File', 'Save']）
            
        Returns:
            是否成功
        """
        try:
            # 构建AppleScript
            script = f'''
            tell application "System Events"
                tell process "{app_name}"
                    click menu item "{menu_path[-1]}" of menu 1 of menu bar item "{menu_path[0]}" of menu bar 1
                end tell
            end tell
            '''
            
            subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                check=True
            )
            
            logger.info(f"已执行菜单命令: {' -> '.join(menu_path)}")
            return True
            
        except Exception as e:
            logger.error(f"执行菜单命令失败: {e}")
            return False


class WebAutomation:
    """网页自动化控制器"""
    
    def __init__(self):
        """初始化网页自动化"""
        pass
    
    async def open_url(self, url: str) -> bool:
        """
        打开URL
        
        Args:
            url: 网址
            
        Returns:
            是否成功
        """
        try:
            subprocess.run(
                ['open', url],
                capture_output=True,
                check=True
            )
            
            logger.info(f"已打开网址: {url}")
            return True
            
        except Exception as e:
            logger.error(f"打开网址失败: {url}, {e}")
            return False
    
    async def search_web(self, query: str, engine: str = "google") -> str:
        """
        网页搜索
        
        Args:
            query: 搜索查询
            engine: 搜索引擎
            
        Returns:
            搜索结果页面URL
        """
        from urllib.parse import quote
        
        engines = {
            'google': 'https://www.google.com/search?q=',
            'bing': 'https://www.bing.com/search?q=',
            'baidu': 'https://www.baidu.com/s?wd=',
            'duckduckgo': 'https://duckduckgo.com/?q='
        }
        
        search_url = engines.get(engine, engines['google'])
        encoded_query = quote(str(query))
        url = f"{search_url}{encoded_query}"
        
        await self.open_url(url)
        
        logger.info(f"已搜索: {query}")
        return url
    
    async def extract_page_content(self, url: str) -> str:
        """
        提取网页内容
        
        Args:
            url: 网址
            
        Returns:
            网页文本内容
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        # 提取纯文本
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(html, 'html.parser')
                        text = soup.get_text(separator=' ', strip=True)
                        return text[:5000]  # 限制长度
                    
            return ""
            
        except Exception as e:
            logger.error(f"提取网页内容失败: {url}, {e}")
            return ""
    
    async def download_file_from_url(
        self, 
        url: str, 
        save_path: str = "~/Downloads"
    ) -> str:
        """
        从URL下载文件
        
        Args:
            url: 文件URL
            save_path: 保存路径
            
        Returns:
            下载的文件路径
        """
        file_ops = FileOperations(save_path)
        return file_ops.download_file(url, save_path)


class AutomationEngine:
    """
    自动化引擎主类
    整合所有自动化功能
    """
    
    def __init__(
        self, 
        download_path: str = "~/Downloads",
        screenshot_path: str = "/tmp/jarvis_screenshots"
    ):
        """
        初始化自动化引擎
        
        Args:
            download_path: 默认下载路径
            screenshot_path: 截图保存路径
        """
        # 初始化各个子系统
        self.file_operations = FileOperations(download_path)
        self.app_controller = ApplicationController()
        self.web_automation = WebAutomation()
        
        # 设置截图路径
        self.screenshot_path = screenshot_path
        Path(screenshot_path).mkdir(parents=True, exist_ok=True)
        
        # 任务队列
        self.task_queue: List[Dict] = []
        self.task_lock = threading.Lock()
        
        # 启动任务处理线程
        self._start_task_processor()
    
    def _start_task_processor(self):
        """启动任务处理线程"""
        def process_tasks():
            while True:
                try:
                    if self.task_queue:
                        task = self.task_queue.pop(0)
                        self._execute_task(task)
                    time.sleep(0.5)
                except Exception as e:
                    logger.error(f"任务处理错误: {e}")
                    time.sleep(1)
        
        thread = threading.Thread(target=process_tasks, daemon=True)
        thread.start()
    
    def _execute_task(self, task: Dict):
        """
        执行任务
        
        Args:
            task: 任务描述
        """
        task_type = task.get('type', 'general')
        
        try:
            if task_type == 'download':
                self._task_download(task)
            elif task_type == 'organize':
                self._task_organize(task)
            elif task_type == 'open_app':
                self._task_open_app(task)
            elif task_type == 'close_app':
                self._task_close_app(task)
            elif task_type == 'web_search':
                self._task_web_search(task)
            elif task_type == 'keystrokes':
                self._task_keystrokes(task)
            else:
                logger.warning(f"未知任务类型: {task_type}")
                
        except Exception as e:
            logger.error(f"任务执行失败: {e}")
    
    def _task_download(self, task: Dict):
        """任务：下载文件"""
        url = task.get('url', '')
        save_path = task.get('save_path', '~/Downloads')
        filename = task.get('filename', None)
        
        result = self.file_operations.download_file(url, save_path, filename)
        logger.info(f"下载任务完成: {url} -> {result}")
    
    def _task_organize(self, task: Dict):
        """任务：整理文件"""
        source = task.get('source', '')
        target = task.get('target', '')
        classification =', None)
        
        self.file_operations.organize task.get('classification_files(source, target, classification)
        logger.info(f"整理任务完成: {source} -> {target}")
    
    def _task_open_app(self, task: Dict):
        """任务：打开应用"""
        app_name = task.get('app', '')
        self.app_controller.open_application(app_name)
        logger.info(f"打开应用任务完成: {app_name}")
    
    def _task_close_app(self, task: Dict):
        """任务：关闭应用"""
        app_name = task.get('app', '')
        self.app_controller.close_application(app_name)
        logger.info(f"关闭应用任务完成: {app_name}")
    
    def _task_web_search(self, task: Dict):
        """任务：网页搜索"""
        query = task.get('query', '')
        engine = task.get('engine', 'google')
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            self.web_automation.search_web(query, engine)
        )
        loop.close()
        
        logger.info(f"搜索任务完成: {query}")
    
    def _task_keystrokes(self, task: Dict):
        """任务：发送按键"""
        keys = task.get('keys', '')
        self.app_controller.send_keystrokes(keys)
        logger.info(f"按键任务完成: {keys}")
    
    # 公开接口
    
    def download_file(
        self, 
        url: str, 
        save_path: str = None,
        filename: str = None
    ) -> str:
        """
        下载文件
        
        Args:
            url: 文件URL
            save_path: 保存路径
            filename: 文件名
            
        Returns:
            下载的文件路径
        """
        return self.file_operations.download_file(url, save_path, filename)
    
    def organize_files(
        self, 
        source_dir: str, 
        target_dir: str,
        classification: Dict = None
    ):
        """
        整理文件
        
        Args:
            source_dir: 源目录
            target_dir: 目标目录
            classification: 分类规则
        """
        self.file_operations.organize_files(source_dir, target_dir, classification)
    
    def control_application(
        self, 
        app_name: str, 
        action: str,
        params: Dict = None
    ) -> bool:
        """
        控制应用程序
        
        Args:
            app_name: 应用名称
            action: 操作（open, close, keystrokes, menu）
            params: 额外参数
            
        Returns:
            是否成功
        """
        if action == 'open':
            return self.app_controller.open_application(app_name)
        elif action == 'close':
            return self.app_controller.close_application(app_name)
        elif action == 'keystrokes':
            keys = params.get('keys', '')
            self.app_controller.send_keystrokes(keys)
            return True
        elif action == 'menu':
            menu_path = params.get('menu_path', [])
            return self.app_controller.execute_menu_command(app_name, menu_path)
        
        return False
    
    def handle_web_operation(
        self, 
        url: str, 
        action: str,
        params: Dict = None
    ) -> bool:
        """
        处理网页操作
        
        Args:
            url: 网址
            action: 操作（open, search, download）
            params: 额外参数
            
        Returns:
            是否成功
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            if action == 'open':
                result = loop.run_until_complete(
                    self.web_automation.open_url(url)
                )
            elif action == 'search':
                query = params.get('query', url)
                engine = params.get('engine', 'google')
                result = loop.run_until_complete(
                    self.web_automation.search_web(query, engine)
                )
            elif action == 'download':
                save_path = params.get('save_path', '~/Downloads')
                result = loop.run_until_complete(
                    self.web_automation.download_file_from_url(url, save_path)
                )
            else:
                result = False
                
        finally:
            loop.close()
        
        return result
    
    def type_text(self, text: str):
        """
        输入文本
        
        Args:
            text: 要输入的文本
        """
        try:
            # 逐字符输入，避免过快
            for char in text:
                self.app_controller.send_keystrokes(char)
                time.sleep(0.01)
                
        except Exception as e:
            logger.error(f"文本输入失败: {e}")
    
    def click(self, coordinates: Tuple[int, int]):
        """
        点击坐标
        
        Args:
            coordinates: (x, y) 坐标
        """
        try:
            import pyautogui
            x, y = coordinates
            pyautogui.click(x=x, y=y)
            logger.info(f"已点击坐标: {coordinates}")
            
        except Exception as e:
            logger.error(f"点击失败: {e}")
    
    def press_keys(self, keys: List[str]):
        """
        按下按键组合
        
        Args:
            keys: 按键列表
        """
        try:
            import pyautogui
            pyautogui.hotkey(*keys)
            logger.info(f"已按下按键组合: {keys}")
            
        except Exception as e:
            logger.error(f"按键失败: {e}")
    
    def scroll(self, direction: str = 'down', amount: int = 1):
        """
        滚动
        
        Args:
            direction: 方向（up, down, left, right）
            amount: 滚动量
        """
        try:
            import pyautogui
            
            if direction == 'up':
                pyautogui.scroll(amount)
            elif direction == 'down':
                pyautogui.scroll(-amount)
            elif direction == 'left':
                pyautogui.hscroll(-amount)
            elif direction == 'right':
                pyautogui.hscroll(amount)
                
            logger.info(f"已滚动: {direction} {amount}")
            
        except Exception as e:
            logger.error(f"滚动失败: {e}")
    
    def take_screenshot(self, filename: str = None) -> str:
        """
        截图
        
        Args:
            filename: 文件名
            
        Returns:
            截图文件路径
        """
        try:
            import pyautogui
            
            if filename is None:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            filepath = os.path.join(self.screenshot_path, filename)
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            
            logger.info(f"截图已保存: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"截图失败: {e}")
            raise
    
    def get_available_apps(self) -> List[str]:
        """获取可用的应用程序列表"""
        return self.app_controller.get_running_apps()
    
    def add_task(self, task: Dict):
        """
        添加任务到队列
        
        Args:
            task: 任务描述
        """
        with self.task_lock:
            self.task_queue.append(task)
        logger.info(f"任务已添加: {task.get('type', 'unknown')}")
    
    def execute_now(self, task: Dict):
        """
        立即执行任务
        
        Args:
            task: 任务描述
        """
        self._execute_task(task)
