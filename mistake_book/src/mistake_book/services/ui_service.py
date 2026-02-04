"""UI服务 - 处理UI相关的业务逻辑"""

from typing import List, Dict, Any, Optional
from mistake_book.core.data_manager import DataManager


class UIService:
    """UI服务类 - 封装UI层需要的业务逻辑"""
    
    def __init__(self, data_manager: DataManager):
        """
        初始化UI服务
        
        Args:
            data_manager: 数据管理器
        """
        self.data_manager = data_manager
    
    def get_all_questions(self) -> List[Dict[str, Any]]:
        """
        获取所有错题
        
        Returns:
            错题列表
        """
        return self.data_manager.search_questions({})
    
    def search_questions(self, keyword: str) -> List[Dict[str, Any]]:
        """
        搜索错题（按关键词）
        
        Args:
            keyword: 搜索关键词
        
        Returns:
            匹配的错题列表
        """
        if not keyword or not keyword.strip():
            return self.get_all_questions()
        
        # 搜索题目内容、答案、解析中包含关键词的题目
        all_questions = self.get_all_questions()
        keyword_lower = keyword.lower().strip()
        
        filtered = []
        for q in all_questions:
            # 搜索内容
            if keyword_lower in q.get('content', '').lower():
                filtered.append(q)
                continue
            # 搜索答案
            if keyword_lower in q.get('answer', '').lower():
                filtered.append(q)
                continue
            # 搜索解析
            if keyword_lower in q.get('explanation', '').lower():
                filtered.append(q)
                continue
            # 搜索科目
            if keyword_lower in q.get('subject', '').lower():
                filtered.append(q)
                continue
            # 搜索题型
            if keyword_lower in q.get('question_type', '').lower():
                filtered.append(q)
                continue
        
        return filtered
    
    def filter_questions(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        根据筛选条件获取错题
        
        Args:
            filters: 筛选条件字典
                - subject: 科目
                - difficulty: 难度 (1-5)
                - mastery_level: 掌握度 (0-3)
                - tags: 标签列表
        
        Returns:
            筛选后的错题列表
        """
        # 构建数据库查询条件
        db_filters = {}
        
        # 科目筛选
        if 'subject' in filters and filters['subject']:
            db_filters['subject'] = filters['subject']
        
        # 掌握度筛选
        if 'mastery_level' in filters and filters['mastery_level'] is not None:
            db_filters['mastery_level'] = filters['mastery_level']
        
        # 从数据库获取
        questions = self.data_manager.search_questions(db_filters)
        
        # 难度筛选（内存过滤）
        if 'difficulty' in filters and filters['difficulty'] is not None:
            questions = [q for q in questions if q.get('difficulty') == filters['difficulty']]
        
        # 标签筛选（内存过滤）
        if 'tags' in filters and filters['tags']:
            questions = [
                q for q in questions 
                if any(tag in q.get('tags', []) for tag in filters['tags'])
            ]
        
        return questions
    
    def get_navigation_data(self) -> Dict[str, Any]:
        """
        获取导航树数据
        
        Returns:
            导航树数据结构
        """
        # 获取所有科目（从数据库中的实际数据）
        all_questions = self.get_all_questions()
        subjects = sorted(set(q.get('subject', '') for q in all_questions if q.get('subject')))
        
        # 如果没有数据，使用默认科目列表
        if not subjects:
            subjects = ["数学", "物理", "化学", "英语", "语文"]
        
        # 获取所有标签
        tags = set()
        for q in all_questions:
            tags.update(q.get('tags', []))
        tags = sorted(tags)
        
        # 统计各掌握度的题目数量
        mastery_counts = {0: 0, 1: 0, 2: 0, 3: 0}
        for q in all_questions:
            level = q.get('mastery_level', 0)
            mastery_counts[level] = mastery_counts.get(level, 0) + 1
        
        return {
            'subjects': subjects,
            'tags': tags,
            'mastery_levels': [
                {'name': '🔴 生疏', 'value': 0, 'count': mastery_counts[0]},
                {'name': '🟡 学习中', 'value': 1, 'count': mastery_counts[1]},
                {'name': '🟢 掌握', 'value': 2, 'count': mastery_counts[2]},
                {'name': '🔵 熟练', 'value': 3, 'count': mastery_counts[3]},
            ]
        }
    
    def get_filter_options(self) -> Dict[str, List[str]]:
        """
        获取筛选器选项
        
        Returns:
            筛选器选项字典
        """
        nav_data = self.get_navigation_data()
        
        return {
            'subjects': ['全部'] + nav_data['subjects'],
            'difficulties': ['全部', '1星', '2星', '3星', '4星', '5星'],
            'mastery_levels': ['全部', '生疏', '学习中', '掌握', '熟练']
        }
    
    def parse_filter_from_ui(self, subject_text: str, difficulty_text: str, 
                            mastery_text: str) -> Dict[str, Any]:
        """
        解析UI筛选器的值为数据库查询条件
        
        Args:
            subject_text: 科目文本（如 "数学" 或 "全部"）
            difficulty_text: 难度文本（如 "3星" 或 "全部"）
            mastery_text: 掌握度文本（如 "掌握" 或 "全部"）
        
        Returns:
            筛选条件字典
        """
        filters = {}
        
        # 解析科目
        if subject_text and subject_text != "全部":
            filters['subject'] = subject_text
        
        # 解析难度
        if difficulty_text and difficulty_text != "全部":
            # 从 "3星" 提取数字
            try:
                difficulty = int(difficulty_text[0])
                filters['difficulty'] = difficulty
            except (ValueError, IndexError):
                pass
        
        # 解析掌握度
        if mastery_text and mastery_text != "全部":
            mastery_map = {
                '生疏': 0,
                '学习中': 1,
                '掌握': 2,
                '熟练': 3
            }
            if mastery_text in mastery_map:
                filters['mastery_level'] = mastery_map[mastery_text]
        
        return filters
    
    def get_statistics_summary(self) -> Dict[str, int]:
        """
        获取统计摘要（用于右侧统计面板）
        
        Returns:
            统计数据字典
        """
        all_questions = self.get_all_questions()
        
        # 按掌握度统计
        mastery_counts = {0: 0, 1: 0, 2: 0, 3: 0}
        for q in all_questions:
            level = q.get('mastery_level', 0)
            mastery_counts[level] = mastery_counts.get(level, 0) + 1
        
        # 待复习数量（这里简化处理，实际应该检查 next_review_date）
        from datetime import datetime
        due_count = 0
        for q in all_questions:
            next_review = q.get('next_review_date')
            if next_review and isinstance(next_review, datetime):
                if next_review <= datetime.now():
                    due_count += 1
        
        return {
            'total_questions': len(all_questions),
            'mastered': mastery_counts[2] + mastery_counts[3],  # 掌握 + 熟练
            'learning': mastery_counts[1],  # 学习中
            'unfamiliar': mastery_counts[0],  # 生疏
            'due_count': due_count  # 待复习
        }
