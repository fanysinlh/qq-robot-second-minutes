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

class TomatoBot(botpy.Client):
    def __init__(self, config_path: str = "config.yaml", db_path: str = "token_tomato.db", is_sandbox: bool = True):
        """
        初始化代币番茄钟机器人
        
        Args:
            config_path: 配置文件路径
            db_path: 数据库路径
            is_sandbox: 是否使用沙盒环境（测试中的机器人应设为True）
        """
        # 读取配置
        self.config = read(config_path)
        self.is_sandbox = is_sandbox
        
        # 初始化父类 - 使用默认权限配置
        intents = botpy.Intents.default()
        super().__init__(intents=intents, is_sandbox=is_sandbox)
        
        # 初始化任务管理器
        ai_service = self.config.get("ai_service", "deepseek")
        self.task_manager = TokenTomatoManager(db_path, ai_service=ai_service, config_dict=self.config)
        
        # 初始化调度器
        self.scheduler = TomatoScheduler(self.task_manager, self._send_notification)
        
        # 命令前缀
        self.command_prefix = "\\"
        
        # 帮助信息
        self.help_text = """
🍅 代币番茄钟机器人使用指南

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
• 机器人会自动提醒即将到期的任务
"""
    
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
    
    async def on_at_message_create(self, message: Message):
        """处理@机器人的消息（频道）"""
        await self._handle_message(message)
    
    async def on_direct_message_create(self, message: Message):
        """处理私信消息"""
        await self._handle_message(message)
    
    async def on_group_at_message_create(self, message: Message):
        """处理QQ群@机器人的消息"""
        logging.info(f"收到QQ群@消息: {message.content}")
        await self._handle_message(message)
    
    async def on_c2c_message_create(self, message: Message):
        """处理单聊消息"""
        logging.info(f"收到单聊消息: {message.content}")
        await self._handle_message(message)
    
    async def _handle_message(self, message: Message):
        """处理消息的核心逻辑"""
        # 忽略机器人自己的消息（安全检查bot属性）
        if hasattr(message.author, 'bot') and message.author.bot:
            return
        
        content = message.content.strip()
        
        # 安全获取用户ID（群聊和频道使用不同的ID字段）
        user_id = getattr(message.author, 'member_openid', 
                         getattr(message.author, 'id', 'unknown_user'))
        
        # 安全获取用户名（群聊和频道可能有不同的属性）
        username = getattr(message.author, 'username', 
                          getattr(message.author, 'nick', 
                                 getattr(message.author, 'name', f'用户{str(user_id)[:8]}')))
        
        # 移除@机器人的部分
        content = re.sub(r'<@!\d+>', '', content).strip()
        
        # 检查是否是命令
        if not content.startswith(self.command_prefix):
            return
        
        # 解析命令
        command_text = content[len(self.command_prefix):].strip()
        
        try:
            await self._process_command(message, user_id, username, command_text)
        except Exception as e:
            logging.error(f"处理命令时发生错误: {e}")
            await self._safe_reply(message, f"❌ 处理命令时发生错误: {str(e)}")
    
    async def _safe_reply(self, message, reply_text: str):
        """安全的回复方法 - 处理不同类型的消息"""
        try:
            # 检查是否是群聊消息
            if hasattr(message, 'group_openid'):
                # 群聊消息 - 由于权限限制，记录到日志
                print(f"📨 群聊回复 (无权限): {reply_text}")
                logging.info(f"群聊回复内容: {reply_text}")
            else:
                # 频道或私信消息 - 正常回复
                await message.reply(reply_text)
        except Exception as e:
            logging.error(f"回复消息失败: {e}")
            print(f"⚠️ 回复失败，内容: {reply_text}")
    
    async def _process_command(self, message: Message, user_id: str, username: str, command_text: str):
        """处理具体命令"""
        parts = command_text.split()
        if not parts:
            return
        
        command = parts[0].lower()
        
        # 创建任务命令
        if command == "cr":
            await self._handle_create_task(message, user_id, username, command_text)
        
        # 完成任务命令
        elif command == "fi":
            await self._handle_finish_task(message, user_id, parts)
        
        # 查询任务命令
        elif command == "ch":
            await self._handle_check_tasks(message, user_id, parts)
        
        # 统计信息命令
        elif command == "stats":
            await self._handle_stats(message, user_id, username)
        
        # 帮助命令
        elif command == "help":
            await self._safe_reply(message, self.help_text)
        
        # 管理员命令（可选）
        elif command == "admin" and self._is_admin(user_id):
            await self._handle_admin_command(message, parts)
        
        else:
            await self._safe_reply(message, f"❓ 未知命令: {command}\n使用 \\help 查看帮助信息")
    
    async def _handle_create_task(self, message: Message, user_id: str, username: str, command_text: str):
        """处理创建任务命令"""
        # 解析命令：\cr 任务名称 截止时间
        match = re.match(r'cr\s+(.+?)\s+(.+)$', command_text, re.IGNORECASE)
        
        if not match:
            await self._safe_reply(message,
                "❌ 命令格式错误！\n\n"
                "正确格式：\\cr <任务名称> <截止时间>\n"
                "示例：\\cr 完成作业 明天 18:00\n"
                "      \\cr 锻炼身体 2小时后\n\n"
                "使用 \\help 查看详细帮助"
            )
            return
        
        task_name = match.group(1).strip()
        deadline_str = match.group(2).strip()
        
        # 验证任务名称
        if len(task_name) < 2:
            await self._safe_reply(message, "❌ 任务名称至少需要2个字符")
            return
        
        if len(task_name) > 100:
            await self._safe_reply(message, "❌ 任务名称不能超过100个字符")
            return
        
        # 创建任务
        success, response = self.task_manager.create_task(user_id, username, task_name, deadline_str)
        await self._safe_reply(message, response)
        
        if success:
            logging.info(f"用户 {username}({user_id}) 创建任务: {task_name}")
    
    async def _handle_finish_task(self, message: Message, user_id: str, parts: list):
        """处理完成任务命令"""
        if len(parts) < 2:
            await self._safe_reply(message,
                "❌ 命令格式错误！\n\n"
                "正确格式：\\fi <任务ID>\n"
                "示例：\\fi 1\n\n"
                "使用 \\ch 查看您的任务ID"
            )
            return
        
        try:
            task_id = int(parts[1])
        except ValueError:
            await self._safe_reply(message, "❌ 任务ID必须是数字")
            return
        
        # 完成任务
        success, response = self.task_manager.complete_task(user_id, task_id)
        await self._safe_reply(message, response)
        
        if success:
            logging.info(f"用户 {user_id} 完成任务: {task_id}")
    
    async def _handle_check_tasks(self, message: Message, user_id: str, parts: list):
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
                    await self._safe_reply(message, "❌ 搜索命令需要指定关键词\n示例：\\ch -s 学习")
                    return
        
        # 查询任务
        response = self.task_manager.query_tasks(user_id, query_type, search_query)
        await self._safe_reply(message, response)
    
    async def _handle_stats(self, message: Message, user_id: str, username: str):
        """处理统计信息命令"""
        stats_text = self.task_manager.format_user_stats(user_id, username)
        await self._safe_reply(message, stats_text)
    
    async def _handle_admin_command(self, message: Message, parts: list):
        """处理管理员命令（可选功能）"""
        if len(parts) < 2:
            return
        
        admin_cmd = parts[1].lower()
        
        if admin_cmd == "status":
            # 显示系统状态
            scheduler_status = self.scheduler.get_scheduler_status()
            status_text = f"🤖 机器人状态\n\n" \
                         f"📊 调度器状态: {'运行中' if scheduler_status['is_running'] else '已停止'}\n" \
                         f"⏰ 定时任务数: {scheduler_status['total_jobs']}\n" \
                         f"🕒 下次运行: {scheduler_status['next_run_time']}\n"
            
            await self._safe_reply(message, status_text)
        
        elif admin_cmd == "restart_scheduler":
            # 重启调度器
            self.scheduler.stop()
            await asyncio.sleep(1)
            self.scheduler.start()
            await self._safe_reply(message, "✅ 调度器已重启")
    
    def _is_admin(self, user_id: str) -> bool:
        """检查用户是否为管理员"""
        # 这里可以配置管理员用户ID列表
        admin_users = getattr(self.config, 'admin_users', [])
        return user_id in admin_users
    
    async def _send_notification(self, user_id: str, message_text: str):
        """发送通知给用户（用于定时任务）"""
        try:
            # 这里需要根据实际情况发送消息
            # 由于botpy的限制，可能需要通过频道或群聊发送
            # 具体实现需要根据你的机器人部署环境调整
            
            # 示例：通过日志记录（实际应该发送消息）
            logging.info(f"通知用户 {user_id}: {message_text}")
            
            # 如果你有用户与频道的映射关系，可以这样发送：
            # channel = await self.fetch_channel(channel_id)
            # await channel.send(f"<@{user_id}> {message_text}")
            
        except Exception as e:
            logging.error(f"发送通知失败: {e}")

