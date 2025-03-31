"""
播放列表服务 - 处理播放列表相关操作
"""

from typing import Dict, List
from .api_client import ApiClient


class PlaylistService:
    """处理播放列表相关操作"""
    
    def __init__(self, api_client: ApiClient):
        """
        初始化播放列表服务
        
        Args:
            api_client: API客户端实例
        """
        self.api_client = api_client
    
    def get_my_playlists(self) -> List[Dict]:
        """
        获取当前用户的所有播放列表
        
        Returns:
            播放列表列表
        """
        return self.api_client.get("/api/playlists/me")
    
    def get_user_playlists(self, user_id: int) -> List[Dict]:
        """
        获取指定用户的所有播放列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            播放列表列表
        """
        return self.api_client.get(f"/api/playlists/user/{user_id}")
    
    def get_playlist(self, playlist_id: int) -> Dict:
        """
        获取播放列表详情
        
        Args:
            playlist_id: 播放列表ID
            
        Returns:
            播放列表详情
        """
        return self.api_client.get(f"/api/playlists/{playlist_id}")
    
    def create_playlist(self, name: str, description: str = "") -> Dict:
        """
        创建新播放列表
        
        Args:
            name: 播放列表名称
            description: 播放列表描述
            
        Returns:
            创建的播放列表详情
        """
        data = {
            "name": name,
            "description": description
        }
        
        return self.api_client.post("/api/playlists", data)
    
    def update_playlist(self, playlist_id: int, name: str, description: str) -> Dict:
        """
        更新播放列表
        
        Args:
            playlist_id: 播放列表ID
            name: 新名称
            description: 新描述
            
        Returns:
            更新后的播放列表详情
        """
        data = {
            "name": name,
            "description": description
        }
        
        return self.api_client.put(f"/api/playlists/{playlist_id}", data)
    
    def delete_playlist(self, playlist_id: int) -> None:
        """
        删除播放列表
        
        Args:
            playlist_id: 播放列表ID
        """
        self.api_client.delete(f"/api/playlists/{playlist_id}")
    
    def add_song_to_playlist(self, playlist_id: int, song_id: int) -> Dict:
        """
        添加歌曲到播放列表
        
        Args:
            playlist_id: 播放列表ID
            song_id: 歌曲ID
            
        Returns:
            更新后的播放列表详情
        """
        return self.api_client.post(f"/api/playlists/{playlist_id}/songs/{song_id}")
    
    def remove_song_from_playlist(self, playlist_id: int, song_id: int) -> Dict:
        """
        从播放列表移除歌曲
        
        Args:
            playlist_id: 播放列表ID
            song_id: 歌曲ID
            
        Returns:
            更新后的播放列表详情
        """
        return self.api_client.delete(f"/api/playlists/{playlist_id}/songs/{song_id}")