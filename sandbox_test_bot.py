#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沙盒环境QQ机器人测试
专门用于"测试中"状态的机器人
"""

import asyncio
import botpy
from botpy.ext.cog_yaml import read
from botpy.message import Message
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)

class SandboxTestBot(botpy.Client):
    def __init__(self):
        # 读取配置
        self.config = read("config.yaml")
        
        # 初始化父类 - 使用沙盒环境
        intents = botpy.Intents(public_guild_messages=True)
        super().__init__(intents=intents, is_sandbox=True)  # 关键：启用沙盒模式
    
    async def on_ready(self):
        """机器人就绪事件"""
        print(f"✅ 沙盒环境机器人已成功登录!")
        try:
            print(f"🤖 机器人ID: {self.robot.id}")
            print(f"📛 机器人名称: {self.robot.name}")
        except:
            print(f"🤖 机器人信息获取中...")
        print("🏖️ 当前运行在沙盒环境中")
        print("🎉 连接测试成功！")
        print()
        print("💡 现在可以启动完整的代币番茄钟机器人了！")
    
    async def on_at_message_create(self, message: Message):
        """处理@机器人的消息"""
        content = message.content.strip()
        
        if "test" in content.lower():
            await message.reply("🍅 沙盒环境机器人连接正常！\n当前处于测试模式。")
        elif "ping" in content.lower():
            await message.reply("🏓 Pong! 沙盒环境响应正常！")

def main():
    print("🏖️ QQ机器人沙盒环境测试")
    print("=" * 35)
    print("💡 此版本专门用于'测试中'状态的机器人")
    print()
    
    try:
        bot = SandboxTestBot()
        print(f"📋 使用配置:")
        print(f"   AppID: {bot.config['appid']}")
        print(f"   Secret: {bot.config['secret'][:10]}...")
        print(f"   环境: 沙盒环境 (Sandbox)")
        print()
        print("🚀 尝试连接沙盒环境...")
        
        # 运行机器人
        bot.run(appid=bot.config["appid"], secret=bot.config["secret"])
        
    except KeyboardInterrupt:
        print("\n👋 测试已停止")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print()
        print("💡 沙盒环境解决方案:")
        print("1. 确认在QQ开放平台的【沙盒环境】中设置了IP白名单")
        print("2. 沙盒环境地址: https://sandbox.api.sgroup.qq.com")
        print("3. 确认机器人状态为'测试中'")
        print("4. 检查沙盒环境的权限配置")
        print()
        print("🔗 QQ开放平台: https://q.qq.com/")

if __name__ == "__main__":
    main()
