"""错题服务 - 处理错题相关的业务逻辑"""

from typing import Dict, Any, Optional
from pathlib import Path
from mistake_book.core.data_manager import DataManager
from mistake_book.services.ocr_engine import OCREngine
from mistake_book.utils.validators import validate_question
from mistake_book.utils.image_processor import ImageProcessor
from mistake_book.config.paths import get_app_paths
import logging
import shutil
from datetime import datetime

logger = logging.getLogger(__name__)


class QuestionService:
    """错题服务类 - 封装错题相关的业务逻辑"""
    
    def __init__(self, data_manager: DataManager, ocr_engine: Optional[OCREngine] = None):
        """
        初始化错题服务
        
        Args:
            data_manager: 数据管理器
            ocr_engine: OCR引擎（可选）
        """
        self.data_manager = data_manager
        self.ocr_engine = ocr_engine
        self.image_processor = ImageProcessor()
        self.app_paths = get_app_paths()
    
    def _copy_image_to_storage(self, source_path: str) -> Optional[str]:
        """
        将图片复制到应用的图片存储目录
        
        Args:
            source_path: 源图片路径
        
        Returns:
            存储后的相对路径，失败返回None
        """
        try:
            source = Path(source_path)
            if not source.exists():
                logger.error(f"源图片不存在: {source_path}")
                return None
            
            # 生成唯一的文件名：时间戳_原文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{timestamp}_{source.name}"
            
            # 目标路径
            dest_path = self.app_paths.images_dir / new_filename
            
            # 复制文件
            shutil.copy2(source, dest_path)
            logger.info(f"图片已复制到: {dest_path}")
            
            # 返回相对于images_dir的文件名（便于数据库存储）
            return new_filename
            
        except Exception as e:
            logger.error(f"复制图片失败: {e}")
            return None
    
    def get_image_full_path(self, relative_path: Optional[str]) -> Optional[Path]:
        """
        根据相对路径获取图片的完整路径
        
        Args:
            relative_path: 相对路径（文件名）
        
        Returns:
            完整路径，如果不存在返回None
        """
        if not relative_path:
            return None
        
        # 如果是绝对路径（兼容旧数据）
        path = Path(relative_path)
        if path.is_absolute():
            return path if path.exists() else None
        
        # 相对路径，拼接images_dir
        full_path = self.app_paths.images_dir / relative_path
        return full_path if full_path.exists() else None
    
    def create_question(self, question_data: Dict[str, Any]) -> tuple[bool, str, Optional[int]]:
        """
        创建新错题
        
        Args:
            question_data: 错题数据字典
        
        Returns:
            (成功标志, 消息, 题目ID)
        """
        # 验证数据
        is_valid, error_msg = validate_question(question_data)
        if not is_valid:
            return False, error_msg, None
        
        try:
            # 处理图片：如果有图片路径，复制到专门的文件夹
            if question_data.get("image_path"):
                relative_path = self._copy_image_to_storage(question_data["image_path"])
                if relative_path:
                    # 保存相对路径到数据库
                    question_data["image_path"] = relative_path
                    logger.info(f"图片已保存，相对路径: {relative_path}")
                else:
                    # 复制失败，保留原路径（兼容性）
                    logger.warning("图片复制失败，使用原路径")
            
            # 保存到数据库
            question_id = self.data_manager.add_question(question_data)
            return True, f"错题添加成功！题目ID: {question_id}", question_id
        except Exception as e:
            logger.error(f"保存错题失败: {e}")
            return False, f"保存失败: {str(e)}", None
    
    def recognize_image(self, image_path: Path, preprocess: bool = True) -> tuple[bool, str, Optional[str]]:
        """
        识别图片中的文字
        
        Args:
            image_path: 图片路径
            preprocess: 是否进行预处理
        
        Returns:
            (成功标志, 消息, 识别文本)
        """
        if not self.ocr_engine:
            return False, "OCR功能未启用\n\n请安装依赖:\npip install paddleocr\n\n或者:\npip install pytesseract", None
        
        if not self.ocr_engine.is_available():
            return False, "OCR引擎不可用\n\n请检查依赖是否正确安装", None
        
        try:
            # 图像预处理
            processed_path = image_path
            if preprocess:
                logger.info("开始图像预处理...")
                processed_path = self.image_processor.preprocess_for_ocr(image_path, enhance=True)
            
            # OCR识别
            logger.info("开始OCR识别...")
            recognized_text = self.ocr_engine.recognize(processed_path)
            
            # 清理临时文件
            if preprocess and processed_path != image_path:
                try:
                    processed_path.unlink()
                except Exception:
                    pass
            
            if recognized_text and recognized_text.strip():
                return True, "识别成功", recognized_text
            else:
                return False, "未能识别出文字\n\n建议:\n1. 确保图片清晰\n2. 文字对比度足够\n3. 尝试重新拍照", None
                
        except Exception as e:
            logger.error(f"OCR识别失败: {e}")
            return False, f"OCR识别失败\n\n错误信息:\n{str(e)}", None
    
    def recognize_image_with_retry(self, image_path: Path) -> tuple[bool, str, Optional[str]]:
        """
        识别图片 - 失败时自动重试(不预处理)
        
        Args:
            image_path: 图片路径
        
        Returns:
            (成功标志, 消息, 识别文本)
        """
        # 第一次尝试:使用预处理
        success, message, text = self.recognize_image(image_path, preprocess=True)
        
        if success:
            return success, message, text
        
        # 第二次尝试:不预处理（降低日志级别，避免误导用户）
        logger.debug("预处理识别失败,尝试直接识别...")
        success, message, text = self.recognize_image(image_path, preprocess=False)
        
        return success, message, text
    
    def update_question(self, question_id: int, updates: Dict[str, Any]) -> tuple[bool, str]:
        """
        更新错题信息
        
        Args:
            question_id: 题目ID
            updates: 更新的字段
        
        Returns:
            (成功标志, 消息)
        """
        try:
            success = self.data_manager.update_question(question_id, updates)
            if success:
                return True, "更新成功"
            else:
                return False, "题目不存在"
        except Exception as e:
            logger.error(f"更新错题失败: {e}")
            return False, f"更新失败: {str(e)}"
    
    def delete_question(self, question_id: int) -> tuple[bool, str]:
        """
        删除错题
        
        Args:
            question_id: 题目ID
        
        Returns:
            (成功标志, 消息)
        """
        try:
            success = self.data_manager.delete_question(question_id)
            if success:
                return True, "删除成功"
            else:
                return False, "题目不存在"
        except Exception as e:
            logger.error(f"删除错题失败: {e}")
            return False, f"删除失败: {str(e)}"
    
    def get_question_detail(self, question_id: int) -> tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        获取错题详细信息
        
        Args:
            question_id: 题目ID
        
        Returns:
            (成功标志, 消息, 题目详情)
        """
        try:
            question = self.data_manager.get_question(question_id)
            if question:
                return True, "获取成功", question
            else:
                return False, "题目不存在", None
        except Exception as e:
            logger.error(f"获取错题详情失败: {e}")
            return False, f"获取失败: {str(e)}", None
