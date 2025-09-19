#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复后的代币番茄钟机器人
专门处理群聊回复问题
"""

import asyncio
import re
import botpy
from botpy.message import Message
from botpy.ext.cog_yaml import read
from datetime import datetime
from task_manager import TokenTomatoManager
from scheduler import TomatoScheduler
import logging
import sys
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tomato_bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

class FixedTomatoBot(botpy.Client):
    def __init__(self, config_path: str = "config.yaml", db_path: str = "token_tomato.db", is_sandbox: bool = True):
        """
        初始化修复后的代币番茄钟机器人
        """
        # 读取配置
        self.config = read(config_path)
        self.is_sandbox = is_sandbox
        
        # 初始化父类
        intents = botpy.Intents.default()
        super().__init__(intents=intents, is_sandbox=is_sandbox)
        
        # 初始化任务管理器
        ai_service = self.config.get("ai_service", "deepseek")
        self.task_manager = TokenTomatoManager(db_path, ai_service=ai_service, config_dict=self.config)
        
        # 初始化调度器
        self.scheduler = TomatoScheduler(self.task_manager, self._send_notification)
        
        # 命令前缀
        self.command_prefix = "\\"
    
    async def on_ready(self):
        """机器人就绪事件"""
        env_type = "沙盒环境" if self.is_sandbox else "正式环境"
        
        try:
            bot_name = getattr(self.robot, 'name', '代币番茄钟机器人')
            logging.info(f"机器人已登录: {bot_name} (运行在{env_type})")
            print(f"🤖 机器人: {bot_name}")
        except:
            logging.info(f"机器人已登录 (运行在{env_type})")
            print(f"🤖 机器人: 代币番茄钟机器人")
        
        logging.info("🍅 代币番茄钟机器人启动成功！")
        
        # 启动调度器
        self.scheduler.start()
        logging.info("定时任务调度器已启动")
        
        print(f"✅ 机器人已成功启动！")
        print(f"🌍 环境: {env_type}")
        print(f"🍅 代币番茄钟系统已就绪！")
        print()
        print("📝 使用说明:")
        print("• @机器人 \\help - 查看帮助")
        print("• @机器人 \\cr 任务名称 截止时间 - 创建任务")
        print("• @机器人 \\ch - 查看任务")
        print("• @机器人 \\fi 任务ID - 完成任务")
    
    async def on_group_at_message_create(self, message):
        """处理QQ群@机器人的消息 - 修复版本"""
        logging.info(f"收到QQ群@消息: {message.content}")
        await self._handle_group_message(message)
    
    async def on_at_message_create(self, message: Message):
        """处理频道@机器人的消息"""
        await self._handle_message(message)
    
    async def on_direct_message_create(self, message: Message):
        """处理私信消息"""
        await self._handle_message(message)
    
    async def _handle_group_message(self, message):
        """专门处理群聊消息的方法"""
        try:
            # 忽略机器人自己的消息
            if hasattr(message.author, 'bot') and message.author.bot:
                return
            
            content = message.content.strip()
            user_id = message.author.member_openid  # 群聊使用member_openid
            
            # 安全获取用户名
            username = self._get_safe_username(message.author, user_id)
            
            # 移除@机器人的部分
            content = re.sub(r'<@!\d+>', '', content).strip()
            
            # 检查是否是命令
            if not content.startswith(self.command_prefix):
                return
            
            # 解析命令
            command_text = content[len(self.command_prefix):].strip()
            
            # 处理命令并获取回复
            reply_text = await self._process_group_command(user_id, username, command_text)
            
            # 发送回复
            await self._send_group_reply(message, reply_text)
            
        except Exception as e:
            logging.error(f"处理群聊消息时发生错误: {e}")
            try:
                await self._send_group_reply(message, f"❌ 处理命令时发生错误: {str(e)}")
            except:
                pass
    
    def _get_safe_username(self, author, user_id: str) -> str:
        """安全获取用户名"""
        # 尝试不同的用户名属性
        user_attrs = ['username', 'nick', 'name', 'user_openid', 'member_openid']
        
        for attr in user_attrs:
            if hasattr(author, attr):
                value = getattr(author, attr)
                if value and str(value).strip():
                    return str(value)
        
        return f'用户{user_id[:8]}'
    
    async def _send_group_reply(self, message, reply_text: str):
        """发送群聊回复 - 尝试多种方式"""
        success = False
        
        # 方式1: 尝试标准reply（可能不支持参数）
        try:
            # 根据错误信息，reply()可能不接受参数
            # 我们先尝试无参数调用
            await message.reply()
            success = True
            logging.info("群聊回复发送成功 (无参数reply)")
        except Exception as e:
            logging.debug(f"无参数reply失败: {e}")
        
        # 方式2: 通过API发送群消息
        if not success:
            try:
                group_openid = getattr(message, 'group_openid', None)
                if group_openid and hasattr(self, 'api'):
                    await self.api.post_group_message(
                        group_openid=group_openid,
                        msg_type=0,  # 文本消息
                        content=reply_text
                    )
                    success = True
                    logging.info("群聊回复发送成功 (API)")
            except Exception as e:
                logging.debug(f"API发送失败: {e}")
        
        # 方式3: 记录到日志（如果无法发送回复）
        if not success:
            logging.warning(f"无法发送群聊回复，内容: {reply_text}")
            print(f"⚠️ 无法发送群聊回复: {reply_text}")
    
    async def _process_group_command(self, user_id: str, username: str, command_text: str) -> str:
        """处理群聊命令并返回回复文本"""
        parts = command_text.split()
        if not parts:
            return "❓ 请输入有效命令，使用 \\help 查看帮助"
        
        command = parts[0].lower()
        
        try:
            # 创建任务命令
            if command == "cr":
                return await self._handle_create_task_command(user_id, username, command_text)
            
            # 完成任务命令
            elif command == "fi":
                return await self._handle_finish_task_command(user_id, parts)
            
            # 查询任务命令
            elif command == "ch":
                return self._handle_check_tasks_command(user_id, parts)
            
            # 统计信息命令
            elif command == "stats":
                return self.task_manager.format_user_stats(user_id, username)
            
            # 帮助命令
            elif command == "help":
                return self._get_help_text()
            
            else:
                return f"❓ 未知命令: {command}\n使用 \\help 查看帮助信息"
                
        except Exception as e:
            logging.error(f"处理命令时出错: {e}")
            return f"❌ 处理命令时发生错误: {str(e)}"
    
    async def _handle_create_task_command(self, user_id: str, username: str, command_text: str) -> str:
        """处理创建任务命令"""
        match = re.match(r'cr\s+(.+?)\s+(.+)$', command_text, re.IGNORECASE)
        
        if not match:
            return ("❌ 命令格式错误！\n\n"
                   "正确格式：\\cr <任务名称> <截止时间>\n"
                   "示例：\\cr 完成作业 明天 18:00\n"
                   "      \\cr 锻炼身体 2小时后\n\n"
                   "使用 \\help 查看详细帮助")
        
        task_name = match.group(1).strip()
        deadline_str = match.group(2).strip()
        
        # 验证任务名称
        if len(task_name) < 2:
            return "❌ 任务名称至少需要2个字符"
        
        if len(task_name) > 100:
            return "❌ 任务名称不能超过100个字符"
        
        # 创建任务
        success, response = self.task_manager.create_task(user_id, username, task_name, deadline_str)
        return response
    
    async def _handle_finish_task_command(self, user_id: str, parts: list) -> str:
        """处理完成任务命令"""
        if len(parts) < 2:
            return ("❌ 命令格式错误！\n\n"
                   "正确格式：\\fi <任务ID>\n"
                   "示例：\\fi 1\n\n"
                   "使用 \\ch 查看您的任务ID")
        
        try:
            task_id = int(parts[1])
        except ValueError:
            return "❌ 任务ID必须是数字"
        
        # 完成任务
        success, response = self.task_manager.complete_task(user_id, task_id)
        return response
    
    def _handle_check_tasks_command(self, user_id: str, parts: list) -> str:
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
        
        # 查询任务
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

💡 提示：
• 任务价值由AI智能评估，转换为相应代币奖励
• 按时完成获得奖励，过期会扣除代币
• 机器人会自动提醒即将到期的任务"""
    
    async def _handle_message(self, message: Message):
        """处理频道和私信消息的核心逻辑"""
        # 忽略机器人自己的消息
        if message.author.bot:
            return
        
        content = message.content.strip()
        user_id = message.author.id
        
        # 安全获取用户名
        username = getattr(message.author, 'username', 
                          getattr(message.author, 'nick', 
                                 getattr(message.author, 'name', f'用户{user_id}')))
        
        # 移除@机器人的部分
        content = re.sub(r'<@!\d+>', '', content).strip()
        
        # 检查是否是命令
        if not content.startswith(self.command_prefix):
            return
        
        # 解析命令
        command_text = content[len(self.command_prefix):].strip()
        
        try:
            reply_text = await self._process_group_command(user_id, username, command_text)
            await message.reply(reply_text)
        except Exception as e:
            logging.error(f"处理命令时发生错误: {e}")
            await message.reply(f"❌ 处理命令时发生错误: {str(e)}")
    
    async def _send_notification(self, user_id: str, message_text: str):
        """发送通知给用户（用于定时任务）"""
        try:
            logging.info(f"通知用户 {user_id}: {message_text}")
        except Exception as e:
            logging.error(f"发送通知失败: {e}")

def main():
    """主函数"""
    print("🍅 修复版代币番茄钟机器人启动中...")
    
    try:
        print("💡 使用沙盒环境启动（适合'测试中'状态的机器人）")
        print()
        
        bot = FixedTomatoBot(is_sandbox=True)
        bot.run(appid=bot.config["appid"], secret=bot.config["secret"])
        
    except KeyboardInterrupt:
        print("\n👋 机器人正在关闭...")
    except Exception as e:
        logging.error(f"机器人运行出错: {e}")
        print(f"❌ 机器人运行出错: {e}")
    finally:
        print("🔚 机器人已关闭")

if __name__ == "__main__":
    main()
