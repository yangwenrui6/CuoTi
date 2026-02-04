"""云同步抽象（预留接口）"""

from abc import ABC, abstractmethod


class CloudSyncService(ABC):
    """云同步服务抽象"""
    
    @abstractmethod
    def upload(self, local_path: str) -> bool:
        """上传到云端"""
        pass
    
    @abstractmethod
    def download(self, remote_path: str, local_path: str) -> bool:
        """从云端下载"""
        pass
