"""SQLAlchemy ORM模型"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# 多对多关联表
question_tags = Table(
    "question_tags",
    Base.metadata,
    Column("question_id", Integer, ForeignKey("questions.id")),
    Column("tag_id", Integer, ForeignKey("tags.id"))
)


class Question(Base):
    """错题模型"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True)
    subject = Column(String(50), nullable=False)  # 学科
    question_type = Column(String(20))  # 题型
    content = Column(Text, nullable=False)  # 题目内容
    answer = Column(Text)  # 正确答案
    my_answer = Column(Text)  # 我的答案
    explanation = Column(Text)  # 解析
    difficulty = Column(Integer, default=3)  # 难度1-5
    image_path = Column(String(500))  # 图片路径
    
    # 复习相关
    mastery_level = Column(Integer, default=0)
    easiness_factor = Column(Float, default=2.5)
    repetitions = Column(Integer, default=0)
    interval = Column(Integer, default=0)
    next_review_date = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    tags = relationship("Tag", secondary=question_tags, back_populates="questions")
    reviews = relationship("ReviewRecord", back_populates="question")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "subject": self.subject,
            "question_type": self.question_type,
            "content": self.content,
            "answer": self.answer,
            "my_answer": self.my_answer,
            "explanation": self.explanation,
            "difficulty": self.difficulty,
            "image_path": self.image_path,
            "mastery_level": self.mastery_level,
            "easiness_factor": self.easiness_factor,
            "repetitions": self.repetitions,
            "interval": self.interval,
            "next_review_date": self.next_review_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "tags": [tag.name for tag in self.tags]
        }


class Tag(Base):
    """标签模型"""
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    color = Column(String(7), default="#3498db")  # 十六进制颜色
    
    questions = relationship("Question", secondary=question_tags, back_populates="tags")


class ReviewRecord(Base):
    """复习记录"""
    __tablename__ = "review_records"
    
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    review_date = Column(DateTime, default=datetime.now)
    result = Column(Integer)  # ReviewResult枚举值
    time_spent = Column(Integer)  # 耗时（秒）
    
    question = relationship("Question", back_populates="reviews")
