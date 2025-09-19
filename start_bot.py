#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代币番茄钟机器人启动脚本
"""

import os
import sys
from tomato_bot import main

if __name__ == "__main__":
    print("🍅 代币番茄钟机器人")
    print("=" * 40)
    print("功能特性：")
    print("• 智能任务创建和价值评估")
    print("• 代币奖励和惩罚机制")
    print("• 自动提醒和过期处理")
    print("• 多样化任务查询")
    print("• 个人统计分析")
    print("=" * 40)
    print()
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        sys.exit(1)
    
    # 检查必要文件
    required_files = [
        "database.py",
        "task_evaluator.py", 
        "task_manager.py",
        "scheduler.py",
        "tomato_bot.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
        sys.exit(1)
    
    print("✅ 环境检查通过，启动机器人...")
    print()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 机器人已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

