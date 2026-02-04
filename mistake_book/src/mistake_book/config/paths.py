"""跨平台路径管理"""

from pathlib import Path
from platformdirs import user_data_dir, user_config_dir, user_log_dir


class AppPaths:
    """应用路径管理"""
    
    def __init__(self):
        self.app_name = "MistakeBook"
        self.data_dir = Path(user_data_dir(self.app_name))
        self.config_dir = Path(user_config_dir(self.app_name))
        self.log_dir = Path(user_log_dir(self.app_name))
        
        # 创建必要目录
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def database_file(self) -> Path:
        """数据库文件路径"""
        return self.data_dir / "mistakes.db"
    
    @property
    def config_file(self) -> Path:
        """配置文件路径"""
        return self.config_dir / "settings.json"
    
    @property
    def log_file(self) -> Path:
        """日志文件路径"""
        return self.log_dir / "app.log"
    
    @property
    def backup_dir(self) -> Path:
        """备份目录"""
        backup = self.data_dir / "backups"
        backup.mkdir(exist_ok=True)
        return backup


def get_app_paths() -> AppPaths:
    """获取应用路径实例"""
    return AppPaths()
