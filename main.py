import sys
from PyQt6.QtWidgets import QApplication
from src.ui import MainWindow

def main():
    # Initialize the Qt Application
    app = QApplication(sys.argv)
    
    # Create the main window
    window = MainWindow()
    
    # Center the window on the screen
    screen_geometry = app.primaryScreen().geometry()
    window_geometry = window.geometry()
    
    x = (screen_geometry.width() - window_geometry.width()) // 2
    y = (screen_geometry.height() - window_geometry.height()) // 2
    window.move(x, y)
    
    # Display the window
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
