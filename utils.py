import sys
from PyQt6.QtCore import Qt, QTimer, QTime,pyqtSignal,QObject,QDateTime,QEvent
from PyQt6.QtGui import QPixmap, QGuiApplication, QMouseEvent
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton

background_window = None
overlay_window = None


def close_windows():
    global background_window, overlay_window
    background_window.close()
    overlay_window.close()

time_points = [
    QTime(10, 0,0),   # 10:00
    QTime(12, 0,0),   # 12:00
    QTime(22, 16,0)   # 15:30
]

def compare_qtime(time1, time2):
    """
    Compare two QTime objects and return -1 if time1 is earlier,
    1 if time1 is later, and 0 if they are equal.
    """
    # Compare by converting to total seconds
    total_seconds1 = time1.hour() * 3600 + time1.minute() * 60 + time1.second()
    total_seconds2 = time2.hour() * 3600 + time2.minute() * 60 + time2.second()

    if total_seconds1 < total_seconds2:
        return -1
    elif total_seconds1 > total_seconds2:
        return 1
    else:
        return 0

class MainScheduler:
    def __init__(self,args=[[],[],[]]):
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_time)
        self.timer.start(1000)  # 每秒检查一次
        self.start_timepoints=args[0]
        self.end_timepoints=args[1]
        self.texts=args[2]
        
        self.ChildClock=None
        self.ChildBackground=None

        # check_time_on_start
        this_time=QTime.currentTime()
        for index in range(len(self.start_timepoints)):
            if this_time >=self.start_timepoints[index] and this_time < self.end_timepoints[index]:
                self.period_start(self.end_timepoints[index],self.texts[index])
                return
        for index in range(len(self.start_timepoints)-1):
            if this_time >=self.end_timepoints[index] and this_time <self.start_timepoints[index+1]:
                self.period_end(self.start_timepoints[index+1])
                return
        self.period_end(self.start_timepoints[0])

    def check_time(self):
        current_time = QDateTime.currentDateTime().time()

        for index, time_point in enumerate(self.start_timepoints):
            if compare_qtime(current_time,time_point)==0:
                self.period_start(self.end_timepoints[index],self.texts[index])
        for time_point in self.end_timepoints:
            if compare_qtime(current_time,time_point)==0:
                self.period_end(time_point)
    def period_start(self, time_point,clock_text):
        # start a clock, close the background
        if self.ChildBackground:
            self.ChildBackground.close()
            self.ChildBackground=None
        self.ChildClock=DraggableClock(
            {
                'to_time':time_point,
                'text':clock_text,
            }
        )
        self.ChildClock.show()
        print(f"Start a new time period.")
    
    def period_end(self,time_point):
        # close the clock, start the background
        if self.ChildClock:
            self.ChildClock.close()
            self.ChildClock=None
        self.ChildBackground=BackgroundWindow()
        self.ChildBackground.show()
        print(f"Reached time point:")
        
class DraggableClock(QWidget):
    def __init__(self,args):
        self.to_time=args['to_time']
        self.text=args['text']
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.layout = QVBoxLayout(self)
        
        self.clock_label = QLabel(self)
        self.clock_label.setStyleSheet("font-size: 24px; color: white; background-color: black; padding: 10px; border-radius: 10px;")
        self.clock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.clock_label)

        self.countdown_label = QLabel(self)
        self.countdown_label.setStyleSheet("font-size: 18px; color: white; background-color: black; padding: 5px; border-radius: 5px;")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.countdown_label)

        self.text_label = QLabel(self.text, self)
        self.text_label.setStyleSheet("font-size: 14px; color: white; background-color: black; padding: 5px; border-radius: 5px;")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.text_label)

        self.setLayout(self.layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)  # Update every second

        self.update_clock()

        # Set the position of the widget
        self.move(100, 100)

    def update_clock(self):
        current_time = QTime.currentTime()
        current_time_str = current_time.toString('hh:mm:ss')
        self.clock_label.setText(f"Current Time: {current_time_str}")

        target_time = self.to_time
        if current_time < target_time:
            time_to_target = current_time.secsTo(target_time)
            hours = time_to_target // 3600
            minutes = (time_to_target % 3600) // 60
            seconds = time_to_target % 60
            countdown_str = f"Countdown to {self.to_time.hour():02}:{self.to_time.minute():02}:{self.to_time.second():02}: {hours:02}:{minutes:02}:{seconds:02}"
        else:
            countdown_str = "Target time passed"

        self.countdown_label.setText(countdown_str)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.offset)

