#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 Jarvis AI Agent - 核心代理系统
 版本: 1.0.0
 功能: 具备强大AI能力的桌面助手，支持多AI服务接入和电脑操作控制
"""

import os
import sys
import json
import time
import logging
import threading
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from datetime import datetime
import asyncio
import aiohttp

# 导入子模块
from ai_router import AIRouter
from computer_vision import ComputerVision
from automation import AutomationEngine
from task_planner import TaskPlanner

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/jarvis_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class JarvisAgent:
    """
    Jarvis AI Agent 主类
    负责协调所有子系统，提供统一的接口
    """
    
    def __init__(self, config_path: str = None):
        """
        初始化 Jarvis Agent
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'config', 
            'config.json'
        )
        self.config = self._load_config()
        
        # 初始化核心组件
        self.ai_router = AIRouter(self.config.get('ai_services', {}))
        self.computer_vision = ComputerVision()
        self.automation = AutomationEngine()
        self.task_planner = TaskPlanner()
        
        # 状态管理
        self.is_running = False
        self.current_task = None
        self.conversation_history = []
        
        # 启动主循环
        self._start_main_loop()
        
        logger.info("Jarvis Agent 初始化完成")
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
        
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "ai_services": {
                "openai": {"enabled": False, "api_key": "", "model": "gpt-4"},
                "doubao": {"enabled": False, "api_key": "", "model": "doubao-pro-32k"},
                "minimax": {"enabled": False, "api_key": "", "model": "abab6.5s-chat"},
                "qwen": {"enabled": False, "api_key": "", "model": "qwen-turbo"}
            },
            "automation": {
                "screenshot_path": "/tmp/jarvis_screenshots",
                "download_path": "~/Downloads",
                "paper_storage": "~/Desktop/Papers"
            },
            "general": {
                "language": "zh",
                "theme": "dark",
                "startup": True
            }
        }
    
    def _start_main_loop(self):
        """启动主处理循环"""
        self.is_running = True
        self.main_thread = threading.Thread(target=self._main_loop, daemon=True)
        self.main_thread.start()
    
    def _main_loop(self):
        """主处理循环"""
        while self.is_running:
            try:
                # 检查任务队列
                if self.task_planner.has_pending_tasks():
                    task = self.task_planner.get_next_task()
                    self._execute_task(task)
                else:
                    time.sleep(0.5)
            except Exception as e:
                logger.error(f"主循环错误: {e}")
                time.sleep(1)
    
    def _execute_task(self, task: Dict):
        """
        执行单个任务
        
        Args:
            task: 任务描述字典
        """
        self.current_task = task
        task_type = task.get('type', 'general')
        
        try:
            if task_type == 'search_download':
                self._handle_search_download(task)
            elif task_type == 'file_organize':
                self._handle_file_organize(task)
            elif task_type == 'app_control':
                self._handle_app_control(task)
            elif task_type == 'web_operation':
                self._handle_web_operation(task)
            else:
                self._handle_general_task(task)
            
            self.task_planner.complete_task(task['id'])
        except Exception as e:
            logger.error(f"执行任务失败: {e}")
            self.task_planner.fail_task(task['id'], str(e))
        
        self.current_task = None
    
    def _handle_search_download(self, task: Dict):
        """处理搜索下载任务（如论文搜索下载）"""
        query = task.get('query', '')
        save_path = task.get('save_path', '~/Desktop/Papers')
        
        # 使用AI分析最佳搜索策略
        strategy = self.ai_router.analyze_and_route(
            f"为以下查询制定最佳搜索和下载策略: {query}"
        )
        
        # 执行搜索
        search_results = self._search_papers(query)
        
        # 下载选定的论文
        for result in search_results:
            if result.get('selected', False):
                self._download_paper(result, save_path)
    
    def _handle_file_organize(self, task: Dict):
        """处理文件整理任务"""
        source_dir = task.get('source', '')
        target_dir = task.get('target', '')
        rule = task.get('rule', 'auto')
        
        # 使用AI智能分类
        classification = self.ai_router.analyze_and_route(
            f"分析以下文件并提供分类建议: 源目录{source_dir}，目标目录{target_dir}"
        )
        
        # 执行自动化分类
        self.automation.organize_files(source_dir, target_dir, classification)
    
    def _handle_app_control(self, task: Dict):
        """处理应用程序控制任务"""
        app_name = task.get('app', '')
        action = task.get('action', '')
        params = task.get('params', {})
        
        # 执行应用操作
        self.automation.control_application(app_name, action, params)
    
    def _handle_web_operation(self, task: Dict):
        """处理网页操作任务"""
        url = task.get('url', '')
        action = task.get('action', '')
        params = task.get('params', {})
        
        # 使用自动化引擎处理网页操作
        self.automation.handle_web_operation(url, action, params)
    
    def _handle_general_task(self, task: Dict):
        """处理一般任务"""
        instruction = task.get('instruction', '')
        
        # 路由到合适的AI服务
        response = self.ai_router.analyze_and_route(instruction)
        
        # 执行实际操作
        if task.get('execute', True):
            self._execute_instruction(response)
    
    def _search_papers(self, query: str) -> List[Dict]:
        """
        搜索学术论文
        
        Args:
            query: 搜索查询
            
        Returns:
            搜索结果列表
        """
        results = []
        
        try:
            # 使用学术搜索引擎API
            # 这里可以接入Google Scholar, arXiv, Semantic Scholar等
            search_engines = ['semantic_scholar', 'arxiv', 'google_scholar']
            
            for engine in search_engines:
                engine_results = self._search_with_engine(engine, query)
                results.extend(engine_results)
            
            # 使用AI排序和过滤
            ranked_results = self.ai_router.analyze_and_route(
                f"对以下论文搜索结果进行排序和过滤，返回最相关的10篇: {json.dumps(results)}"
            )
            
        except Exception as e:
            logger.error(f"论文搜索失败: {e}")
        
        return results
    
    def _search_with_engine(self, engine: str, query: str) -> List[Dict]:
        """
        使用特定搜索引擎搜索
        
        Args:
            engine: 搜索引擎名称
            query: 搜索查询
            
        Returns:
            搜索结果
        """
        # 这里实现具体的搜索引擎逻辑
        # 实际使用需要接入相应的API
        return []
    
    def _download_paper(self, paper_info: Dict, save_path: str):
        """
        下载论文
        
        Args:
            paper_info: 论文信息
            save_path: 保存路径
        """
        try:
            # 获取论文URL
            pdf_url = paper_info.get('pdf_url', '')
            title = paper_info.get('title', 'unknown_paper')
            
            if pdf_url:
                # 使用自动化引擎下载
                file_path = self.automation.download_file(pdf_url, save_path, title)
                
                # 重命名为规范格式
                if file_path:
                    self._rename_paper_file(file_path, paper_info)
                    
        except Exception as e:
            logger.error(f"论文下载失败: {e}")
    
    def _rename_paper_file(self, file_path: str, paper_info: Dict):
        """
        重命名论文文件
        
        Args:
            file_path: 文件路径
            paper_info: 论文信息
        """
        try:
            title = paper_info.get('title', 'unknown')
            authors = paper_info.get('authors', [])
            year = paper_info.get('year', datetime.now().year)
            
            # 规范化文件名
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))[:50]
            authors_str = "_".join(authors[:2]) if authors else "Unknown"
            
            new_name = f"{year}_{authors_str}_{safe_title}.pdf"
            new_path = os.path.join(os.path.dirname(file_path), new_name)
            
            os.rename(file_path, new_path)
            
        except Exception as e:
            logger.error(f"文件重命名失败: {e}")
    
    def _execute_instruction(self, instruction: str):
        """
        执行AI生成的指令
        
        Args:
            instruction: 指令描述
        """
        # 解析指令并执行相应操作
        action_type = self._parse_action_type(instruction)
        
        if action_type == 'screenshot':
            self.computer_vision.take_screenshot()
        elif action_type == 'type_text':
            text = self._extract_text_to_type(instruction)
            self.automation.type_text(text)
        elif action_type == 'click':
            coords = self._extract_coordinates(instruction)
            self.automation.click(coords)
        elif action_type == 'key_press':
            keys = self._extract_keys(instruction)
            self.automation.press_keys(keys)
        else:
            logger.warning(f"未知的指令类型: {action_type}")
    
    def _parse_action_type(self, instruction: str) -> str:
        """解析指令类型"""
        instruction_lower = instruction.lower()
        
        if any(keyword in instruction_lower for keyword in ['截图', 'screenshot', '截屏']):
            return 'screenshot'
        elif any(keyword in instruction_lower for keyword in ['输入', 'type', '打字']):
            return 'type_text'
        elif any(keyword in instruction_lower for keyword in ['点击', 'click', '鼠标']):
            return 'click'
        elif any(keyword in instruction_lower for keyword in ['按键', 'press', '快捷键']):
            return 'key_press'
        
        return 'unknown'
    
    def _extract_text_to_type(self, instruction: str) -> str:
        """提取要输入的文本"""
        # 使用AI提取要输入的文本
        return self.ai_router.analyze_and_route(
            f"从以下指令中提取要输入的文本: {instruction}"
        )
    
    def _extract_coordinates(self, instruction: str) -> tuple:
        """提取点击坐标"""
        # 使用计算机视觉识别点击位置
        return self.computer_vision.find_click_target(instruction)
    
    def _extract_keys(self, instruction: str) -> List[str]:
        """提取按键"""
        return self.ai_router.analyze_and_route(
            f"从以下指令中提取按键序列: {instruction}"
        ).split('+')
    
    async def process_voice_command(self, audio_data: bytes) -> str:
        """
        处理语音命令
        
        Args:
            audio_data: 音频数据
            
        Returns:
            命令文本
        """
        try:
            # 使用语音识别服务
            command = await self._transcribe_audio(audio_data)
            
            # 处理命令
            response = self.process_command(command)
            
            return response
            
        except Exception as e:
            logger.error(f"语音命令处理失败: {e}")
            return "抱歉，处理语音命令时出错"
    
    async def _transcribe_audio(self, audio_data: bytes) -> str:
        """
        转录音频为文本
        
        Args:
            audio_data: 音频数据
            
        Returns:
            转录文本
        """
        # 这里可以接入语音识别API（如Whisper）
        return ""
    
    def process_command(self, command: str) -> str:
        """
        处理文本命令
        
        Args:
            command: 用户命令
            
        Returns:
            响应文本
        """
        # 记录到对话历史
        self.conversation_history.append({
            'role': 'user',
            'content': command,
            'timestamp': datetime.now().isoformat()
        })
        
        try:
            # 路由到AI服务
            response = self.ai_router.analyze_and_route(command)
            
            # 记录AI响应
            self.conversation_history.append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now().isoformat()
            })
            
            # 如果需要执行操作
            if self._should_execute(response):
                self._execute_instruction(response)
            
            return response
            
        except Exception as e:
            error_msg = f"处理命令时出错: {e}"
            logger.error(error_msg)
            return error_msg
    
    def _should_execute(self, response: str) -> bool:
        """判断是否需要执行操作"""
        execute_keywords = ['执行', '操作', '完成', '去做', '帮我']
        return any(keyword in response for keyword in execute_keywords)
    
    def get_status(self) -> Dict:
        """获取Agent状态"""
        return {
            'is_running': self.is_running,
            'current_task': self.current_task,
            'pending_tasks': self.task_planner.get_pending_count(),
            'ai_services': list(self.ai_router.services.keys()),
            'available_apps': self.automation.get_available_apps()
        }
    
    def stop(self):
        """停止Agent"""
        self.is_running = False
        logger.info("Jarvis Agent 已停止")


def main():
    """主入口"""
    agent = JarvisAgent()
    
    try:
        # 保持运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        agent.stop()


if __name__ == "__main__":
    main()
