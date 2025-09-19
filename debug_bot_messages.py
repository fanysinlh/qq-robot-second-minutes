#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试QQ机器人消息接收
用于排查消息处理问题
"""

import asyncio
import botpy
from botpy.ext.cog_yaml import read
from botpy.message import Message
import logging
import json

# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class DebugBot(botpy.Client):
    def __init__(self):
        # 读取配置
        self.config = read("config.yaml")
        
        # 初始化父类 - 使用沙盒环境，并启用所有消息类型
        intents = botpy.Intents(
            public_guild_messages=True,    # 公开频道消息
            guild_messages=True,           # 私域频道消息
            direct_message=True            # 私信消息
        )
        super().__init__(intents=intents, is_sandbox=True)
        
        self.message_count = 0
    
    async def on_ready(self):
        """机器人就绪事件"""
        print("🔍 调试机器人已启动")
        print(f"🤖 机器人名称: {getattr(self.robot, 'name', '未知')}")
        print("📡 正在监听所有消息类型...")
        print("💡 请在QQ群中@机器人发送消息进行测试")
        print()
    
    async def on_message_create(self, message: Message):
        """处理所有消息"""
        self.message_count += 1
        print(f"\n📨 收到消息 #{self.message_count}")
        print(f"   消息内容: {message.content}")
        print(f"   发送者: {message.author.username}")
        print(f"   消息ID: {message.id}")
        print(f"   频道ID: {getattr(message, 'channel_id', 'N/A')}")
        print(f"   是否@机器人: {message.mention_everyone or (hasattr(message, 'mentions') and len(message.mentions) > 0)}")
        
        # 尝试回复
        try:
            await message.reply("🔍 调试机器人收到消息！")
            print("   ✅ 回复成功")
        except Exception as e:
            print(f"   ❌ 回复失败: {e}")
    
    async def on_at_message_create(self, message: Message):
        """处理@消息"""
        self.message_count += 1
        print(f"\n🎯 收到@消息 #{self.message_count}")
        print(f"   消息内容: {message.content}")
        print(f"   发送者: {message.author.username}")
        print(f"   消息ID: {message.id}")
        print(f"   频道ID: {getattr(message, 'channel_id', 'N/A')}")
        
        # 尝试回复
        try:
            await message.reply("🎯 调试机器人收到@消息！")
            print("   ✅ @消息回复成功")
        except Exception as e:
            print(f"   ❌ @消息回复失败: {e}")
    
    async def on_direct_message_create(self, message: Message):
        """处理私信消息"""
        self.message_count += 1
        print(f"\n💬 收到私信 #{self.message_count}")
        print(f"   消息内容: {message.content}")
        print(f"   发送者: {message.author.username}")
        
        try:
            await message.reply("💬 调试机器人收到私信！")
            print("   ✅ 私信回复成功")
        except Exception as e:
            print(f"   ❌ 私信回复失败: {e}")
    
    async def on_guild_message_create(self, message: Message):
        """处理频道消息"""
        self.message_count += 1
        print(f"\n🏰 收到频道消息 #{self.message_count}")
        print(f"   消息内容: {message.content}")
        print(f"   发送者: {message.author.username}")
        print(f"   频道ID: {getattr(message, 'channel_id', 'N/A')}")
        
        # 检查是否包含关键词
        if "test" in message.content.lower() or "测试" in message.content:
            try:
                await message.reply("🏰 调试机器人收到频道消息！")
                print("   ✅ 频道消息回复成功")
            except Exception as e:
                print(f"   ❌ 频道消息回复失败: {e}")

def main():
    print("🔍 QQ机器人消息调试工具")
    print("=" * 40)
    print("此工具用于调试机器人消息接收问题")
    print()
    
    try:
        bot = DebugBot()
        print("🚀 启动调试机器人...")
        print("💡 请在QQ群中@机器人或发送包含'test'的消息")
        print("🛑 按 Ctrl+C 停止调试")
        print()
        
        bot.run(appid=bot.config["appid"], secret=bot.config["secret"])
        
    except KeyboardInterrupt:
        print("\n👋 调试已停止")
        print(f"📊 总共收到 {getattr(bot, 'message_count', 0)} 条消息")
    except Exception as e:
        print(f"❌ 调试失败: {e}")

if __name__ == "__main__":
    main()
