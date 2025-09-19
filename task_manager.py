import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from database import TokenTomatoDatabase
from task_evaluator import TaskEvaluator, TaskEvaluatorConfig, StaticTaskEvaluatorConfig

class TokenTomatoManager:
    def __init__(self, db_path: str = "token_tomato.db", ai_service: str = "deepseek", config_dict: dict = None):
        """
        初始化代币番茄钟管理器
        
        Args:
            db_path: 数据库路径
            ai_service: AI服务类型 ("deepseek", "openai", "zhipu", "simple")
            config_dict: 配置字典（从config.yaml读取）
        """
        self.db = TokenTomatoDatabase(db_path)
        
        # 使用新的配置系统或回退到静态配置
        if config_dict:
            config = TaskEvaluatorConfig(config_dict)
            self.evaluator = config.get_evaluator(ai_service)
        else:
            self.evaluator = StaticTaskEvaluatorConfig.get_evaluator(ai_service)
    
    def parse_datetime(self, time_str: str) -> Optional[datetime]:
        """
        解析时间字符串为datetime对象
        支持多种格式：
        - 2024-12-25 18:00
        - 12-25 18:00
        - 明天 18:00
        - 后天 9:30
        - 3天后 15:00
        - 1小时后
        - 30分钟后
        """
        time_str = time_str.strip()
        now = datetime.now()
        
        try:
            # 标准格式：YYYY-MM-DD HH:MM
            if re.match(r'\d{4}-\d{1,2}-\d{1,2}\s+\d{1,2}:\d{2}', time_str):
                return datetime.strptime(time_str, '%Y-%m-%d %H:%M')
            
            # 简化格式：MM-DD HH:MM
            if re.match(r'\d{1,2}-\d{1,2}\s+\d{1,2}:\d{2}', time_str):
                year = now.year
                return datetime.strptime(f'{year}-{time_str}', '%Y-%m-%d %H:%M')
            
            # 相对时间：明天、后天等
            if '明天' in time_str:
                time_part = re.search(r'(\d{1,2}):(\d{2})', time_str)
                if time_part:
                    hour, minute = int(time_part.group(1)), int(time_part.group(2))
                    tomorrow = now + timedelta(days=1)
                    return tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            if '后天' in time_str:
                time_part = re.search(r'(\d{1,2}):(\d{2})', time_str)
                if time_part:
                    hour, minute = int(time_part.group(1)), int(time_part.group(2))
                    day_after_tomorrow = now + timedelta(days=2)
                    return day_after_tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # N天后
            days_match = re.search(r'(\d+)天后\s+(\d{1,2}):(\d{2})', time_str)
            if days_match:
                days, hour, minute = int(days_match.group(1)), int(days_match.group(2)), int(days_match.group(3))
                target_date = now + timedelta(days=days)
                return target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # N小时后
            hours_match = re.search(r'(\d+)小时后', time_str)
            if hours_match:
                hours = int(hours_match.group(1))
                return now + timedelta(hours=hours)
            
            # N分钟后
            minutes_match = re.search(r'(\d+)分钟后', time_str)
            if minutes_match:
                minutes = int(minutes_match.group(1))
                return now + timedelta(minutes=minutes)
            
            # 今天 HH:MM
            if '今天' in time_str:
                time_part = re.search(r'(\d{1,2}):(\d{2})', time_str)
                if time_part:
                    hour, minute = int(time_part.group(1)), int(time_part.group(2))
                    return now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # 只有时间：HH:MM（默认为今天）
            if re.match(r'^\d{1,2}:\d{2}$', time_str):
                hour, minute = map(int, time_str.split(':'))
                target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                # 如果时间已过，则设为明天
                if target_time <= now:
                    target_time += timedelta(days=1)
                return target_time
            
        except ValueError:
            pass
        
        return None
    
    def create_task(self, user_id: str, username: str, task_name: str, deadline_str: str) -> Tuple[bool, str]:
        """
        创建新任务
        
        Args:
            user_id: 用户ID
            username: 用户名
            task_name: 任务名称
            deadline_str: 截止时间字符串
            
        Returns:
            (成功标志, 消息)
        """
        # 确保用户存在
        self.db.create_user(user_id, username)
        
        # 解析截止时间
        deadline = self.parse_datetime(deadline_str)
        if not deadline:
            return False, f"无法解析时间格式：{deadline_str}\n\n支持的格式：\n• 2024-12-25 18:00\n• 12-25 18:00\n• 明天 18:00\n• 3天后 15:00\n• 2小时后\n• 30分钟后"
        
        # 检查时间是否为未来时间
        if deadline <= datetime.now():
            return False, "截止时间必须是未来时间"
        
        # 评估任务价值
        tokens = self.evaluator.evaluate_task_value(task_name, deadline)
        
        # 创建任务
        task_id = self.db.create_task(user_id, task_name, deadline, tokens)
        
        if task_id:
            difficulty_desc = self.evaluator.get_task_difficulty_description(tokens)
            suggestions = self.evaluator.suggest_task_optimization(task_name, tokens)
            
            message = f"✅ 任务创建成功！\n\n" \
                     f"📝 任务ID: {task_id}\n" \
                     f"📋 任务名称: {task_name}\n" \
                     f"⏰ 截止时间: {deadline.strftime('%Y-%m-%d %H:%M')}\n" \
                     f"💰 奖励代币: {tokens}\n" \
                     f"🎯 难度等级: {difficulty_desc}\n\n" \
                     f"{suggestions}"
            
            return True, message
        else:
            return False, "创建任务失败，请稍后重试"
    
    def complete_task(self, user_id: str, task_id: int) -> Tuple[bool, str]:
        """
        完成任务
        
        Args:
            user_id: 用户ID
            task_id: 任务ID
            
        Returns:
            (成功标志, 消息)
        """
        success, message = self.db.complete_task(task_id, user_id)
        
        if success:
            # 获取用户当前代币数
            current_tokens = self.db.get_user_tokens(user_id)
            message += f"\n💰 当前代币总数: {current_tokens}"
        
        return success, message
    
    def query_tasks(self, user_id: str, query_type: str = "", search_query: str = "") -> str:
        """
        查询任务
        
        Args:
            user_id: 用户ID
            query_type: 查询类型 ("", "-a", "-f", "-s")
            search_query: 搜索关键词（用于-s选项）
            
        Returns:
            格式化的任务列表
        """
        if query_type == "-a":
            # 查询所有任务
            tasks = self.db.get_user_tasks(user_id, "all")
            title = "📋 您的所有任务"
        elif query_type == "-f":
            # 查询已完成任务
            tasks = self.db.get_user_tasks(user_id, "completed")
            title = "✅ 您的已完成任务"
        elif query_type == "-s":
            # 搜索任务
            tasks = self.db.get_user_tasks(user_id, "all", search_query)
            title = f"🔍 搜索结果 (关键词: {search_query})"
        else:
            # 查询未完成任务（默认）
            tasks = self.db.get_user_tasks(user_id, "pending")
            title = "⏳ 您的未完成任务"
        
        if not tasks:
            return f"{title}\n\n暂无任务"
        
        # 获取用户当前代币数
        current_tokens = self.db.get_user_tokens(user_id)
        
        result = f"{title}\n💰 当前代币: {current_tokens}\n\n"
        
        for i, task in enumerate(tasks, 1):
            status_emoji = {
                'pending': '⏳',
                'completed': '✅',
                'expired': '❌'
            }.get(task['status'], '❓')
            
            # 计算剩余时间
            now = datetime.now()
            if task['status'] == 'pending':
                time_left = task['deadline'] - now
                if time_left.total_seconds() > 0:
                    days = time_left.days
                    hours = time_left.seconds // 3600
                    if days > 0:
                        time_desc = f"剩余{days}天{hours}小时"
                    else:
                        minutes = (time_left.seconds % 3600) // 60
                        if hours > 0:
                            time_desc = f"剩余{hours}小时{minutes}分钟"
                        else:
                            time_desc = f"剩余{minutes}分钟"
                else:
                    time_desc = "已过期"
                    status_emoji = '⚠️'
            else:
                time_desc = task['deadline'].strftime('%m-%d %H:%M')
            
            result += f"{i}. {status_emoji} [{task['task_id']}] {task['task_name']}\n" \
                     f"   ⏰ {time_desc} | 💰 {task['tokens']}代币\n\n"
        
        # 添加操作提示
        if query_type == "":
            result += "💡 使用 /fi <任务ID> 完成任务\n" \
                     "💡 使用 /ch -a 查看所有任务\n" \
                     "💡 使用 /ch -f 查看已完成任务\n" \
                     "💡 使用 /ch -s <关键词> 搜索任务"
        
        return result
    
    def get_daily_reminders(self, date: datetime = None) -> List[Dict]:
        """获取每日提醒任务"""
        return self.db.get_daily_deadlines(date)
    
    def process_expired_tasks(self) -> List[Dict]:
        """处理过期任务"""
        expired_tasks = self.db.get_expired_tasks()
        processed_tasks = []
        
        for task in expired_tasks:
            if self.db.expire_task(task['task_id']):
                processed_tasks.append(task)
        
        return processed_tasks
    
    def get_user_stats(self, user_id: str) -> Dict:
        """获取用户统计信息"""
        all_tasks = self.db.get_user_tasks(user_id, "all")
        completed_tasks = [t for t in all_tasks if t['status'] == 'completed']
        pending_tasks = [t for t in all_tasks if t['status'] == 'pending']
        expired_tasks = [t for t in all_tasks if t['status'] == 'expired']
        
        total_earned = sum(t['tokens'] for t in completed_tasks)
        total_lost = sum(t['tokens'] // 2 for t in expired_tasks)  # 过期任务扣除一半代币
        
        current_tokens = self.db.get_user_tokens(user_id)
        
        return {
            'current_tokens': current_tokens,
            'total_tasks': len(all_tasks),
            'completed_tasks': len(completed_tasks),
            'pending_tasks': len(pending_tasks),
            'expired_tasks': len(expired_tasks),
            'total_earned': total_earned,
            'total_lost': total_lost,
            'completion_rate': len(completed_tasks) / len(all_tasks) * 100 if all_tasks else 0
        }
    
    def format_user_stats(self, user_id: str, username: str) -> str:
        """格式化用户统计信息"""
        stats = self.get_user_stats(user_id)
        
        return f"📊 {username} 的番茄钟统计\n\n" \
               f"💰 当前代币: {stats['current_tokens']}\n" \
               f"📋 总任务数: {stats['total_tasks']}\n" \
               f"✅ 已完成: {stats['completed_tasks']}\n" \
               f"⏳ 进行中: {stats['pending_tasks']}\n" \
               f"❌ 已过期: {stats['expired_tasks']}\n" \
               f"📈 完成率: {stats['completion_rate']:.1f}%\n" \
               f"💎 累计获得: {stats['total_earned']} 代币\n" \
               f"💸 累计扣除: {stats['total_lost']} 代币"
