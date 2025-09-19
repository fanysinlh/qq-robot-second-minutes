#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立的调度器启动脚本
用于处理过期任务和代币扣除
"""

import time
from datetime import datetime
from task_manager import TokenTomatoManager
from scheduler import TomatoScheduler
from botpy.ext.cog_yaml import read
import os


class StandaloneScheduler:
    def __init__(self):
        """初始化独立调度器"""
        # 读取配置
        config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
        self.config = read(config_path)
        
        # 初始化任务管理器
        ai_service = self.config.get("ai_service", "deepseek")
        self.task_manager = TokenTomatoManager(
            "token_tomato.db", 
            ai_service=ai_service, 
            config_dict=self.config
        )
        
        # 初始化调度器（使用同步回调函数）
        self.scheduler = TomatoScheduler(self.task_manager, self._notification_callback)
    
    def _notification_callback(self, user_id: str, message: str):
        """通知回调函数（同步版本，独立调度器模式下只记录日志）"""
        print(f"[{datetime.now()}] 通知用户 {user_id[:8]}...: {message[:100]}...")
        # 在独立调度器模式下，我们只记录通知，不实际发送
        # 如果需要发送通知，可以集成其他通知方式（如邮件、webhook等）
    
    def run(self):
        """运行独立调度器"""
        print("🍅 代币番茄钟 - 独立调度器")
        print("=" * 40)
        print(f"启动时间: {datetime.now()}")
        print()
        print("📋 调度任务:")
        print("• 每天 08:00 - 每日任务提醒")
        print("• 每天 23:00 - 处理过期任务并扣除代币")
        print("• 每小时 - 检查即将到期任务")
        print("• 每30分钟 - 紧急任务提醒")
        print()
        print("✅ 调度器已启动，按 Ctrl+C 停止")
        print("=" * 40)
        
        try:
            # 启动调度器
            self.scheduler.start()
            
            # 立即执行一次过期任务检查（用于测试）
            print("🔍 立即执行一次过期任务检查...")
            expired_tasks = self.task_manager.process_expired_tasks()
            if expired_tasks:
                print(f"✅ 处理了 {len(expired_tasks)} 个过期任务")
                for task in expired_tasks:
                    print(f"  - 任务ID {task['task_id']}: {task['task_name']} (用户: {task['user_id'][:8]}...)")
                    print(f"    扣除代币: {task['tokens'] // 2}")
            else:
                print("ℹ️  当前没有过期任务")
            print()
            
            # 显示调度器状态
            status = self.scheduler.get_scheduler_status()
            print("📊 调度器状态:")
            print(f"  运行状态: {'✅ 运行中' if status['is_running'] else '❌ 已停止'}")
            print(f"  定时任务数: {status['total_jobs']}")
            print(f"  下次运行: {status['next_run_time']}")
            print()
            
            # 保持运行
            while True:
                time.sleep(60)  # 每分钟检查一次
                
        except KeyboardInterrupt:
            print("\n🛑 调度器停止中...")
            self.scheduler.stop()
            print("✅ 调度器已停止")
        except Exception as e:
            print(f"❌ 调度器运行错误: {e}")
            self.scheduler.stop()


def main():
    scheduler = StandaloneScheduler()
    scheduler.run()


if __name__ == "__main__":
    main()
