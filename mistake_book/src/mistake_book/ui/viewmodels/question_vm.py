"""错题ViewModel"""

from PyQt6.QtCore import QObject, pyqtSignal


class QuestionViewModel(QObject):
    """错题视图模型"""
    
    data_changed = pyqtSignal()
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self._questions = []
    
    def load_questions(self):
        """加载错题列表"""
        self._questions = self.data_manager.search_questions({})
        self.data_changed.emit()
    
    @property
    def questions(self):
        return self._questions
