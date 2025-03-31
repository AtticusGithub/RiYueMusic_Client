"""
音频播放器 - 使用VLC处理音频播放
"""

import vlc
from PyQt6.QtCore import QTimer, pyqtSignal, QObject


class AudioPlayer(QObject):
    """VLC音频播放器封装"""
    
    # 信号定义
    position_changed = pyqtSignal(int)
    duration_changed = pyqtSignal(int)
    playback_status_changed = pyqtSignal(bool)  # True表示正在播放
    media_finished = pyqtSignal()
    
    # 播放模式常量
    PLAY_MODE_NORMAL = 0   # 正常播放（播放完当前列表后停止）
    PLAY_MODE_LOOP = 1     # 循环播放（播放完当前列表后从头开始）
    PLAY_MODE_SHUFFLE = 2  # 随机播放（随机选择下一首）
    PLAY_MODE_SINGLE_LOOP = 3  # 单曲循环（重复播放当前歌曲）

    def __init__(self):
        super().__init__()
        
        # 创建VLC实例和播放器
        self.instance = vlc.Instance('--no-video')
        self.player = self.instance.media_player_new()
        
        # 当前播放媒体
        self.media = None
        
        # 认证令牌
        self.auth_token = None
        
        # 更新计时器
        self.timer = QTimer()
        self.timer.setInterval(1000)  # 每秒更新一次
        self.timer.timeout.connect(self._update_status)
        
        # 添加事件管理器以捕获媒体信息
        self.event_manager = self.player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerLengthChanged, self._handle_length_changed)
        # 添加这一行 - 监听播放结束事件
        self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self._handle_end_reached)
    
        
        # 当前状态
        self.is_playing = False
        self.duration = 0
        self.server_duration = None  # 存储服务器提供的时长

        # 播放模式
        self.play_mode = self.PLAY_MODE_NORMAL
        
        # 用于随机播放的历史记录
        self.played_history = []

    def _handle_length_changed(self, event):
        """处理媒体长度变化事件"""
        # 获取媒体长度（毫秒）
        length = self.player.get_length()
        if length > 0:
            # 首次获取有效时长或服务器未提供时长
            if self.duration == 0 or self.server_duration is None:
                self.duration = length
                self.duration_changed.emit(self.duration)
                print(f"媒体长度初始化: {length} ms")
            # 只在时长有显著变化(>1秒)时更新，避免微小波动导致的频繁更新
            elif abs(length - self.duration) > 1000:
                self.duration = length
                self.duration_changed.emit(self.duration)
                print(f"媒体长度显著变化: {length} ms")

    def set_server_duration(self, duration_str):
        """
        设置服务器提供的时长
        
        Args:
            duration_str: 格式化的时长字符串 (mm:ss)
        """
        if not duration_str:
            return
            
        try:
            # 解析时长字符串 (格式: "分:秒")
            parts = duration_str.split(":")
            if len(parts) == 2:
                minutes = int(parts[0])
                seconds = int(parts[1])
                # 转换为毫秒
                self.server_duration = (minutes * 60 + seconds) * 1000
                self.duration = self.server_duration
                self.duration_changed.emit(self.duration)
                print(f"从服务器设置时长: {self.server_duration} ms")
        except Exception as e:
            print(f"解析服务器时长时出错: {e}")
    
    def _update_status(self):
        """更新播放状态和进度"""
        if self.is_playing:
            # 获取当前播放位置
            position = self.player.get_time()
            self.position_changed.emit(position)
            
            # 检查是否播放结束
            if position >= self.duration and self.duration > 0:
                self.stop()
                self.media_finished.emit()
    
    def set_auth_token(self, token: str) -> None:
        """
        设置认证令牌
        
        Args:
            token: JWT令牌
        """
        self.auth_token = token

    def play(self, url=None):
        """
        播放音频
        
        Args:
            url: 音频URL，如果为None则播放/恢复当前音频
        """
        if url:
            # 创建新的媒体
            self.media = self.instance.media_new(url)
            self.player.set_media(self.media)
        
        # 播放
        self.player.play()
        self.is_playing = True
        self.playback_status_changed.emit(True)
        
        # 启动更新计时器
        self.timer.start()

        def _try_get_duration(self):
            """尝试再次获取媒体时长"""
            length = self.player.get_length()
            if length > 0:
                self.duration = length
                self.duration_changed.emit(self.duration)
    
    def pause(self):
        """暂停播放"""
        if self.is_playing:
            self.player.pause()
            self.is_playing = False
            self.playback_status_changed.emit(False)
            self.timer.stop()
    
    def resume(self):
        """恢复播放"""
        if not self.is_playing and self.media:
            self.player.play()
            self.is_playing = True
            self.playback_status_changed.emit(True)
            self.timer.start()
    
    def stop(self):
        """停止播放"""
        self.player.stop()
        self.is_playing = False
        self.playback_status_changed.emit(False)
        self.timer.stop()
    
    def toggle_play_pause(self):
        """切换播放/暂停状态"""
        if self.is_playing:
            self.pause()
        else:
            self.resume()
    
    def set_position(self, position):
        """
        设置播放位置
        
        Args:
            position: 位置（毫秒）
        """
        self.player.set_time(position)
    
    def set_volume(self, volume):
        """
        设置音量
        
        Args:
            volume: 音量（0-100）
        """
        self.player.audio_set_volume(volume)
    
    def get_volume(self):
        """
        获取当前音量
        
        Returns:
            当前音量（0-100）
        """
        return self.player.audio_get_volume()
    
    def is_playing_status(self):
        """
        获取播放状态
        
        Returns:
            是否正在播放
        """
        return self.is_playing
    
    def set_play_mode(self, mode: int) -> None:
        """
        设置播放模式
        
        Args:
            mode: 播放模式（PLAY_MODE_NORMAL, PLAY_MODE_LOOP, PLAY_MODE_SHUFFLE）
        """
        self.play_mode = mode

    def _handle_end_reached(self, event):
        """处理媒体播放结束事件"""
        print("媒体播放结束")
        self.is_playing = False
        self.playback_status_changed.emit(False)
        
        # 对于单曲循环模式，通知界面重新播放当前歌曲
        if self.play_mode == self.PLAY_MODE_SINGLE_LOOP:
            print("单曲循环模式：通知重新播放当前歌曲")
            # 发射一个特殊信号，让上层重新加载并播放当前歌曲
            self.repeat_current_song = True
            self.media_finished.emit()
        else:
            # 其他模式
            self.repeat_current_song = False
            self.media_finished.emit()