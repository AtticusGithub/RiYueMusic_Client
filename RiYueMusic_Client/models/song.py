"""
歌曲相关模型 - 表示歌曲、专辑和艺术家
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Artist:
    """艺术家信息类"""
    id: int
    name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Artist':
        """
        从字典创建艺术家对象
        
        Args:
            data: 包含艺术家信息的字典
            
        Returns:
            艺术家对象
        """
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            bio=data.get('bio'),
            avatar_url=data.get('avatarUrl')
        )


@dataclass
class Album:
    """专辑信息类"""
    id: int
    title: str
    artist_id: int
    artist_name: str
    release_date: Optional[str] = None
    cover_url: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Album':
        """
        从字典创建专辑对象
        
        Args:
            data: 包含专辑信息的字典
            
        Returns:
            专辑对象
        """
        return cls(
            id=data.get('id'),
            title=data.get('title'),
            artist_id=data.get('artistId'),
            artist_name=data.get('artistName'),
            release_date=data.get('releaseDate'),
            cover_url=data.get('coverUrl')
        )


@dataclass
class Song:
    """歌曲信息类"""
    id: int
    title: str
    artist_id: Optional[int] = None
    artist_name: Optional[str] = None
    album_id: Optional[int] = None
    album_title: Optional[str] = None
    duration: Optional[str] = None
    file_url: Optional[str] = None
    lyric_url: Optional[str] = None
    play_count: int = 0
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Song':
        """
        从字典创建歌曲对象
        
        Args:
            data: 包含歌曲信息的字典
            
        Returns:
            歌曲对象
        """
        return cls(
            id=data.get('id'),
            title=data.get('title'),
            artist_id=data.get('artistId'),
            artist_name=data.get('artistName'),
            album_id=data.get('albumId'),
            album_title=data.get('albumTitle'),
            duration=data.get('duration'),
            file_url=data.get('fileUrl'),
            lyric_url=data.get('lyricUrl'),
            play_count=data.get('playCount', 0)
        )