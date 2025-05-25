import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QComboBox, QLabel, 
                            QSlider, QSpinBox, QFileDialog, QScrollArea, 
                            QGridLayout)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QSize
from PIL import Image, ImageEnhance, ImageOps

class CalligraphyPracticeTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.images = []  # 存储原始图片路径
        self.processed_images = []  # 存储处理后的QPixmap
        self.contrast = 1.0
        self.brightness = 1.0
        self.cols = 5  # 默认每行/列5个字
        self.repeats = 1  # 默认重复1次
        self.layout_mode = "横向（从右到左）"  # 默认排列方式

    def init_ui(self):
        self.setWindowTitle("书法练习工具")
        self.setGeometry(100, 100, 1000, 600)

        # 主容器（改为垂直布局）
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # 顶部内容容器（原左右区域）
        top_container = QWidget()
        top_layout = QHBoxLayout(top_container)
        main_layout.addWidget(top_container)

        # 左侧设置区域（顶端对齐）
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.setAlignment(Qt.AlignTop)  # 关键修改：设置布局顶端对齐
        settings_widget.setFixedWidth(250)
        top_layout.addWidget(settings_widget)

        # 文件选择按钮
        self.select_btn = QPushButton("选择书法单字图片")
        self.select_btn.clicked.connect(self.select_images)
        settings_layout.addWidget(self.select_btn)

        # 排列方式选择
        layout_label = QLabel("排列方式:")
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["横向（从右到左）", "纵向（从右到左）"])
        self.layout_combo.setCurrentText("横向（从右到左）")
        self.layout_combo.currentTextChanged.connect(self.update_layout_mode)
        settings_layout.addWidget(layout_label)
        settings_layout.addWidget(self.layout_combo)

        # 对比度调整
        contrast_label = QLabel("对比度 (1.0):")
        contrast_label.setObjectName("对比度 (1.0):")
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(1, 20)
        self.contrast_slider.setValue(10)
        self.contrast_slider.valueChanged.connect(lambda v: self.update_param("contrast", v/10))
        settings_layout.addWidget(contrast_label)
        settings_layout.addWidget(self.contrast_slider)

        # 亮度调整
        brightness_label = QLabel("亮度 (1.0):")
        brightness_label.setObjectName("亮度 (1.0):")
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(1, 20)
        self.brightness_slider.setValue(10)
        self.brightness_slider.valueChanged.connect(lambda v: self.update_param("brightness", v/10))
        settings_layout.addWidget(brightness_label)
        settings_layout.addWidget(self.brightness_slider)

        # 每行/列字数
        cols_label = QLabel("每行/列字数:")
        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(1, 10)
        self.cols_spin.setValue(5)
        self.cols_spin.valueChanged.connect(self.update_cols)
        settings_layout.addWidget(cols_label)
        settings_layout.addWidget(self.cols_spin)

        # 重复次数设置
        repeats_label = QLabel("重复次数:")
        self.repeats_spin = QSpinBox()
        self.repeats_spin.setRange(1, 10)
        self.repeats_spin.setValue(1)
        self.repeats_spin.valueChanged.connect(self.update_repeats)
        settings_layout.addWidget(repeats_label)
        settings_layout.addWidget(self.repeats_spin)

        # 新增Label框（顶端对齐）
        new_label = QLabel("书法练习辅助设置")
        new_label.setAlignment(Qt.AlignTop)
        settings_layout.addWidget(new_label)

        # 右侧图片展示区域
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_layout = QGridLayout(self.scroll_widget)
        self.scroll_layout.setContentsMargins(5, 5, 5, 5)
        self.scroll_layout.setSpacing(5)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        top_layout.addWidget(self.scroll_area, 1)

        # 底部版权标记
        copyright_label = QLabel("版权所有 ©天津市南开区南开小学-7jul")
        copyright_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(copyright_label)

    def select_images(self):
        """选择批量图片"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择书法单字图片", "", "图片文件 (*.jpg *.jpeg *.png *.bmp)"
        )
        if files:
            self.images = files
            self.process_images()
            self.update_display()

    def process_image(self, img_path):
        """处理单张图片"""
        # 打开原始图片
        pil_img = Image.open(img_path).convert("RGB")
        
        # 调整对比度和亮度
        enhancer = ImageEnhance.Contrast(pil_img)
        pil_img = enhancer.enhance(self.contrast)
        enhancer = ImageEnhance.Brightness(pil_img)
        pil_img = enhancer.enhance(self.brightness)
        
        # 转换为QPixmap
        qimg = QImage(pil_img.tobytes(), pil_img.width, pil_img.height, 
                     pil_img.width*3, QImage.Format_RGB888)
        return QPixmap.fromImage(qimg)

    def process_images(self):
        """处理所有选中的图片"""
        self.processed_images = [self.process_image(path) for path in self.images]

    def update_layout_mode(self, mode):
        """更新排列方式并刷新显示（新增）"""
        self.layout_mode = mode
        self.update_display()

    def update_display(self):
        """更新图片展示区域"""
        # 清空现有布局
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # 计算图片尺寸（保持原逻辑）
        area_width = self.scroll_area.viewport().width() - 20  # 预留滚动条空间
        img_width = (area_width - (self.cols-1)*5) // self.cols  # 减去间距
        img_height = int(img_width * 1.2)  # 假设书法字图片高宽比1.2:1

        # 根据重复次数生成展示列表
        display_images = self.processed_images * self.repeats
        total_images = len(display_images)

        # 根据排列方式计算布局位置（新增核心逻辑）
        for idx, pixmap in enumerate(display_images):
            if self.layout_mode == "横向（从右到左）":
                # 横向排列：行优先，列从右到左
                row = idx // self.cols
                col = self.cols - 1 - (idx % self.cols)  # 列索引反向
            else:  # 纵向（从右到左）
                # 纵向排列：列优先，列从右到左，行从上到下
                total_cols = (total_images + self.cols - 1) // self.cols  # 总列数
                current_col = idx // self.cols  # 当前列索引（正向）
                col = total_cols - 1 - current_col  # 列索引反向
                row = idx % self.cols  # 行索引保持正向

            label = QLabel()
            label.setAlignment(Qt.AlignTop)  # 新增：设置顶端对齐
            label.setPixmap(pixmap.scaled(QSize(img_width, img_height), 
                                         Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.scroll_layout.addWidget(label, row, col)

    def update_param(self, param_type, value):
        """更新参数并刷新显示"""
        if param_type == "contrast":
            self.contrast = value
            self.findChild(QLabel, "对比度 (1.0):").setText(f"对比度 ({value:.1f})")
        elif param_type == "brightness":
            self.brightness = value
            self.findChild(QLabel, "亮度 (1.0):").setText(f"亮度 ({value:.1f})")
        self.process_images()
        self.update_display()

    def update_cols(self, value):
        """更新每行字数并刷新显示"""
        self.cols = value
        self.update_display()

    def update_repeats(self, value):
        """更新重复次数并刷新显示（新增）"""
        self.repeats = value
        self.update_display()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CalligraphyPracticeTool()
    window.show()
    sys.exit(app.exec_())