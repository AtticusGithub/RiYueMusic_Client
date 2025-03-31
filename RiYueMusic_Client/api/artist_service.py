"""
艺术家服务 - 处理艺术家相关操作
"""

from typing import Dict, List, Optional
from .api_client import ApiClient


class ArtistService:
    """处理艺术家相关操作"""
    
    def __init__(self, api_client: ApiClient):
        """
        初始化艺术家服务
        
        Args:
            api_client: API客户端实例
        """
        self.api_client = api_client
    
    def get_all_artists(self) -> List[Dict]:
        """
        获取所有艺术家
        
        Returns:
            艺术家列表
        """
        return self.api_client.get("/api/artists")
    
    def get_artist(self, artist_id: int) -> Dict:
        """
        获取特定艺术家详情
        
        Args:
            artist_id: 艺术家ID
            
        Returns:
            艺术家详情
        """
        return self.api_client.get(f"/api/artists/{artist_id}")
    
    def search_artists(self, name: str) -> List[Dict]:
        """
        搜索艺术家
        
        Args:
            name: 艺术家名称
            
        Returns:
            符合条件的艺术家列表
        """
        return self.api_client.get("/api/artists/search", {"name": name})
    
    def create_artist(self, name: str, bio: Optional[str] = None, avatar_url: Optional[str] = None) -> Dict:
        """
        创建新艺术家
        
        Args:
            name: 艺术家名称
            bio: 艺术家简介
            avatar_url: 头像URL
            
        Returns:
            创建的艺术家详情
        """
        data = {
            "name": name,
            "bio": bio or "",
            "avatarUrl": avatar_url or ""
        }
        
        return self.api_client.post("/api/artists", data)
    
    def update_artist(self, artist_id: int, name: str, bio: Optional[str] = None, avatar_url: Optional[str] = None) -> Dict:
        """
        更新艺术家信息
        
        Args:
            artist_id: 艺术家ID
            name: 新名称
            bio: 新简介
            avatar_url: 新头像URL
            
        Returns:
            更新后的艺术家详情
        """
        data = {
            "name": name,
            "bio": bio or "",
            "avatarUrl": avatar_url or ""
        }
        
        return self.api_client.put(f"/api/artists/{artist_id}", data)
    
    def delete_artist(self, artist_id: int) -> None:
        """
        删除艺术家及其所有歌曲
        
        Args:
            artist_id: 艺术家ID
        """
        return self.api_client.delete(f"/api/artists/{artist_id}")