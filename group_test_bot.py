#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQ群聊机器人测试版本
专门用于测试群聊消息接收和回复
"""

import asyncio
import botpy
from botpy.ext.cog_yaml import read
from botpy.message import Message
import logging
import re

# 配置日志
logging.basicConfig(level=logging.INFO)

class GroupTestBot(botpy.Client):
    def __init__(self):
        # 读取配置
        self.config = read("config.yaml")
        
        # 初始化父类 - 专注于群聊消息
        intents = botpy.Intents(
            public_guild_messages=True,
            guild_messages=True
        )
        super().__init__(intents=intents, is_sandbox=True)
        
        self.message_count = 0
    
    async def on_ready(self):
        """机器人就绪事件"""
        print("🤖 群聊测试机器人已启动！")
        print("🎯 专门用于测试QQ群聊功能")
        print("📝 请在群中@机器人并发送消息")
        print("=" * 50)
        print("💡 测试命令:")
        print("   @机器人 test")
        print("   @机器人 ping")
        print("   @机器人 \\help")
        print("=" * 50)
    
    async def on_at_message_create(self, message: Message):
        """处理@机器人的群聊消息"""
        self.message_count += 1
        
        print(f"\n🎯 收到第{self.message_count}条@消息:")
        print(f"   👤 用户: {message.author.username}")
        print(f"   📝 原始内容: {message.content}")
        print(f"   🆔 用户ID: {message.author.id}")
        print(f"   📍 频道ID: {getattr(message, 'guild_id', 'N/A')}")
        print(f"   📍 子频道ID: {getattr(message, 'channel_id', 'N/A')}")
        
        # 清理@标记
        clean_content = re.sub(r'<@!\d+>', '', message.content).strip()
        print(f"   ✨ 清理后内容: '{clean_content}'")
        
        # 根据内容回复
        try:
            if not clean_content:
                reply_text = "👋 你好！我是代币番茄钟机器人！\n\n请发送命令，例如:\n• test - 测试连接\n• \\help - 查看帮助"
            elif "test" in clean_content.lower():
                reply_text = "✅ 测试成功！机器人工作正常！\n🍅 代币番茄钟系统已就绪！"
            elif "ping" in clean_content.lower():
                reply_text = "🏓 Pong! 机器人响应正常！"
            elif "help" in clean_content.lower() or "\\help" in clean_content:
                reply_text = """🍅 代币番茄钟机器人帮助

📝 基本命令:
• \\cr <任务名> <时间> - 创建任务
• \\fi <任务ID> - 完成任务  
• \\ch - 查看任务
• \\stats - 查看统计

⏰ 时间格式:
• 明天 18:00
• 2小时后
• 12-25 20:00

🤖 当前状态: 测试环境运行正常"""
            else:
                reply_text = f"📨 我收到了你的消息: {clean_content}\n\n💡 发送 'test' 测试功能，或 '\\help' 查看帮助"
            
            # 发送回复
            await message.reply(reply_text)
            print(f"   ✅ 回复发送成功: {reply_text[:50]}...")
            
        except Exception as e:
            print(f"   ❌ 回复发送失败: {e}")
            
            # 尝试简单回复
            try:
                await message.reply("🤖 机器人收到消息，但回复时出现问题")
                print("   ⚠️ 简化回复发送成功")
            except Exception as e2:
                print(f"   ❌ 简化回复也失败: {e2}")
        
        print("-" * 50)
    
    async def on_guild_message_create(self, message: Message):
        """监听所有群聊消息（不需要@）"""
        # 只记录，不回复（避免刷屏）
        if not message.author.bot:  # 忽略机器人消息
            print(f"📨 群消息: {message.author.username}: {message.content[:50]}")
    
    async def on_message_create(self, message: Message):
        """监听所有消息"""
        if not message.author.bot:  # 忽略机器人消息
            print(f"🔔 收到消息: {message.author.username}: {message.content[:30]}")

def main():
    print("🤖 QQ群聊机器人测试")
    print("=" * 30)
    print("💡 此版本专门用于测试群聊功能")
    print("🎯 请在QQ群中@机器人发送消息")
    print()
    
    try:
        bot = GroupTestBot()
        print(f"📋 配置:")
        print(f"   AppID: {bot.config['appid']}")
        print(f"   环境: 沙盒环境")
        print()
        print("🚀 启动群聊测试机器人...")
        print()
        
        bot.run(appid=bot.config["appid"], secret=bot.config["secret"])
        
    except KeyboardInterrupt:
        print("\n👋 测试结束")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print()
        print("💡 可能的解决方案:")
        print("1. 检查机器人是否有群聊权限")
        print("2. 确认在正确的测试群中")
        print("3. 检查群聊设置是否允许机器人")
        print("4. 尝试将机器人设为群管理员")

if __name__ == "__main__":
    main()

