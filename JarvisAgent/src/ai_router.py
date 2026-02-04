#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 Jarvis AI Agent - AI服务路由系统
 版本: 1.0.0
 功能: 智能路由AI请求到最合适的服务提供商
"""

import os
import json
import time
import logging
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import aiohttp
import asyncio

logger = logging.getLogger(__name__)


class AIServiceBase(ABC):
    """AI服务基类"""
    
    @abstractmethod
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        """发送对话请求"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict:
        """获取模型信息"""
        pass


class OpenAIService(AIServiceBase):
    """OpenAI GPT服务"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY', '')
        self.model = model
        self.base_url = "https://api.openai.com/v1"
    
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        """发送对话请求到OpenAI"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": kwargs.get('max_tokens', 4096),
                "temperature": kwargs.get('temperature', 0.7)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['choices'][0]['message']['content']
                    else:
                        error = await response.text()
                        raise Exception(f"OpenAI API错误: {error}")
                        
        except Exception as e:
            logger.error(f"OpenAI请求失败: {e}")
            raise
    
    def get_model_info(self) -> Dict:
        """获取模型信息"""
        return {
            "name": "GPT-4",
            "provider": "OpenAI",
            "max_tokens": 8192,
            "context_window": 8192,
            "capabilities": ["chat", "reasoning", "coding", "analysis"]
        }


class DoubaoService(AIServiceBase):
    """豆包AI服务"""
    
    def __init__(self, api_key: str = None, model: str = "doubao-pro-32k"):
        self.api_key = api_key or os.environ.get('DOUBAO_API_KEY', '')
        self.model = model
        self.base_url = "https://ark.cn-beijing.volces.com/api/v3"
    
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        """发送对话请求到豆包"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": self._format_messages(messages),
                "max_tokens": kwargs.get('max_tokens', 4096),
                "temperature": kwargs.get('temperature', 0.7)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['choices'][0]['message']['content']
                    else:
                        error = await response.text()
                        raise Exception(f"豆包API错误: {error}")
                        
        except Exception as e:
            logger.error(f"豆包请求失败: {e}")
            raise
    
    def _format_messages(self, messages: List[Dict]) -> List[Dict]:
        """格式化消息"""
        formatted = []
        for msg in messages:
            formatted.append({
                "role": msg.get('role', 'user'),
                "content": msg.get('content', '')
            })
        return formatted
    
    def get_model_info(self) -> Dict:
        """获取模型信息"""
        return {
            "name": "豆包Pro",
            "provider": "字节跳动",
            "max_tokens": 32768,
            "context_window": 32768,
            "capabilities": ["chat", "reasoning", "coding", "multimodal"]
        }


class MinimaxService(AIServiceBase):
    """MiniMax AI服务"""
    
    def __init__(self, api_key: str = None, model: str = "abab6.5s-chat"):
        self.api_key = api_key or os.environ.get('MINIMAX_API_KEY', '')
        self.model = model
        self.base_url = "https://api.minimax.chat/v1"
    
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        """发送对话请求到MiniMax"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "tokens_to_generate": kwargs.get('max_tokens', 4096),
                "temperature": kwargs.get('temperature', 0.7)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/text/chatcompletion_v2",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['choices'][0]['message']['content']
                    else:
                        error = await response.text()
                        raise Exception(f"MiniMax API错误: {error}")
                        
        except Exception as e:
            logger.error(f"MiniMax请求失败: {e}")
            raise
    
    def get_model_info(self) -> Dict:
        """获取模型信息"""
        return {
            "name": "ABAB 6.5s",
            "provider": "MiniMax",
            "max_tokens": 16384,
            "context_window": 16384,
            "capabilities": ["chat", "reasoning", "long_context"]
        }


