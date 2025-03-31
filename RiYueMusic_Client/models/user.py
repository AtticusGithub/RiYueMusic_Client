"""
用户模型 - 表示系统用户
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """用户信息类"""
    id: int
    username: str
    email: str
    profile_picture: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """
        从字典创建用户对象
        
        Args:
            data: 包含用户信息的字典
            
        Returns:
            用户对象
        """
        return cls(
            id=data.get('id'),
            username=data.get('username'),
            email=data.get('email'),
            profile_picture=data.get('profilePicture')
        )