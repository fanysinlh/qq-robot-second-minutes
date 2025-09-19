#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQ机器人事件调试版本
检查所有可能的消息事件类型
"""

import asyncio
import botpy
from botpy.ext.cog_yaml import read
from botpy.message import Message
import logging

# 配置详细日志
logging.basicConfig(level=logging.DEBUG)

class EventDebugBot(botpy.Client):
    def __init__(self):
        # 读取配置
        self.config = read("config.yaml")
        
        # 使用最基本的权限设置
        intents = botpy.Intents.default()
        super().__init__(intents=intents, is_sandbox=True)
        
        self.event_count = 0
    
    async def on_ready(self):
        """机器人就绪事件"""
        print("🔍 事件调试机器人已启动！")
        print(f"🤖 机器人名称: {getattr(self.robot, 'name', '未知')}")
        print("📡 监听所有可能的事件...")
        print("=" * 60)
        print("💡 请在QQ群中尝试以下操作:")
        print("   1. @机器人 发送消息")
        print("   2. 直接发送消息（不@机器人）")
        print("   3. 发送图片或表情")
        print("=" * 60)
    
    # 尝试所有可能的消息事件
    async def on_message_create(self, message):
        """通用消息创建事件"""
        self.event_count += 1
        print(f"🎯 [事件{self.event_count}] MESSAGE_CREATE")
        print(f"   作者: {message.author.username}")
        print(f"   内容: {message.content}")
        print(f"   消息ID: {message.id}")
        print("-" * 40)
    
    async def on_at_message_create(self, message):
        """@消息事件"""
        self.event_count += 1
        print(f"🎯 [事件{self.event_count}] AT_MESSAGE_CREATE")
        print(f"   作者: {message.author.username}")
        print(f"   内容: {message.content}")
        try:
            await message.reply("✅ 收到@消息！")
            print("   回复: 成功")
        except Exception as e:
            print(f"   回复: 失败 - {e}")
        print("-" * 40)
    
    async def on_direct_message_create(self, message):
        """私信事件"""
        self.event_count += 1
        print(f"🎯 [事件{self.event_count}] DIRECT_MESSAGE_CREATE")
        print(f"   作者: {message.author.username}")
        print(f"   内容: {message.content}")
        print("-" * 40)
    
    async def on_guild_message_create(self, message):
        """频道消息事件"""
        self.event_count += 1
        print(f"🎯 [事件{self.event_count}] GUILD_MESSAGE_CREATE")
        print(f"   作者: {message.author.username}")
        print(f"   内容: {message.content}")
        print("-" * 40)
    
    async def on_public_message_delete(self, message):
        """消息删除事件"""
        self.event_count += 1
        print(f"🎯 [事件{self.event_count}] PUBLIC_MESSAGE_DELETE")
        print("-" * 40)
    
    # 添加群聊相关事件监听
    async def on_group_at_message_create(self, message):
        """群聊@消息（如果存在这个事件）"""
        self.event_count += 1
        print(f"🎯 [事件{self.event_count}] GROUP_AT_MESSAGE_CREATE")
        try:
            author_name = getattr(message.author, 'username', 
                                getattr(message.author, 'nick', 
                                       getattr(message.author, 'name', '未知用户')))
            print(f"   作者: {author_name}")
            print(f"   内容: {message.content}")
            
            # 尝试回复 - 群聊消息可能需要不同的回复方式
            try:
                await message.reply("✅ 群聊@消息收到！机器人工作正常！")
                print("   回复: 成功")
            except Exception as reply_error:
                print(f"   回复失败: {reply_error}")
                # 尝试其他回复方式
                try:
                    # 检查是否有其他回复方法
                    if hasattr(message, 'send'):
                        await message.send("✅ 群聊@消息收到！机器人工作正常！")
                        print("   使用send方法回复成功")
                    else:
                        print("   无法找到合适的回复方法")
                except Exception as e2:
                    print(f"   所有回复方式都失败: {e2}")
            
        except Exception as e:
            print(f"   处理错误: {e}")
            print(f"   消息对象: {dir(message.author)}")
        print("-" * 40)
    
    # 监听所有未知事件
    async def on_socket_response(self, msg):
        """原始WebSocket消息"""
        if msg.get('t'):  # 如果有事件类型
            event_type = msg.get('t')
            if event_type not in ['HEARTBEAT_ACK', 'HEARTBEAT']:  # 忽略心跳
                self.event_count += 1
                print(f"🔍 [事件{self.event_count}] RAW_EVENT: {event_type}")
                print(f"   数据: {msg.get('d', {})}")
                print("-" * 40)

def main():
    print("🔍 QQ机器人事件调试")
    print("=" * 30)
    print("💡 此版本会显示所有收到的事件")
    print("🎯 用于诊断消息接收问题")
    print()
    
    try:
        bot = EventDebugBot()
        print(f"📋 配置:")
        print(f"   AppID: {bot.config['appid']}")
        print(f"   环境: 沙盒环境")
        print()
        print("🚀 启动事件调试机器人...")
        print()
        
        bot.run(appid=bot.config["appid"], secret=bot.config["secret"])
        
    except KeyboardInterrupt:
        print("\n👋 调试结束")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main()
