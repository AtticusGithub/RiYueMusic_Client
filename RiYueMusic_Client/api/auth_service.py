"""
认证服务 - 处理用户注册和登录
"""

from typing import Dict, Optional
from .api_client import ApiClient


class AuthService:
    """处理用户身份验证和注册"""
    
    def __init__(self, api_client: ApiClient):
        """
        初始化认证服务
        
        Args:
            api_client: API客户端实例
        """
        self.api_client = api_client
    
    def register(self, username: str, password: str, email: str) -> Dict:
        """
        注册新用户
        
        Args:
            username: 用户名
            password: 密码
            email: 电子邮件
            
        Returns:
            用户信息
        """
        data = {
            "username": username,
            "password": password,
            "email": email
        }
        
        return self.api_client.post("/api/auth/signup", data)
    
    def login(self, username: str, password: str) -> Dict:
        """
        用户登录
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            包含令牌和用户信息的字典
        """
        data = {
            "username": username,
            "password": password
        }
        
        response = self.api_client.post("/api/auth/signin", data)
        
        # 保存令牌到API客户端
        if "token" in response:
            self.api_client.set_token(response["token"])
        
        return response
    
    def logout(self) -> None:
        """用户登出，清除令牌"""
        self.api_client.clear_token()
    
    def get_current_user(self) -> Optional[Dict]:
        """
        获取当前登录用户信息
        
        Returns:
            用户信息或None（如果未登录）
        """
        if not self.api_client.token:
            return None
            
        try:
            return self.api_client.get("/api/users/me")
        except Exception:
            # 如果请求失败（例如令牌过期），清除令牌
            self.api_client.clear_token()
            return None