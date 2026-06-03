# Modern Premium QSS Stylesheet for Video Blocker

MAIN_WINDOW_STYLE = """
QMainWindow {
    background-color: #0d0e12;
}
"""

CENTRAL_WIDGET_STYLE = """
QWidget#centralWidget {
    background-color: #0d0e12;
}
"""

TITLE_STYLE = """
QLabel#appTitle {
    color: #ffffff;
    font-size: 32px;
    font-weight: 800;
    font-family: 'Inter', 'Segoe UI', 'Ubuntu', 'Helvetica Neue', sans-serif;
    letter-spacing: 3px;
    margin-top: 50px;
    margin-bottom: 8px;
}
"""

SUBTITLE_STYLE = """
QLabel#appSubtitle {
    color: #64748b;
    font-size: 14px;
    font-weight: 500;
    font-family: 'Inter', 'Segoe UI', 'Ubuntu', sans-serif;
    margin-bottom: 50px;
}
"""

# Styling for the card/container around the buttons to give a beautiful modern glassmorphism or elevated card look
CARD_STYLE = """
QFrame#cardFrame {
    background-color: #161822;
    border: 1px solid #232634;
    border-radius: 20px;
    padding: 30px;
}
"""

HOST_BUTTON_STYLE = """
QPushButton#hostButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6366f1, stop:1 #4f46e5);
    color: #ffffff;
    font-size: 16px;
    font-weight: 700;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    border: none;
    border-radius: 12px;
    padding: 16px 24px;
    min-width: 180px;
}
QPushButton#hostButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #818cf8, stop:1 #6366f1);
    border: 1px solid rgba(255, 255, 255, 0.15);
}
QPushButton#hostButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4f46e5, stop:1 #4338ca);
}
"""

GUEST_BUTTON_STYLE = """
QPushButton#guestButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ec4899, stop:1 #db2777);
    color: #ffffff;
    font-size: 16px;
    font-weight: 700;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    border: none;
    border-radius: 12px;
    padding: 16px 24px;
    min-width: 180px;
}
QPushButton#guestButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f472b6, stop:1 #ec4899);
    border: 1px solid rgba(255, 255, 255, 0.15);
}
QPushButton#guestButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #db2777, stop:1 #be185d);
}
"""

FOOTER_STYLE = """
QLabel#footerText {
    color: #3b4252;
    font-size: 11px;
    font-weight: 600;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    margin-bottom: 15px;
}
"""

BACK_BUTTON_STYLE = """
QPushButton#backButton {
    background-color: transparent;
    color: #94a3b8;
    font-size: 14px;
    font-weight: 600;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    border: 1px solid #2d3142;
    border-radius: 10px;
    padding: 10px 20px;
}
QPushButton#backButton:hover {
    color: #f1f5f9;
    background-color: #1e2030;
    border-color: #4c566a;
}
QPushButton#backButton:pressed {
    background-color: #13141f;
}
"""

ROLE_TITLE_STYLE = """
QLabel#roleTitle {
    color: #ffffff;
    font-size: 48px;
    font-weight: 900;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    letter-spacing: 4px;
}
"""

ROLE_CONTAINER_STYLE = """
QFrame#roleContainer {
    background-color: #161822;
    border: 1px solid #232634;
    border-radius: 20px;
}
"""

MESSAGE_BOX_STYLE = """
QMessageBox {
    background-color: #161822;
}
QMessageBox QLabel {
    color: #e5e7eb;
    font-size: 14px;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
QMessageBox QPushButton {
    background-color: #1e2030;
    color: #e5e7eb;
    font-size: 13px;
    font-weight: 600;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    border: 1px solid #2d3142;
    border-radius: 8px;
    padding: 6px 18px;
    min-width: 70px;
}
QMessageBox QPushButton:hover {
    background-color: #2b2f44;
    border-color: #4c566a;
}
QMessageBox QPushButton:pressed {
    background-color: #13141f;
}
"""

DASHBOARD_HEADER_STYLE = """
QWidget#dashboardHeader {
    background-color: #13141f;
    border-bottom: 1px solid #232634;
}
"""

DASHBOARD_TITLE_STYLE = """
QLabel#dashboardTitle {
    color: #ffffff;
    font-size: 18px;
    font-weight: 800;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    letter-spacing: 1px;
}
"""

