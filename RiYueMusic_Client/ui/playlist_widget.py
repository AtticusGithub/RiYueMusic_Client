"""
播放列表控件 - 显示和管理播放列表
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QMenu, QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from ..models.playlist import Playlist
from ..models.song import Song
from ..api.playlist_service import PlaylistService


class PlaylistWidget(QWidget):
    """播放列表控件"""
    
    # 自定义信号
    song_selected = pyqtSignal(Song)  # 选择歌曲信号
    
    def __init__(self, playlist_service: PlaylistService, parent=None):
        """
        初始化播放列表控件
        
        Args:
            playlist_service: 播放列表服务
            parent: 父窗口
        """
        super().__init__(parent)
        
        self.playlist_service = playlist_service
        self.current_playlist = None
        self.playlists = []
        
        self._init_ui()
    
    def _init_ui(self) -> None:
        """初始化UI"""
        layout = QVBoxLayout()
        
        # 播放列表选择
        playlist_selector_layout = QHBoxLayout()
        
        playlist_selector_layout.addWidget(QLabel("我的播放列表:"))
        
        # 创建播放列表按钮
        create_playlist_button = QPushButton("+")
        create_playlist_button.setFixedWidth(30)
        create_playlist_button.clicked.connect(self._on_create_playlist)
        playlist_selector_layout.addWidget(create_playlist_button)
        
        layout.addLayout(playlist_selector_layout)
        
        # 播放列表选择器
        self.playlist_list = QListWidget()
        self.playlist_list.setMaximumHeight(150)
        self.playlist_list.itemClicked.connect(self._on_playlist_selected)
        self.playlist_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.playlist_list.customContextMenuRequested.connect(self._show_playlist_context_menu)
        layout.addWidget(self.playlist_list)
        
        # 歌曲列表
        layout.addWidget(QLabel("歌曲:"))
        
        self.song_list = QListWidget()
        self.song_list.itemDoubleClicked.connect(self._on_song_double_clicked)
        self.song_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.song_list.customContextMenuRequested.connect(self._show_song_context_menu)
        layout.addWidget(self.song_list)
        
        self.setLayout(layout)
    
    def load_playlists(self) -> None:
        """加载用户的播放列表"""
        try:
            # 获取用户播放列表
            playlists_data = self.playlist_service.get_my_playlists()
            
            # 转换为播放列表对象
            self.playlists = []
            for playlist_data in playlists_data:
                playlist = Playlist.from_dict(playlist_data)
                self.playlists.append(playlist)
            
            # 更新播放列表选择器
            self._update_playlist_list()
        except Exception as e:
            QMessageBox.warning(self, "加载失败", f"无法加载播放列表: {str(e)}")
    
    def _update_playlist_list(self) -> None:
        """更新播放列表选择器"""
        self.playlist_list.clear()
        
        for playlist in self.playlists:
            item = QListWidgetItem(playlist.name)
            item.setData(Qt.ItemDataRole.UserRole, playlist.id)
            self.playlist_list.addItem(item)
    
    def _update_song_list(self) -> None:
        """更新歌曲列表"""
        self.song_list.clear()
        
        if not self.current_playlist:
            return
        
        for song in self.current_playlist.songs:
            text = f"{song.title}"
            if song.artist_name:
                text += f" - {song.artist_name}"
            
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, song)
            self.song_list.addItem(item)
            
    def _on_playlist_selected(self, item: QListWidgetItem) -> None:
        """
        处理播放列表选择
        
        Args:
            item: 选中的列表项
        """
        playlist_id = item.data(Qt.ItemDataRole.UserRole)
        
        # 查找选中的播放列表
        for playlist in self.playlists:
            if playlist.id == playlist_id:
                self.current_playlist = playlist
                break
        
        # 重新加载播放列表内容
        try:
            playlist_data = self.playlist_service.get_playlist(playlist_id)
            self.current_playlist = Playlist.from_dict(playlist_data)
            self._update_song_list()
        except Exception as e:
            QMessageBox.warning(self, "加载失败", f"无法加载播放列表: {str(e)}")
    
    def _on_song_double_clicked(self, item: QListWidgetItem) -> None:
        """
        处理歌曲双击
        
        Args:
            item: 双击的列表项
        """
        song = item.data(Qt.ItemDataRole.UserRole)
        self.song_selected.emit(song)
    
    def _on_create_playlist(self) -> None:
        """处理创建播放列表"""
        name, ok = QInputDialog.getText(
            self, "创建播放列表", "播放列表名称:", 
            text="新播放列表"
        )
        
        if ok and name:
            try:
                # 创建播放列表
                playlist_data = self.playlist_service.create_playlist(name)
                
                # 添加到播放列表集合
                playlist = Playlist.from_dict(playlist_data)
                self.playlists.append(playlist)
                
                # 更新UI
                self._update_playlist_list()
                
                # 选择新创建的播放列表
                for i in range(self.playlist_list.count()):
                    item = self.playlist_list.item(i)
                    if item.data(Qt.ItemDataRole.UserRole) == playlist.id:
                        self.playlist_list.setCurrentItem(item)
                        self._on_playlist_selected(item)
                        break
            except Exception as e:
                QMessageBox.warning(self, "创建失败", f"无法创建播放列表: {str(e)}")
    
    def _show_playlist_context_menu(self, position) -> None:
        """显示播放列表上下文菜单"""
        item = self.playlist_list.itemAt(position)
        if not item:
            return
        
        playlist_id = item.data(Qt.ItemDataRole.UserRole)
        
        # 创建上下文菜单
        menu = QMenu()
        play_action = menu.addAction("播放")
        rename_action = menu.addAction("重命名")
        delete_action = menu.addAction("删除")
        
        # 显示菜单并获取选择的操作
        action = menu.exec(self.playlist_list.mapToGlobal(position))
        
        if action == play_action:
            # 播放整个播放列表
            for playlist in self.playlists:
                if playlist.id == playlist_id:
                    self.current_playlist = playlist
                    self._update_song_list()
                    # 如果播放列表有歌曲，播放第一首
                    if len(playlist.songs) > 0:
                        self.song_list.setCurrentRow(0)
                        song = self.song_list.item(0).data(Qt.ItemDataRole.UserRole)
                        self.song_selected.emit(song)
                    break
        elif action == rename_action:
            self._rename_playlist(playlist_id, item.text())
        elif action == delete_action:
            self._delete_playlist(playlist_id)
    
    def _rename_playlist(self, playlist_id: int, current_name: str) -> None:
        """
        重命名播放列表
        
        Args:
            playlist_id: 播放列表ID
            current_name: 当前名称
        """
        name, ok = QInputDialog.getText(
            self, "重命名播放列表", "新名称:", 
            text=current_name
        )
        
        if ok and name and name != current_name:
            try:
                # 获取当前描述
                description = ""
                for playlist in self.playlists:
                    if playlist.id == playlist_id:
                        description = playlist.description or ""
                        break
                
                # 更新播放列表
                playlist_data = self.playlist_service.update_playlist(
                    playlist_id, name, description
                )
                
                # 重新加载播放列表
                self.load_playlists()
            except Exception as e:
                QMessageBox.warning(self, "重命名失败", f"无法重命名播放列表: {str(e)}")
    
    def _delete_playlist(self, playlist_id: int) -> None:
        """
        删除播放列表
        
        Args:
            playlist_id: 播放列表ID
        """
        confirm = QMessageBox.question(
            self, "确认删除", 
            "确定要删除此播放列表吗？此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                # 删除播放列表
                self.playlist_service.delete_playlist(playlist_id)
                
                # 如果当前显示的就是被删除的播放列表，清空
                if self.current_playlist and self.current_playlist.id == playlist_id:
                    self.current_playlist = None
                    self.song_list.clear()
                
                # 重新加载播放列表
                self.load_playlists()
            except Exception as e:
                QMessageBox.warning(self, "删除失败", f"无法删除播放列表: {str(e)}")
    
    def _show_song_context_menu(self, position) -> None:
        """
        显示歌曲上下文菜单
        
        Args:
            position: 鼠标位置
        """
        if not self.current_playlist:
            return
        
        item = self.song_list.itemAt(position)
        if not item:
            return
        
        song = item.data(Qt.ItemDataRole.UserRole)
        
        # 创建上下文菜单
        menu = QMenu()
        play_action = menu.addAction("播放")
        remove_action = menu.addAction("从播放列表移除")
        
        # 显示菜单并获取选择的操作
        action = menu.exec(self.song_list.mapToGlobal(position))
        
        if action == play_action:
            self.song_selected.emit(song)
        elif action == remove_action:
            self._remove_song_from_playlist(song.id)
    
    def _remove_song_from_playlist(self, song_id: int) -> None:
        """
        从播放列表移除歌曲
        
        Args:
            song_id: 歌曲ID
        """
        if not self.current_playlist:
            return
        
        try:
            # 从播放列表移除歌曲
            playlist_data = self.playlist_service.remove_song_from_playlist(
                self.current_playlist.id, song_id
            )
            
            # 更新当前播放列表
            self.current_playlist = Playlist.from_dict(playlist_data)
            self._update_song_list()
        except Exception as e:
            QMessageBox.warning(self, "移除失败", f"无法从播放列表移除歌曲: {str(e)}")