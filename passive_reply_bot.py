#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
被动回复版QQ群聊机器人
专门处理权限受限的测试环境
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
logging.basicConfig(level=logging.INFO)

class PassiveReplyBot(botpy.Client):
    def __init__(self, config_path: str = "config.yaml", db_path: str = "token_tomato.db"):
        """
        被动回复版代币番茄钟机器人
        适用于权限受限的测试环境
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
        
        # 用户状态缓存（用于多步操作）
        self.user_states = {}
    
    async def on_ready(self):
        """机器人就绪事件"""
        try:
            bot_name = getattr(self.robot, 'name', '代币番茄钟机器人')
            print(f"🤖 机器人: {bot_name}")
        except:
            print(f"🤖 机器人: 代币番茄钟机器人")
        
        # 启动调度器
        self.scheduler.start()
        
        print(f"✅ 被动回复版代币番茄钟机器人已启动！")
        print(f"🌍 环境: 沙盒环境 (权限受限)")
        print(f"🍅 系统已就绪！")
        print()
        print("⚠️ 注意: 由于权限限制，机器人无法主动发送群聊消息")
        print("💡 解决方案:")
        print("1. 在QQ开放平台申请群聊消息权限")
        print("2. 或者使用QQ频道代替群聊")
        print("3. 或者等待机器人正式上线")
        print()
        print("📝 当前功能:")
        print("• 能接收和处理群聊@消息")
        print("• 任务数据正常保存到数据库")
        print("• 可以通过日志查看处理结果")
        print("• 频道和私信功能正常")
        print("=" * 50)
    
    async def on_group_at_message_create(self, message):
        """处理QQ群@机器人的消息 - 被动处理版"""
        print(f"\n📨 收到群聊@消息: {message.content}")
        
        try:
            # 获取用户信息
            user_id = message.author.member_openid
            username = f"用户{user_id[:8]}"
            
            print(f"👤 用户: {username}")
            print(f"📍 群ID: {message.group_openid}")
            
            # 清理消息内容
            content = re.sub(r'<@!\d+>', '', message.content).strip()
            print(f"📝 清理后内容: '{content}'")
            
            # 处理命令
            if content.startswith(self.command_prefix):
                result = await self._process_command(user_id, username, content)
                print(f"📋 处理结果: {result}")
                
                # 由于无法发送群聊消息，我们通过其他方式提供反馈
                await self._provide_feedback(user_id, result, message)
            else:
                print(f"💬 收到非命令消息，已记录")
            
        except Exception as e:
            print(f"❌ 处理群聊消息时出错: {e}")
            logging.error(f"处理群聊消息时出错: {e}")
        
        print("-" * 50)
    
    async def _provide_feedback(self, user_id: str, result: str, message):
        """提供用户反馈 - 多种方式"""
        
        # 方式1: 记录到日志（用户可以查看终端）
        print(f"💬 回复内容: {result}")
        logging.info(f"用户 {user_id} 的操作结果: {result}")
        
        # 方式2: 尝试通过其他渠道发送（如果有的话）
        try:
            # 检查是否可以发送私信（通常权限更宽松）
            if hasattr(self, 'api') and hasattr(self.api, 'post_dms'):
                await self.api.post_dms(
                    recipient_id=user_id,
                    msg_type=0,
                    content=f"🍅 群聊操作结果:\n{result}"
                )
                print("✅ 已通过私信发送结果")
                return
        except Exception as e:
            print(f"⚠️ 私信发送失败: {e}")
        
        # 方式3: 保存到文件（用户可以查看）
        try:
            with open(f"user_feedback_{user_id[:8]}.txt", "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now()}] {result}\n")
            print(f"📄 结果已保存到文件: user_feedback_{user_id[:8]}.txt")
        except Exception as e:
            print(f"⚠️ 文件保存失败: {e}")
        
        # 方式4: 显示操作提示
        print(f"""
💡 由于权限限制，无法直接回复群聊消息
📋 用户 {user_id[:8]} 的操作已完成
📝 结果: {result[:100]}...
        
🔧 解决权限问题的方法:
1. 在QQ开放平台申请"群聊消息权限"
2. 将机器人状态从"测试中"改为"已上线"
3. 使用QQ频道代替群聊
4. 联系QQ开放平台技术支持
        """)
    
    async def _process_command(self, user_id: str, username: str, content: str) -> str:
        """处理命令并返回结果"""
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
                   "示例：\\cr 完成作业 明天 18:00")
        
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
                    return "❌ 搜索命令需要指定关键词"
        
        return self.task_manager.query_tasks(user_id, query_type, search_query)
    
    def _get_help_text(self) -> str:
        """获取帮助文本"""
        return """🍅 代币番茄钟机器人帮助

📝 基本命令:
• \\cr <任务名> <时间> - 创建任务
• \\fi <任务ID> - 完成任务  
• \\ch - 查看任务
• \\stats - 查看统计

⚠️ 当前限制:
由于测试环境权限限制，机器人无法直接回复群聊消息
但所有功能都正常工作，结果会显示在终端日志中

🔧 完整功能需要:
1. 申请群聊消息权限
2. 机器人正式上线
3. 或使用QQ频道"""
    
    # 处理频道和私信消息（这些通常有权限）
    async def on_at_message_create(self, message):
        """处理频道@消息"""
        try:
            user_id = message.author.id
            username = getattr(message.author, 'username', f'用户{user_id}')
            
            content = re.sub(r'<@!\d+>', '', message.content).strip()
            
            if content.startswith(self.command_prefix):
                result = await self._process_command(user_id, username, content)
                await message.reply(result)
                print(f"✅ 频道回复成功: {result[:50]}...")
            
        except Exception as e:
            logging.error(f"处理频道消息出错: {e}")
    
    async def on_direct_message_create(self, message):
        """处理私信消息"""
        try:
            user_id = message.author.id
            username = getattr(message.author, 'username', f'用户{user_id}')
            
            content = message.content.strip()
            
            if content.startswith(self.command_prefix):
                result = await self._process_command(user_id, username, content)
                await message.reply(result)
                print(f"✅ 私信回复成功: {result[:50]}...")
            
        except Exception as e:
            logging.error(f"处理私信出错: {e}")
    
    async def _send_notification(self, user_id: str, message_text: str):
        """发送通知给用户"""
        logging.info(f"通知用户 {user_id}: {message_text}")

def main():
    print("🍅 被动回复版代币番茄钟机器人")
    print("=" * 40)
    print("⚠️  适用于权限受限的测试环境")
    print()
    
    try:
        bot = PassiveReplyBot()
        bot.run(appid=bot.config["appid"], secret=bot.config["secret"])
        
    except KeyboardInterrupt:
        print("\n👋 机器人已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        logging.error(f"机器人启动失败: {e}")

if __name__ == "__main__":
    main()

