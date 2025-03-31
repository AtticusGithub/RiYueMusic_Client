#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音乐播放器应用程序 - 客户端主程序入口
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtGui import QFont
import os

from ui.main_window import MainWindow


def main():
    """主程序入口"""
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("音乐播放器")
    app.setOrganizationName("RiYueMusic")
    
    # 设置应用程序图标
    # app.setWindowIcon(QIcon("path/to/icon.png"))
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序事件循环
    sys.exit(app.exec())


if __name__ == "__main__":
    main()