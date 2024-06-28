import sys, os, shutil, random, time
from PyQt6.QtCore import Qt, QTimer, QTime, pyqtSignal, QObject, QDateTime, QEvent
from PyQt6.QtGui import QPixmap, QGuiApplication, QMouseEvent, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QSystemTrayIcon,
)
import soundfile as sf
import sounddevice as sd

TIME_DELAY = 0.1

def play_wav(file_path):
    # 使用 soundfile 读取音频文件
    data, samplerate = sf.read(file_path)
    # 使用 sounddevice 播放音频
    sd.play(data, samplerate, blocking=False)
    # sd.wait()  # 等待播放完毕


background_window = None
overlay_window = None


def close_windows():
    global background_window, overlay_window
    background_window.close()
    overlay_window.close()


time_points = [
    QTime(10, 0, 0),  # 10:00
    QTime(12, 0, 0),  # 12:00
    QTime(22, 16, 0),  # 15:30
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
    def __init__(self, args={}):
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_time)
        self.timer.start(1000)  # 每秒检查一次
        self.start_timepoints = args.get("start_timepoints", [])
        self.end_timepoints = args.get("end_timepoints", [])
        self.texts = args.get("texts", [])
        self.img_dir = args.get("img_dir", "")
        self.audio_dir_when_start = args.get("audio_dir_when_start", "")
        self.audio_dir_when_end = args.get("audio_dir_when_end", "")

        self.ChildClock = None
        self.ChildBackground = None

        # check_time_on_start
        this_time = QTime.currentTime()
        for index in range(len(self.start_timepoints)):
            if (
                this_time >= self.start_timepoints[index]
                and this_time < self.end_timepoints[index]
            ):
                self.period_start(index)
                return
        for index in range(len(self.start_timepoints) - 1):
            if (
                this_time >= self.end_timepoints[index]
                and this_time < self.start_timepoints[index + 1]
            ):
                self.period_end(index + 1)
                return
        self.period_end(0)

    def parse_img_dir(self):
        # 从img_dir中解析出图片文件名
        if not os.path.exists(self.img_dir):
            return []
        img_files = os.listdir(self.img_dir)
        img_files = [os.path.join(self.img_dir, img_file) for img_file in img_files]
        return img_files

    def check_time(self):
        current_time = QDateTime.currentDateTime().time()

        for index, time_point in enumerate(self.start_timepoints):
            if compare_qtime(current_time, time_point) == 0:
                self.period_start(index)
        for index, time_point in enumerate(self.end_timepoints):
            if compare_qtime(current_time, time_point) == 0:
                self.period_end(index)

    def period_start(self, index):
        # play the audio file saying it's starting
        if os.path.exists(self.audio_dir_when_start):
            start_audios = os.listdir(self.audio_dir_when_start)
            start_audio = random.choice(start_audios)
            print(f"Playing audio: {start_audio}")
            play_wav(os.path.join(self.audio_dir_when_start, start_audio))

        # start a clock, close the background
        if self.ChildBackground:
            self.ChildBackground.close()
            self.ChildBackground = None
        self.ChildClock = DraggableClock(
            {
                "to_time": self.end_timepoints[index],
                "text": self.texts[index],
            }
        )
        self.ChildClock.show()
        print(f"Start a new time period.")

    def period_end(self, index):
        # play the audio file saying it's ending
        if os.path.exists(self.audio_dir_when_end):
            end_audios = os.listdir(self.audio_dir_when_end)
            end_audio = random.choice(end_audios)
            print(f"Playing audio: {end_audio}")
            play_wav(os.path.join(self.audio_dir_when_end, end_audio))

        # close the clock, start the background
        if self.ChildClock:
            self.ChildClock.close()
            self.ChildClock = None
        self.ChildBackground = BackgroundWindow(
            {
                "img_path": random.choice(self.parse_img_dir()),
                "text": self.texts[index],
                "to_time": self.start_timepoints[
                    index
                ],  # Time when the relax period ends
            }
        )
        self.ChildBackground.show()
        print(f"Reached time point:")


class DraggableClock(QWidget):

    def __init__(self, args):
        self.WINDOW_WIDTH = 320
        self.WINDOW_HEIGHT = 240
        self.to_time = args["to_time"]
        self.text = args["text"]
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.layout = QVBoxLayout(self)

        self.clock_label = QLabel(self)
        self.clock_label.setStyleSheet(
            "font-size: 24px; color: white; background-color: black; padding: 10px; border-radius: 10px;"
        )
        self.clock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.clock_label)

        self.countdown_label = QLabel(self)
        self.countdown_label.setStyleSheet(
            "font-size: 24px; color: white; background-color: black; padding: 5px; border-radius: 5px;"
        )
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.countdown_label)

        self.text_label = QLabel(self.text, self)
        self.text_label.setStyleSheet(
            "font-size: 20px; color: white; background-color: black; padding: 5px; border-radius: 5px;"
        )
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.text_label)

        self.setLayout(self.layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)  # Update every second

        self.update_clock()

        # Set the position of the widget
        # 获取屏幕的大小
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        print(f"Primary screen size: {screen_width}x{screen_height}")

        # 获取窗口的大小
        window_width = self.geometry().width()
        window_height = self.geometry().height()
        print(f"Window size: {window_width}x{window_height}")

        # 计算窗口的新位置
        x = screen_width - self.WINDOW_WIDTH
        y = screen_height - self.WINDOW_HEIGHT

        # 移动窗口到右下角位置
        self.setGeometry(x, y, self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

    def update_clock(self):
        current_time = QTime.currentTime()
        current_time_str = current_time.toString("hh:mm:ss")
        self.clock_label.setText(f"Current Time: {current_time_str}")

        target_time = self.to_time
        if current_time < target_time:
            time_to_target = current_time.secsTo(target_time)
            hours = time_to_target // 3600
            minutes = (time_to_target % 3600) // 60
            seconds = time_to_target % 60
            countdown_str = f"Countdown: {hours:02}:{minutes:02}:{seconds:02}"
        else:
            countdown_str = "Target time passed"

        self.countdown_label.setText(countdown_str)
        self.text_label.setText(
            f"{self.text} Till {self.to_time.hour():02}:{self.to_time.minute():02}:{self.to_time.second():02}"
        )

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.offset)


