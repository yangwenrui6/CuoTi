"""OCR引擎（EasyOCR）"""

from pathlib import Path
from abc import ABC, abstractmethod
from typing import Optional
import logging
import threading
import os

logger = logging.getLogger(__name__)


class OCREngine(ABC):
    """OCR引擎抽象基类"""
    
    @abstractmethod
    def recognize(self, image_path: Path) -> str:
        """识别图片中的文字"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查引擎是否可用"""
        pass


class EasyOCREngine(OCREngine):
    """EasyOCR实现 - 纯Python OCR引擎,支持中文"""
    
    def __init__(self, langs: list = None):
        """
        初始化EasyOCR引擎（延迟加载）
        
        Args:
            langs: 识别语言列表,默认['ch_sim', 'en']（中文+英文）
        """
        self.langs = langs or ['ch_sim', 'en']
        self.reader = None
        self._initialized = False
        self._init_attempted = False
        self._init_lock = threading.Lock()  # 线程锁，防止重复初始化
        self._init_thread = None  # 初始化线程
    
    def _lazy_init(self):
        """延迟初始化 - 只在第一次使用时才加载模型"""
        with self._init_lock:
            if self._init_attempted:
                return
            
            self._init_attempted = True
        
        try:
            import easyocr
            import os
            
            # 获取模型存储路径（优先使用环境变量）
            model_storage_directory = os.environ.get('EASYOCR_MODULE_PATH')
            if model_storage_directory:
                # 确保路径存在
                model_path = Path(model_storage_directory)
                model_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"使用自定义模型路径: {model_storage_directory}")
            else:
                model_storage_directory = None
                logger.info("使用默认模型路径")
            
            # 创建reader,首次使用会下载模型
            logger.info("正在初始化EasyOCR...")
            logger.info("提示：首次使用需要下载模型文件（约100-200MB），请耐心等待")
            logger.info("如果下载失败，请检查网络连接或手动下载模型")
            
            if model_storage_directory:
                self.reader = easyocr.Reader(
                    self.langs, 
                    gpu=False, 
                    verbose=False,
                    model_storage_directory=model_storage_directory
                )
            else:
                self.reader = easyocr.Reader(self.langs, gpu=False, verbose=False)
            
            self._initialized = True
            logger.info(f"✅ EasyOCR初始化成功 (语言: {self.langs})")
        except ImportError:
            logger.error("❌ EasyOCR未安装,请运行: pip install easyocr")
        except KeyboardInterrupt:
            logger.warning("⚠️  用户中断了模型下载")
            raise
        except Exception as e:
            logger.error(f"❌ EasyOCR初始化失败: {e}")
            logger.error("可能的原因：")
            logger.error("  1. 网络连接问题，无法下载模型")
            logger.error("  2. 磁盘空间不足")
            logger.error("  3. 模型文件损坏，请删除模型目录后重试")
    
    def _lazy_init_async(self):
        """异步延迟初始化 - 在后台线程中加载模型，不阻塞UI"""
        with self._init_lock:
            if self._init_attempted:
                return
            
            # 标记已尝试初始化，防止重复启动线程
            self._init_attempted = True
            
            # 创建并启动后台线程
            self._init_thread = threading.Thread(
                target=self._lazy_init_worker,
                name="EasyOCR-Init",
                daemon=True  # 守护线程，程序退出时自动结束
            )
            self._init_thread.start()
            logger.info("🔄 OCR模型正在后台加载，不会影响程序使用...")
    
    def _lazy_init_worker(self):
        """后台线程工作函数 - 实际执行初始化"""
        try:
            import easyocr
            import os
            
            # 获取模型存储路径（优先使用环境变量）
            model_storage_directory = os.environ.get('EASYOCR_MODULE_PATH')
            if model_storage_directory:
                # 确保路径存在
                model_path = Path(model_storage_directory)
                model_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"使用自定义模型路径: {model_storage_directory}")
            else:
                model_storage_directory = None
                logger.info("使用默认模型路径")
            
            logger.info("正在后台初始化EasyOCR...")
            logger.info("提示：首次使用需要下载模型文件（约100-200MB）")
            
            if model_storage_directory:
                self.reader = easyocr.Reader(
                    self.langs, 
                    gpu=False, 
                    verbose=False,
                    model_storage_directory=model_storage_directory
                )
            else:
                self.reader = easyocr.Reader(self.langs, gpu=False, verbose=False)
            
            self._initialized = True
            logger.info(f"✅ EasyOCR后台初始化成功 (语言: {self.langs})")
            
            # 触发初始化完成回调
            if hasattr(self, '_on_init_complete') and self._on_init_complete:
                self._on_init_complete()
                
        except ImportError:
            logger.error("❌ EasyOCR未安装,请运行: pip install easyocr")
        except Exception as e:
            logger.error(f"❌ EasyOCR后台初始化失败: {e}")
            logger.error("可能的原因：")
            logger.error("  1. 网络连接问题，无法下载模型")
            logger.error("  2. 磁盘空间不足")
            logger.error("  3. 模型文件损坏，请删除模型目录后重试")
    
    def set_init_complete_callback(self, callback):
        """设置初始化完成回调函数"""
        self._on_init_complete = callback
    
    def is_available(self) -> bool:
        """
        检查引擎是否可用
        
        注意：延迟加载模式下，此方法只检查easyocr是否已安装，
        不会触发模型加载。真正的初始化在首次调用recognize()时进行。
        """
        # 如果已经尝试过初始化，返回初始化结果
        if self._init_attempted:
            return self._initialized and self.reader is not None
        
        # 如果还没尝试初始化，检查easyocr是否已安装
        try:
            import easyocr
            return True  # easyocr已安装，认为可用
        except ImportError:
            return False  # easyocr未安装，不可用
    
    def is_initializing(self) -> bool:
        """检查是否正在初始化"""
        return self._init_attempted and not self._initialized
    
    def wait_for_init(self, timeout: float = None) -> bool:
        """
        等待初始化完成
        
        Args:
            timeout: 超时时间（秒），None表示无限等待
            
        Returns:
            是否初始化成功
        """
        if self._init_thread and self._init_thread.is_alive():
            self._init_thread.join(timeout)
        return self._initialized
    
    def recognize(self, image_path: Path) -> str:
        """
        识别图片中的文字
        
        Args:
            image_path: 图片路径
            
        Returns:
            识别出的文字
        """
        # 延迟初始化：只在真正使用时才加载模型
        if not self._init_attempted:
            # 同步初始化（阻塞式）
            logger.info("首次使用OCR，开始加载模型...")
            self._lazy_init()
        
        # 如果正在后台初始化，等待完成
        if self.is_initializing():
            logger.info("等待OCR模型加载完成...")
            success = self.wait_for_init(timeout=300)  # 最多等待5分钟
            if not success:
                raise RuntimeError("OCR模型加载超时（5分钟）")
        
        if not self._initialized or not self.reader:
            raise RuntimeError("EasyOCR引擎未初始化或初始化失败")
        
        try:
            # 使用numpy数组而不是文件路径，避免中文路径问题
            import numpy as np
            from PIL import Image
            
            # 读取图片为numpy数组
            img = Image.open(image_path)
            img_array = np.array(img)
            
            # 执行OCR识别（传入numpy数组而不是路径）
            # 使用更宽松的参数以提高识别率
            result = self.reader.readtext(
                img_array,
                detail=1,  # 返回详细信息（包括位置和置信度）
                paragraph=False,  # 不合并段落，保持原始行
                min_size=10,  # 最小文字尺寸（像素）
                text_threshold=0.5,  # 文字检测阈值（降低以检测更多文字）
                low_text=0.3,  # 低置信度文字阈值
                link_threshold=0.3,  # 文字连接阈值
                canvas_size=2560,  # 画布大小（增大以处理高分辨率图片）
                mag_ratio=1.5,  # 放大比例
            )
            
            if not result:
                logger.warning("未识别到任何文字")
                return ""
            
            # 提取文字内容
            lines = []
            for detection in result:
                bbox = detection[0]  # 边界框坐标
                text = detection[1]  # 文字内容
                confidence = detection[2]  # 置信度
                
                # 降低置信度阈值，保留更多结果
                if confidence > 0.1:  # 从0.3降低到0.1
                    lines.append(text)
                    logger.debug(f"识别: {text} (置信度: {confidence:.2f})")
            
            recognized_text = "\n".join(lines)
            logger.info(f"识别成功,共{len(lines)}行文字")
            return recognized_text
            
        except Exception as e:
            logger.error(f"OCR识别失败: {e}")
            raise


def create_ocr_engine(async_init: bool = False) -> Optional[OCREngine]:
    """
    创建OCR引擎（延迟初始化）
    
    Args:
        async_init: 是否异步初始化（后台线程加载模型）
    
    Returns:
        EasyOCR引擎实例（未初始化，将在首次使用时初始化）
    """
    try:
        # 只检查easyocr是否已安装，不立即初始化
        import easyocr
        # 使用中文+英文模型以支持中英文混合识别
        engine = EasyOCREngine(langs=['ch_sim', 'en'])
        
        if async_init:
            # 异步初始化：在后台线程中加载模型
            engine._lazy_init_async()
            logger.info("OCR引擎已准备就绪（正在后台加载模型，不影响程序使用）")
        else:
            # 同步初始化：首次使用时才加载
            logger.info("OCR引擎已准备就绪（将在首次使用时加载模型）")
        
        return engine
    except ImportError:
        logger.warning("EasyOCR未安装,OCR功能将被禁用")
        return None
    except Exception as e:
        logger.error(f"OCR引擎准备失败: {e}")
        return None
