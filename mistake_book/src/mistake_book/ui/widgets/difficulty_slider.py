"""难度滑块组件"""

from PyQt6.QtWidgets import QSlider


class DifficultySlider(QSlider):
    """难度滑块"""
    
    def __init__(self):
        super().__init__()
        self.setMinimum(1)
        self.setMaximum(5)
