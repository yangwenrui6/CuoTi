"""截图压缩和OCR预处理"""

from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
import logging
import tempfile
import uuid

logger = logging.getLogger(__name__)


class ImageProcessor:
    """图片处理器 - 提供压缩和OCR预处理功能"""
    
    def compress(self, image_path: Path, max_size: int = 1024, quality: int = 85) -> Path:
        """
        压缩图片
        
        Args:
            image_path: 原图路径
            max_size: 最大尺寸(宽或高)
            quality: 压缩质量(1-100)
            
        Returns:
            压缩后的图片路径（使用临时文件，避免中文路径问题）
        """
        try:
            img = Image.open(image_path)
            
            # 保持宽高比缩放
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # 使用临时文件，避免中文路径问题
            temp_dir = Path(tempfile.gettempdir())
            temp_filename = f"ocr_compressed_{uuid.uuid4().hex}{image_path.suffix}"
            output_path = temp_dir / temp_filename
            
            # 保存压缩图片
            img.save(output_path, optimize=True, quality=quality)
            logger.info(f"图片压缩成功: {output_path}")
            
            return output_path
        except Exception as e:
            logger.error(f"图片压缩失败: {e}")
            return image_path
    
    def preprocess_for_ocr(self, image_path: Path, enhance: bool = True) -> Path:
        """
        OCR预处理 - 提高识别准确率
        
        Args:
            image_path: 原图路径
            enhance: 是否进行增强处理
            
        Returns:
            处理后的图片路径（使用临时文件，避免中文路径问题）
        """
        try:
            img = Image.open(image_path)
            
            # 1. 转为灰度图
            img = img.convert("L")
            
            if enhance:
                # 2. 增强对比度
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.5)
                
                # 3. 锐化
                img = img.filter(ImageFilter.SHARPEN)
                
                # 4. 去噪
                img = img.filter(ImageFilter.MedianFilter(size=3))
            
            # 使用临时文件，避免中文路径问题
            # 生成唯一的临时文件名
            temp_dir = Path(tempfile.gettempdir())
            temp_filename = f"ocr_processed_{uuid.uuid4().hex}{image_path.suffix}"
            output_path = temp_dir / temp_filename
            
            img.save(output_path)
            
            logger.info(f"图片预处理成功: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"图片预处理失败: {e}")
            return image_path
    
    def auto_rotate(self, image_path: Path) -> Path:
        """
        自动旋转图片(根据EXIF信息)
        
        Args:
            image_path: 原图路径
            
        Returns:
            旋转后的图片路径
        """
        try:
            img = Image.open(image_path)
            
            # 读取EXIF方向信息
            try:
                from PIL import ImageOps
                img = ImageOps.exif_transpose(img)
            except Exception:
                pass
            
            # 保存
            output_path = image_path.parent / f"{image_path.stem}_rotated{image_path.suffix}"
            img.save(output_path)
            
            logger.info(f"图片旋转成功: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"图片旋转失败: {e}")
            return image_path
    
    def crop_to_content(self, image_path: Path, border: int = 10) -> Path:
        """
        自动裁剪到内容区域(去除白边)
        
        Args:
            image_path: 原图路径
            border: 保留的边距
            
        Returns:
            裁剪后的图片路径
        """
        try:
            img = Image.open(image_path)
            
            # 转为灰度图
            gray = img.convert("L")
            
            # 获取边界框
            bbox = gray.getbbox()
            
            if bbox:
                # 添加边距
                bbox = (
                    max(0, bbox[0] - border),
                    max(0, bbox[1] - border),
                    min(img.width, bbox[2] + border),
                    min(img.height, bbox[3] + border)
                )
                
                # 裁剪
                img = img.crop(bbox)
            
            # 保存
            output_path = image_path.parent / f"{image_path.stem}_cropped{image_path.suffix}"
            img.save(output_path)
            
            logger.info(f"图片裁剪成功: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"图片裁剪失败: {e}")
            return image_path
