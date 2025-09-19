#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动独立调度器的简单脚本
使用正斜杠路径
"""

import sys
import os

# 确保当前目录在Python路径中
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from start_scheduler import main

if __name__ == "__main__":
    main()
