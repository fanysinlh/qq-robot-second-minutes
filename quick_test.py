#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试机器人消息接收
"""

import asyncio
import botpy
from botpy.ext.cog_yaml import read
from botpy.message import Message

class QuickTestBot(botpy.Client):
    def __init__(self):
        config = read("config.yaml")
        intents = botpy.Intents.all()  # 启用所有权限
        super().__init__(intents=intents, is_sandbox=True)
        self.config = config
    
    async def on_ready(self):
        print("🤖 快速测试机器人已启动")
        print("🔍 监听所有类型的消息...")
        print("📝 请尝试:")
        print("   1. 私信机器人")
        print("   2. 在群/频道中@机器人")
        print("   3. 发送任何内容测试")
        print("=" * 40)
    
    async def on_message_create(self, message: Message):
        """所有消息"""
        print(f"📨 [普通消息] {message.author.username}: {message.content}")
    
    async def on_at_message_create(self, message: Message):
        """@消息"""
        print(f"🎯 [@消息] {message.author.username}: {message.content}")
        try:
            await message.reply("✅ 我收到了你的@消息！")
            print("   → 回复成功")
        except Exception as e:
            print(f"   → 回复失败: {e}")
    
    async def on_direct_message_create(self, message: Message):
        """私信"""
        print(f"💬 [私信] {message.author.username}: {message.content}")
        try:
            await message.reply("✅ 我收到了你的私信！")
            print("   → 私信回复成功")
        except Exception as e:
            print(f"   → 私信回复失败: {e}")
    
    async def on_guild_message_create(self, message: Message):
        """频道消息"""
        print(f"🏰 [频道消息] {message.author.username}: {message.content}")

def main():
    print("🔍 快速测试机器人消息接收")
    print("=" * 35)
    
    try:
        bot = QuickTestBot()
        bot.run(appid=bot.config["appid"], secret=bot.config["secret"])
    except KeyboardInterrupt:
        print("\n👋 测试结束")
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main()
