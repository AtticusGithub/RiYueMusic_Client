"""
播放列表模型 - 表示用户播放列表
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from .song import Song


@dataclass
class Playlist:
    """播放列表信息类"""
    id: int
    name: str
    user_id: int
    username: str
    description: Optional[str] = None
    cover_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    songs: List[Song] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Playlist':
        """
        从字典创建播放列表对象
        
        Args:
            data: 包含播放列表信息的字典
            
        Returns:
            播放列表对象
        """
        created_at = None
        if 'createdAt' in data and data['createdAt']:
            try:
                created_at = datetime.fromisoformat(data['createdAt'].replace('Z', '+00:00'))
            except (ValueError, TypeError):
                pass
        
        updated_at = None
        if 'updatedAt' in data and data['updatedAt']:
            try:
                updated_at = datetime.fromisoformat(data['updatedAt'].replace('Z', '+00:00'))
            except (ValueError, TypeError):
                pass
        
        songs = []
        if 'songs' in data and data['songs']:
            songs = [Song.from_dict(song_data) for song_data in data['songs']]
        
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            user_id=data.get('userId'),
            username=data.get('username'),
            description=data.get('description'),
            cover_url=data.get('coverUrl'),
            created_at=created_at,
            updated_at=updated_at,
            songs=songs
        )