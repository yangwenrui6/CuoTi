"""表单验证"""


def validate_question(data: dict) -> tuple[bool, str]:
    """验证错题数据"""
    if not data.get("content"):
        return False, "题目内容不能为空"
    if not data.get("subject"):
        return False, "学科不能为空"
    return True, ""
