#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级调试工具
专门排查QQ机器人消息接收问题
"""

import asyncio
import botpy
from botpy.ext.cog_yaml import read
from botpy.message import Message
import logging
import json
import time
from datetime import datetime

# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class AdvancedDebugBot(botpy.Client):
    def __init__(self):
        # 读取配置
        self.config = read("config.yaml")
        
        # 尝试所有可能的Intent组合
        intents = botpy.Intents.all()  # 启用所有权限
        super().__init__(intents=intents, is_sandbox=True)
        
        self.start_time = datetime.now()
        self.connection_count = 0
        self.message_count = 0
        
        print(f"🔧 调试配置:")
        print(f"   AppID: {self.config['appid']}")
        print(f"   沙盒环境: True")
        print(f"   启动时间: {self.start_time}")
        print()
    
    async def on_ready(self):
        """机器人就绪事件"""
        self.connection_count += 1
        print(f"✅ 机器人第{self.connection_count}次连接成功!")
        print(f"⏰ 当前时间: {datetime.now()}")
        
        try:
            # 尝试获取机器人信息
            bot_info = getattr(self, 'robot', None)
            if bot_info:
                print(f"🤖 机器人信息:")
                print(f"   ID: {getattr(bot_info, 'id', 'N/A')}")
                print(f"   名称: {getattr(bot_info, 'name', 'N/A')}")
                print(f"   用户名: {getattr(bot_info, 'username', 'N/A')}")
            
            # 尝试获取权限信息
            print(f"🔑 权限配置:")
            print(f"   Intents: {self.intents}")
            
        except Exception as e:
            print(f"⚠️ 获取机器人信息时出错: {e}")
        
        print("=" * 60)
        print("🎯 现在请在QQ群中@机器人发送任何消息")
        print("📱 测试群号: 776755857")
        print("🔍 如果没有任何输出，说明消息没有到达机器人")
        print("=" * 60)
    
    async def on_error(self, event, *args, **kwargs):
        """错误事件"""
        print(f"❌ 发生错误: {event}")
        print(f"   参数: {args}")
        print(f"   关键字参数: {kwargs}")
    
    async def on_message_create(self, message: Message):
        """最基础的消息事件"""
        self.message_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        print(f"\n🔔 [{timestamp}] 收到消息 #{self.message_count}:")
        print(f"   👤 发送者: {message.author.username} (ID: {message.author.id})")
        print(f"   📝 内容: {message.content}")
        print(f"   🏷️ 消息ID: {message.id}")
        
        # 尝试获取更多信息
        try:
            print(f"   📍 频道ID: {getattr(message, 'guild_id', 'N/A')}")
            print(f"   📍 子频道ID: {getattr(message, 'channel_id', 'N/A')}")
            print(f"   ⏰ 时间戳: {getattr(message, 'timestamp', 'N/A')}")
            print(f"   🤖 是否机器人: {message.author.bot}")
        except Exception as e:
            print(f"   ⚠️ 获取额外信息失败: {e}")
        
        # 如果不是机器人发送的消息，尝试回复
        if not message.author.bot:
            try:
                reply_text = f"🎯 调试回复 #{self.message_count}\n⏰ 时间: {timestamp}\n✅ 机器人正常工作!"
                await message.reply(reply_text)
                print(f"   ✅ 回复发送成功")
            except Exception as e:
                print(f"   ❌ 回复失败: {e}")
        
        print("-" * 50)
    
    async def on_at_message_create(self, message: Message):
        """@消息事件"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n🎯 [{timestamp}] 收到@消息:")
        print(f"   👤 发送者: {message.author.username}")
        print(f"   📝 内容: {message.content}")
        
        try:
            await message.reply("🎯 @消息收到！机器人工作正常！")
            print(f"   ✅ @消息回复成功")
        except Exception as e:
            print(f"   ❌ @消息回复失败: {e}")
    
    async def on_guild_message_create(self, message: Message):
        """群/频道消息事件"""
        if not message.author.bot:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\n🏰 [{timestamp}] 群消息:")
            print(f"   👤 {message.author.username}: {message.content[:50]}")
    
    async def on_direct_message_create(self, message: Message):
        """私信事件"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n💬 [{timestamp}] 私信:")
        print(f"   👤 {message.author.username}: {message.content}")
        
        try:
            await message.reply("💬 私信收到！")
            print(f"   ✅ 私信回复成功")
        except Exception as e:
            print(f"   ❌ 私信回复失败: {e}")
    
    async def on_resumed(self):
        """重连成功事件"""
        print(f"🔄 WebSocket重连成功 - {datetime.now()}")
    
    async def on_disconnect(self):
        """断开连接事件"""
        print(f"⚠️ WebSocket断开连接 - {datetime.now()}")

def main():
    print("🔍 QQ机器人高级调试工具")
    print("=" * 40)
    print("🎯 此工具将显示所有可能的消息事件")
    print("📊 包括连接状态、错误信息、消息详情等")
    print()
    
    try:
        bot = AdvancedDebugBot()
        print("🚀 启动高级调试模式...")
        print()
        
        bot.run(appid=bot.config["appid"], secret=bot.config["secret"])
        
    except KeyboardInterrupt:
        print(f"\n👋 调试结束")
        print(f"📊 统计信息:")
        print(f"   连接次数: {bot.connection_count if 'bot' in locals() else 0}")
        print(f"   消息数量: {bot.message_count if 'bot' in locals() else 0}")
    except Exception as e:
        print(f"❌ 调试工具启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
