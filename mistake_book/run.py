"""启动脚本 - 从项目根目录运行"""

import sys
from pathlib import Path

# 将src目录添加到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# 导入并运行主程序
from mistake_book.main import main

if __name__ == "__main__":
    main()