PLAYBACK_PANEL_STYLE = """
QFrame#playbackPanel {
    background-color: #161822;
    border: 1px solid #232634;
    border-radius: 16px;
}
"""

PLAYBACK_HEADER_STYLE = """
QLabel#playbackHeader {
    color: #f8fafc;
    font-size: 18px;
    font-weight: 700;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
"""

PATH_INPUT_STYLE = """
QLineEdit#pathInput {
    background-color: #0d0e12;
    color: #f1f5f9;
    border: 1px solid #2d3142;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
QLineEdit#pathInput:focus {
    border-color: #6366f1;
}
"""

BROWSE_BUTTON_STYLE = """
QPushButton#browseButton {
    background-color: #1e2030;
    color: #ffffff;
    font-size: 13px;
    font-weight: 600;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    border: 1px solid #2d3142;
    border-radius: 8px;
    padding: 10px 18px;
}
QPushButton#browseButton:hover {
    background-color: #2b2f44;
    border-color: #4c566a;
}
QPushButton#browseButton:pressed {
    background-color: #13141f;
}
"""

MEDIA_BUTTON_STYLE = """
QPushButton#mediaButton {
    background-color: #1e2030;
    color: #ffffff;
    font-size: 14px;
    font-weight: 600;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    border: 1px solid #2d3142;
    border-radius: 10px;
    padding: 12px;
    min-width: 60px;
}
QPushButton#mediaButton:hover {
    background-color: #2b2f44;
    border-color: #6366f1;
}
QPushButton#mediaButton:pressed {
    background-color: #13141f;
}
"""

SLIDER_STYLE = """
QSlider::groove:horizontal {
    border: none;
    height: 6px;
    background: #1e2030;
    border-radius: 3px;
}
QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366f1, stop:1 #4f46e5);
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #ffffff;
    border: none;
    width: 14px;
    height: 14px;
    margin: -4px 0;
    border-radius: 7px;
}
QSlider::handle:horizontal:hover {
    background: #818cf8;
}
"""

TIME_LABEL_STYLE = """
QLabel#timeLabel {
    color: #64748b;
    font-size: 12px;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
"""

BLOCK_BUTTON_STYLE = """
QPushButton#blockButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ef4444, stop:1 #dc2626);
    color: #ffffff;
    font-size: 16px;
    font-weight: 800;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    letter-spacing: 1px;
    border: none;
    border-radius: 12px;
    padding: 18px;
}
QPushButton#blockButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f87171, stop:1 #ef4444);
    border: 1px solid rgba(255, 255, 255, 0.2);
}
QPushButton#blockButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #dc2626, stop:1 #b91c1c);
}
"""

SIDEBAR_PANEL_STYLE = """
QFrame#sidebarPanel {
    background-color: #12131a;
    border: 1px solid #232634;
    border-radius: 16px;
}
"""

SIDEBAR_HEADER_STYLE = """
QLabel#sidebarHeader {
    color: #f8fafc;
    font-size: 15px;
    font-weight: 700;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
"""

DEVICE_ITEM_STYLE = """
QFrame#deviceItem {
    background-color: #181a24;
    border: 1px solid #252838;
    border-radius: 10px;
    padding: 10px;
}
QFrame#deviceItem:hover {
    background-color: #1f2230;
    border-color: #3b4252;
}
"""

DEVICE_HOST_STYLE = """
QLabel#deviceHost {
    color: #f1f5f9;
    font-size: 13px;
    font-weight: 600;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
"""

DEVICE_IP_STYLE = """
QLabel#deviceIp {
    color: #64748b;
    font-size: 11px;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
"""

ACTIVE_INDICATOR_STYLE = """
QLabel#activeIndicator {
    background-color: #10b981;
    border-radius: 5px;
    min-width: 10px;
    max-width: 10px;
    min-height: 10px;
    max-height: 10px;
}
"""

INACTIVE_INDICATOR_STYLE = """
QLabel#activeIndicator {
    background-color: #475569;
    border-radius: 5px;
    min-width: 10px;
    max-width: 10px;
    min-height: 10px;
    max-height: 10px;
}
"""

