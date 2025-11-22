"""
Main window for Eromang application
Provides the main UI framework with navigation and module switching
"""

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QPushButton,
    QLabel,
    QStatusBar,
    QToolBar,
    QMessageBox,
)
from loguru import logger

from ..managers.config_manager import get_config_manager


class MainWindow(QMainWindow):
    """Main application window with navigation sidebar"""

    def __init__(self):
        super().__init__()
        self.config_manager = get_config_manager()
        self.init_ui()
        self.load_window_state()

    def init_ui(self):
        """Initialize the user interface"""
        # Set window properties
        self.setWindowTitle(self.config_manager.get("app.name", "Eromang"))
        self.setMinimumSize(
            self.config_manager.get("window.min_width", 1024),
            self.config_manager.get("window.min_height", 768),
        )

        # Create central widget with main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create navigation sidebar
        self.nav_widget = self.create_navigation_sidebar()
        main_layout.addWidget(self.nav_widget)

        # Create stacked widget for module views
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # Create module placeholder widgets
        self.create_module_widgets()

        # Create menu bar
        self.create_menu_bar()

        # Create toolbar
        self.create_toolbar()

        # Create status bar
        self.create_status_bar()

        # Apply theme
        self.apply_theme()

        logger.info("Main window initialized")

    def create_navigation_sidebar(self) -> QWidget:
        """
        Create navigation sidebar with module buttons

        Returns:
            Navigation sidebar widget
        """
        nav_widget = QWidget()
        nav_widget.setObjectName("navigationSidebar")
        nav_widget.setFixedWidth(200)
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)

        # Application title/logo
        title_label = QLabel(self.config_manager.get("app.name", "Eromang"))
        title_label.setObjectName("appTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFixedHeight(60)
        nav_layout.addWidget(title_label)

        # Navigation buttons
        self.nav_buttons = {}

        # Manga module button
        if self.config_manager.get("modules.manga.enabled", True):
            manga_btn = self.create_nav_button("漫画", "manga")
            nav_layout.addWidget(manga_btn)
            self.nav_buttons["manga"] = manga_btn

        # Video module button
        if self.config_manager.get("modules.video.enabled", True):
            video_btn = self.create_nav_button("视频", "video")
            nav_layout.addWidget(video_btn)
            self.nav_buttons["video"] = video_btn

        # Document module button
        if self.config_manager.get("modules.document.enabled", True):
            document_btn = self.create_nav_button("文档", "document")
            nav_layout.addWidget(document_btn)
            self.nav_buttons["document"] = document_btn

        # Add stretch to push buttons to top
        nav_layout.addStretch()

        # Settings button at bottom
        settings_btn = self.create_nav_button("设置", "settings")
        nav_layout.addWidget(settings_btn)
        self.nav_buttons["settings"] = settings_btn

        return nav_widget

    def create_nav_button(self, text: str, module_id: str) -> QPushButton:
        """
        Create a navigation button

        Args:
            text: Button text
            module_id: Module identifier

        Returns:
            Navigation button
        """
        button = QPushButton(text)
        button.setObjectName("navButton")
        button.setCheckable(True)
        button.setFixedHeight(50)
        button.clicked.connect(lambda: self.switch_module(module_id))
        return button

    def create_module_widgets(self):
        """Create placeholder widgets for each module"""
        # Import module widgets (will be implemented later)
        # For now, create placeholder widgets

        # Manga module placeholder
        manga_widget = QWidget()
        manga_layout = QVBoxLayout(manga_widget)
        manga_label = QLabel("漫画模块")
        manga_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        manga_label.setStyleSheet("font-size: 24px; color: #888;")
        manga_layout.addWidget(manga_label)
        self.stacked_widget.addWidget(manga_widget)

        # Video module placeholder
        video_widget = QWidget()
        video_layout = QVBoxLayout(video_widget)
        video_label = QLabel("视频模块")
        video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        video_label.setStyleSheet("font-size: 24px; color: #888;")
        video_layout.addWidget(video_label)
        self.stacked_widget.addWidget(video_widget)

        # Document module placeholder
        document_widget = QWidget()
        document_layout = QVBoxLayout(document_widget)
        document_label = QLabel("文档模块")
        document_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        document_label.setStyleSheet("font-size: 24px; color: #888;")
        document_layout.addWidget(document_label)
        self.stacked_widget.addWidget(document_widget)

        # Settings module placeholder
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_label = QLabel("设置")
        settings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings_label.setStyleSheet("font-size: 24px; color: #888;")
        settings_layout.addWidget(settings_label)
        self.stacked_widget.addWidget(settings_widget)

        # Map module IDs to widget indices
        self.module_indices = {
            "manga": 0,
            "video": 1,
            "document": 2,
            "settings": 3,
        }

        # Set default module
        self.switch_module("manga")

    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("文件(&F)")

        import_action = QAction("导入媒体库...", self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self.import_library)
        file_menu.addAction(import_action)

        file_menu.addSeparator()

        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("视图(&V)")

        fullscreen_action = QAction("全屏", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.setCheckable(True)
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)

        # Tools menu
        tools_menu = menubar.addMenu("工具(&T)")

        scan_action = QAction("扫描媒体库", self)
        scan_action.setShortcut("Ctrl+R")
        scan_action.triggered.connect(self.scan_libraries)
        tools_menu.addAction(scan_action)

        # Help menu
        help_menu = menubar.addMenu("帮助(&H)")

        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        """Create application toolbar"""
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Add toolbar actions
        # These will be implemented later with proper icons

    def create_status_bar(self):
        """Create application status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")

    def switch_module(self, module_id: str):
        """
        Switch to a different module

        Args:
            module_id: Module identifier
        """
        if module_id in self.module_indices:
            # Update stacked widget
            self.stacked_widget.setCurrentIndex(self.module_indices[module_id])

            # Update button states
            for btn_id, button in self.nav_buttons.items():
                button.setChecked(btn_id == module_id)

            # Update status bar
            module_names = {
                "manga": "漫画模块",
                "video": "视频模块",
                "document": "文档模块",
                "settings": "设置",
            }
            self.status_bar.showMessage(f"当前模块: {module_names.get(module_id, module_id)}")

            logger.info(f"Switched to module: {module_id}")

    def apply_theme(self):
        """Apply application theme"""
        theme = self.config_manager.get("app.theme", "dark")

        if theme == "dark":
            self.setStyleSheet(self.get_dark_theme_stylesheet())
        else:
            self.setStyleSheet(self.get_light_theme_stylesheet())

    def get_dark_theme_stylesheet(self) -> str:
        """
        Get dark theme stylesheet

        Returns:
            QSS stylesheet string
        """
        return """
            QMainWindow {
                background-color: #1e1e1e;
            }

            #navigationSidebar {
                background-color: #252526;
                border-right: 1px solid #3e3e42;
            }

            #appTitle {
                background-color: #2d2d30;
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
                border-bottom: 1px solid #3e3e42;
            }

            #navButton {
                background-color: transparent;
                color: #cccccc;
                border: none;
                text-align: left;
                padding-left: 20px;
                font-size: 14px;
            }

            #navButton:hover {
                background-color: #2a2d2e;
            }

            #navButton:checked {
                background-color: #37373d;
                color: #ffffff;
                border-left: 3px solid #007acc;
            }

            QMenuBar {
                background-color: #2d2d30;
                color: #cccccc;
            }

            QMenuBar::item:selected {
                background-color: #3e3e42;
            }

            QMenu {
                background-color: #252526;
                color: #cccccc;
                border: 1px solid #3e3e42;
            }

            QMenu::item:selected {
                background-color: #094771;
            }

            QToolBar {
                background-color: #2d2d30;
                border-bottom: 1px solid #3e3e42;
            }

            QStatusBar {
                background-color: #007acc;
                color: #ffffff;
            }
        """

    def get_light_theme_stylesheet(self) -> str:
        """
        Get light theme stylesheet

        Returns:
            QSS stylesheet string
        """
        return """
            QMainWindow {
                background-color: #f3f3f3;
            }

            #navigationSidebar {
                background-color: #f0f0f0;
                border-right: 1px solid #d0d0d0;
            }

            #appTitle {
                background-color: #e0e0e0;
                color: #000000;
                font-size: 18px;
                font-weight: bold;
                border-bottom: 1px solid #d0d0d0;
            }

            #navButton {
                background-color: transparent;
                color: #333333;
                border: none;
                text-align: left;
                padding-left: 20px;
                font-size: 14px;
            }

            #navButton:hover {
                background-color: #e5e5e5;
            }

            #navButton:checked {
                background-color: #d0d0d0;
                color: #000000;
                border-left: 3px solid #0078d4;
            }
        """

    def load_window_state(self):
        """Load window size and position from config"""
        width = self.config_manager.get("window.width", 1280)
        height = self.config_manager.get("window.height", 900)
        self.resize(width, height)

        # Center window if no position saved
        pos_x = self.config_manager.get("window.position_x")
        pos_y = self.config_manager.get("window.position_y")

        if pos_x is not None and pos_y is not None:
            self.move(pos_x, pos_y)
        else:
            self.center_window()

        # Restore maximized state
        if self.config_manager.get("window.maximized", False):
            self.showMaximized()

    def save_window_state(self):
        """Save window size and position to config"""
        if not self.isMaximized():
            self.config_manager.set("window.width", self.width(), save=False)
            self.config_manager.set("window.height", self.height(), save=False)
            self.config_manager.set("window.position_x", self.x(), save=False)
            self.config_manager.set("window.position_y", self.y(), save=False)

        self.config_manager.set("window.maximized", self.isMaximized(), save=True)

    def center_window(self):
        """Center window on screen"""
        screen = self.screen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def toggle_fullscreen(self, checked: bool):
        """
        Toggle fullscreen mode

        Args:
            checked: Whether fullscreen is enabled
        """
        if checked:
            self.showFullScreen()
        else:
            self.showNormal()

    def import_library(self):
        """Import media library (placeholder)"""
        QMessageBox.information(self, "导入媒体库", "此功能将在后续版本中实现")

    def scan_libraries(self):
        """Scan media libraries (placeholder)"""
        QMessageBox.information(self, "扫描媒体库", "此功能将在后续版本中实现")

    def show_about(self):
        """Show about dialog"""
        about_text = f"""
        <h2>{self.config_manager.get("app.name", "Eromang")}</h2>
        <p>版本: {self.config_manager.get("app.version", "0.1.0")}</p>
        <p>一个多功能媒体管理软件</p>
        <p>支持漫画、视频和文档管理</p>
        """
        QMessageBox.about(self, "关于", about_text)

    def closeEvent(self, event):
        """
        Handle window close event

        Args:
            event: Close event
        """
        self.save_window_state()
        logger.info("Main window closed")
        event.accept()
