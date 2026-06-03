import sys
import os
import time
import socket
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QGraphicsDropShadowEffect, QStackedWidget, 
    QMessageBox, QSlider, QFileDialog, QTabWidget, QLineEdit
)
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QColor, QCursor
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

from src.ui import styles
from src.ui.draggable_queue import QueueListWidget
from src.core.network import DiscoveryServer, DiscoveryClient, MediaServerThread

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Network thread state variables
        self.discovery_server = None
        self.discovery_client = None
        self.active_devices = {}  # {ip: {"hostname": str, "frame": QFrame, ...}}
        self.timeout_timer = None
        
        # Blocker streaming state
        self.media_server = None
        self.transmission_blocked = False
        
        # Native QMediaPlayer setup (Host)
        self.media_player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.media_player.setAudioOutput(self.audio_output)
        
        # Playback state signal listener for synchronization triggers
        self.media_player.playbackStateChanged.connect(self.on_playback_state_changed)
        
        # Native QMediaPlayer setup (Guest)
        self.guest_media_player = QMediaPlayer(self)
        self.guest_audio_output = QAudioOutput(self)
        self.guest_media_player.setAudioOutput(self.guest_audio_output)
        self.guest_media_player.errorOccurred.connect(self.on_guest_media_error)
        
        self.init_ui()

    def init_ui(self):
        # Window setup
        self.setWindowTitle("Video Blocker")
        self.resize(800, 600)
        self.setMinimumSize(720, 560)
        self.setStyleSheet(styles.MAIN_WINDOW_STYLE)

        # Main Stacked Widget
        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)

        # Create the views
        self.create_selection_view()
        self.create_host_view()
        self.create_guest_view()

        # Set initial view to selection menu
        self.stacked_widget.setCurrentIndex(0)

    def create_selection_view(self):
        # Selection screen container
        selection_widget = QWidget(self)
        selection_widget.setObjectName("centralWidget")
        selection_widget.setStyleSheet(styles.CENTRAL_WIDGET_STYLE)

        main_layout = QVBoxLayout(selection_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(0)

        # 1. Top Spacer
        main_layout.addStretch(1)

        # 2. Title Section
        self.title_label = QLabel("VIDEO BLOCKER", self)
        self.title_label.setObjectName("appTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(styles.TITLE_STYLE)
        main_layout.addWidget(self.title_label)

        self.subtitle_label = QLabel("Select your environment role to continue", self)
        self.subtitle_label.setObjectName("appSubtitle")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setStyleSheet(styles.SUBTITLE_STYLE)
        main_layout.addWidget(self.subtitle_label)

        # 3. Card Frame (Elevated Container)
        self.card_frame = QFrame(self)
        self.card_frame.setObjectName("cardFrame")
        self.card_frame.setStyleSheet(styles.CARD_STYLE)
        
        # Add drop shadow
        card_shadow = QGraphicsDropShadowEffect(self)
        card_shadow.setBlurRadius(30)
        card_shadow.setColor(QColor(0, 0, 0, 160))
        card_shadow.setOffset(0, 10)
        self.card_frame.setGraphicsEffect(card_shadow)

        card_layout = QHBoxLayout(self.card_frame)
        card_layout.setContentsMargins(24, 40, 24, 40)
        card_layout.setSpacing(20)

        # Host Button
        self.host_button = QPushButton("Host", self)
        self.host_button.setObjectName("hostButton")
        self.host_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.host_button.setStyleSheet(styles.HOST_BUTTON_STYLE)
        self.host_button.clicked.connect(self.on_host_clicked)
        card_layout.addWidget(self.host_button)

        # Guest Button
        self.guest_button = QPushButton("Guest", self)
        self.guest_button.setObjectName("guestButton")
        self.guest_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.guest_button.setStyleSheet(styles.GUEST_BUTTON_STYLE)
        self.guest_button.clicked.connect(self.on_guest_clicked)
        card_layout.addWidget(self.guest_button)

        main_layout.addWidget(self.card_frame)

        # 4. Bottom Spacer
        main_layout.addStretch(2)

        # 5. Footer Text
        self.footer_label = QLabel("v1.0.0 • Developed with PyQt6", self)
        self.footer_label.setObjectName("footerText")
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer_label.setStyleSheet(styles.FOOTER_STYLE)
        main_layout.addWidget(self.footer_label)

        self.stacked_widget.addWidget(selection_widget)

    def create_host_view(self):
        # Host screen container
        host_widget = QWidget(self)
        host_widget.setObjectName("centralWidget")
        host_widget.setStyleSheet(styles.CENTRAL_WIDGET_STYLE)

        main_layout = QVBoxLayout(host_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Header Bar
        header_bar = QWidget(self)
        header_bar.setObjectName("dashboardHeader")
        header_bar.setStyleSheet(styles.DASHBOARD_HEADER_STYLE)
        
        header_layout = QHBoxLayout(header_bar)
        header_layout.setContentsMargins(20, 15, 20, 15)

        # Back button
        back_btn = QPushButton("◀ Volver", self)
        back_btn.setObjectName("backButton")
        back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        back_btn.setStyleSheet(styles.BACK_BUTTON_STYLE)
        back_btn.clicked.connect(self.go_to_menu)
        header_layout.addWidget(back_btn)

        header_layout.addStretch(1)

        # Header Title
        header_title = QLabel("PANEL DE CONTROL HOST", self)
        header_title.setObjectName("dashboardTitle")
        header_title.setStyleSheet(styles.DASHBOARD_TITLE_STYLE)
        header_layout.addWidget(header_title)

        header_layout.addStretch(1)

        # Status badge indicator
        status_container = QHBoxLayout()
        status_container.setSpacing(8)
        status_indicator = QLabel(self)
        status_indicator.setObjectName("activeIndicator")
        status_indicator.setStyleSheet(styles.ACTIVE_INDICATOR_STYLE)
        
        status_text = QLabel("Servidor Activo", self)
        status_text.setStyleSheet("color: #10b981; font-size: 13px; font-weight: 700; font-family: 'Inter';")
        status_container.addWidget(status_indicator)
        status_container.addWidget(status_text)
        
        header_layout.addLayout(status_container)
        main_layout.addWidget(header_bar)

        # 2. Content Area (Two Columns Layout)
        content_widget = QWidget(self)
        content_widget.setStyleSheet("background-color: transparent;")
        
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        # Left Column: Video Controls Panel (Stretch 3)
        playback_panel = QFrame(self)
        playback_panel.setObjectName("playbackPanel")
        playback_panel.setStyleSheet(styles.PLAYBACK_PANEL_STYLE)
        
        panel_shadow = QGraphicsDropShadowEffect(self)
        panel_shadow.setBlurRadius(20)
        panel_shadow.setColor(QColor(0, 0, 0, 120))
        panel_shadow.setOffset(0, 6)
        playback_panel.setGraphicsEffect(panel_shadow)

        playback_layout = QVBoxLayout(playback_panel)
        playback_layout.setContentsMargins(25, 25, 25, 25)
        playback_layout.setSpacing(20)

        # Section Header
        playback_header = QLabel("Control de Reproducción", self)
        playback_header.setObjectName("playbackHeader")
        playback_header.setStyleSheet(styles.PLAYBACK_HEADER_STYLE)
        playback_layout.addWidget(playback_header)

        # Video Preview Display Area (Using QStackedWidget to host viewport dynamically)
        self.video_preview = QFrame(self)
        self.video_preview.setObjectName("videoScreen")
        self.video_preview.setFixedHeight(260)
        self.video_preview.setStyleSheet(styles.VIDEO_SCREEN_STYLE)
        
        self.video_stack = QStackedWidget(self.video_preview)
        
        # Page 0: Dark Placeholder Screen
        placeholder_widget = QWidget(self)
        placeholder_layout = QVBoxLayout(placeholder_widget)
        placeholder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_layout.setSpacing(12)
        
        play_icon = QLabel("▶", self)
        play_icon.setObjectName("videoPlayIcon")
        play_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        play_icon.setStyleSheet(styles.VIDEO_PLAY_ICON_STYLE)
        placeholder_layout.addWidget(play_icon)
        
        self.preview_text = QLabel("Vista Previa del Video\nNingún archivo cargado", self)
        self.preview_text.setObjectName("videoPreviewText")
        self.preview_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_text.setStyleSheet(styles.VIDEO_PREVIEW_TEXT_STYLE)
        placeholder_layout.addWidget(self.preview_text)
        
        self.video_stack.addWidget(placeholder_widget)
        
        # Page 1: Native Video Viewport Widget
        self.video_widget = QVideoWidget(self)
        self.video_stack.addWidget(self.video_widget)
        
        # Add stack to outer preview frame layout
        preview_outer_layout = QVBoxLayout(self.video_preview)
        preview_outer_layout.setContentsMargins(0, 0, 0, 0)
        preview_outer_layout.addWidget(self.video_stack)
        
        # Attach player viewport
        self.media_player.setVideoOutput(self.video_widget)
        
        playback_layout.addWidget(self.video_preview)

        # Timeline Slider
        slider_layout = QVBoxLayout()
        slider_layout.setSpacing(6)

        timeline_labels = QHBoxLayout()
        self.time_curr = QLabel("00:00", self)
        self.time_curr.setObjectName("timeLabel")
        self.time_curr.setStyleSheet(styles.TIME_LABEL_STYLE)
        self.time_total = QLabel("00:00", self)
        self.time_total.setObjectName("timeLabel")
        self.time_total.setStyleSheet(styles.TIME_LABEL_STYLE)
        timeline_labels.addWidget(self.time_curr)
        timeline_labels.addStretch(1)
        timeline_labels.addWidget(self.time_total)
        slider_layout.addLayout(timeline_labels)

        self.progress_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.progress_slider.setValue(0) 
        self.progress_slider.setStyleSheet(styles.SLIDER_STYLE)
        self.progress_slider.sliderMoved.connect(self.set_media_position)
        slider_layout.addWidget(self.progress_slider)

        playback_layout.addLayout(slider_layout)

        # Connect QMediaPlayer signals to keep slider & timestamps in sync
        self.media_player.positionChanged.connect(self.on_position_changed)
        self.media_player.durationChanged.connect(self.on_duration_changed)

        # Media Control Buttons (Includes "Abrir Video" at the start)
        media_btn_layout = QHBoxLayout()
        media_btn_layout.setSpacing(12)
        media_btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        open_btn = QPushButton("📁  Abrir Video", self)
        open_btn.setObjectName("mediaButton")
        open_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        open_btn.setStyleSheet(styles.MEDIA_BUTTON_STYLE)
        open_btn.clicked.connect(self.on_browse_clicked)
        media_btn_layout.addWidget(open_btn)

        play_btn = QPushButton("▶  Play", self)
        play_btn.setObjectName("mediaButton")
        play_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        play_btn.setStyleSheet(styles.MEDIA_BUTTON_STYLE)
        play_btn.clicked.connect(self.media_player.play)
        media_btn_layout.addWidget(play_btn)

        pause_btn = QPushButton("❚❚  Pause", self)
        pause_btn.setObjectName("mediaButton")
        pause_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        pause_btn.setStyleSheet(styles.MEDIA_BUTTON_STYLE)
        pause_btn.clicked.connect(self.media_player.pause)
        media_btn_layout.addWidget(pause_btn)

        stop_btn = QPushButton("■  Stop", self)
        stop_btn.setObjectName("mediaButton")
        stop_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        stop_btn.setStyleSheet(styles.MEDIA_BUTTON_STYLE)
        stop_btn.clicked.connect(self.on_stop_clicked)
        media_btn_layout.addWidget(stop_btn)

        playback_layout.addLayout(media_btn_layout)

        playback_layout.addStretch(1)

        # Giant Blocker Button
        self.block_btn = QPushButton("BLOQUEAR TRANSMISIÓN", self)
        self.block_btn.setObjectName("blockButton")
        self.block_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.block_btn.setStyleSheet(styles.BLOCK_BUTTON_STYLE)
        self.block_btn.clicked.connect(self.on_block_clicked)
        
        red_shadow = QGraphicsDropShadowEffect(self)
        red_shadow.setBlurRadius(20)
        red_shadow.setColor(QColor(239, 68, 68, 90))
        red_shadow.setOffset(0, 4)
        self.block_btn.setGraphicsEffect(red_shadow)
        
        playback_layout.addWidget(self.block_btn)

        content_layout.addWidget(playback_panel, stretch=3)

        # Right Column: Tabbed Sidebar Panel (Stretch 1)
        sidebar_panel = QFrame(self)
        sidebar_panel.setObjectName("sidebarPanel")
        sidebar_panel.setFixedWidth(280)
        sidebar_panel.setStyleSheet(styles.SIDEBAR_PANEL_STYLE)
        
        sidebar_shadow = QGraphicsDropShadowEffect(self)
        sidebar_shadow.setBlurRadius(20)
        sidebar_shadow.setColor(QColor(0, 0, 0, 120))
        sidebar_shadow.setOffset(0, 6)
        sidebar_panel.setGraphicsEffect(sidebar_shadow)

        sidebar_layout = QVBoxLayout(sidebar_panel)
        sidebar_layout.setContentsMargins(10, 15, 10, 15)
        sidebar_layout.setSpacing(10)

        # Sidebar Title
        self.sidebar_header = QLabel("Clientes Conectados (0)", self)
        self.sidebar_header.setObjectName("sidebarHeader")
        self.sidebar_header.setStyleSheet(styles.SIDEBAR_HEADER_STYLE)
        sidebar_layout.addWidget(self.sidebar_header)

        # QTabWidget
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setStyleSheet(styles.TAB_WIDGET_STYLE)

        # --- TAB 1: Dispositivos ---
        devices_tab = QWidget()
        devices_tab_layout = QVBoxLayout(devices_tab)
        devices_tab_layout.setContentsMargins(4, 10, 4, 4)
        devices_tab_layout.setSpacing(10)

        # Devices list container (starts empty, dynamic addition)
        self.devices_list_layout = QVBoxLayout()
        self.devices_list_layout.setSpacing(10)

        devices_tab_layout.addLayout(self.devices_list_layout)
        devices_tab_layout.addStretch(1)
        self.tab_widget.addTab(devices_tab, "Dispositivos")

        # --- TAB 2: Cola de Reproducción ---
        queue_tab = QWidget()
        queue_tab_layout = QVBoxLayout(queue_tab)
        queue_tab_layout.setContentsMargins(4, 10, 4, 4)
        queue_tab_layout.setSpacing(10)

        # Draggable Queue List replacing static rendering
        self.queue_list = QueueListWidget(self)
        
        # Initial simulated play queue data
        queue_items = [
            ("01", "introduccion_proyecto.mp4", "04:12"),
            ("02", "demo_bloqueador_v2.mkv", "08:45"),
            ("03", "feedback_cliente.mp4", "12:10"),
        ]
        self.queue_list.populate(queue_items)
        
        queue_tab_layout.addWidget(self.queue_list)
        self.tab_widget.addTab(queue_tab, "Cola")

        sidebar_layout.addWidget(self.tab_widget)
        content_layout.addWidget(sidebar_panel, stretch=1)

        main_layout.addWidget(content_widget, stretch=1)

        self.stacked_widget.addWidget(host_widget)

    def create_guest_view(self):
        # Guest screen container
        guest_widget = QWidget(self)
        guest_widget.setObjectName("centralWidget")
        guest_widget.setStyleSheet(styles.CENTRAL_WIDGET_STYLE)

        guest_outer_layout = QVBoxLayout(guest_widget)
        guest_outer_layout.setContentsMargins(0, 0, 0, 0)
        guest_outer_layout.setSpacing(0)

        # Guest view stack manager
        self.guest_stack = QStackedWidget(guest_widget)
        guest_outer_layout.addWidget(self.guest_stack)

        # PAGE 0: Connection Panel View
        connection_widget = QWidget(self)
        connection_widget.setObjectName("centralWidget")
        connection_widget.setStyleSheet(styles.CENTRAL_WIDGET_STYLE)
        
        connection_layout = QVBoxLayout(connection_widget)
        connection_layout.setContentsMargins(40, 40, 40, 40)
        connection_layout.addStretch(1)

        # Container card
        container = QFrame(self)
        container.setObjectName("roleContainer")
        container.setStyleSheet(styles.ROLE_CONTAINER_STYLE)

        # Shadow for container
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 140))
        shadow.setOffset(0, 8)
        container.setGraphicsEffect(shadow)

        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(30, 40, 30, 40)
        container_layout.setSpacing(25)

        # Large "GUEST" Label
        guest_title = QLabel("MODO GUEST", self)
        guest_title.setObjectName("roleTitle")
        guest_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        guest_title.setStyleSheet(styles.ROLE_TITLE_STYLE)
        container_layout.addWidget(guest_title)

        # Connection status label
        self.guest_status_label = QLabel("Estado: Desconectado", self)
        self.guest_status_label.setStyleSheet("color: #94a3b8; font-size: 14px; font-weight: 600; font-family: 'Inter';")
        self.guest_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.guest_status_label)

        # IP Input layout
        ip_layout = QVBoxLayout()
        ip_layout.setSpacing(8)
        
        ip_label = QLabel("Dirección IP del Host (para VPN/Tailscale):", self)
        ip_label.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 600; font-family: 'Inter';")
        ip_layout.addWidget(ip_label)

        self.guest_ip_input = QLineEdit(self)
        self.guest_ip_input.setObjectName("pathInput")
        self.guest_ip_input.setPlaceholderText("Ej. 100.115.12.34 (Dejar vacío para auto-descubrimiento en LAN)")
        self.guest_ip_input.setStyleSheet(styles.PATH_INPUT_STYLE)
        ip_layout.addWidget(self.guest_ip_input)
        
        container_layout.addLayout(ip_layout)

        # Connect button
        self.guest_connect_btn = QPushButton("Conectar", self)
        self.guest_connect_btn.setObjectName("connectButton")
        self.guest_connect_btn.setCheckable(True)
        self.guest_connect_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.guest_connect_btn.setStyleSheet(styles.GUEST_CONNECT_BUTTON_STYLE)
        self.guest_connect_btn.clicked.connect(self.on_guest_connect_clicked)
        container_layout.addWidget(self.guest_connect_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Back Button
        back_btn = QPushButton("Volver", self)
        back_btn.setObjectName("backButton")
        back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        back_btn.setStyleSheet(styles.BACK_BUTTON_STYLE)
        back_btn.clicked.connect(self.go_to_menu)
        container_layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        connection_layout.addWidget(container)
        connection_layout.addStretch(1)
        self.guest_stack.addWidget(connection_widget)

        # PAGE 1: Control-less Video Viewport for Host Broadcasting
        self.guest_video_widget = QVideoWidget(self)
        self.guest_video_widget.setStyleSheet("background-color: #000000;")
        self.guest_stack.addWidget(self.guest_video_widget)

        # Bind Guest video player output canvas
        self.guest_media_player.setVideoOutput(self.guest_video_widget)

        self.stacked_widget.addWidget(guest_widget)

    def on_guest_connect_clicked(self):
        if self.guest_connect_btn.isChecked():
            host_ip = self.guest_ip_input.text().strip()
            if not host_ip:
                host_ip = None # Fallback to auto-discovery
                
            self.guest_status_label.setText("Estado: Conectado (Unicast)" if host_ip else "Estado: Escuchando Broadcast...")
            self.guest_status_label.setStyleSheet("color: #10b981; font-size: 14px; font-weight: 600; font-family: 'Inter';")
            
            # Start client thread
            self.discovery_client = DiscoveryClient(host_ip, self)
            self.discovery_client.block_triggered.connect(self.on_guest_block_triggered)
            self.discovery_client.unblock_triggered.connect(self.on_guest_unblock_triggered)
            self.discovery_client.play_triggered.connect(self.guest_media_player.play)
            self.discovery_client.pause_triggered.connect(self.guest_media_player.pause)
            self.discovery_client.seek_triggered.connect(self.guest_media_player.setPosition)
            self.discovery_client.sync_triggered.connect(self.on_guest_sync_triggered)
            self.discovery_client.start()
            
            # Toggle button text and styling to red disconnect
            self.guest_connect_btn.setText("Desconectar")
            self.guest_connect_btn.setStyleSheet(styles.GUEST_DISCONNECT_BUTTON_STYLE)
            self.guest_ip_input.setEnabled(False)
        else:
            if self.discovery_client:
                self.discovery_client.stop()
                self.discovery_client = None
                
            self.on_guest_unblock_triggered() # Clear video canvas and reset view stack
            
            self.guest_status_label.setText("Estado: Desconectado")
            self.guest_status_label.setStyleSheet("color: #94a3b8; font-size: 14px; font-weight: 600; font-family: 'Inter';")
            self.guest_connect_btn.setText("Conectar")
            self.guest_connect_btn.setStyleSheet(styles.GUEST_CONNECT_BUTTON_STYLE)
            self.guest_ip_input.setEnabled(True)

    def add_or_update_discovered_device(self, hostname, ip):
        now = time.time()
        
        # If device is already in active tracker list, update last seen stamp and return
        if ip in self.active_devices:
            self.active_devices[ip]["last_seen"] = now
            return

        print(f"[NETWORK] Discovered active client: {hostname} ({ip})")
        
        # Construct device card dynamically
        dev_frame = QFrame(self)
        dev_frame.setObjectName("deviceItem")
        dev_frame.setStyleSheet(styles.DEVICE_ITEM_STYLE)
        
        dev_layout = QHBoxLayout(dev_frame)
        dev_layout.setContentsMargins(10, 8, 10, 8)
        dev_layout.setSpacing(8)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        host_label = QLabel(hostname, self)
        host_label.setObjectName("deviceHost")
        host_label.setStyleSheet(styles.DEVICE_HOST_STYLE)
        
        ip_label = QLabel(ip, self)
        ip_label.setObjectName("deviceIp")
        ip_label.setStyleSheet(styles.DEVICE_IP_STYLE)
        
        text_layout.addWidget(host_label)
        text_layout.addWidget(ip_label)
        
        dev_layout.addLayout(text_layout)
        dev_layout.addStretch(1)
        
        # Active/Inactive indicator dot
        green_dot = QLabel(self)
        green_dot.setObjectName("activeIndicator")
        green_dot.setStyleSheet(styles.ACTIVE_INDICATOR_STYLE)
        dev_layout.addWidget(green_dot, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Checkable active/inactive toggle button (ON/OFF)
        toggle_btn = QPushButton("ON", self)
        toggle_btn.setObjectName("deviceToggle")
        toggle_btn.setCheckable(True)
        toggle_btn.setChecked(True)
        toggle_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        toggle_btn.setStyleSheet(styles.DEVICE_TOGGLE_STYLE)
        
        # Connect toggle handler to visually dim item and swap button tags
        toggle_btn.toggled.connect(
            lambda checked, h=hostname, f=dev_frame, btn=toggle_btn, dot=green_dot, hl=host_label, ipl=ip_label: 
            self.on_device_toggled(h, checked, f, btn, dot, hl, ipl)
        )
        dev_layout.addWidget(toggle_btn, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        # Insert card widget into the layouts list
        self.devices_list_layout.addWidget(dev_frame)
        
        # Track device state references
        self.active_devices[ip] = {
            "hostname": hostname,
            "frame": dev_frame,
            "btn": toggle_btn,
            "dot": green_dot,
            "hl": host_label,
            "ipl": ip_label,
            "last_seen": now,
            "active": True
        }
        
        self.update_devices_count()

        # If a late Guest connects and transmission is blocked, sync them immediately
        if self.transmission_blocked and self.discovery_server:
            host_ip = self.get_local_ip()
            stream_url = f"http://{host_ip}:50007/video"
            self.discovery_server.send_command(ip, f"BLOCK_VIDEO:{stream_url}")
            curr_pos = self.media_player.position()
            self.discovery_server.send_command(ip, f"SEEK:{curr_pos}")
            if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                self.discovery_server.send_command(ip, "PLAY")
            else:
                self.discovery_server.send_command(ip, "PAUSE")

    def check_device_timeouts(self):
        now = time.time()
        to_delete = []
        for ip, device_info in self.active_devices.items():
            # If no packet was received from client in past 8 seconds, consider timed out
            if now - device_info["last_seen"] > 8.0:
                to_delete.append(ip)
                
        for ip in to_delete:
            print(f"[NETWORK] Client {self.active_devices[ip]['hostname']} ({ip}) timed out. Removing.")
            device_info = self.active_devices[ip]
            
            # Remove widget card from layout list
            self.devices_list_layout.removeWidget(device_info["frame"])
            device_info["frame"].deleteLater()
            
            del self.active_devices[ip]
            
        if to_delete:
            self.update_devices_count()

    def update_devices_count(self):
        if hasattr(self, 'sidebar_header'):
            self.sidebar_header.setText(f"Clientes Conectados ({len(self.active_devices)})")

    def on_device_toggled(self, hostname, active, frame, button, dot, host_label, ip_label):
        for ip, device_info in self.active_devices.items():
            if device_info["hostname"] == hostname:
                device_info["active"] = active
                # If blocker is active, immediately unblock or block the device that was toggled
                if self.transmission_blocked and self.discovery_server:
                    if active:
                        host_ip = self.get_local_ip()
                        stream_url = f"http://{host_ip}:50007/video"
                        self.discovery_server.send_command(ip, f"BLOCK_VIDEO:{stream_url}")
                        curr_pos = self.media_player.position()
                        self.discovery_server.send_command(ip, f"SEEK:{curr_pos}")
                        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                            self.discovery_server.send_command(ip, "PLAY")
                        else:
                            self.discovery_server.send_command(ip, "PAUSE")
                    else:
                        self.discovery_server.send_command(ip, "UNBLOCK")
                break

        if active:
            button.setText("ON")
            dot.setStyleSheet(styles.ACTIVE_INDICATOR_STYLE)
            frame.setObjectName("deviceItem")
            frame.setStyleSheet(styles.DEVICE_ITEM_STYLE)
            host_label.setStyleSheet("color: #f1f5f9;")
            ip_label.setStyleSheet("color: #64748b;")
            print(f"[ACTION] Device {hostname} ENABLED.")
        else:
            button.setText("OFF")
            dot.setStyleSheet(styles.INACTIVE_INDICATOR_STYLE)
            frame.setObjectName("deviceItemInactive")
            frame.setStyleSheet(styles.DEVICE_ITEM_INACTIVE_STYLE)
            host_label.setStyleSheet("color: #475569;")
            ip_label.setStyleSheet("color: #334155;")
            print(f"[ACTION] Device {hostname} DISABLED.")
        
        # Repaint styles for the modified frame
        frame.style().unpolish(frame)
        frame.style().polish(frame)

    # QMediaPlayer event slot callbacks
    def on_position_changed(self, position):
        if not self.progress_slider.isSliderDown():
            self.progress_slider.setValue(position)
        self.time_curr.setText(self.format_time(position))
        
        # Periodic drift sync corrections (every 3 seconds)
        if self.transmission_blocked:
            now = time.time()
            if not hasattr(self, 'last_sync_time'):
                self.last_sync_time = 0
            if now - self.last_sync_time > 3.0:
                self.last_sync_time = now
                self.broadcast_command(f"SYNC:{position}")

    def on_duration_changed(self, duration):
        self.progress_slider.setRange(0, duration)
        self.time_total.setText(self.format_time(duration))

    def set_media_position(self, position):
        self.media_player.setPosition(position)
        if self.transmission_blocked:
            self.broadcast_command(f"SEEK:{position}")

    def on_stop_clicked(self):
        self.media_player.stop()
        self.progress_slider.setValue(0)
        self.time_curr.setText("00:00")
        print("[PLAYBACK] Stop clicked. Resetting timeline.")
        if self.transmission_blocked:
            self.broadcast_command("UNBLOCK")

    def format_time(self, ms):
        seconds = (ms // 1000) % 60
        minutes = (ms // 60000) % 60
        hours = (ms // 3600000)
        if hours > 0:
            return f"{hours:d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

    def on_browse_clicked(self):
        print("[ACTION] Open file clicked. Opening file dialog...")
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo de video", "", "Video Files (*.mp4 *.mkv *.avi *.mov *.wmv)"
        )
        if file_path:
            filename = os.path.basename(file_path)
            self.preview_text.setText(f"Vista Previa del Video\nCargado: {filename}")
            print(f"[ACTION] Selected video: {file_path}")
            
            # Load selected local video path to media player and swap view stack index
            self.media_player.setSource(QUrl.fromLocalFile(file_path))
            self.video_stack.setCurrentIndex(1)

    def on_host_clicked(self):
        print("[ACTION] Host role selected!")
        self.stacked_widget.setCurrentIndex(1)
        
        # Clean state tracker
        self.active_devices = {}
        self.update_devices_count()
        
        # Start UDP Discovery Server thread
        self.discovery_server = DiscoveryServer(self)
        self.discovery_server.device_found.connect(self.add_or_update_discovered_device)
        self.discovery_server.start()
        
        # Start Timeout pruning timer
        self.timeout_timer = QTimer(self)
        self.timeout_timer.timeout.connect(self.check_device_timeouts)
        self.timeout_timer.start(2000) # Check timeouts every 2 seconds

    def on_guest_clicked(self):
        print("[ACTION] Guest button clicked. Verifying OS...")
        
        # Enforce Windows-only requirement for Guest view
        if sys.platform != "win32":
            print(f"[ACTION] OS is {sys.platform}. OS is not Windows! Displaying warning alert.")
            
            # Show a beautifully styled warning alert box
            alert = QMessageBox(self)
            alert.setIcon(QMessageBox.Icon.Warning)
            alert.setWindowTitle("Compatibilidad")
            alert.setText("Esta función solo es soportada en Windows.")
            alert.setStyleSheet(styles.MESSAGE_BOX_STYLE)
            alert.exec()
        else:
            print("[ACTION] OS is Windows. Navigating to Guest View.")
            self.stacked_widget.setCurrentIndex(2)

    def on_block_clicked(self):
        if not self.transmission_blocked:
            # Check if video is loaded
            if not self.media_player.source().isValid() or self.media_player.source().isEmpty():
                alert = QMessageBox(self)
                alert.setIcon(QMessageBox.Icon.Warning)
                alert.setWindowTitle("Advertencia")
                alert.setText("Debe cargar un archivo de video antes de bloquear la transmisión.")
                alert.setStyleSheet(styles.MESSAGE_BOX_STYLE)
                alert.exec()
                return

            print("[ACTION] TRANSMISSION BLOCKED! Initializing Media Server and signaling Guests.")
            self.transmission_blocked = True
            
            # Change block button text & style to warning alert orange color
            self.block_btn.setText("DESBLOQUEAR TRANSMISIÓN")
            self.block_btn.setStyleSheet("""
                QPushButton#blockButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #d97706, stop:1 #b45309);
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
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fbbf24, stop:1 #d97706);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }
                QPushButton#blockButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b45309, stop:1 #92400e);
                }
            """)
            
            # Get loaded video path and fire up HTTP Range Server QThread
            local_file = self.media_player.source().toLocalFile()
            self.media_server = MediaServerThread(local_file, port=50007, parent=self)
            self.media_server.start()
            
            # Format and send BLOCK command to active Clients
            host_ip = self.get_local_ip()
            stream_url = f"http://{host_ip}:50007/video"
            self.broadcast_command(f"BLOCK_VIDEO:{stream_url}")
            
            # Synchronize position and state
            curr_pos = self.media_player.position()
            self.broadcast_command(f"SEEK:{curr_pos}")
            if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                self.broadcast_command("PLAY")
            else:
                self.broadcast_command("PAUSE")

        else:
            print("[ACTION] TRANSMISSION UNBLOCKED! Stopping Server and resetting Guests.")
            self.transmission_blocked = False
            
            # Restore block button style
            self.block_btn.setText("BLOQUEAR TRANSMISIÓN")
            self.block_btn.setStyleSheet(styles.BLOCK_BUTTON_STYLE)
            
            # Stop Media Server
            if self.media_server:
                self.media_server.stop()
                self.media_server = None
                
            # Broadcast unblock command
            self.broadcast_command("UNBLOCK")

    def broadcast_command(self, command):
        if self.discovery_server:
            for ip, dev in self.active_devices.items():
                if dev.get("active", True):
                    self.discovery_server.send_command(ip, command)

    def on_playback_state_changed(self, state):
        if not self.transmission_blocked:
            return
            
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.broadcast_command("PLAY")
        elif state == QMediaPlayer.PlaybackState.PausedState:
            self.broadcast_command("PAUSE")
        elif state == QMediaPlayer.PlaybackState.StoppedState:
            self.broadcast_command("UNBLOCK")

    # Guest listener callbacks
    def on_guest_block_triggered(self, url):
        print(f"[GUEST] Blocker triggered! Source stream: {url}")
        self.guest_media_player.setSource(QUrl(url))
        self.guest_stack.setCurrentIndex(1)
        self.guest_media_player.play()

    def on_guest_unblock_triggered(self):
        print("[GUEST] Blocker disabled. Restoring UI control dashboard.")
        self.guest_media_player.stop()
        self.guest_media_player.setSource(QUrl())
        self.guest_stack.setCurrentIndex(0)

    def on_guest_sync_triggered(self, host_position):
        guest_position = self.guest_media_player.position()
        # If play drift exceeds 1.0 second, force alignment
        if abs(guest_position - host_position) > 1000:
            print(f"[GUEST] Correcting playback drift: Host={host_position}ms, Guest={guest_position}ms")
            self.guest_media_player.setPosition(host_position)

    def on_guest_media_error(self, error, error_string):
        print(f"[GUEST ERROR] Media Player error encountered: {error_string} (Code: {error})")

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Doesn't need to connect successfully, just assigns an interface
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    def go_to_menu(self):
        print("[ACTION] Navigating back to main menu.")
        
        # Halt QMediaPlayer media playback cleanly
        self.media_player.stop()
        self.video_stack.setCurrentIndex(0)
        self.preview_text.setText("Vista Previa del Video\nNingún archivo cargado")
        self.time_curr.setText("00:00")
        self.time_total.setText("00:00")
        self.progress_slider.setValue(0)
        
        # Stop Server socket thread
        if self.discovery_server:
            self.discovery_server.stop()
            self.discovery_server = None
            
        # Stop timeout timer
        if self.timeout_timer:
            self.timeout_timer.stop()
            self.timeout_timer = None
            
        # Stop media server and unblock if active
        if hasattr(self, 'media_server') and self.media_server:
            self.broadcast_command("UNBLOCK")
            self.media_server.stop()
            self.media_server = None
        self.transmission_blocked = False
        self.block_btn.setText("BLOQUEAR TRANSMISIÓN")
        self.block_btn.setStyleSheet(styles.BLOCK_BUTTON_STYLE)
            
        # Clean UI devices layout
        if hasattr(self, 'devices_list_layout'):
            while self.devices_list_layout.count() > 0:
                item = self.devices_list_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                    
        self.active_devices = {}
        self.update_devices_count()
        
        # Stop Guest socket thread
        if self.discovery_client:
            self.discovery_client.stop()
            self.discovery_client = None
            
        # Clean up Guest player and stack
        if hasattr(self, 'guest_media_player'):
            self.guest_media_player.stop()
            self.guest_media_player.setSource(QUrl())
        if hasattr(self, 'guest_stack'):
            self.guest_stack.setCurrentIndex(0)
            
        # Reset Guest UI controls if they exist
        if hasattr(self, 'guest_connect_btn') and self.guest_connect_btn is not None:
            self.guest_connect_btn.setChecked(False)
            self.guest_connect_btn.setText("Conectar")
            self.guest_connect_btn.setStyleSheet(styles.GUEST_CONNECT_BUTTON_STYLE)
        if hasattr(self, 'guest_ip_input') and self.guest_ip_input is not None:
            self.guest_ip_input.setEnabled(True)
            self.guest_ip_input.clear()
        if hasattr(self, 'guest_status_label') and self.guest_status_label is not None:
            self.guest_status_label.setText("Estado: Desconectado")
            self.guest_status_label.setStyleSheet("color: #94a3b8; font-size: 14px; font-weight: 600; font-family: 'Inter';")
            
        self.stacked_widget.setCurrentIndex(0)
