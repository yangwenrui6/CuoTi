"""自定义异常"""


class MistakeBookError(Exception):
    """基础异常"""
    pass


class DataError(MistakeBookError):
    """数据错误"""
    pass


class OCRFailed(MistakeBookError):
    """OCR识别失败"""
    pass


class DatabaseError(MistakeBookError):
    """数据库错误"""
    pass
