#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作版代币番茄钟机器人
基于demo.py的成功模式
"""

import asyncio
import re
import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import GroupMessage, Message
from datetime import datetime
from task_manager import TokenTomatoManager
from scheduler import TomatoScheduler
import os
import sys

# 配置日志
_log = logging.get_logger()

class WorkingTomatoBot(botpy.Client):
    def __init__(self):
        """
        工作版代币番茄钟机器人
        """
        # 读取配置
        self.config = read(os.path.join(os.path.dirname(__file__), "./config.yaml"))
        
        # 使用与demo.py相同的Intents配置
        intents = botpy.Intents(public_messages=True)
        super().__init__(intents=intents)
        
        # 初始化任务管理器
        ai_service = self.config.get("ai_service", "deepseek")
        self.task_manager = TokenTomatoManager("token_tomato.db", ai_service=ai_service, config_dict=self.config)
        
        # 初始化调度器
        self.scheduler = TomatoScheduler(self.task_manager, self._send_notification)
        
        # 命令前缀
        self.command_prefix = "\\"
    
    async def on_ready(self):
        """机器人就绪事件"""
        _log.info(f"🍅 代币番茄钟机器人「{self.robot.name}」已启动！")
        
        # 启动调度器
        self.scheduler.start()
        
        print(f"✅ 代币番茄钟机器人已成功启动！")
        print(f"🤖 机器人: {self.robot.name}")
        print(f"🍅 系统已就绪！")
        print()
        print("📝 使用说明:")
        print("• @机器人 \\help - 查看帮助")
        print("• @机器人 \\cr 任务名称 截止时间 - 创建任务")
        print("• @机器人 \\ch - 查看任务")
        print("• @机器人 \\fi 任务ID - 完成任务")
        print("=" * 50)
    
    async def on_group_at_message_create(self, message: GroupMessage):
        """处理QQ群@消息 - 使用demo.py的成功模式"""
        _log.info(f"收到群聊@消息: {message.content}")
        
        try:
            # 获取用户信息
            user_id = message.author.member_openid
            username = f"用户{user_id[:8]}"
            
            # 清理消息内容
            content = re.sub(r'<@!\d+>', '', message.content).strip()
            
            # 处理命令
            if content.startswith(self.command_prefix):
                # 处理命令并获取回复
                reply_text = await self._process_command(user_id, username, content)
            else:
                # 非命令消息的默认回复
                reply_text = f"👋 你好！我是代币番茄钟机器人！\n\n请发送命令，例如:\n• \\help - 查看帮助\n• \\cr 任务名 时间 - 创建任务"
            
            # 使用demo.py的回复方式 - 关键是要指定content参数！
            await message.reply(content=reply_text)
            _log.info(f"群聊回复成功: {reply_text[:50]}...")
            
        except Exception as e:
            _log.error(f"处理群聊消息时出错: {e}")
            try:
                await message.reply(content=f"❌ 处理消息时发生错误: {str(e)}")
            except:
                pass
    
    async def on_at_message_create(self, message: Message):
        """处理频道@消息"""
        _log.info(f"收到频道@消息: {message.content}")
        
        try:
            # 获取用户信息
            user_id = message.author.id
            username = getattr(message.author, 'username', f'用户{user_id}')
            
            # 清理消息内容
            content = re.sub(r'<@!\d+>', '', message.content).strip()
            
            # 处理命令
            if content.startswith(self.command_prefix):
                reply_text = await self._process_command(user_id, username, content)
            else:
                reply_text = f"👋 你好 {username}！我是代币番茄钟机器人！\n\n请发送命令，例如:\n• \\help - 查看帮助"
            
            # 频道消息回复
            await message.reply(content=reply_text)
            _log.info(f"频道回复成功: {reply_text[:50]}...")
            
        except Exception as e:
            _log.error(f"处理频道消息时出错: {e}")
            try:
                await message.reply(content=f"❌ 处理消息时发生错误: {str(e)}")
            except:
                pass
    
    async def on_direct_message_create(self, message: Message):
        """处理私信消息"""
        _log.info(f"收到私信: {message.content}")
        
        try:
            # 获取用户信息
            user_id = message.author.id
            username = getattr(message.author, 'username', f'用户{user_id}')
            
            content = message.content.strip()
            
            # 处理命令
            if content.startswith(self.command_prefix):
                reply_text = await self._process_command(user_id, username, content)
            else:
                reply_text = f"👋 你好 {username}！我是代币番茄钟机器人！\n\n请发送命令，例如:\n• \\help - 查看帮助"
            
            # 私信回复
            await message.reply(content=reply_text)
            _log.info(f"私信回复成功: {reply_text[:50]}...")
            
        except Exception as e:
            _log.error(f"处理私信时出错: {e}")
            try:
                await message.reply(content=f"❌ 处理消息时发生错误: {str(e)}")
            except:
                pass
    
    async def _process_command(self, user_id: str, username: str, content: str) -> str:
        """处理命令并返回回复文本"""
        # 移除命令前缀
        command_text = content[len(self.command_prefix):].strip()
        parts = command_text.split()
        
        if not parts:
            return "❓ 请输入有效命令，使用 \\help 查看帮助"
        
        command = parts[0].lower()
        
        try:
            # 创建任务命令
            if command == "cr":
                return await self._handle_create_task(user_id, username, command_text)
            
            # 完成任务命令
            elif command == "fi":
                return self._handle_finish_task(user_id, parts)
            
            # 查询任务命令
            elif command == "ch":
                return self._handle_check_tasks(user_id, parts)
            
            # 统计信息命令
            elif command == "stats":
                return self.task_manager.format_user_stats(user_id, username)
            
            # 帮助命令
            elif command == "help":
                return self._get_help_text()
            
            else:
                return f"❓ 未知命令: {command}\n使用 \\help 查看帮助信息"
                
        except Exception as e:
            _log.error(f"处理命令时出错: {e}")
            return f"❌ 处理命令时发生错误: {str(e)}"
    
    async def _handle_create_task(self, user_id: str, username: str, command_text: str) -> str:
        """处理创建任务命令"""
        match = re.match(r'cr\s+(.+?)\s+(.+)$', command_text, re.IGNORECASE)
        
        if not match:
            return ("❌ 命令格式错误！\n\n"
                   "正确格式：\\cr <任务名称> <截止时间>\n"
                   "示例：\\cr 完成作业 明天 18:00\n"
                   "      \\cr 锻炼身体 2小时后")
        
        task_name = match.group(1).strip()
        deadline_str = match.group(2).strip()
        
        if len(task_name) < 2:
            return "❌ 任务名称至少需要2个字符"
        
        if len(task_name) > 100:
            return "❌ 任务名称不能超过100个字符"
        
        # 创建任务
        success, response = self.task_manager.create_task(user_id, username, task_name, deadline_str)
        
        if success:
            _log.info(f"用户 {username}({user_id}) 创建任务: {task_name}")
        
        return response
    
    def _handle_finish_task(self, user_id: str, parts: list) -> str:
        """处理完成任务命令"""
        if len(parts) < 2:
            return ("❌ 命令格式错误！\n\n"
                   "正确格式：\\fi <任务ID>\n"
                   "示例：\\fi 1")
        
        try:
            task_id = int(parts[1])
        except ValueError:
            return "❌ 任务ID必须是数字"
        
        success, response = self.task_manager.complete_task(user_id, task_id)
        
        if success:
            _log.info(f"用户 {user_id} 完成任务: {task_id}")
        
        return response
    
    def _handle_check_tasks(self, user_id: str, parts: list) -> str:
        """处理查询任务命令"""
        query_type = ""
        search_query = ""
        
        if len(parts) > 1:
            if parts[1] == "-a":
                query_type = "-a"
            elif parts[1] == "-f":
                query_type = "-f"
            elif parts[1] == "-s":
                query_type = "-s"
                if len(parts) > 2:
                    search_query = " ".join(parts[2:])
                else:
                    return "❌ 搜索命令需要指定关键词\n示例：\\ch -s 学习"
        
        return self.task_manager.query_tasks(user_id, query_type, search_query)
    
    def _get_help_text(self) -> str:
        """获取帮助文本"""
        return """🍅 代币番茄钟机器人使用指南

