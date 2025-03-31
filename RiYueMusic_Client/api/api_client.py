"""
API客户端 - 处理与后端API的所有通信
"""

import requests
import json
from typing import Dict, List, Optional, Any


class ApiClient:
    """API通信的基础客户端"""
    
    def __init__(self, base_url: str):
        """
        初始化API客户端
        
        Args:
            base_url: API基础URL
        """
        self.base_url = base_url
        self.token = None
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def set_token(self, token: str) -> None:
        """
        设置认证令牌
        
        Args:
            token: JWT令牌
        """
        self.token = token
        self.headers["Authorization"] = f"Bearer {token}"
    
    def clear_token(self) -> None:
        """清除认证令牌"""
        self.token = None
        if "Authorization" in self.headers:
            del self.headers["Authorization"]
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """
        发送GET请求
        
        Args:
            endpoint: API端点
            params: URL参数
            
        Returns:
            解析后的JSON响应
            
        Raises:
            Exception: 请求失败
        """
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = f"GET {url} failed with status {response.status_code}"
            try:
                error_details = response.json()
                error_msg += f": {error_details}"
            except:
                error_msg += f": {response.text}"
            raise Exception(error_msg)
    
    def post(self, endpoint: str, data: Dict = None, files: Dict = None) -> Any:
        """
        发送POST请求
        
        Args:
            endpoint: API端点
            data: 请求体数据
            files: 上传的文件
            
        Returns:
            解析后的JSON响应
            
        Raises:
            Exception: 请求失败
        """
        url = f"{self.base_url}{endpoint}"
        headers = self.headers.copy()
        
        if files:
            # 如果上传文件，不设置Content-Type让requests自动处理
            if "Content-Type" in headers:
                del headers["Content-Type"]
            
            response = requests.post(
                url, 
                headers=headers, 
                data=data, 
                files=files
            )
        else:
            # 正常JSON请求
            response = requests.post(
                url, 
                headers=headers, 
                data=json.dumps(data) if data else None
            )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = f"POST {url} failed with status {response.status_code}"
            try:
                error_details = response.json()
                error_msg += f": {error_details}"
            except:
                error_msg += f": {response.text}"
            raise Exception(error_msg)
    
    def put(self, endpoint: str, data: Dict = None) -> Any:
        """
        发送PUT请求
        
        Args:
            endpoint: API端点
            data: 请求体数据
            
        Returns:
            解析后的JSON响应
            
        Raises:
            Exception: 请求失败
        """
        url = f"{self.base_url}{endpoint}"
        response = requests.put(
            url, 
            headers=self.headers,
            data=json.dumps(data) if data else None
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = f"PUT {url} failed with status {response.status_code}"
            try:
                error_details = response.json()
                error_msg += f": {error_details}"
            except:
                error_msg += f": {response.text}"
            raise Exception(error_msg)
    
    def delete(self, endpoint: str) -> Any:
        """
        发送DELETE请求
        
        Args:
            endpoint: API端点
            
        Returns:
            解析后的JSON响应或None
            
        Raises:
            Exception: 请求失败
        """
        url = f"{self.base_url}{endpoint}"
        response = requests.delete(url, headers=self.headers)
        
        if response.status_code in [200, 204]:
            try:
                return response.json()
            except:
                return None
        else:
            error_msg = f"DELETE {url} failed with status {response.status_code}"
            try:
                error_details = response.json()
                error_msg += f": {error_details}"
            except:
                error_msg += f": {response.text}"
            raise Exception(error_msg)