#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终修复版QQ群聊机器人
基于调试信息的完整解决方案
"""

import asyncio
import re
import botpy
from botpy.ext.cog_yaml import read
from datetime import datetime
from task_manager import TokenTomatoManager
from scheduler import TomatoScheduler
import logging
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class FinalGroupBot(botpy.Client):
    def __init__(self, config_path: str = "config.yaml", db_path: str = "token_tomato.db"):
        """
        最终修复版代币番茄钟机器人
        """
        # 读取配置
        self.config = read(config_path)
        
        # 初始化父类
        intents = botpy.Intents.default()
        super().__init__(intents=intents, is_sandbox=True)
        
        # 初始化任务管理器
        ai_service = self.config.get("ai_service", "deepseek")
        self.task_manager = TokenTomatoManager(db_path, ai_service=ai_service, config_dict=self.config)
        
        # 初始化调度器
        self.scheduler = TomatoScheduler(self.task_manager, self._send_notification)
        
        # 命令前缀
        self.command_prefix = "\\"
    
    async def on_ready(self):
        """机器人就绪事件"""
        try:
            bot_name = getattr(self.robot, 'name', '代币番茄钟机器人')
            print(f"🤖 机器人: {bot_name}")
        except:
            print(f"🤖 机器人: 代币番茄钟机器人")
        
        # 启动调度器
        self.scheduler.start()
        
        print(f"✅ 代币番茄钟机器人已启动！")
        print(f"🌍 环境: 沙盒环境")
        print(f"🍅 系统已就绪！")
        print()
        print("📝 群聊使用说明:")
        print("• @机器人 \\help - 查看帮助")
        print("• @机器人 \\cr 任务名称 截止时间 - 创建任务")
        print("• @机器人 \\ch - 查看任务")
        print("• @机器人 \\fi 任务ID - 完成任务")
        print("=" * 50)
    
    async def on_group_at_message_create(self, message):
        """处理QQ群@机器人的消息 - 最终修复版"""
        print(f"\n📨 收到群聊@消息: {message.content}")
        
        try:
            # 获取用户信息
            user_id = message.author.member_openid
            username = f"用户{user_id[:8]}"  # 使用ID前8位作为用户名
            
            print(f"👤 用户: {username} (ID: {user_id})")
            print(f"📍 群ID: {message.group_openid}")
            
            # 清理消息内容
            content = re.sub(r'<@!\d+>', '', message.content).strip()
            print(f"📝 清理后内容: '{content}'")
            
            # 检查是否是命令
            if not content.startswith(self.command_prefix):
                reply_text = f"👋 你好！我是代币番茄钟机器人！\n\n请发送命令，例如:\n• \\help - 查看帮助\n• \\cr 任务名 时间 - 创建任务"
            else:
                # 处理命令
                reply_text = await self._process_command(user_id, username, content)
            
            # 发送回复
            success = await self._send_group_message(message.group_openid, reply_text)
            
            if success:
                print(f"✅ 回复发送成功")
            else:
                print(f"❌ 回复发送失败")
            
        except Exception as e:
            print(f"❌ 处理群聊消息时出错: {e}")
            logging.error(f"处理群聊消息时出错: {e}")
        
        print("-" * 50)
    
    async def _send_group_message(self, group_openid: str, content: str) -> bool:
        """发送群聊消息 - 使用正确的API方法"""
        try:
            # 方式1: 使用api.post_group_message
            if hasattr(self, 'api') and hasattr(self.api, 'post_group_message'):
                print(f"🔧 尝试API方式1: post_group_message")
                await self.api.post_group_message(
                    group_openid=group_openid,
                    msg_type=0,  # 文本消息
                    content=content
                )
                return True
            
        except Exception as e:
            print(f"❌ API方式1失败: {e}")
        
        try:
            # 方式2: 使用api.send_group_message (如果存在)
            if hasattr(self, 'api') and hasattr(self.api, 'send_group_message'):
                print(f"🔧 尝试API方式2: send_group_message")
                await self.api.send_group_message(
                    group_openid=group_openid,
                    content=content
                )
                return True
            
        except Exception as e:
            print(f"❌ API方式2失败: {e}")
        
        try:
            # 方式3: 直接构造HTTP请求
            print(f"🔧 尝试API方式3: 直接HTTP请求")
            
            # 获取access_token
            if hasattr(self, 'robot') and hasattr(self.robot, 'token'):
                token = self.robot.token
                
                import requests
                url = f"https://sandbox.api.sgroup.qq.com/v2/groups/{group_openid}/messages"
                headers = {
                    'Authorization': f'QQBot {token}',
                    'Content-Type': 'application/json'
                }
                data = {
                    'msg_type': 0,
                    'content': content
                }
                
                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    return True
                else:
                    print(f"HTTP请求失败: {response.status_code} - {response.text}")
            
        except Exception as e:
            print(f"❌ API方式3失败: {e}")
        
        # 如果所有方式都失败，至少记录到日志
        print(f"⚠️ 无法发送群聊回复，记录到日志: {content}")
        logging.info(f"群聊回复 (群:{group_openid}): {content}")
        return False
    
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
            logging.error(f"处理命令时出错: {e}")
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
        return """🍅 代币番茄钟机器人帮助

📝 基本命令:
• \\cr <任务名> <时间> - 创建任务
• \\fi <任务ID> - 完成任务  
• \\ch - 查看未完成任务
• \\ch -a - 查看所有任务
• \\ch -f - 查看已完成任务
• \\ch -s <关键词> - 搜索任务
• \\stats - 查看个人统计

⏰ 时间格式:
• 明天 18:00
• 2小时后
• 12-25 20:00
• 3天后 15:00

🎯 功能特色:
• AI智能评估任务价值
• 自动代币奖励和惩罚
• 定时提醒功能
• 完整的任务管理

💡 示例:
\\cr 完成作业 明天 18:00
\\fi 1
\\ch -s 学习"""
    
    # 处理其他消息类型
    async def on_at_message_create(self, message):
        """处理频道@消息"""
        try:
            await self._handle_channel_message(message)
        except Exception as e:
            logging.error(f"处理频道消息出错: {e}")
    
    async def _handle_channel_message(self, message):
        """处理频道消息"""
        user_id = message.author.id
        username = getattr(message.author, 'username', f'用户{user_id}')
        
        content = re.sub(r'<@!\d+>', '', message.content).strip()
        
        if content.startswith(self.command_prefix):
            reply_text = await self._process_command(user_id, username, content)
            await message.reply(reply_text)
    
    async def on_direct_message_create(self, message):
        """处理私信消息"""
        try:
            await self._handle_channel_message(message)
        except Exception as e:
            logging.error(f"处理私信出错: {e}")
    
    async def _send_notification(self, user_id: str, message_text: str):
        """发送通知给用户"""
        logging.info(f"通知用户 {user_id}: {message_text}")

def main():
    print("🍅 最终修复版代币番茄钟机器人")
    print("=" * 40)
    
    try:
        bot = FinalGroupBot()
        bot.run(appid=bot.config["appid"], secret=bot.config["secret"])
        
    except KeyboardInterrupt:
        print("\n👋 机器人已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        logging.error(f"机器人启动失败: {e}")

if __name__ == "__main__":
    main()