# class DraggableClock(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.initUI()

#     def initUI(self):
#         self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
#         self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

#         self.layout = QVBoxLayout()
#         self.clock_label = QLabel(self)
#         self.clock_label.setStyleSheet("font-size: 24px; color: white; background-color: black; padding: 10px; border-radius: 10px;")
#         self.clock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
#         self.layout.addWidget(self.clock_label)
#         self.setLayout(self.layout)

#         self.timer = QTimer(self)
#         self.timer.timeout.connect(self.update_clock)
#         self.timer.start(1000)  # Update every second

#         self.update_clock()

#     def update_clock(self):
#         current_time = QTime.currentTime().toString('hh:mm:ss')
#         self.clock_label.setText(current_time)

#     def mousePressEvent(self, event: QMouseEvent):
#         if event.button() == Qt.MouseButton.LeftButton:
#             self.offset = event.pos()

#     def mouseMoveEvent(self, event: QMouseEvent):
#         if event.buttons() == Qt.MouseButton.LeftButton:
#             self.move(event.globalPosition().toPoint() - self.offset)


class ChildWindow(QMainWindow):
    window_closed=pyqtSignal()
    window_minimized=pyqtSignal()
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Overlay Window")
        self.setWindowFlags(
            Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool
        )  # No title bar, stay on top, tool window

        # Get the primary screen and set the window geometry
        screen = QGuiApplication.primaryScreen()
        geometry = screen.geometry()
        self.setGeometry(geometry)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.initUI()
        # self.destroyed.connect(lambda: self.emit_window_closed)
    
    def child_minimize_and_emit(self):
        # self.showMinimized()
        self.close()
        self.window_minimized.emit()
    
    def child_close_and_emit(self):
        # 当前应用只有这一个窗口的时候，当唯一的窗口关掉了，那程序就关闭了
        self.close()
        self.window_closed.emit()
    
    def initUI(self):
        # Create a central widget with a transparent background
        central_widget = QWidget(self)
        central_widget.setStyleSheet("background: transparent;")
        self.setCentralWidget(central_widget)

        # Create a label for the overlay text
        overlay_label = QLabel("Hello, this is centered text!", self)
        overlay_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_label.setStyleSheet("font-size: 24px; color: white;")
        
        # button to close the window
        button = QPushButton('Click me', self)
        button.clicked.connect(self.child_minimize_and_emit)
        

        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(overlay_label)
        layout.addWidget(button)

class BackgroundWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Background Window")
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)  # No title bar

        # Get the primary screen and set the window geometry
        screen = QGuiApplication.primaryScreen()
        geometry = screen.geometry()
        self.setGeometry(geometry)

        self.showFullScreen()
        

        self.initUI()
        self.new_child()
    
    def new_child(self):
        self.child_window = ChildWindow()
        self.child_window.window_closed.connect(self.should_close)
        self.child_window.window_minimized.connect(self.should_minimize)
        self.child_window.show()
        self.child_window.setWindowFlags(
            Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool
        )
    
    def changeEvent(self,event):
        if event.type()==QEvent.Type.WindowStateChange:
            state=self.windowState()
            if (not state & Qt.WindowState.WindowMinimized )and state & Qt.WindowState.WindowFullScreen:
                print("background change to the fullscreen")
                self.new_child()
    
    def should_minimize(self):
        print(f'Background windows should minimize now.')
        self.showMinimized()
    def should_close(self):
        print(f'Background windows should close now.')
        self.close()
    
    def initUI(self):
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create a label for the background image
        background_label = QLabel(self)
        # img_pixmap = QPixmap(r"C:\Users\Dusk_Hermit\Downloads\pixiv\ほうき星\ほうき星_2024-02-17_116153937_神里綾華_p0.jpg")
        img_pixmap = QPixmap(r"C:\Users\Dusk_Hermit\Downloads\pixiv\Rafa\Rafa_黄泉_115941077_p0.jpg")
        img_pixmap = img_pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio)
        background_label.setPixmap(img_pixmap)
        layout.addWidget(background_label)
        
        self.setCentralWidget(central_widget)
        
