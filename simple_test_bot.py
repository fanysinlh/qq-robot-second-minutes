#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版QQ机器人测试
用于验证基础连接和配置
"""

import asyncio
import botpy
from botpy.ext.cog_yaml import read
from botpy.message import Message
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)

class SimpleTestBot(botpy.Client):
    def __init__(self):
        # 读取配置
        self.config = read("config.yaml")
        
        # 初始化父类
        intents = botpy.Intents(public_guild_messages=True)
        super().__init__(intents=intents)
    
    async def on_ready(self):
        """机器人就绪事件"""
        print(f"✅ 机器人已成功登录: {self.user}")
        print(f"🤖 机器人ID: {self.user.id}")
        print(f"📛 机器人名称: {self.user.username}")
        print("🎉 连接测试成功！")
    
    async def on_at_message_create(self, message: Message):
        """处理@机器人的消息"""
        if message.content.strip() == "test":
            await message.reply("🍅 代币番茄钟机器人连接正常！")

def main():
    print("🔍 QQ机器人连接测试")
    print("=" * 30)
    
    try:
        bot = SimpleTestBot()
        print(f"📋 使用配置:")
        print(f"   AppID: {bot.config['appid']}")
        print(f"   Secret: {bot.config['secret'][:10]}...")
        print()
        print("🚀 尝试连接...")
        
        # 运行机器人
        bot.run(appid=bot.config["appid"], secret=bot.config["secret"])
        
    except KeyboardInterrupt:
        print("\n👋 测试已停止")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print()
        print("💡 可能的解决方案:")
        print("1. 检查QQ开放平台中机器人应用状态")
        print("2. 确认AppID和Secret是否正确")
        print("3. 检查是否在正确的环境（沙盒/正式）")
        print("4. 确认机器人已通过审核")
        print()
        print("🔗 QQ开放平台: https://q.qq.com/")

if __name__ == "__main__":
    main()
