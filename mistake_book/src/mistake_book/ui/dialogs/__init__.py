"""对话框模块"""

from .add_question.dialog import AddQuestionDialog
from .detail.dialog import DetailDialog as QuestionDetailDialog
from .review_module_selector import ReviewModuleSelectorDialog
from .review.dialog import ReviewDialog
from .review_history_dialog import ReviewHistoryDialog

__all__ = [
    "AddQuestionDialog", 
    "QuestionDetailDialog", 
    "ReviewModuleSelectorDialog", 
    "ReviewDialog",
    "ReviewHistoryDialog"
]
