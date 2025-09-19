import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import Callable, List, Dict, Any
import threading
from task_manager import TokenTomatoManager

class TomatoScheduler:
    def __init__(self, task_manager: TokenTomatoManager, notification_callback: Callable = None):
        """
        初始化定时调度器
        
        Args:
            task_manager: 任务管理器实例
            notification_callback: 通知回调函数，用于发送消息给用户
        """
        self.task_manager = task_manager
        self.notification_callback = notification_callback
        self.is_running = False
        self.scheduler_thread = None
        
        # 设置定时任务
        self._setup_scheduled_jobs()
    
    def _setup_scheduled_jobs(self):
        """设置定时任务"""
        # 每天早上8点检查当天截止的任务
        schedule.every().day.at("08:00").do(self._daily_reminder_job)
        
        # 每天晚上23点处理过期任务
        schedule.every().day.at("23:00").do(self._process_expired_tasks_job)
        
        # 每小时检查即将到期的任务（1小时内）
        schedule.every().hour.do(self._hourly_reminder_job)
        
        # 每30分钟检查即将到期的任务（30分钟内）
        schedule.every(30).minutes.do(self._urgent_reminder_job)
    
    def _daily_reminder_job(self):
        """每日提醒任务"""
        try:
            today = datetime.now()
            daily_tasks = self.task_manager.get_daily_reminders(today)
            
            if daily_tasks and self.notification_callback:
                # 按用户分组任务
                user_tasks = {}
                for task in daily_tasks:
                    user_id = task['user_id']
                    if user_id not in user_tasks:
                        user_tasks[user_id] = []
                    user_tasks[user_id].append(task)
                
                # 为每个用户发送提醒
                for user_id, tasks in user_tasks.items():
                    message = self._format_daily_reminder(tasks)
                    asyncio.create_task(self.notification_callback(user_id, message))
                    
            print(f"[{datetime.now()}] 每日提醒任务完成，提醒了 {len(daily_tasks)} 个任务")
            
        except Exception as e:
            print(f"每日提醒任务执行失败: {e}")
    
    def _process_expired_tasks_job(self):
        """处理过期任务"""
        try:
            expired_tasks = self.task_manager.process_expired_tasks()
            
            if expired_tasks and self.notification_callback:
                # 按用户分组过期任务
                user_expired = {}
                for task in expired_tasks:
                    user_id = task['user_id']
                    if user_id not in user_expired:
                        user_expired[user_id] = []
                    user_expired[user_id].append(task)
                
                # 为每个用户发送过期通知
                for user_id, tasks in user_expired.items():
                    message = self._format_expired_notification(tasks)
                    asyncio.create_task(self.notification_callback(user_id, message))
            
            print(f"[{datetime.now()}] 过期任务处理完成，处理了 {len(expired_tasks)} 个任务")
            
        except Exception as e:
            print(f"过期任务处理失败: {e}")
    
    def _hourly_reminder_job(self):
        """每小时提醒即将到期的任务"""
        try:
            now = datetime.now()
            one_hour_later = now + timedelta(hours=1)
            
            # 获取1小时内到期的任务
            upcoming_tasks = self._get_upcoming_tasks(now, one_hour_later)
            
            if upcoming_tasks and self.notification_callback:
                user_tasks = {}
                for task in upcoming_tasks:
                    user_id = task['user_id']
                    if user_id not in user_tasks:
                        user_tasks[user_id] = []
                    user_tasks[user_id].append(task)
                
                for user_id, tasks in user_tasks.items():
                    message = self._format_hourly_reminder(tasks)
                    asyncio.create_task(self.notification_callback(user_id, message))
            
            print(f"[{datetime.now()}] 每小时提醒完成，提醒了 {len(upcoming_tasks)} 个任务")
            
        except Exception as e:
            print(f"每小时提醒执行失败: {e}")
    
    def _urgent_reminder_job(self):
        """紧急提醒（30分钟内到期）"""
        try:
            now = datetime.now()
            thirty_minutes_later = now + timedelta(minutes=30)
            
            # 获取30分钟内到期的任务
            urgent_tasks = self._get_upcoming_tasks(now, thirty_minutes_later)
            
            if urgent_tasks and self.notification_callback:
                user_tasks = {}
                for task in urgent_tasks:
                    user_id = task['user_id']
                    if user_id not in user_tasks:
                        user_tasks[user_id] = []
                    user_tasks[user_id].append(task)
                
                for user_id, tasks in user_tasks.items():
                    message = self._format_urgent_reminder(tasks)
                    asyncio.create_task(self.notification_callback(user_id, message))
            
            print(f"[{datetime.now()}] 紧急提醒完成，提醒了 {len(urgent_tasks)} 个任务")
            
        except Exception as e:
            print(f"紧急提醒执行失败: {e}")
    
    def _get_upcoming_tasks(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """获取指定时间范围内的待完成任务"""
        # 这里需要从数据库获取指定时间范围内的任务
        # 为了简化，我们直接从task_manager获取所有用户的任务
        # 在实际应用中，你可能需要在数据库层面实现这个查询
        
        upcoming_tasks = []
        try:
            # 获取所有用户ID（这里简化处理，实际应该有用户管理）
            # 暂时返回空列表，具体实现需要根据你的用户管理方式调整
            pass
        except Exception as e:
            print(f"获取即将到期任务失败: {e}")
        
        return upcoming_tasks
    
    def _format_daily_reminder(self, tasks: List[Dict]) -> str:
        """格式化每日提醒消息"""
        message = "🌅 早上好！今天有以下任务需要完成：\n\n"
        
        for i, task in enumerate(tasks, 1):
            deadline_str = task['deadline'].strftime('%H:%M')
            message += f"{i}. 📝 {task['task_name']}\n" \
                      f"   ⏰ 截止时间: {deadline_str}\n" \
                      f"   💰 奖励代币: {task['tokens']}\n\n"
        
        message += "💪 加油完成任务，获得丰厚代币奖励！"
        return message
    
    def _format_expired_notification(self, tasks: List[Dict]) -> str:
        """格式化过期任务通知"""
        message = "⚠️ 任务过期通知\n\n"
        
        total_penalty = 0
        for i, task in enumerate(tasks, 1):
            penalty = task['tokens'] // 2
            total_penalty += penalty
            message += f"{i}. ❌ {task['task_name']}\n" \
                      f"   📅 截止时间: {task['deadline'].strftime('%m-%d %H:%M')}\n" \
                      f"   💸 扣除代币: {penalty}\n\n"
        
        message += f"总计扣除 {total_penalty} 代币\n" \
                  "💡 下次记得及时完成任务哦！"
        return message
    
    def _format_hourly_reminder(self, tasks: List[Dict]) -> str:
        """格式化每小时提醒消息"""
        message = "⏰ 任务即将到期提醒（1小时内）\n\n"
        
        for i, task in enumerate(tasks, 1):
            time_left = task['deadline'] - datetime.now()
            minutes_left = int(time_left.total_seconds() / 60)
            
            message += f"{i}. 🔥 {task['task_name']}\n" \
                      f"   ⏰ 还有 {minutes_left} 分钟到期\n" \
                      f"   💰 奖励代币: {task['tokens']}\n\n"
        
        message += "⚡ 抓紧时间完成任务！"
        return message
    
    def _format_urgent_reminder(self, tasks: List[Dict]) -> str:
        """格式化紧急提醒消息"""
        message = "🚨 紧急提醒！任务即将到期（30分钟内）\n\n"
        
        for i, task in enumerate(tasks, 1):
            time_left = task['deadline'] - datetime.now()
            minutes_left = int(time_left.total_seconds() / 60)
            
            message += f"{i}. 🔥🔥 {task['task_name']}\n" \
                      f"   ⏰ 还有 {minutes_left} 分钟到期！\n" \
                      f"   💰 奖励代币: {task['tokens']}\n\n"
        
        message += "🏃‍♂️ 最后冲刺时间！快去完成任务！"
        return message
    
    def start(self):
        """启动调度器"""
        if self.is_running:
            print("调度器已在运行中")
            return
        
        self.is_running = True
        
        def run_scheduler():
            print(f"[{datetime.now()}] 番茄钟调度器启动")
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
            print(f"[{datetime.now()}] 番茄钟调度器停止")
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
    
    def stop(self):
        """停止调度器"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        print("调度器已停止")
    
    def get_next_run_time(self) -> str:
        """获取下次运行时间"""
        jobs = schedule.get_jobs()
        if not jobs:
            return "无定时任务"
        
        next_run = min(job.next_run for job in jobs)
        return next_run.strftime('%Y-%m-%d %H:%M:%S')
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """获取调度器状态"""
        jobs = schedule.get_jobs()
        return {
            'is_running': self.is_running,
            'total_jobs': len(jobs),
            'next_run_time': self.get_next_run_time(),
            'jobs': [
                {
                    'job': str(job.job_func.__name__),
                    'next_run': job.next_run.strftime('%Y-%m-%d %H:%M:%S') if job.next_run else 'N/A',
                    'interval': str(job.interval) + ' ' + str(job.unit) if hasattr(job, 'interval') else 'N/A'
                }
                for job in jobs
            ]
        }

# 使用示例
if __name__ == "__main__":
    # 创建任务管理器
    task_manager = TokenTomatoManager()
    
    # 定义通知回调函数（这里只是打印，实际应该发送QQ消息）
    async def notification_callback(user_id: str, message: str):
        print(f"发送给用户 {user_id} 的消息：\n{message}\n")
    
    # 创建并启动调度器
    scheduler = TomatoScheduler(task_manager, notification_callback)
    scheduler.start()
    
    try:
        # 保持程序运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("收到停止信号")
        scheduler.stop()


