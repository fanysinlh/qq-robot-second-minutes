import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import os

class TokenTomatoDatabase:
    def __init__(self, db_path: str = "token_tomato.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT,
                    tokens INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建任务表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    task_name TEXT NOT NULL,
                    deadline TIMESTAMP NOT NULL,
                    tokens INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP NULL,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # 创建代币交易记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS token_transactions (
                    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    task_id INTEGER,
                    amount INTEGER,
                    transaction_type TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (task_id) REFERENCES tasks (task_id)
                )
            ''')
            
            conn.commit()
    
    def create_user(self, user_id: str, username: str) -> bool:
        """创建新用户"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
                    (user_id, username)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"创建用户失败: {e}")
            return False
    
    def get_user_tokens(self, user_id: str) -> int:
        """获取用户代币数量"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT tokens FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
    
    def update_user_tokens(self, user_id: str, amount: int, task_id: Optional[int] = None, 
                          transaction_type: str = "manual", description: str = "") -> bool:
        """更新用户代币数量"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 更新用户代币
                cursor.execute(
                    "UPDATE users SET tokens = tokens + ? WHERE user_id = ?",
                    (amount, user_id)
                )
                
                # 记录交易
                cursor.execute(
                    "INSERT INTO token_transactions (user_id, task_id, amount, transaction_type, description) VALUES (?, ?, ?, ?, ?)",
                    (user_id, task_id, amount, transaction_type, description)
                )
                
                conn.commit()
                return True
        except Exception as e:
            print(f"更新代币失败: {e}")
            return False
    
    def create_task(self, user_id: str, task_name: str, deadline: datetime, tokens: int) -> Optional[int]:
        """创建新任务"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO tasks (user_id, task_name, deadline, tokens) VALUES (?, ?, ?, ?)",
                    (user_id, task_name, deadline.isoformat(), tokens)
                )
                task_id = cursor.lastrowid
                conn.commit()
                return task_id
        except Exception as e:
            print(f"创建任务失败: {e}")
            return None
    
    def get_task_by_id(self, task_id: int) -> Optional[Dict]:
        """根据ID获取任务"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT task_id, user_id, task_name, deadline, tokens, status, created_at, completed_at FROM tasks WHERE task_id = ?",
                (task_id,)
            )
            result = cursor.fetchone()
            if result:
                return {
                    'task_id': result[0],
                    'user_id': result[1],
                    'task_name': result[2],
                    'deadline': datetime.fromisoformat(result[3]),
                    'tokens': result[4],
                    'status': result[5],
                    'created_at': datetime.fromisoformat(result[6]),
                    'completed_at': datetime.fromisoformat(result[7]) if result[7] else None
                }
            return None
    
    def complete_task(self, task_id: int, user_id: str) -> Tuple[bool, str]:
        """完成任务"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 获取任务信息
                task = self.get_task_by_id(task_id)
                if not task:
                    return False, "任务不存在"
                
                if task['user_id'] != user_id:
                    return False, "这不是您的任务"
                
                if task['status'] != 'pending':
                    return False, "任务已经完成或已过期"
                
                # 检查是否在截止时间内
                now = datetime.now()
                if now > task['deadline']:
                    return False, "任务已过期，无法完成"
                
                # 更新任务状态
                cursor.execute(
                    "UPDATE tasks SET status = 'completed', completed_at = ? WHERE task_id = ?",
                    (now.isoformat(), task_id)
                )
                
                conn.commit()
                
                # 奖励代币
                self.update_user_tokens(
                    user_id, 
                    task['tokens'], 
                    task_id, 
                    "task_completion", 
                    f"完成任务: {task['task_name']}"
                )
                
                return True, f"任务完成！获得 {task['tokens']} 代币"
                
        except Exception as e:
            print(f"完成任务失败: {e}")
            return False, "完成任务时发生错误"
    
    def get_user_tasks(self, user_id: str, status_filter: str = "all", search_query: str = "") -> List[Dict]:
        """获取用户任务列表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            base_query = "SELECT task_id, task_name, deadline, tokens, status, created_at FROM tasks WHERE user_id = ?"
            params = [user_id]
            
            # 状态过滤
            if status_filter == "pending":
                base_query += " AND status = 'pending'"
            elif status_filter == "completed":
                base_query += " AND status = 'completed'"
            elif status_filter == "expired":
                base_query += " AND status = 'expired'"
            
            # 搜索过滤
            if search_query:
                base_query += " AND task_name LIKE ?"
                params.append(f"%{search_query}%")
            
            base_query += " ORDER BY created_at DESC"
            
            cursor.execute(base_query, params)
            results = cursor.fetchall()
            
            tasks = []
            for result in results:
                tasks.append({
                    'task_id': result[0],
                    'task_name': result[1],
                    'deadline': datetime.fromisoformat(result[2]),
                    'tokens': result[3],
                    'status': result[4],
                    'created_at': datetime.fromisoformat(result[5])
                })
            
            return tasks
    
    def get_expired_tasks(self) -> List[Dict]:
        """获取已过期但未处理的任务"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            cursor.execute(
                "SELECT task_id, user_id, task_name, deadline, tokens FROM tasks WHERE status = 'pending' AND deadline < ?",
                (now,)
            )
            results = cursor.fetchall()
            
            expired_tasks = []
            for result in results:
                expired_tasks.append({
                    'task_id': result[0],
                    'user_id': result[1],
                    'task_name': result[2],
                    'deadline': datetime.fromisoformat(result[3]),
                    'tokens': result[4]
                })
            
            return expired_tasks
    
    def expire_task(self, task_id: int) -> bool:
        """标记任务为过期并扣除代币"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 获取任务信息
                task = self.get_task_by_id(task_id)
                if not task:
                    return False
                
                # 更新任务状态
                cursor.execute(
                    "UPDATE tasks SET status = 'expired' WHERE task_id = ?",
                    (task_id,)
                )
                
                conn.commit()
                
                # 扣除代币（惩罚）
                penalty = task['tokens'] // 2  # 扣除一半代币作为惩罚
                self.update_user_tokens(
                    task['user_id'], 
                    -penalty, 
                    task_id, 
                    "task_penalty", 
                    f"任务过期惩罚: {task['task_name']}"
                )
                
                return True
                
        except Exception as e:
            print(f"处理过期任务失败: {e}")
            return False
    
    def get_daily_deadlines(self, date: datetime = None) -> List[Dict]:
        """获取指定日期截止的任务"""
        if date is None:
            date = datetime.now()
        
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT task_id, user_id, task_name, deadline, tokens FROM tasks WHERE status = 'pending' AND deadline >= ? AND deadline < ?",
                (start_of_day.isoformat(), end_of_day.isoformat())
            )
            results = cursor.fetchall()
            
            tasks = []
            for result in results:
                tasks.append({
                    'task_id': result[0],
                    'user_id': result[1],
                    'task_name': result[2],
                    'deadline': datetime.fromisoformat(result[3]),
                    'tokens': result[4]
                })
            
            return tasks