📝 创建任务：
\\cr <任务名称> <截止时间>
示例：\\cr 完成作业 明天 18:00
      \\cr 锻炼身体 2小时后
      \\cr 学习Python 12-25 20:00

✅ 完成任务：
\\fi <任务ID>
示例：\\fi 1

📋 查询任务：
\\ch        - 查看未完成任务
\\ch -a     - 查看所有任务
\\ch -f     - 查看已完成任务
\\ch -s <关键词> - 搜索任务
示例：\\ch -s 学习

📊 其他命令：
\\stats     - 查看个人统计
\\help      - 显示帮助信息

⏰ 时间格式支持：
• 2024-12-25 18:00
• 12-25 18:00
• 明天 18:00
• 后天 9:30
• 3天后 15:00
• 2小时后
• 30分钟后

💡 功能特色：
• AI智能评估任务价值，转换为相应代币奖励
• 按时完成获得奖励，过期会扣除代币
• 机器人会自动提醒即将到期的任务"""
    
    async def _send_notification(self, user_id: str, message_text: str):
        """发送通知给用户（用于定时任务）"""
        _log.info(f"通知用户 {user_id}: {message_text}")

def main():
    print("🍅 工作版代币番茄钟机器人")
    print("=" * 40)
    print("基于demo.py的成功模式")
    print()
    
    try:
        bot = WorkingTomatoBot()
        bot.run(appid=bot.config["appid"], secret=bot.config["secret"])
        
    except KeyboardInterrupt:
        print("\n👋 机器人已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        _log.error(f"机器人启动失败: {e}")

if __name__ == "__main__":
    main()