DEVICE_TOGGLE_STYLE = """
QPushButton#deviceToggle {
    background-color: #1e2030;
    color: #10b981;
    font-size: 10px;
    font-weight: 800;
    font-family: 'Inter', sans-serif;
    border: 1px solid #2d3142;
    border-radius: 6px;
    padding: 4px 10px;
    min-width: 44px;
}
QPushButton#deviceToggle:checked {
    background-color: #10b981;
    color: #ffffff;
    border: none;
}
"""

DEVICE_ITEM_INACTIVE_STYLE = """
QFrame#deviceItemInactive {
    background-color: #0d0e12;
    border: 1px dashed #222533;
    border-radius: 10px;
    padding: 10px;
}
"""

VIDEO_SCREEN_STYLE = """
QFrame#videoScreen {
    background-color: #06070a;
    border: 1px solid #1e2030;
    border-radius: 14px;
}
"""

VIDEO_PLAY_ICON_STYLE = """
QLabel#videoPlayIcon {
    color: #1e2030;
    font-size: 56px;
    font-family: 'Inter', sans-serif;
}
"""

VIDEO_PREVIEW_TEXT_STYLE = """
QLabel#videoPreviewText {
    color: #3b4252;
    font-size: 13px;
    font-weight: 700;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
"""

TAB_WIDGET_STYLE = """
QTabWidget::pane {
    border: none;
    background-color: transparent;
    top: -1px;
}
QTabBar {
    background-color: transparent;
    qproperty-drawBase: 0;
}
QTabBar::tab {
    background-color: #0c0d12;
    color: #64748b;
    font-size: 12px;
    font-weight: 700;
    font-family: 'Inter', sans-serif;
    border: 1px solid #1e2030;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 8px 12px;
    margin-right: 4px;
}
QTabBar::tab:selected {
    background-color: #12131a;
    color: #f8fafc;
    border: 1px solid #232634;
    border-bottom: 2px solid #6366f1;
}
QTabBar::tab:hover:!selected {
    background-color: #1a1c29;
    color: #cbd5e1;
}
"""

QUEUE_ITEM_STYLE = """
QFrame#queueItem {
    background-color: #181a24;
    border: 1px solid #252838;
    border-radius: 10px;
    padding: 10px;
}
QFrame#queueItem:hover {
    background-color: #1f2230;
    border-color: #3b4252;
}
"""

QUEUE_TITLE_STYLE = """
QLabel#queueTitle {
    color: #e2e8f0;
    font-size: 12px;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
}
"""

QUEUE_DURATION_STYLE = """
QLabel#queueDuration {
    color: #64748b;
    font-size: 11px;
    font-family: 'Inter', sans-serif;
}
"""

QUEUE_INDEX_STYLE = """
QLabel#queueIndex {
    color: #6366f1;
    font-size: 11px;
    font-weight: 800;
    font-family: 'Inter', sans-serif;
}
"""

QUEUE_NAV_BUTTON_STYLE = """
QPushButton#queueNavBtn {
    background-color: #1e2030;
    color: #94a3b8;
    font-size: 8px;
    font-weight: bold;
    border: 1px solid #2d3142;
    border-radius: 4px;
    min-width: 20px;
    max-width: 20px;
    min-height: 18px;
    max-height: 18px;
}
QPushButton#queueNavBtn:hover {
    background-color: #2b2f44;
    color: #6366f1;
    border-color: #6366f1;
}
QPushButton#queueNavBtn:pressed {
    background-color: #13141f;
}
"""

GUEST_CONNECT_BUTTON_STYLE = """
QPushButton#connectButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #10b981, stop:1 #059669);
    color: #ffffff;
    font-size: 15px;
    font-weight: 700;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    border: none;
    border-radius: 12px;
    padding: 14px 28px;
    min-width: 180px;
}
QPushButton#connectButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #34d399, stop:1 #10b981);
    border: 1px solid rgba(255, 255, 255, 0.15);
}
QPushButton#connectButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #059669, stop:1 #047857);
}
"""

GUEST_DISCONNECT_BUTTON_STYLE = """
QPushButton#connectButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ef4444, stop:1 #dc2626);
    color: #ffffff;
    font-size: 15px;
    font-weight: 700;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    border: none;
    border-radius: 12px;
    padding: 14px 28px;
    min-width: 180px;
}
QPushButton#connectButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f87171, stop:1 #ef4444);
    border: 1px solid rgba(255, 255, 255, 0.15);
}
QPushButton#connectButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #dc2626, stop:1 #b91c1c);
}
"""






