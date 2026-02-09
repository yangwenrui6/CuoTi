"""对话框工厂 - 负责创建和配置对话框"""

from typing import Dict, Any, Optional


class DialogFactory:
    """对话框工厂 - 负责创建和配置对话框"""
    
    def __init__(self, services: Dict[str, Any], event_bus=None):
        """
        初始化工厂
        
        Args:
            services: 服务字典 {question_service, review_service, ui_service}
            event_bus: 事件总线（可选）
        """
        self.question_service = services.get('question_service')
        self.review_service = services.get('review_service')
        self.ui_service = services.get('ui_service')
        self.event_bus = event_bus
    
    def create_add_question_dialog(self, parent=None):
        """创建添加错题对话框"""
        from mistake_book.ui.dialogs.add_question import (
            AddQuestionController,
            AddQuestionDialog
        )
        
        controller = AddQuestionController(
            self.question_service,
            self.event_bus
        )
        return AddQuestionDialog(controller, parent)
    
    def create_detail_dialog(self, question_data: Dict[str, Any], parent=None):
        """
        创建详情对话框
        
        Args:
            question_data: 题目数据
            parent: 父窗口
        """
        from mistake_book.ui.dialogs.detail import (
            DetailDialogController,
            DetailDialog
        )
        
        controller = DetailDialogController(
            self.question_service,
            question_data,
            self.event_bus
        )
        return DetailDialog(controller, parent)
    
    def create_review_dialog(self, questions: list, parent=None):
        """
        创建复习对话框
        
        Args:
            questions: 待复习题目列表
            parent: 父窗口
        """
        from mistake_book.ui.dialogs.review import (
            ReviewDialogController,
            ReviewDialog
        )
        
        controller = ReviewDialogController(
            self.review_service,
            questions,
            self.event_bus
        )
        return ReviewDialog(controller, parent)
    
    def create_review_module_selector(self, parent=None):
        """
        创建复习模块选择器
        
        Args:
            parent: 父窗口
        """
        from mistake_book.ui.dialogs.review_module_selector import ReviewModuleSelectorDialog
        
        # 获取DataManager实例（通过review_service）
        data_manager = self.review_service.data_manager if hasattr(self.review_service, 'data_manager') else None
        
        selector = ReviewModuleSelectorDialog(
            data_manager,
            self.review_service,
            parent
        )
        
        # 连接信号：当用户选择模块后，创建并显示复习对话框
        def on_module_selected(subject: str, question_type: str):
            """处理模块选择"""
            # 构建筛选条件
            filters = {}
            if subject and subject != "REVIEW_HISTORY":
                filters['subject'] = subject
            if question_type:
                filters['question_type'] = question_type
            
            # 获取题目列表
            if subject == "REVIEW_HISTORY":
                # 复习历史模式 - 直接获取最近复习的题目
                recent_questions = self.review_service.get_recently_reviewed_questions(30)
                
                if not recent_questions:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.information(parent, "提示", "暂无复习历史")
                    return
                
                # 创建并显示复习对话框
                review_dialog = self.create_review_dialog(recent_questions, parent)
                # 连接继续复习信号 - 重新打开模块选择器
                review_dialog.review_completed.connect(lambda: self._on_continue_review(parent))
                review_dialog.exec()
                return
            else:
                # 正常复习模式
                questions = data_manager.search_questions(filters)
            
            if not questions:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(parent, "提示", "没有符合条件的题目")
                return
            
            # 创建并显示复习对话框
            review_dialog = self.create_review_dialog(questions, parent)
            # 连接继续复习信号 - 重新打开模块选择器
            review_dialog.review_completed.connect(lambda: self._on_continue_review(parent))
            review_dialog.exec()
        
        selector.module_selected.connect(on_module_selected)
        
        return selector
    
    def _on_continue_review(self, parent=None):
        """
        处理继续复习请求 - 重新打开模块选择器
        
        Args:
            parent: 父窗口
        """
        # 使用QTimer延迟调用，避免对话框关闭时的冲突
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, lambda: self.create_review_module_selector(parent).exec())
