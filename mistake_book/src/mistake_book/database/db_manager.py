"""数据库连接池、事务、初始化、备份"""

from contextlib import contextmanager
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from mistake_book.database.models import Base
import shutil
from datetime import datetime


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        Base.metadata.create_all(self.engine)
    
    @contextmanager
    def session_scope(self) -> Session:
        """提供事务会话上下文"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_fresh_session(self) -> Session:
        """获取新的会话（用于确保数据最新）"""
        return self.SessionLocal()
    
    def backup(self, backup_dir: Path) -> Path:
        """备份数据库"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"backup_{timestamp}.db"
        shutil.copy2(self.db_path, backup_path)
        return backup_path
    
    def restore(self, backup_path: Path):
        """恢复数据库"""
        shutil.copy2(backup_path, self.db_path)