class ChildWindow(QMainWindow):
    window_closed = pyqtSignal()
    window_minimized = pyqtSignal()

    def __init__(self, args={}):
        self.text = args.get("text", "")
        super().__init__()
        self.is_destroyed = False

        self.setWindowTitle("Overlay Window")
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )  # No title bar, stay on top, tool window

        # Get the primary screen and set the window geometry
        screen = QGuiApplication.primaryScreen()
        geometry = screen.geometry()
        self.setGeometry(geometry)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.initUI()
        # self.destroyed.connect(lambda: self.child_close_and_emit)

    def child_minimize_and_emit(self):
        # self.showMinimized()
        if self.is_destroyed:
            return
        self.is_destroyed = True
        self.close()
        time.sleep(TIME_DELAY)
        self.window_minimized.emit()

    def child_close_and_emit(self):
        # 当前应用只有这一个窗口的时候，当唯一的窗口关掉了，那程序就关闭了
        if self.is_destroyed:
            return
        self.is_destroyed = True
        self.close()
        time.sleep(TIME_DELAY)
        self.window_closed.emit()

    def initUI(self):
        # Create a central widget with a transparent background
        central_widget = QWidget(self)
        central_widget.setStyleSheet("background: transparent;")

        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_widget = QWidget(self)
        layout.addWidget(layout_widget)
        layout_widget.setStyleSheet("background-color: rgba(0, 0, 0, 128);")

        # 应该占有60%的屏幕高宽
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.geometry()
        layout_widget_width = int(screen_geometry.width() * 0.6)
        layout_widget_height = int(screen_geometry.height() * 0.6)

        layout_widget.setGeometry(0, 0, layout_widget_width, layout_widget_height)

        inner_layout = QVBoxLayout(layout_widget)
        # Create a label for the overlay text
        overlay_label = QLabel(self.text, self)
        overlay_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_label.setStyleSheet(
            "font-size: 48px; color: white;a background-color: white;background:transparent;"
        )
        # overlay_label.setStyleSheet("background-color: rgba(0, 0, 0, 128);")
        inner_layout.addWidget(overlay_label)

        # button to close the window
        hbox_widget = QWidget(self)
        hbox_widget.setStyleSheet("background: transparent;")
        hbox_layout = QHBoxLayout(hbox_widget)
        inner_layout.addWidget(hbox_widget)

        button = QPushButton("Minimize", self)
        button.clicked.connect(self.child_minimize_and_emit)
        button.setStyleSheet(
            "background-color: white; color: black; padding: 20px; border-radius: 5px;width:200px;"
        )

        button_close = QPushButton("Shutdown", self)
        button_close.clicked.connect(self.child_close_and_emit)
        button_close.setStyleSheet(
            "background-color: white; color: black; padding: 20px; border-radius: 5px;"
        )

        hbox_layout.addWidget(button)
        hbox_layout.addWidget(button_close)


class BackgroundWindow(QMainWindow):
    def __init__(self, args={}):
        super().__init__()
        self.img_path = args.get("img_path", "")
        self.text = args.get("text", "")
        self.to_time = args.get("to_time", None)

        self.setWindowTitle("Background Window")
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )  # No title bar

        # Get the primary screen and set the window geometry
        screen = QGuiApplication.primaryScreen()
        geometry = screen.geometry()
        self.setGeometry(geometry)

        self.showFullScreen()

        self.initUI()
        self.new_child()

    def new_child(self):
        self.child_window = ChildWindow(
            {
                "text": f'下一阶段：{self.text}\n Relax till {self.to_time.toString("hh:mm:ss")}'
            }
        )
        self.child_window.window_closed.connect(self.should_close)
        self.child_window.window_minimized.connect(self.should_minimize)
        self.child_window.show()
        self.child_window.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            time.sleep(TIME_DELAY)
            state = self.windowState()
            if (
                not state & Qt.WindowState.WindowMinimized
            ) and state & Qt.WindowState.WindowFullScreen:
                print("background change to the fullscreen")
                self.new_child()

    def should_minimize(self):
        print(f"Background windows should minimize now.")
        self.showMinimized()

    def should_close(self):
        print(f"Background windows should close now.")
        self.close()

    def initUI(self):
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create a label for the background image
        background_label = QLabel(self)
        # img_pixmap = QPixmap(r"C:\Users\Dusk_Hermit\Downloads\pixiv\ほうき星\ほうき星_2024-02-17_116153937_神里綾華_p0.jpg")
        img_pixmap = QPixmap(self.img_path)
        img_pixmap = img_pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        background_label.setPixmap(img_pixmap)
        layout.addWidget(background_label)

        self.setCentralWidget(central_widget)

    def mousePressEvent(self, event: QMouseEvent):
        time.sleep(TIME_DELAY)
        if self.isActiveWindow():
            self.child_window.raise_()
            self.child_window.activateWindow()
