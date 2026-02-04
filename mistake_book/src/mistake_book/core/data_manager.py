"""业务层：封装增删改查和统计逻辑"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from mistake_book.database.db_manager import DatabaseManager
from mistake_book.database.models import Question, Tag


class DataManager:
    """数据管理业务层"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def add_question(self, question_data: Dict[str, Any]) -> int:
        """添加错题"""
        with self.db.session_scope() as session:
            question = Question(**question_data)
            session.add(question)
            session.flush()
            return question.id
    
    def update_question(self, question_id: int, updates: Dict[str, Any]) -> bool:
        """更新错题"""
        with self.db.session_scope() as session:
            question = session.query(Question).filter_by(id=question_id).first()
            if question:
                for key, value in updates.items():
                    setattr(question, key, value)
                return True
            return False
    
    def delete_question(self, question_id: int) -> bool:
        """删除错题"""
        with self.db.session_scope() as session:
            question = session.query(Question).filter_by(id=question_id).first()
            if question:
                session.delete(question)
                return True
            return False
    
    def get_question(self, question_id: int) -> Optional[Dict[str, Any]]:
        """获取单个错题（返回完整信息）"""
        with self.db.session_scope() as session:
            question = session.query(Question).filter_by(id=question_id).first()
            if question:
                return question.to_dict()
            return None
    
    def search_questions(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """搜索错题（确保获取最新数据）"""
        with self.db.session_scope() as session:
            # 清除会话缓存，确保获取最新数据
            session.expire_all()
            
            query = session.query(Question)
            
            # 科目筛选
            if "subject" in filters:
                query = query.filter_by(subject=filters["subject"])
            
            # 掌握度筛选
            if "mastery_level" in filters:
                query = query.filter_by(mastery_level=filters["mastery_level"])
            
            # 难度筛选
            if "difficulty" in filters:
                query = query.filter_by(difficulty=filters["difficulty"])
            
            # 标签筛选
            if "tags" in filters and filters["tags"]:
                # 筛选包含指定标签的题目
                for tag_name in filters["tags"]:
                    query = query.join(Question.tags).filter(Tag.name == tag_name)
            
            questions = query.all()
            return [q.to_dict() for q in questions]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计数据（实时从数据库查询）"""
        with self.db.session_scope() as session:
            # 清除会话缓存，确保获取最新数据
            session.expire_all()
            
            total = session.query(Question).count()
            
            # 按掌握度统计
            mastered = session.query(Question).filter(
                Question.mastery_level.in_([2, 3])
            ).count()  # 掌握 + 熟练
            
            learning = session.query(Question).filter_by(mastery_level=1).count()
            unfamiliar = session.query(Question).filter_by(mastery_level=0).count()
            
            # 待复习数量
            from datetime import datetime
            due_count = session.query(Question).filter(
                Question.next_review_date <= datetime.now()
            ).count()
            
            return {
                "total_questions": total,
                "mastered": mastered,
                "learning": learning,
                "unfamiliar": unfamiliar,
                "due_count": due_count
            }
