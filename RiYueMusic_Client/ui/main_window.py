"""
主窗口 - 音乐应用程序主界面
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTabWidget, QLineEdit, QListWidget, QListWidgetItem,
    QMessageBox, QInputDialog, QFileDialog, QSplitter, QMenu, QToolBar
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QSettings
from PyQt6.QtGui import QAction, QIcon

from ..api.api_client import ApiClient
from ..api.auth_service import AuthService
from ..api.song_service import SongService
from ..api.playlist_service import PlaylistService
from ..api.artist_service import ArtistService
from ..models.song import Song, Artist, Album
from ..utils.config import Config
from .login_dialog import LoginDialog
from .player_widget import PlayerWidget
from .playlist_widget import PlaylistWidget


class MainWindow(QMainWindow):
    """音乐应用程序主窗口"""
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        # 设置窗口基本属性
        self.setWindowTitle("RiYueMusic")
        self.setMinimumSize(1000, 600)
        
        # 加载配置
        self.config = Config()
        
        # 创建API客户端和服务
        self.api_client = ApiClient(self.config.get_api_url())
        self.auth_service = AuthService(self.api_client)
        self.song_service = SongService(self.api_client)
        self.playlist_service = PlaylistService(self.api_client)

        # 创建艺术家服务
        self.artist_service = ArtistService(self.api_client)
        
        # 恢复保存的令牌（如果有）
        token = self.config.get_token()
        if token:
            self.api_client.set_token(token)
        
        # 当前用户
        self.current_user = None
        
        # 创建UI
        self._init_ui()
        
        # 尝试自动登录
        self._check_login_status()
    
    def _init_ui(self) -> None:
        """初始化UI"""
        # 创建中央部件
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # 创建工具栏
        self._create_toolbar()
        
        # 创建主要布局
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧面板
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        # 搜索
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索歌曲、艺术家或专辑...")
        self.search_input.returnPressed.connect(self._on_search)
        search_layout.addWidget(self.search_input)
        
        search_button = QPushButton("搜索")
        search_button.clicked.connect(self._on_search)
        search_layout.addWidget(search_button)
        
        left_layout.addLayout(search_layout)
        
        # 选项卡
        self.tabs = QTabWidget()
        
        # 歌曲选项卡
        songs_tab = QWidget()
        songs_layout = QVBoxLayout()
        songs_tab.setLayout(songs_layout)
        
        self.songs_list = QListWidget()
        self.songs_list.itemDoubleClicked.connect(self._on_song_double_clicked)
        songs_layout.addWidget(self.songs_list)

        # 在歌曲列表初始化后添加
        self.songs_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.songs_list.customContextMenuRequested.connect(self._show_song_context_menu)
        
        # 艺术家选项卡
        artists_tab = QWidget()
        artists_layout = QVBoxLayout()
        artists_tab.setLayout(artists_layout)
        
        self.artists_list = QListWidget()
        self.artists_list.itemDoubleClicked.connect(self._on_artist_double_clicked)
        artists_layout.addWidget(self.artists_list)

        # 在_init_ui方法中，设置艺术家列表的上下文菜单
        self.artists_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.artists_list.customContextMenuRequested.connect(self._show_artist_context_menu)
        
        # 专辑选项卡
        albums_tab = QWidget()
        albums_layout = QVBoxLayout()
        albums_tab.setLayout(albums_layout)
        
        self.albums_list = QListWidget()
        self.albums_list.itemDoubleClicked.connect(self._on_album_double_clicked)
        albums_layout.addWidget(self.albums_list)
        
        # 添加选项卡
        self.tabs.addTab(songs_tab, "歌曲")
        self.tabs.addTab(artists_tab, "艺术家")
        self.tabs.addTab(albums_tab, "专辑")
        
        left_layout.addWidget(self.tabs)
        
        # 右侧面板（播放列表）
        self.playlist_widget = PlaylistWidget(self.playlist_service)
        self.playlist_widget.song_selected.connect(self._on_playlist_song_selected)
        
        # 添加面板到分割器
        splitter.addWidget(left_panel)
        splitter.addWidget(self.playlist_widget)
        
        # 设置分割器初始尺寸
        splitter.setSizes([500, 300])
        
        main_layout.addWidget(splitter)
        
        # 底部播放器控件
        self.player_widget = PlayerWidget(config=self.config)
        self.player_widget.next_song_requested.connect(self._on_next_song_requested)
        self.player_widget.previous_song_requested.connect(self._on_previous_song_requested)
        
        main_layout.addWidget(self.player_widget)
        
        # 设置初始音量
        volume = self.config.get_volume()
        self.player_widget.volume_slider.setValue(volume)

    def _show_artist_context_menu(self, position) -> None:
        """
        显示艺术家上下文菜单
        
        Args:
            position: 鼠标位置
        """
        item = self.artists_list.itemAt(position)
        if not item:
            return
        
        artist = item.data(Qt.ItemDataRole.UserRole)
        
        # 创建上下文菜单
        menu = QMenu()
        view_action = menu.addAction("查看所有歌曲")
        delete_action = menu.addAction("删除艺术家")
        
        # 显示菜单并获取选择的操作
        action = menu.exec(self.artists_list.mapToGlobal(position))
        
        if action == view_action:
            self._on_artist_double_clicked(item)
        elif action == delete_action:
            self._delete_artist(artist)

    def _delete_artist(self, artist) -> None:
        """
        删除艺术家
        
        Args:
            artist: 艺术家对象
        """
        # 确认对话框，强调这会删除所有相关歌曲
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            f"确定要删除艺术家\"{artist.name}\"及其所有歌曲吗？此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # 再次确认，因为这是一个重要操作
                confirm = QMessageBox.warning(
                    self,
                    "最终确认",
                    f"删除艺术家\"{artist.name}\"将永久删除所有相关歌曲和专辑。\n\n确定要继续吗？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if confirm == QMessageBox.StandardButton.Yes:
                    # 执行删除
                    self.artist_service.delete_artist(artist.id)
                    
                    # 检查是否正在播放该艺术家的歌曲，如果是则停止播放
                    if (self.player_widget.current_song and 
                        self.player_widget.current_song.artist_id == artist.id):
                        self.player_widget.stop()
                    
                    # 刷新列表
                    self._load_artists()
                    self._load_songs()
                    self._load_albums()
                    
                    QMessageBox.information(
                        self, "删除成功", 
                        f"艺术家\"{artist.name}\"及其所有歌曲已成功删除。"
                    )
            except Exception as e:
                QMessageBox.critical(
                    self, "删除失败", 
                    f"无法删除艺术家: {str(e)}"
                )

    def _show_song_context_menu(self, position) -> None:
        """
        显示歌曲上下文菜单
        
        Args:
            position: 鼠标位置
        """
        item = self.songs_list.itemAt(position)
        if not item:
            return
        
        song = item.data(Qt.ItemDataRole.UserRole)
        
        # 创建上下文菜单
        menu = QMenu()
        play_action = menu.addAction("播放")
        add_to_playlist_action = menu.addAction("添加到播放列表")
        delete_action = menu.addAction("删除")
        
        # 显示菜单并获取选择的操作
        action = menu.exec(self.songs_list.mapToGlobal(position))
        
        if action == play_action:
            self._play_song(song)
        elif action == add_to_playlist_action:
            self._show_add_to_playlist_dialog(song)
        elif action == delete_action:
            self._delete_song(song)

    def _show_add_to_playlist_dialog(self, song) -> None:
        """
        显示添加歌曲到播放列表对话框
        
        Args:
            song: 要添加的歌曲
        """
        if not self.current_user:
            QMessageBox.warning(self, "未登录", "请先登录后再添加歌曲到播放列表")
            return
        
        try:
            # 获取用户的播放列表
            playlists = self.playlist_service.get_my_playlists()
            
            if not playlists:
                # 没有播放列表，提示创建
                reply = QMessageBox.question(
                    self,
                    "没有播放列表",
                    "您还没有播放列表。是否创建一个新的播放列表？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self._create_playlist(song)  # 创建新播放列表并添加歌曲
                return
            
            # 有播放列表，显示选择对话框
            playlist_names = [playlist['name'] for playlist in playlists]
            playlist_names.append("创建新播放列表...")
            
            playlist_name, ok = QInputDialog.getItem(
                self, "选择播放列表", "请选择要添加到的播放列表:",
                playlist_names, 0, False
            )
            
            if not ok:
                return
            
            if playlist_name == "创建新播放列表...":
                self._create_playlist(song)  # 创建新播放列表并添加歌曲
            else:
                # 查找播放列表ID
                playlist_id = None
                for playlist in playlists:
                    if playlist['name'] == playlist_name:
                        playlist_id = playlist['id']
                        break
                
                if playlist_id is None:
                    QMessageBox.warning(self, "错误", "无法找到选择的播放列表")
                    return
                
                # 添加歌曲到播放列表
                self.playlist_service.add_song_to_playlist(playlist_id, song.id)
                
                QMessageBox.information(
                    self, "添加成功", 
                    f"歌曲\"{song.title}\"已添加到播放列表\"{playlist_name}\""
                )
                
                # 刷新播放列表
                self.playlist_widget.load_playlists()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"添加歌曲到播放列表失败: {str(e)}")

    def _create_playlist(self, song=None) -> None:
        """
        创建新播放列表
        
        Args:
            song: 要添加的歌曲（可选）
        """
        if not self.current_user:
            QMessageBox.warning(self, "未登录", "请先登录后再创建播放列表")
            return
        
        # 获取播放列表名称
        name, ok = QInputDialog.getText(
            self, "创建播放列表", "播放列表名称:"
        )
        
        if not ok or not name:
            return
        
        # 获取播放列表描述（可选）
        description, ok = QInputDialog.getText(
            self, "播放列表描述", "描述 (可选):"
        )
        
        if not ok:
            return
        
        try:
            # 创建播放列表
            playlist_data = self.playlist_service.create_playlist(
                name, description if description else ""
            )
            
            # 如果有歌曲要添加
            if song:
                self.playlist_service.add_song_to_playlist(
                    playlist_data['id'], song.id
                )
                
                QMessageBox.information(
                    self, "创建成功", 
                    f"播放列表\"{name}\"已创建，并添加了歌曲\"{song.title}\""
                )
            else:
                QMessageBox.information(
                    self, "创建成功", 
                    f"播放列表\"{name}\"已创建"
                )
            
            # 刷新播放列表
            self.playlist_widget.load_playlists()
        except Exception as e:
            QMessageBox.critical(self, "创建失败", f"无法创建播放列表: {str(e)}")

    def _delete_song(self, song: Song) -> None:
        """
        删除歌曲
        
        Args:
            song: 歌曲对象
        """
        # 确认对话框
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            f"确定要删除歌曲 \"{song.title}\" 吗？此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # 删除歌曲
                self.song_service.delete_song(song.id)
                
                # 如果正在播放这首歌，停止播放
                if (self.player_widget.current_song and 
                    self.player_widget.current_song.id == song.id):
                    self.player_widget.stop()
                
                # 刷新歌曲列表
                self._load_songs()
                
                QMessageBox.information(
                    self, "删除成功", 
                    f"歌曲 \"{song.title}\" 已成功删除。"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "删除失败", 
                    f"无法删除歌曲: {str(e)}"
                )
    
    def _create_toolbar(self) -> None:
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # 登录/用户按钮
        self.login_action = QAction("登录", self)
        self.login_action.triggered.connect(self._show_login_dialog)
        toolbar.addAction(self.login_action)
        
        # 刷新按钮
        refresh_action = QAction("刷新", self)
        refresh_action.triggered.connect(self._load_data)
        toolbar.addAction(refresh_action)
        
        # 上传歌曲
        upload_action = QAction("上传歌曲", self)
        upload_action.triggered.connect(self._show_upload_dialog)
        toolbar.addAction(upload_action)
        
        # 设置按钮
        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self._show_settings_dialog)
        toolbar.addAction(settings_action)
    
    def _check_login_status(self) -> None:
        """检查登录状态"""
        try:
            # 尝试获取当前用户信息
            user_data = self.auth_service.get_current_user()
            if user_data:
                self.current_user = user_data
                self._update_login_status(True)
                
                # 载入数据
                self._load_data()
            else:
                self._update_login_status(False)
                self._show_login_dialog()
        except Exception:
            self._update_login_status(False)
            self._show_login_dialog()
    
    def _update_login_status(self, logged_in: bool) -> None:
        """
        更新登录状态和UI
        
        Args:
            logged_in: 是否已登录
        """
        if logged_in and self.current_user:
            self.login_action.setText(f"用户: {self.current_user.get('username')}")
            
            # 保存令牌
            token = self.api_client.token
            if token:
                self.config.set_token(token)
        else:
            self.login_action.setText("登录")
            self.config.clear_token()
    
    def _show_login_dialog(self) -> None:
        """显示登录对话框"""
        dialog = LoginDialog(self.auth_service, self)
        dialog.login_successful.connect(self._on_login_successful)
        dialog.exec()
    
    def _on_login_successful(self, user_data: dict) -> None:
        """
        处理登录成功
        
        Args:
            user_data: 用户信息
        """
        self.current_user = user_data
        self._update_login_status(True)
        
        # 保存令牌
        token = self.api_client.token
        if token:
            self.config.set_token(token)
        
        # 加载数据
        self._load_data()
    
    def _load_data(self) -> None:
        """加载数据"""
        # 加载歌曲
        self._load_songs()
        
        # 加载艺术家
        self._load_artists()
        
        # 加载专辑
        self._load_albums()
        
        # 加载播放列表
        self.playlist_widget.load_playlists()
    
    def _load_songs(self) -> None:
        """加载歌曲列表"""
        try:
            songs_data = self.song_service.get_all_songs()
            
            self.songs_list.clear()
            
            for song_data in songs_data:
                song = Song.from_dict(song_data)
                
                text = song.title
                if song.artist_name:
                    text += f" - {song.artist_name}"
                
                item = QListWidgetItem(text)
                item.setData(Qt.ItemDataRole.UserRole, song)
                self.songs_list.addItem(item)
        except Exception as e:
            QMessageBox.warning(self, "加载失败", f"无法加载歌曲: {str(e)}")
    
    def _load_artists(self) -> None:
        """加载艺术家列表"""
        try:
            artists_data = self.song_service.get_all_artists()
            
            self.artists_list.clear()
            
            for artist_data in artists_data:
                artist = Artist.from_dict(artist_data)
                
                item = QListWidgetItem(artist.name)
                item.setData(Qt.ItemDataRole.UserRole, artist)
                self.artists_list.addItem(item)
        except Exception as e:
            QMessageBox.warning(self, "加载失败", f"无法加载艺术家: {str(e)}")
    
    def _load_albums(self) -> None:
        """加载专辑列表"""
        try:
            # 暂未实现API获取所有专辑，通过艺术家获取
            albums = []
            artists_data = self.song_service.get_all_artists()
            
            for artist_data in artists_data:
                artist_id = artist_data.get('id')
                artist_albums = self.song_service.get_albums_by_artist(artist_id)
                albums.extend(artist_albums)
            
            self.albums_list.clear()
            
            for album_data in albums:
                album = Album.from_dict(album_data)
                
                text = album.title
                if album.artist_name:
                    text += f" - {album.artist_name}"
                
                item = QListWidgetItem(text)
                item.setData(Qt.ItemDataRole.UserRole, album)
                self.albums_list.addItem(item)
        except Exception as e:
            QMessageBox.warning(self, "加载失败", f"无法加载专辑: {str(e)}")
    
    def _on_search(self) -> None:
        """处理搜索"""
        query = self.search_input.text().strip()
        if not query:
            return
        
        # 确定当前选项卡
        current_tab = self.tabs.currentIndex()
        
        try:
            if current_tab == 0:  # 歌曲
                self._search_songs(query)
            elif current_tab == 1:  # 艺术家
                self._search_artists(query)
            elif current_tab == 2:  # 专辑
                self._search_albums(query)
        except Exception as e:
            QMessageBox.warning(self, "搜索失败", f"搜索失败: {str(e)}")
    
    def _search_songs(self, query: str) -> None:
        """
        搜索歌曲
        
        Args:
            query: 搜索关键词
        """
        songs_data = self.song_service.search_songs(query)
        
        self.songs_list.clear()
        
        for song_data in songs_data:
            song = Song.from_dict(song_data)
            
            text = song.title
            if song.artist_name:
                text += f" - {song.artist_name}"
            
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, song)
            self.songs_list.addItem(item)
    
    def _search_artists(self, query: str) -> None:
        """
        搜索艺术家
        
        Args:
            query: 搜索关键词
        """
        artists_data = self.song_service.search_artists(query)
        
        self.artists_list.clear()
        
        for artist_data in artists_data:
            artist = Artist.from_dict(artist_data)
            
            item = QListWidgetItem(artist.name)
            item.setData(Qt.ItemDataRole.UserRole, artist)
            self.artists_list.addItem(item)
    
    def _search_albums(self, query: str) -> None:
        """
        搜索专辑
        
        Args:
            query: 搜索关键词
        """
        albums_data = self.song_service.search_albums(query)
        
        self.albums_list.clear()
        
        for album_data in albums_data:
            album = Album.from_dict(album_data)
            
            text = album.title
            if album.artist_name:
                text += f" - {album.artist_name}"
            
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, album)
            self.albums_list.addItem(item)
    
    def _on_song_double_clicked(self, item: QListWidgetItem) -> None:
        """
        处理歌曲双击
        
        Args:
            item: 双击的列表项
        """
        song = item.data(Qt.ItemDataRole.UserRole)
        self._play_song(song)
    
    def _on_artist_double_clicked(self, item: QListWidgetItem) -> None:
        """
        处理艺术家双击
        
        Args:
            item: 双击的列表项
        """
        artist = item.data(Qt.ItemDataRole.UserRole)
        
        try:
            # 获取艺术家的歌曲
            songs_data = self.song_service.get_songs_by_artist(artist.id)
            
            # 切换到歌曲选项卡
            self.tabs.setCurrentIndex(0)
            
            # 更新列表
            self.songs_list.clear()
            
            for song_data in songs_data:
                song = Song.from_dict(song_data)
                
                text = song.title
                if song.album_title:
                    text += f" ({song.album_title})"
                
                item = QListWidgetItem(text)
                item.setData(Qt.ItemDataRole.UserRole, song)
                self.songs_list.addItem(item)
        except Exception as e:
            QMessageBox.warning(self, "加载失败", f"无法加载艺术家歌曲: {str(e)}")
    
    def _on_album_double_clicked(self, item: QListWidgetItem) -> None:
        """
        处理专辑双击
        
        Args:
            item: 双击的列表项
        """
        album = item.data(Qt.ItemDataRole.UserRole)
        
        try:
            # 获取专辑的歌曲
            songs_data = self.song_service.get_songs_by_album(album.id)
            
            # 切换到歌曲选项卡
            self.tabs.setCurrentIndex(0)
            
            # 更新列表
            self.songs_list.clear()
            
            for song_data in songs_data:
                song = Song.from_dict(song_data)
                
                text = song.title
                if song.artist_name:
                    text += f" - {song.artist_name}"
                
                item = QListWidgetItem(text)
                item.setData(Qt.ItemDataRole.UserRole, song)
                self.songs_list.addItem(item)
        except Exception as e:
            QMessageBox.warning(self, "加载失败", f"无法加载专辑歌曲: {str(e)}")
    
    def _on_playlist_song_selected(self, song: Song) -> None:
        """
        处理从播放列表选择歌曲
        
        Args:
            song: 选中的歌曲
        """
        self._play_song(song)
    
    def _play_song(self, song: Song) -> None:
        """
        播放歌曲
        
        Args:
            song: 要播放的歌曲
        """
        if not song:
            return
        
        try:
            # 获取文件URL
            file_url = song.file_url
            
            # 重新构建文件URL，指向新的文件API
            if not file_url.startswith(("http://", "https://")):
                # 从文件路径中提取文件名
                file_name = file_url.split('/')[-1]
                # 使用新的API端点构建URL
                file_url = f"{self.config.get_api_url()}/api/files/music/{file_name}"
            
            # 播放歌曲
            self.player_widget.play_song(song, file_url)
            
            # 增加播放次数
            self.song_service.increment_play_count(song.id)
            
            # 保存最后播放的歌曲
            self.config.set_last_played_song(song.id)
        except Exception as e:
            import traceback
            traceback.print_exc()  # 打印详细错误
            QMessageBox.warning(self, "播放失败", f"无法播放歌曲: {str(e)}")
    
    def _on_next_song_requested(self, random=False) -> None:
        """
        处理请求下一首歌曲
        
        Args:
            random: 是否随机选择下一首
        """
        print(f"请求下一首歌曲，随机模式: {random}")
        
        # 获取当前活动的歌曲列表
        active_list = None
        
        # 检查当前激活的播放列表
        if hasattr(self.playlist_widget, 'song_list') and self.playlist_widget.current_playlist:
            print("使用播放列表中的歌曲列表")
            active_list = self.playlist_widget.song_list
        # 如果没有激活的播放列表，则使用当前选项卡中的列表
        elif self.tabs.currentIndex() == 0:  # 歌曲选项卡
            print("使用歌曲选项卡中的列表")
            active_list = self.songs_list
        
        if not active_list or active_list.count() == 0:
            print("没有可用的歌曲列表或列表为空")
            return
        
        current_row = active_list.currentRow()
        print(f"当前行: {current_row}, 总行数: {active_list.count()}")
        
        if random:
            # 随机模式：随机选择一首不是当前播放的歌曲
            import random as rnd
            if active_list.count() > 1:
                # 生成除当前行外的所有可能行号
                available_rows = [i for i in range(active_list.count()) if i != current_row]
                next_row = rnd.choice(available_rows)
                print(f"随机选择下一行: {next_row}")
            else:
                next_row = 0  # 只有一首歌曲时就播放它
                print("只有一首歌，继续播放")
        else:
            # 正常/循环模式：顺序播放下一首
            next_row = current_row + 1
            print(f"尝试播放下一行: {next_row}")
            
            # 如果到达列表末尾，处理循环
            if next_row >= active_list.count():
                # 检查播放模式
                play_mode = self.player_widget.player.play_mode
                print(f"当前播放模式: {play_mode}")
                
                if play_mode == self.player_widget.player.PLAY_MODE_LOOP:
                    # 循环模式：回到第一首
                    next_row = 0
                    print("循环模式：回到第一首")
                else:
                    # 正常模式：停止播放
                    print("正常模式：到达列表末尾，停止播放")
                    return
        
        # 设置当前行并播放
        print(f"设置当前行为: {next_row} 并播放")
        active_list.setCurrentRow(next_row)
        item = active_list.item(next_row)
        if item:
            song = item.data(Qt.ItemDataRole.UserRole)
            self._play_song(song)
        else:
            print(f"无法获取行 {next_row} 的歌曲数据")

    def _on_previous_song_requested(self) -> None:
        """处理请求上一首歌曲"""
        # 获取当前活动的歌曲列表
        active_list = None
        
        # 检查当前选项卡
        current_tab = self.tabs.currentIndex()
        if current_tab == 0:  # 歌曲选项卡
            active_list = self.songs_list
        
        # 如果有选中的播放列表，优先使用播放列表
        if hasattr(self.playlist_widget, 'current_playlist') and self.playlist_widget.current_playlist:
            active_list = self.playlist_widget.song_list
        
        if not active_list or active_list.count() == 0:
            return
        
        current_row = active_list.currentRow()
        prev_row = current_row - 1
        
        # 如果到达列表开头，根据播放模式处理
        if prev_row < 0:
            if self.player_widget.player.play_mode == self.player_widget.player.PLAY_MODE_LOOP:
                # 循环模式：跳到最后一首
                prev_row = active_list.count() - 1
            else:
                # 正常模式：保持在第一首
                prev_row = 0
        
        # 设置当前行并播放
        active_list.setCurrentRow(prev_row)
        item = active_list.item(prev_row)
        if item:
            song = item.data(Qt.ItemDataRole.UserRole)
            self._play_song(song)
    
    def _play_next_from_list(self, list_widget: QListWidget) -> None:
        """
        从列表中播放下一首歌曲
        
        Args:
            list_widget: 列表控件
        """
        current_row = list_widget.currentRow()
        next_row = current_row + 1
        
        if next_row >= list_widget.count():
            next_row = 0  # 循环到第一首
        
        list_widget.setCurrentRow(next_row)
        item = list_widget.item(next_row)
        if item:
            song = item.data(Qt.ItemDataRole.UserRole)
            self._play_song(song)
    
    def _play_previous_from_list(self, list_widget: QListWidget) -> None:
        """
        从列表中播放上一首歌曲
        
        Args:
            list_widget: 列表控件
        """
        current_row = list_widget.currentRow()
        prev_row = current_row - 1
        
        if prev_row < 0:
            prev_row = list_widget.count() - 1  # 循环到最后一首
        
        list_widget.setCurrentRow(prev_row)
        item = list_widget.item(prev_row)
        if item:
            song = item.data(Qt.ItemDataRole.UserRole)
            self._play_song(song)
    
    def _show_upload_dialog(self) -> None:
        """显示上传歌曲对话框"""
        if not self.current_user:
            QMessageBox.warning(self, "未登录", "请先登录后再上传歌曲")
            return
        
        # 选择文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择音乐文件", "", "音乐文件 (*.mp3 *.wav *.ogg)"
        )
        
        if not file_path:
            return
        
        # 获取歌曲标题（默认为文件名）
        import os
        default_title = os.path.splitext(os.path.basename(file_path))[0]
        
        title, ok = QInputDialog.getText(
            self, "歌曲标题", "输入歌曲标题:", 
            text=default_title
        )
        
        if not ok or not title:
            return
        
        # 处理艺术家选择
        try:
            artists_data = self.song_service.get_all_artists()
            
            # 添加"创建新艺术家"选项
            artist_names = ["创建新艺术家..."] + [artist['name'] for artist in artists_data]
            artist_name, ok = QInputDialog.getItem(
                self, "选择艺术家", "艺术家:", 
                artist_names, 0, False
            )
            
            if not ok:
                return
            
            artist_id = None
            is_new_artist = False  # 标记是否创建了新艺术家
            
            # 如果选择了"创建新艺术家"
            if artist_name == "创建新艺术家...":
                new_artist_name, ok = QInputDialog.getText(
                    self, "新艺术家", "艺术家名称:"
                )
                
                if not ok or not new_artist_name:
                    return
                
                # 获取可选的艺术家简介
                new_artist_bio, ok = QInputDialog.getText(
                    self, "艺术家简介", "简介 (可选):"
                )
                
                if not ok:
                    return
                
                # 创建新艺术家
                try:
                    new_artist_data = {
                        "name": new_artist_name,
                        "bio": new_artist_bio if new_artist_bio else ""
                    }
                    
                    # 创建艺术家的API调用
                    response = self.api_client.post("/api/artists", new_artist_data)
                    artist_id = response.get('id')
                    artist_name = new_artist_name
                    
                    # 刷新艺术家列表
                    self._load_artists()
                    
                    QMessageBox.information(
                        self, "创建成功", 
                        f"艺术家「{new_artist_name}」创建成功！"
                    )
                    
                    is_new_artist = True  # 标记创建了新艺术家
                except Exception as e:
                    QMessageBox.critical(self, "创建失败", f"无法创建艺术家: {str(e)}")
                    return
            else:
                # 查找选择的艺术家ID
                for artist in artists_data:
                    if artist['name'] == artist_name:
                        artist_id = artist['id']
                        break
            
            if not artist_id:
                return
            
            # 选择专辑（可选）
            # 如果是新创建的艺术家，不需要尝试获取专辑列表，直接提供创建选项
            albums_data = [] if is_new_artist else self.song_service.get_albums_by_artist(artist_id)
            
            album_id = None
            album_names = ["(无专辑)", "创建新专辑..."]
            if albums_data:
                album_names += [album['title'] for album in albums_data]
            
            album_name, ok = QInputDialog.getItem(
                self, "选择专辑", "专辑:", 
                album_names, 0, False
            )
            
            if not ok:
                return
            
            if album_name == "创建新专辑...":
                # 实现创建新专辑的代码
                new_album_title, ok = QInputDialog.getText(
                    self, "新专辑", "专辑名称:"
                )
                
                if not ok or not new_album_title:
                    return
                
                # 创建新专辑
                try:
                    new_album_data = {
                        "title": new_album_title,
                        "artistId": artist_id
                    }
                    
                    # 调用创建专辑API
                    response = self.api_client.post("/api/albums", new_album_data)
                    album_id = response.get('id')
                    
                    QMessageBox.information(
                        self, "创建成功", 
                        f"专辑「{new_album_title}」创建成功！"
                    )
                except Exception as e:
                    QMessageBox.critical(self, "创建失败", f"无法创建专辑: {str(e)}")
                    return
            elif album_name != "(无专辑)":
                # 查找选择的专辑ID
                for album in albums_data:
                    if album['title'] == album_name:
                        album_id = album['id']
                        break
            
            # 上传歌曲
            try:
                song_data = self.song_service.upload_song(
                    title, artist_id, album_id, file_path
                )
                
                QMessageBox.information(
                    self, "上传成功", 
                    "歌曲上传成功！将刷新歌曲列表。"
                )
                
                # 刷新歌曲列表
                self._load_songs()
            except Exception as e:
                QMessageBox.critical(self, "上传失败", f"无法上传歌曲: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"发生错误: {str(e)}")
    
    def _show_settings_dialog(self) -> None:
        """显示设置对话框"""
        # API URL设置
        current_url = self.config.get_api_url()
        url, ok = QInputDialog.getText(
            self, "API设置", "API服务器URL:", 
            text=current_url
        )
        
        if ok and url:
            self.config.set("api_url", url)
            self.api_client.base_url = url
            
            QMessageBox.information(
                self, "设置已保存", 
                "设置已更新。建议重新启动应用程序使设置生效。"
            )
    
    def closeEvent(self, event) -> None:
        """
        处理窗口关闭事件
        
        Args:
            event: 关闭事件
        """
        # 保存音量设置
        volume = self.player_widget.volume_slider.value()
        self.config.set_volume(volume)
        
        # 停止播放
        self.player_widget.stop()
        
        super().closeEvent(event)