def create_config_template():
    """创建配置文件模板"""
    config_template = """
# QQ机器人配置
appid: "你的机器人APPID"
secret: "你的机器人SECRET"

# 管理员用户ID列表（可选）
admin_users:
  - "管理员用户ID1"
  - "管理员用户ID2"

# AI服务配置（可选）
ai_service: "deepseek"  # 可选: deepseek, openai, zhipu, simple

# DeepSeek配置（推荐使用）
deepseek:
  api_key: "你的DeepSeek API Key"
  api_base: "https://api.deepseek.com/v1"
  model: "deepseek-chat"

# OpenAI配置（备选）
openai:
  api_key: "你的OpenAI API Key"
  api_base: "https://api.openai.com/v1"
  model: "gpt-3.5-turbo"

# 其他配置
database_path: "token_tomato.db"
log_level: "INFO"
"""
    
    if not os.path.exists("config.yaml"):
        with open("config.yaml", "w", encoding="utf-8") as f:
            f.write(config_template.strip())
        print("✅ 已创建配置文件模板: config.yaml")
        print("📝 请编辑配置文件，填入你的机器人信息")
        return False
    return True

def main():
    """主函数"""
    print("🍅 代币番茄钟机器人启动中...")
    
    # 检查并创建配置文件
    if not create_config_template():
        return
    
    try:
        # 创建并运行机器人（默认使用沙盒环境，适合测试中的机器人）
        print("💡 使用沙盒环境启动（适合'测试中'状态的机器人）")
        print("   如需正式环境，请修改 main() 函数中的 is_sandbox=False")
        print()
        
        bot = TomatoBot(is_sandbox=True)  # 测试中的机器人使用沙盒环境
        bot.run(appid=bot.config["appid"], secret=bot.config["secret"])
        
    except KeyboardInterrupt:
        print("\n👋 机器人正在关闭...")
    except Exception as e:
        logging.error(f"机器人运行出错: {e}")
        print(f"❌ 机器人运行出错: {e}")
        print()
        print("💡 如果出现IP白名单错误，请确认:")
        print("1. 在QQ开放平台的【沙盒环境】中设置了IP白名单")
        print("2. 机器人状态为'测试中'时需要使用沙盒环境")
        print("3. IP白名单设置后需要等待5-15分钟生效")
    finally:
        print("🔚 机器人已关闭")

if __name__ == "__main__":
    main()
