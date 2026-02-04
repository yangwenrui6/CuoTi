"""复习ViewModel"""

from PyQt6.QtCore import QObject, pyqtSignal


class ReviewViewModel(QObject):
    """复习视图模型"""
    
    review_completed = pyqtSignal()
    
    def __init__(self, scheduler, data_manager):
        super().__init__()
        self.scheduler = scheduler
        self.data_manager = data_manager
