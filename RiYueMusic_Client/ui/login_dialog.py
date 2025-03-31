"""
登录对话框 - 处理用户登录和注册
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTabWidget, QWidget, QMessageBox
)
from PyQt6.QtCore import pyqtSignal

from ..api.auth_service import AuthService


class LoginDialog(QDialog):
    """登录和注册对话框"""
    
    # 自定义信号
    login_successful = pyqtSignal(dict)  # 登录成功信号，发送用户信息
    
    def __init__(self, auth_service: AuthService, parent=None):
        """
        初始化登录对话框
        
        Args:
            auth_service: 认证服务
            parent: 父窗口
        """
        super().__init__(parent)
        self.auth_service = auth_service
        
        self.setWindowTitle("登录/注册")
        self.setMinimumWidth(400)
        
        self._init_ui()
    
    def _init_ui(self) -> None:
        """初始化UI"""
        layout = QVBoxLayout()
        
        # 创建选项卡
        tab_widget = QTabWidget()
        
        # 登录选项卡
        login_tab = QWidget()
        login_layout = QVBoxLayout()
        
        # 用户名
        login_layout.addWidget(QLabel("用户名:"))
        self.login_username = QLineEdit()
        login_layout.addWidget(self.login_username)
        
        # 密码
        login_layout.addWidget(QLabel("密码:"))
        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        login_layout.addWidget(self.login_password)
        
        # 登录按钮
        login_button = QPushButton("登录")
        login_button.clicked.connect(self._on_login)
        login_layout.addWidget(login_button)
        
        login_tab.setLayout(login_layout)
        
        # 注册选项卡
        register_tab = QWidget()
        register_layout = QVBoxLayout()
        
        # 用户名
        register_layout.addWidget(QLabel("用户名:"))
        self.register_username = QLineEdit()
        register_layout.addWidget(self.register_username)
        
        # 电子邮件
        register_layout.addWidget(QLabel("电子邮件:"))
        self.register_email = QLineEdit()
        register_layout.addWidget(self.register_email)
        
        # 密码
        register_layout.addWidget(QLabel("密码:"))
        self.register_password = QLineEdit()
        self.register_password.setEchoMode(QLineEdit.EchoMode.Password)
        register_layout.addWidget(self.register_password)
        
        # 确认密码
        register_layout.addWidget(QLabel("确认密码:"))
        self.register_confirm_password = QLineEdit()
        self.register_confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        register_layout.addWidget(self.register_confirm_password)
        
        # 注册按钮
        register_button = QPushButton("注册")
        register_button.clicked.connect(self._on_register)
        register_layout.addWidget(register_button)
        
        register_tab.setLayout(register_layout)
        
        # 添加选项卡到选项卡控件
        tab_widget.addTab(login_tab, "登录")
        tab_widget.addTab(register_tab, "注册")
        
        layout.addWidget(tab_widget)
        
        self.setLayout(layout)
    
    def _on_login(self) -> None:
        """处理登录按钮点击"""
        username = self.login_username.text().strip()
        password = self.login_password.text()
        
        if not username or not password:
            QMessageBox.warning(self, "输入错误", "请输入用户名和密码")
            return
        
        try:
            # 尝试登录
            user_data = self.auth_service.login(username, password)
            # 发出登录成功信号
            self.login_successful.emit(user_data)
            # 关闭对话框
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "登录失败", f"无法登录: {str(e)}")
    
    def _on_register(self) -> None:
        """处理注册按钮点击"""
        username = self.register_username.text().strip()
        email = self.register_email.text().strip()
        password = self.register_password.text()
        confirm_password = self.register_confirm_password.text()
        
        # 验证输入
        if not username or not email or not password:
            QMessageBox.warning(self, "输入错误", "请填写所有字段")
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "密码不匹配", "密码和确认密码不匹配")
            return
        
        try:
            # 尝试注册
            self.auth_service.register(username, password, email)
            # 注册成功后自动登录
            user_data = self.auth_service.login(username, password)
            # 发出登录成功信号
            self.login_successful.emit(user_data)
            # 关闭对话框
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "注册失败", f"无法注册: {str(e)}")