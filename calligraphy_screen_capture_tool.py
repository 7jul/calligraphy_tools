import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, 
                            QVBoxLayout, QLabel, QPushButton, QLineEdit,
                            QComboBox, QHBoxLayout, QSpinBox, QSlider)  # 新增QSlider
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor, QScreen, QPixmap
import keyboard
import os

class SettingsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setWindowFlags(Qt.WindowStaysOnTopHint)  # 添加窗口置顶标志
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 宽度设置
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("宽度:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 2000)
        self.width_spin.setValue(self.parent.width)
        width_layout.addWidget(self.width_spin)
        layout.addLayout(width_layout)
        
        # 高度设置
        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("高度:"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 2000)
        self.height_spin.setValue(self.parent.height)
        height_layout.addWidget(self.height_spin)
        layout.addLayout(height_layout)
        
        # 网格类型
        grid_layout = QHBoxLayout()
        grid_layout.addWidget(QLabel("网格类型:"))
        self.grid_combo = QComboBox()
        self.grid_combo.addItems(["无", "田字格", "米字格", "回宫格"])
        self.grid_combo.setCurrentText({
            "none": "无", "tian": "田字格", 
            "mi": "米字格", "hui": "回宫格"
        }[self.parent.grid_type])
        grid_layout.addWidget(self.grid_combo)
        layout.addLayout(grid_layout)
        
        # 快捷键
        hotkey_layout = QHBoxLayout()
        hotkey_layout.addWidget(QLabel("快捷键:"))
        self.hotkey_edit = QLineEdit(self.parent.hotkey)
        hotkey_layout.addWidget(self.hotkey_edit)
        layout.addLayout(hotkey_layout)
        
        # 文件前缀
        prefix_layout = QHBoxLayout()
        prefix_layout.addWidget(QLabel("文件前缀:"))
        self.prefix_edit = QLineEdit(self.parent.prefix)
        prefix_layout.addWidget(self.prefix_edit)
        layout.addLayout(prefix_layout)

        # 框格宽度设置
        border_layout = QHBoxLayout()
        border_layout.addWidget(QLabel("框格宽度(像素):"))
        self.border_spin = QSpinBox()
        self.border_spin.setRange(1, 10)
        self.border_spin.setValue(self.parent.border_width)
        border_layout.addWidget(self.border_spin)
        layout.addLayout(border_layout)
        
        # 透明度设置
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("透明度(0-100%):"))
        self.opacity_slider = QSlider(Qt.Horizontal)  # 需要确保Qt已从QtCore导入
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(int(self.parent.opacity * 100))
        opacity_layout.addWidget(self.opacity_slider)
        layout.addLayout(opacity_layout)

        apply_btn = QPushButton("应用设置")
        apply_btn.clicked.connect(self.apply_settings)
        layout.addWidget(apply_btn)
        
        self.setLayout(layout)
        self.setWindowTitle("设置")
    
    def apply_settings(self):
        self.parent.width = self.width_spin.value()
        self.parent.height = self.height_spin.value()
        self.parent.grid_type = {
            "无": "none", "田字格": "tian",
            "米字格": "mi", "回宫格": "hui"
        }[self.grid_combo.currentText()]
        self.parent.hotkey = self.hotkey_edit.text()
        self.parent.prefix = self.prefix_edit.text()
        
        # 重新注册热键
        keyboard.remove_hotkey(self.parent.hotkey)
        keyboard.add_hotkey(self.parent.hotkey, self.parent.capture_screen)
        
        # 确保应用所有设置
        self.parent.border_width = self.border_spin.value()
        self.parent.opacity = self.opacity_slider.value() / 100.0
        self.parent.setGeometry(self.parent.x(), self.parent.y(),
                              self.parent.width, self.parent.height)
        self.parent.repaint()  # 改为强制重绘
        self.parent.update()


class CaptureWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("区域截屏工具")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 默认参数
        self.width = 400
        self.height = 400
        self.grid_type = "none"  # none/tian/mi/hui
        self.prefix = "capture"
        self.hotkey = "f1"
        self.counter = 1
        self.border_width = 3  # 新增边框宽度属性
        self.opacity = 1.0     # 新增透明度属性
        
        # 初始化UI
        self.init_ui()
        self.setGeometry(100, 100, self.width, self.height)
        
        # 直接显示设置窗口
        self.settings_window = SettingsWindow(self)
        self.settings_window.show()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 截图区域
        self.capture_area = QWidget()
        self.capture_area.setFixedSize(self.width, self.height)
        main_layout.addWidget(self.capture_area)
        
        # 注册热键
        keyboard.add_hotkey(self.hotkey, self.capture_screen)

    def paintEvent(self, event):
        painter = QPainter(self)
        
        # 绘制实线边框
        painter.setPen(QPen(QColor(255, 0, 0), self.border_width))
        painter.drawRect(0, 0, self.width-1, self.height-1)
        
        # 设置虚线样式
        dash_pen = QPen(QColor(255, 0, 0), self.border_width)
        dash_pen.setStyle(Qt.DashLine)
        painter.setPen(dash_pen)
        painter.setOpacity(self.opacity)

        # 绘制网格
        if self.grid_type == "tian":
            # 田字格虚线
            painter.drawLine(self.width//2, 0, self.width//2, self.height)
            painter.drawLine(0, self.height//2, self.width, self.height//2)
        elif self.grid_type == "mi":
            # 米字格虚线
            painter.drawLine(0, 0, self.width, self.height)
            painter.drawLine(self.width, 0, 0, self.height)
            painter.drawLine(self.width//2, 0, self.width//2, self.height)
            painter.drawLine(0, self.height//2, self.width, self.height//2)
        elif self.grid_type == "hui":
            # 回宫格虚线
            painter.drawLine(self.width//2, 0, self.width//2, self.height)
            painter.drawLine(0, self.height//2, self.width, self.height//2)
            rect_width = self.width // 2    # 宽度1/2
            rect_height = self.height * 2 // 3  # 高度2/3
            x = (self.width - rect_width) // 2  # 水平居中
            y = (self.height - rect_height) // 2 # 垂直居中
            painter.drawRect(x, y, rect_width, rect_height)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
            self.drag_start_pos = event.pos()  # 记录鼠标在窗口内的起始位置
            self.setCursor(Qt.ClosedHandCursor)  # 改变鼠标样式
    
    def mouseMoveEvent(self, event):
        if hasattr(self, 'old_pos'):
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.unsetCursor()  # 恢复鼠标样式
            if hasattr(self, 'drag_start_pos'):
                del self.drag_start_pos
    
    def capture_screen(self):
        screen = QApplication.primaryScreen()
        pixmap = screen.grabWindow(0, self.x(), self.y(), 
                                 self.width, self.height)
        
        # 获取脚本所在目录的绝对路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        save_dir = os.path.join(script_dir, "screenshots")
        
        # 确保目录存在
        if not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)
            
        # 生成文件名
        filename = os.path.join(save_dir, f"{self.prefix}_{self.counter:03d}.jpg")
        while os.path.exists(filename):
            self.counter += 1
            filename = os.path.join(save_dir, f"{self.prefix}_{self.counter:03d}.jpg")
        
        pixmap.save(filename, "jpg")
        self.counter += 1
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CaptureWindow()
    window.show()
    sys.exit(app.exec_())