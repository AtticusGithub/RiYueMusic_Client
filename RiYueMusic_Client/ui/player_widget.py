"""
播放器控件 - 音乐播放控制界面
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QStyle, QSizePolicy, QToolButton, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QAction

from ..utils.player import AudioPlayer
from ..models.song import Song
from ..utils.config import Config


class PlayerWidget(QWidget):
    """音乐播放器控件"""
    
    # 自定义信号
    next_song_requested = pyqtSignal(bool)  # 请求下一首歌曲，参数表示是否随机
    previous_song_requested = pyqtSignal()  # 请求上一首歌曲
    
    def __init__(self, config=None, parent=None):
        """
        初始化播放器控件
        
        Args:
            config: 配置对象
            parent: 父窗口
        """
        super().__init__(parent)
        
        # 保存配置对象
        self.config = config
        
        # 创建音频播放器
        self.player = AudioPlayer()
        self.player.position_changed.connect(self._on_position_changed)
        self.player.duration_changed.connect(self._on_duration_changed)
        self.player.playback_status_changed.connect(self._on_playback_status_changed)
        self.player.media_finished.connect(self._on_media_finished)
        
        # 当前播放的歌曲
        self.current_song = None
        
        self._init_ui()
        
        # 加载保存的播放模式
        if self.config:
            saved_mode = self.config.get_play_mode() if hasattr(self.config, 'get_play_mode') else 0
            self._set_play_mode(saved_mode)
    
    def _init_ui(self) -> None:
        """初始化UI"""
        layout = QVBoxLayout()
        
        # 歌曲信息区域
        info_layout = QHBoxLayout()
        
        # 专辑封面
        self.cover_label = QLabel()
        self.cover_label.setFixedSize(60, 60)
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._set_default_cover()
        info_layout.addWidget(self.cover_label)
        
        # 歌曲和艺术家信息
        song_info_layout = QVBoxLayout()
        self.song_title_label = QLabel("未播放")
        self.song_title_label.setStyleSheet("font-weight: bold;")
        song_info_layout.addWidget(self.song_title_label)
        
        self.artist_label = QLabel("")
        song_info_layout.addWidget(self.artist_label)
        
        info_layout.addLayout(song_info_layout)
        info_layout.addStretch()
        
        layout.addLayout(info_layout)
        
        # 进度条
        progress_layout = QHBoxLayout()
        
        self.time_label = QLabel("0:00")
        progress_layout.addWidget(self.time_label)
        
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.sliderMoved.connect(self._on_progress_slider_moved)
        self.progress_slider.sliderReleased.connect(self._on_progress_slider_released)
        progress_layout.addWidget(self.progress_slider)
        
        self.duration_label = QLabel("0:00")
        progress_layout.addWidget(self.duration_label)
        
        layout.addLayout(progress_layout)
        
        # 控制按钮
        controls_layout = QHBoxLayout()
        
        # 上一首按钮
        self.previous_button = QPushButton()
        self.previous_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipBackward))
        self.previous_button.clicked.connect(self._on_previous_clicked)
        controls_layout.addWidget(self.previous_button)
        
        # 播放/暂停按钮
        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_button.clicked.connect(self._on_play_clicked)
        controls_layout.addWidget(self.play_button)
        
        # 下一首按钮
        self.next_button = QPushButton()
        self.next_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipForward))
        self.next_button.clicked.connect(self._on_next_clicked)
        controls_layout.addWidget(self.next_button)
        
        # 播放模式按钮（带下拉菜单）
        self.play_mode_button = QToolButton()
        self.play_mode_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_mode_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        # 创建播放模式菜单
        play_mode_menu = QMenu()

        # 使用QAction
        self.normal_mode_action = QAction("正常播放", self)
        self.normal_mode_action.setCheckable(True)
        self.normal_mode_action.setChecked(True)
        self.normal_mode_action.triggered.connect(lambda: self._set_play_mode(0))

        self.loop_mode_action = QAction("列表循环", self)
        self.loop_mode_action.setCheckable(True)
        self.loop_mode_action.triggered.connect(lambda: self._set_play_mode(1))

        self.shuffle_mode_action = QAction("随机播放", self)
        self.shuffle_mode_action.setCheckable(True)
        self.shuffle_mode_action.triggered.connect(lambda: self._set_play_mode(2))

        # 添加单曲循环选项
        self.single_loop_mode_action = QAction("单曲循环", self)
        self.single_loop_mode_action.setCheckable(True)
        self.single_loop_mode_action.triggered.connect(lambda: self._set_play_mode(3))

        # 添加到菜单
        play_mode_menu.addAction(self.normal_mode_action)
        play_mode_menu.addAction(self.loop_mode_action)
        play_mode_menu.addAction(self.shuffle_mode_action)
        play_mode_menu.addAction(self.single_loop_mode_action)

        # 设置菜单
        self.play_mode_button.setMenu(play_mode_menu)
        controls_layout.addWidget(self.play_mode_button)
        
        # 音量按钮和滑块
        self.volume_button = QPushButton()
        self.volume_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))
        self.volume_button.clicked.connect(self._on_volume_button_clicked)
        controls_layout.addWidget(self.volume_button)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)  # 默认音量
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        self.volume_slider.setMaximumWidth(100)
        controls_layout.addWidget(self.volume_slider)
        
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        self.setLayout(layout)
    
    def _set_default_cover(self) -> None:
        """设置默认专辑封面"""
        # 使用系统图标作为默认封面
        pixmap = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay).pixmap(60, 60)
        self.cover_label.setPixmap(pixmap)
    
    def _format_time(self, milliseconds: int) -> str:
        """
        格式化时间
        
        Args:
            milliseconds: 毫秒时间
            
        Returns:
            格式化的时间字符串 (MM:SS)
        """
        if milliseconds <= 0:
            return "0:00"
        
        seconds = milliseconds // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        
        return f"{minutes}:{seconds:02d}"
    
    def _on_position_changed(self, position: int) -> None:
        """
        处理播放位置变化
        
        Args:
            position: 当前位置（毫秒）
        """
        # 更新时间标签
        self.time_label.setText(self._format_time(position))
        
        # 更新进度条（避免递归）
        if not self.progress_slider.isSliderDown():
            duration = self.player.duration
            if duration > 0:
                self.progress_slider.setValue(position * 100 // duration)
    
    def _on_duration_changed(self, duration: int) -> None:
        """
        处理播放时长变化
        
        Args:
            duration: 歌曲时长（毫秒）
        """
        self.duration_label.setText(self._format_time(duration))
    
    def _on_playback_status_changed(self, is_playing: bool) -> None:
        """
        处理播放状态变化
        
        Args:
            is_playing: 是否正在播放
        """
        if is_playing:
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        else:
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
    
    # 在 player_widget.py 的 _on_media_finished 方法中
    def _on_media_finished(self) -> None:
        """处理媒体播放结束"""
        print(f"媒体播放结束，当前播放模式: {self.player.play_mode}")
        
        # 根据播放模式决定接下来的操作
        if hasattr(self.player, 'repeat_current_song') and self.player.repeat_current_song:
            # 单曲循环：重新播放当前歌曲
            if self.current_song and hasattr(self, 'current_url'):
                # 重新播放
                self.play_song(self.current_song, self.current_url)
        elif self.player.play_mode == self.player.PLAY_MODE_SINGLE_LOOP:
            # 单曲循环模式：重新播放当前歌曲
            if self.current_song and hasattr(self, 'current_url'):
                # 重新播放
                self.play_song(self.current_song, self.current_url)
        else:
            # 其他模式：请求下一首
            play_mode = self.player.play_mode
            if play_mode == self.player.PLAY_MODE_NORMAL:
                print("正常模式：请求下一首")
                self.next_song_requested.emit(False)
            elif play_mode == self.player.PLAY_MODE_LOOP:
                print("循环模式：请求下一首")
                self.next_song_requested.emit(False)
            elif play_mode == self.player.PLAY_MODE_SHUFFLE:
                print("随机模式：请求随机下一首")
                self.next_song_requested.emit(True)
    
    def _on_progress_slider_moved(self, position: int) -> None:
        """
        处理进度条拖动
        
        Args:
            position: 进度条位置（0-100）
        """
        # 更新时间标签
        if self.player.duration > 0:
            milliseconds = self.player.duration * position // 100
            self.time_label.setText(self._format_time(milliseconds))
    
    def _on_progress_slider_released(self) -> None:
        """处理进度条释放"""
        position = self.progress_slider.value()
        if self.player.duration > 0:
            milliseconds = self.player.duration * position // 100
            self.player.set_position(milliseconds)
    
    def _on_play_clicked(self) -> None:
        """处理播放/暂停按钮点击"""
        if self.current_song:
            self.player.toggle_play_pause()
        
    def _on_previous_clicked(self) -> None:
        """处理上一首按钮点击"""
        self.previous_song_requested.emit()
    
    def _on_next_clicked(self) -> None:
        """处理下一首按钮点击"""
        # 传递参数，表示是否随机选择下一首
        is_random = (self.player.play_mode == self.player.PLAY_MODE_SHUFFLE)
        self.next_song_requested.emit(is_random)
    
    def _on_volume_button_clicked(self) -> None:
        """处理音量按钮点击"""
        if self.player.get_volume() > 0:
            # 静音
            self.volume_slider.setValue(0)
        else:
            # 恢复音量
            self.volume_slider.setValue(80)
    
    def _on_volume_changed(self, volume: int) -> None:
        """
        处理音量变化
        
        Args:
            volume: 音量（0-100）
        """
        self.player.set_volume(volume)
        
        # 更新音量图标
        if volume == 0:
            self.volume_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolumeMuted))
        else:
            self.volume_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))
    
    def _set_play_mode(self, mode: int) -> None:
        """
        设置播放模式
        
        Args:
            mode: 播放模式（0=正常，1=循环，2=随机）
        """
        self.player.set_play_mode(mode)
        
        # 更新菜单项选中状态
        self.normal_mode_action.setChecked(mode == 0)
        self.loop_mode_action.setChecked(mode == 1)
        self.shuffle_mode_action.setChecked(mode == 2)
        self.single_loop_mode_action.setChecked(mode == 3)
        
        # 更新按钮图标
        if mode == 0:  # 正常播放
            self.play_mode_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        elif mode == 1:  # 循环播放
            self.play_mode_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        elif mode == 2:  # 随机播放
            self.play_mode_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogResetButton))
        elif mode == 3:  # 单曲循环
            # 为单曲循环模式设置一个适当的图标 - 可以使用 SP_BrowserReload 或其他合适的图标
            self.play_mode_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown))
    
        
        # 保存设置
        if self.config and hasattr(self.config, 'set_play_mode'):
            self.config.set_play_mode(mode)
    
    def play_song(self, song: Song, url: str) -> None:
        """
        播放歌曲
        
        Args:
            song: 歌曲对象
            url: 音频文件URL
        """
        if not song:
            return
        
        self.current_song = song
        self.current_url = url
        
        # 更新UI
        self.song_title_label.setText(song.title)
        self.artist_label.setText(song.artist_name if song.artist_name else "")
        
        # 如果有服务器提供的时长，优先使用
        if song.duration:
            print(f"使用服务器提供的时长: {song.duration}")
            self.duration_label.setText(song.duration)
            # 告诉播放器服务器提供的时长
            self.player.set_server_duration(song.duration)
        else:
            # 没有服务器时长，初始显示0:00，等待播放器解析
            self.duration_label.setText("0:00")
        
        # 播放歌曲
        self.player.play(url)
    
    def stop(self) -> None:
        """停止播放"""
        self.player.stop()
        self.current_song = None
        self.song_title_label.setText("未播放")
        self.artist_label.setText("")
        self._set_default_cover()