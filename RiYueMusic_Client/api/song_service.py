"""
歌曲服务 - 处理歌曲、专辑和艺术家相关操作
"""

from typing import Dict, List, Optional
import os
from .api_client import ApiClient


class SongService:
    """处理歌曲、专辑和艺术家相关操作"""
    
    def __init__(self, api_client: ApiClient):
        """
        初始化歌曲服务
        
        Args:
            api_client: API客户端实例
        """
        self.api_client = api_client
    
    # 艺术家相关方法
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
    
    # 专辑相关方法
    def get_albums_by_artist(self, artist_id: int) -> List[Dict]:
        """
        获取艺术家的所有专辑
        
        Args:
            artist_id: 艺术家ID
            
        Returns:
            专辑列表
        """
        return self.api_client.get(f"/api/albums/artist/{artist_id}")
    
    def get_album(self, album_id: int) -> Dict:
        """
        获取专辑详情
        
        Args:
            album_id: 专辑ID
            
        Returns:
            专辑详情
        """
        return self.api_client.get(f"/api/albums/{album_id}")
    
    def search_albums(self, title: str) -> List[Dict]:
        """
        搜索专辑
        
        Args:
            title: 专辑标题
            
        Returns:
            符合条件的专辑列表
        """
        return self.api_client.get("/api/albums/search", {"title": title})
    
    # 歌曲相关方法
    def get_all_songs(self) -> List[Dict]:
        """
        获取所有歌曲
        
        Returns:
            歌曲列表
        """
        return self.api_client.get("/api/songs")
    
    def get_song(self, song_id: int) -> Dict:
        """
        获取歌曲详情
        
        Args:
            song_id: 歌曲ID
            
        Returns:
            歌曲详情
        """
        return self.api_client.get(f"/api/songs/{song_id}")
    
    def get_songs_by_album(self, album_id: int) -> List[Dict]:
        """
        获取专辑中的所有歌曲
        
        Args:
            album_id: 专辑ID
            
        Returns:
            歌曲列表
        """
        return self.api_client.get(f"/api/songs/album/{album_id}")
    
    def get_songs_by_artist(self, artist_id: int) -> List[Dict]:
        """
        获取艺术家的所有歌曲
        
        Args:
            artist_id: 艺术家ID
            
        Returns:
            歌曲列表
        """
        return self.api_client.get(f"/api/songs/artist/{artist_id}")
    
    def search_songs(self, title: str) -> List[Dict]:
        """
        搜索歌曲
        
        Args:
            title: 歌曲标题
            
        Returns:
            符合条件的歌曲列表
        """
        return self.api_client.get("/api/songs/search", {"title": title})
    
    def get_top_songs(self) -> List[Dict]:
        """
        获取热门歌曲
        
        Returns:
            热门歌曲列表
        """
        return self.api_client.get("/api/songs/top")
    
    def upload_song(self, title: str, artist_id: int, album_id: Optional[int], file_path: str) -> Dict:
        """
        上传新歌曲
        
        Args:
            title: 歌曲标题
            artist_id: 艺术家ID
            album_id: 专辑ID (可选)
            file_path: 本地文件路径
            
        Returns:
            上传的歌曲详情
        """
        data = {
            "title": title,
            "artistId": artist_id
        }
        
        if album_id:
            data["albumId"] = album_id
        
        files = {
            "file": (os.path.basename(file_path), open(file_path, "rb"))
        }
        
        try:
            return self.api_client.post("/api/songs", data=data, files=files)
        finally:
            files["file"][1].close()
    
    def increment_play_count(self, song_id: int) -> Dict:
        """
        增加歌曲播放次数
        
        Args:
            song_id: 歌曲ID
            
        Returns:
            更新后的歌曲详情
        """
        return self.api_client.put(f"/api/songs/{song_id}/play")
    
    def delete_song(self, song_id: int) -> None:
        """
        删除歌曲
        
        Args:
            song_id: 歌曲ID
        """
        return self.api_client.delete(f"/api/songs/{song_id}")