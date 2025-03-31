"""
配置工具 - 管理应用程序配置和状态
"""

import json
import os
from typing import Dict, Any, Optional


class Config:
    """应用程序配置管理"""
    
    def __init__(self, config_path: str = None):
        """
        初始化配置
        
        Args:
            config_path: 配置文件路径，默认为用户主目录下的.music_client.json
        """
        if config_path is None:
            home_dir = os.path.expanduser("~")
            self.config_path = os.path.join(home_dir, ".music_client.json")
        else:
            self.config_path = config_path
        
        # 默认配置
        self.config = {
            "api_url": "http://localhost:8080",
            "token": None,
            "volume": 80,
            "last_played_song_id": None,
            "theme": "light"
        }
        
        # 加载保存的配置
        self.load()
    
    def load(self) -> None:
        """从文件加载配置"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
            except (json.JSONDecodeError, IOError):
                # 如果配置文件损坏或无法读取，使用默认配置
                pass
    
    def save(self) -> None:
        """将配置保存到文件"""
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=2)
        except IOError:
            # 无法写入配置文件
            pass
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值或默认值
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            key: 配置键
            value: 配置值
        """
        self.config[key] = value
        self.save()
    
    def get_api_url(self) -> str:
        """
        获取API URL
        
        Returns:
            API URL
        """
        return self.get("api_url")
    
    def get_token(self) -> Optional[str]:
        """
        获取认证令牌
        
        Returns:
            认证令牌或None
        """
        return self.get("token")
    
    def set_token(self, token: str) -> None:
        """
        设置认证令牌
        
        Args:
            token: 认证令牌
        """
        self.set("token", token)
    
    def clear_token(self) -> None:
        """清除认证令牌"""
        self.set("token", None)
    
    def get_volume(self) -> int:
        """
        获取音量
        
        Returns:
            音量（0-100）
        """
        return self.get("volume", 80)
    
    def set_volume(self, volume: int) -> None:
        """
        设置音量
        
        Args:
            volume: 音量（0-100）
        """
        self.set("volume", max(0, min(100, volume)))
    
    def set_last_played_song(self, song_id: int) -> None:
        """
        设置最后播放的歌曲
        
        Args:
            song_id: 歌曲ID
        """
        self.set("last_played_song_id", song_id)
    
    def get_last_played_song(self) -> Optional[int]:
        """
        获取最后播放的歌曲ID
        
        Returns:
            歌曲ID或None
        """
        return self.get("last_played_song_id")
    
    def get_play_mode(self) -> int:
        """
        获取播放模式
        
        Returns:
            播放模式（0=正常，1=循环，2=随机）
        """
        return self.get("play_mode", 0)

    def set_play_mode(self, mode: int) -> None:
        """
        设置播放模式
        
        Args:
            mode: 播放模式
        """
        self.set("play_mode", mode)