class QwenService(AIServiceBase):
    """千问AI服务"""
    
    def __init__(self, api_key: str = None, model: str = "qwen-turbo"):
        self.api_key = api_key or os.environ.get('QWEN_API_KEY', '')
        self.model = model
        self.base_url = "https://dashscope.aliyuncs.com/api/v1"
    
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        """发送对话请求到千问"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "input": {
                    "messages": self._format_messages(messages)
                },
                "parameters": {
                    "max_tokens": kwargs.get('max_tokens', 4096),
                    "temperature": kwargs.get('temperature', 0.7)
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/services/aigc/text-generation/generation",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['output']['text']
                    else:
                        error = await response.text()
                        raise Exception(f"千问API错误: {error}")
                        
        except Exception as e:
            logger.error(f"千问请求失败: {e}")
            raise
    
    def _format_messages(self, messages: List[Dict]) -> List[Dict]:
        """格式化消息"""
        formatted = []
        for msg in messages:
            formatted.append({
                "role": msg.get('role', 'user'),
                "content": msg.get('content', '')
            })
        return formatted
    
    def get_model_info(self) -> Dict:
        """获取模型信息"""
        return {
            "name": "通义千问",
            "provider": "阿里巴巴",
            "max_tokens": 16384,
            "context_window": 16384,
            "capabilities": ["chat", "reasoning", "coding", "multimodal"]
        }


class AIRouter:
    """
    AI服务路由中心
    负责智能选择最合适的AI服务
    """
    
    def __init__(self, services_config: Dict):
        """
        初始化AI路由
        
        Args:
            services_config: 服务配置
        """
        self.services: Dict[str, AIServiceBase] = {}
        self.default_service = None
        self.load_balancer = RoundRobinBalancer()
        
        self._initialize_services(services_config)
    
    def _initialize_services(self, config: Dict):
        """初始化各AI服务"""
        service_mapping = {
            'openai': OpenAIService,
            'doubao': DoubaoService,
            'minimax': MinimaxService,
            'qwen': QwenService
        }
        
        for service_name, service_config in config.items():
            if service_config.get('enabled', False):
                try:
                    service_class = service_mapping.get(service_name)
                    if service_class:
                        service = service_class(
                            api_key=service_config.get('api_key', ''),
                            model=service_config.get('model', 'gpt-4')
                        )
                        self.services[service_name] = service
                        
                        if self.default_service is None:
                            self.default_service = service_name
                            
                        logger.info(f"已加载AI服务: {service_name}")
                        
                except Exception as e:
                    logger.error(f"加载服务失败 {service_name}: {e}")
    
    def analyze_and_route(self, query: str, **kwargs) -> str:
        """
        分析查询并路由到最合适的AI服务
        
        Args:
            query: 用户查询
            **kwargs: 额外参数
            
        Returns:
            AI响应文本
        """
        # 根据查询类型选择服务
        selected_service = self._select_service(query)
        
        if not selected_service:
            return "错误: 未配置任何AI服务"
        
        # 准备消息
        messages = self._prepare_messages(query)
        
        try:
            # 调用选定的服务
            service = self.services[selected_service]
            response = asyncio.run(service.chat(messages, **kwargs))
            
            # 更新负载均衡
            self.load_balancer.record_usage(selected_service)
            
            return response
            
        except Exception as e:
            logger.error(f"AI服务调用失败: {e}")
            
            # 尝试备用服务
            fallback_service = self._get_fallback_service(selected_service)
            if fallback_service:
                return self._route_to_service(fallback_service, messages, **kwargs)
            
            return f"抱歉，处理您的请求时出错: {str(e)}"
    
    def _select_service(self, query: str) -> str:
        """
        根据查询智能选择服务
        
        Args:
            query: 用户查询
            
        Returns:
            选定的服务名称
        """
        # 分析查询复杂度
        complexity = self._analyze_complexity(query)
        query_lower = query.lower()
        
        # 根据查询特征选择服务
        if any(keyword in query_lower for keyword in ['代码', '编程', 'code', 'coding', '程序']):
            # 编程任务优先使用GPT-4或Qwen
            if 'openai' in self.services:
                return 'openai'
            elif 'qwen' in self.services:
                return 'qwen'
        
        if any(keyword in query_lower for keyword in ['分析', '研究', 'analysis', 'research', '论文']):
            # 分析任务优先使用GPT-4
            if 'openai' in self.services:
                return 'openai'
        
        if any(keyword in query_lower for keyword in ['图像', '图片', '视觉', 'image', 'vision']):
            # 视觉任务优先使用支持多模态的服务
            if 'doubao' in self.services:
                return 'doubao'
            elif 'qwen' in self.services:
                return 'qwen'
        
        # 默认使用默认服务或轮询
        if self.default_service:
            return self.default_service
        
        # 使用负载均衡选择
        return self.load_balancer.select(list(self.services.keys()))
    
    def _analyze_complexity(self, query: str) -> str:
        """分析查询复杂度"""
        length = len(query)
        
        if length > 1000:
            return 'high'
        elif length > 500:
            return 'medium'
        else:
            return 'low'
    
    def _prepare_messages(self, query: str) -> List[Dict]:
"""准备消息列表"""
        messages = [
            {
                "role": "system",
                "content": """你是一个强大的AI助手，名为Jarvis。
                你可以帮助用户完成各种任务，包括：
                - 信息查询和分析
                - 编程和代码编写
                - 文件操作和管理
                - 网页搜索和内容提取
                - 应用程序控制
                - 任务规划和执行
                
                请始终提供准确、有用的回答。如果需要执行操作，请明确说明要做什么。
                """
            },
            {
                "role": "user",
                "content": query
            }
        ]
        
        return messages
    
    def _route_to_service(self, service_name: str, messages: List[Dict], **kwargs) -> str:
        """路由到指定服务"""
        try:
            service = self.services[service_name]
            return asyncio.run(service.chat(messages, **kwargs))
        except Exception as e:
            logger.error(f"备用服务调用失败: {e}")
            return f"抱歉，无法完成您的请求"
    
    def _get_fallback_service(self, failed_service: str) -> Optional[str]:
        """获取备用服务"""
        available = [s for s in self.services.keys() if s != failed_service]
        if available:
            return available[0]
        return None
    
    def get_available_services(self) -> List[Dict]:
        """获取可用的服务列表"""
        services_info = []
        for name, service in self.services.items():
            info = service.get_model_info()
            info['status'] = 'available'
            services_info.append(info)
        return services_info
    
    def add_service(self, name: str, service: AIServiceBase):
        """添加新服务"""
        self.services[name] = service
        logger.info(f"已添加新服务: {name}")
    
    def remove_service(self, name: str):
        """移除服务"""
        if name in self.services:
            del self.services[name]
            logger.info(f"已移除服务: {name}")


class RoundRobinBalancer:
    """轮询负载均衡器"""
    
    def __init__(self):
        self.usage_count: Dict[str, int] = {}
        self.current_index = 0
    
    def select(self, services: List[str]) -> str:
        """选择下一个服务"""
        # 初始化计数
        for service in services:
            if service not in self.usage_count:
                self.usage_count[service] = 0
        
        # 找到最少使用的服务
        min_usage = min(self.usage_count.values())
        least_used = [s for s, count in self.usage_count.items() 
                     if count == min_usage]
        
        # 如果有多个最少使用的，使用轮询选择
        selected = least_used[self.current_index % len(least_used)]
        
        # 更新索引
        self.current_index = (self.current_index + 1) % len(services)
        
        return selected
    
    def record_usage(self, service: str):
        """记录服务使用"""
        self.usage_count[service] = self.usage_count.get(service, 0) + 1


def create_ai_router(config: Dict = None) -> AIRouter:
    """创建AI路由实例"""
    if config is None:
        config = {
            "openai": {"enabled": False, "api_key": "", "model": "gpt-4"},
            "doubao": {"enabled": False, "api_key": "", "model": "doubao-pro-32k"},
            "minimax": {"enabled": False, "api_key": "", "model": "abab6.5s-chat"},
            "qwen": {"enabled": False, "api_key": "", "model": "qwen-turbo"}
        }
    
    return AIRouter(config)
