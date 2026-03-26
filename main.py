import sys
import os

# 修复 PyInstaller 的 PyQt6 插件路径问题
if hasattr(sys, '_MEIPASS'):
    # 获取打包解压后的临时目录
    base_dir = sys._MEIPASS
    plugin_path = os.path.join(base_dir, 'PyQt6', 'Qt6', 'plugins')
    platforms_path = os.path.join(plugin_path, 'platforms')

    # 强制让 Qt 知道去哪里加载 qwindows.dll 平台插件
    os.environ['QT_PLUGIN_PATH'] = plugin_path
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = platforms_path

# 确保项目根路径正确
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 必须在修改环境变量后，再导入 PyQt6
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QAction
from PyQt6.QtCore import Qt


from core.config_manager import ConfigManager
from core.bot_core import BotCore
from ui.main_window import MainWindow


def create_default_icon():
    """Create a simple colored icon for the tray."""
    pixmap = QPixmap(64, 64)
    pixmap.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor("#89b4fa"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(4, 4, 56, 56, 12, 12)
    painter.setPen(QColor("#1e1e2e"))
    font = painter.font()
    font.setPointSize(24)
    font.setBold(True)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "Q")
    painter.end()
    return QIcon(pixmap)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("QQ Bot Manager")
    app.setQuitOnLastWindowClosed(False)

    icon = create_default_icon()
    app.setWindowIcon(icon)

    # Init core
    config = ConfigManager()
    bot = BotCore(config)

    # Main window
    window = MainWindow(bot)

    # System tray
    tray = QSystemTrayIcon(icon, app)
    tray_menu = QMenu()

    show_action = QAction("显示主窗口", tray_menu)
    show_action.triggered.connect(window.show)
    tray_menu.addAction(show_action)

    tray_menu.addSeparator()

    start_action = QAction("启动机器人", tray_menu)
    start_action.triggered.connect(bot.start)
    tray_menu.addAction(start_action)

    stop_action = QAction("停止机器人", tray_menu)
    stop_action.triggered.connect(bot.stop)
    tray_menu.addAction(stop_action)

    tray_menu.addSeparator()

    quit_action = QAction("退出", tray_menu)
    def on_quit():
        bot.stop()
        tray.hide()
        app.quit()
    quit_action.triggered.connect(on_quit)
    tray_menu.addAction(quit_action)

    tray.setContextMenu(tray_menu)
    tray.setToolTip("QQ Bot Manager")
    tray.activated.connect(lambda reason: window.show() if reason == QSystemTrayIcon.ActivationReason.DoubleClick else None)
    tray.show()

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
