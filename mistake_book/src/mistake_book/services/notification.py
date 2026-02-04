"""系统通知（复习提醒）"""

from plyer import notification


class NotificationService:
    """通知服务"""
    
    def send_review_reminder(self, count: int):
        """发送复习提醒"""
        notification.notify(
            title="错题本提醒",
            message=f"你有 {count} 道题目需要复习",
            app_name="错题本",
            timeout=10
        )
