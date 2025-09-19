#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQ机器人消息调试版本
用于调试消息接收和处理问题
"""

import asyncio
import botpy
from botpy.ext.cog_yaml import read
from botpy.message import Message
import logging

# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class DebugBot(botpy.Client):
    def __init__(self):
        # 读取配置
        self.config = read("config.yaml")
        
        # 初始化父类 - 使用沙盒环境，启用所有消息类型
        intents = botpy.Intents(
            public_guild_messages=True,      # 公开频道消息
            guild_messages=True,             # 频道消息
            direct_message=True,             # 私信
            guild_message_reactions=True     # 消息反应
        )
        super().__init__(intents=intents, is_sandbox=True)
    
    async def on_ready(self):
        """机器人就绪事件"""
        print("🔍 调试机器人已启动！")
        print(f"🤖 机器人名称: {getattr(self.robot, 'name', '未知')}")
        print("📡 开始监听所有消息...")
        print("=" * 50)
    
    async def on_message_create(self, message: Message):
        """监听所有消息"""
        print(f"📨 收到消息:")
        print(f"   作者: {message.author.username}")
        print(f"   内容: {message.content}")
        print(f"   频道: {getattr(message, 'guild_id', 'N/A')}")
        print(f"   是否@机器人: {self.robot.id in message.content if hasattr(self, 'robot') else 'N/A'}")
        print("-" * 30)
    
    async def on_at_message_create(self, message: Message):
        """处理@机器人的消息"""
        print(f"🎯 收到@消息:")
        print(f"   作者: {message.author.username}")
        print(f"   原始内容: {message.content}")
        
        # 清理消息内容
        import re
        clean_content = re.sub(r'<@!\d+>', '', message.content).strip()
        print(f"   清理后内容: {clean_content}")
        
        # 测试回复
        try:
            await message.reply("🍅 我收到了你的消息！这是测试回复。")
            print("   ✅ 回复发送成功")
        except Exception as e:
            print(f"   ❌ 回复发送失败: {e}")
        
        print("-" * 30)
    
    async def on_direct_message_create(self, message: Message):
        """处理私信消息"""
        print(f"💬 收到私信:")
        print(f"   作者: {message.author.username}")
        print(f"   内容: {message.content}")
        
        try:
            await message.reply("🍅 私信收到！这是测试回复。")
            print("   ✅ 私信回复成功")
        except Exception as e:
            print(f"   ❌ 私信回复失败: {e}")
        
        print("-" * 30)
    
    async def on_guild_message_create(self, message: Message):
        """处理频道消息"""
        print(f"🏰 收到频道消息:")
        print(f"   作者: {message.author.username}")
        print(f"   内容: {message.content}")
        print(f"   频道ID: {getattr(message, 'guild_id', 'N/A')}")
        print("-" * 30)

def main():
    print("🔍 QQ机器人消息调试")
    print("=" * 30)
    print("💡 此版本会显示所有收到的消息")
    print("🎯 请在QQ中@机器人发送消息进行测试")
    print()
    
    try:
        bot = DebugBot()
        print(f"📋 配置信息:")
        print(f"   AppID: {bot.config['appid']}")
        print(f"   环境: 沙盒环境")
        print()
        print("🚀 启动调试机器人...")
        
        bot.run(appid=bot.config["appid"], secret=bot.config["secret"])
        
    except KeyboardInterrupt:
        print("\n👋 调试已停止")
    except Exception as e:
        print(f"❌ 调试机器人启动失败: {e}")
        print()
        print("💡 可能的问题:")
        print("1. 机器人权限不足")
        print("2. 频道/群组权限问题")
        print("3. 消息类型权限未开启")

if __name__ == "__main__":
    main()