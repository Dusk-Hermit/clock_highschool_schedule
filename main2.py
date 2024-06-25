import sys
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QGuiApplication, QPainter, QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton

from string import Template

class FullScreenWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Full Screen Window")
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)  # No title bar

        # Get the primary screen and set the window geometry
        screen = QGuiApplication.primaryScreen()
        geometry = screen.geometry()
        self.setGeometry(geometry)

        self.showFullScreen()

        self.initUI()

    def initUI(self):

        # Create a central widget with a vertical layout
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        # layout.setContentsMargins(0, 0, 0, 0)
        # layout.setSpacing(0)

        # Create a label for the overlay text
        overlay_label = QLabel('Hello, this is centered text!', self)
        overlay_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_label.setStyleSheet("font-size: 24px; color: white;")

        # Add the overlay label to the layout
        layout.addWidget(overlay_label)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # add a button
        button = QPushButton('Click me', self)
        layout.addWidget(button)
        button.clicked.connect(lambda: self.close())

        # Set the central widget
        self.setCentralWidget(central_widget)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        
        # Draw the image
        image_pixmap = QPixmap(r"C:\Users\Dusk_Hermit\Downloads\pixiv\ほうき星\ほうき星_2024-02-17_116153937_神里綾華_p0.jpg")  
        # Replace with your image path
        
        img_size = image_pixmap.size()
        this_size = self.size()
        size_to_use = img_size.scaled(this_size, Qt.AspectRatioMode.KeepAspectRatio)
        print(f'img_size: {img_size}, this_size: {this_size}, size_to_use: {size_to_use}')
        image_pixmap = image_pixmap.scaled(size_to_use)
        xy_pos =None
        if size_to_use.width() == this_size.width():
            xy_pos = (0, (this_size.height() - size_to_use.height()) // 2)
        elif size_to_use.height() == this_size.height():
            xy_pos = ((this_size.width() - size_to_use.width()) // 2, 0)
        else:
            raise ValueError('This should not happen')
        rect = QRect(*xy_pos, size_to_use.width(), size_to_use.height())
        painter.drawPixmap(rect, image_pixmap)
        
        
        # painter.drawPixmap(*position, image_pixmap)
        

def main():
    app = QApplication(sys.argv)
    window = FullScreenWindow()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
