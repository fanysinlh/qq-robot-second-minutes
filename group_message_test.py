#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQ群消息对象结构探索
"""

import asyncio
import botpy
from botpy.ext.cog_yaml import read
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)

class GroupMessageTestBot(botpy.Client):
    def __init__(self):
        # 读取配置
        self.config = read("config.yaml")
        
        # 使用默认权限
        intents = botpy.Intents.default()
        super().__init__(intents=intents, is_sandbox=True)
    
    async def on_ready(self):
        """机器人就绪事件"""
        print("🔍 群消息结构探索机器人已启动！")
        print("📝 请在群中@机器人，我会分析消息对象结构")
        print("=" * 50)
    
    async def on_group_at_message_create(self, message):
        """分析群聊@消息对象结构"""
        print(f"\n🎯 收到群聊@消息，开始分析...")
        print(f"消息内容: {message.content}")
        
        # 分析消息对象结构
        print(f"\n📊 消息对象属性:")
        for attr in sorted(dir(message)):
            if not attr.startswith('_'):
                try:
                    value = getattr(message, attr)
                    if callable(value):
                        print(f"   {attr}(): 方法")
                    else:
                        print(f"   {attr}: {type(value).__name__} = {value}")
                except Exception as e:
                    print(f"   {attr}: 无法访问 - {e}")
        
        # 分析作者对象结构
        print(f"\n👤 作者对象属性:")
        for attr in sorted(dir(message.author)):
            if not attr.startswith('_'):
                try:
                    value = getattr(message.author, attr)
                    if callable(value):
                        print(f"   {attr}(): 方法")
                    else:
                        print(f"   {attr}: {type(value).__name__} = {value}")
                except Exception as e:
                    print(f"   {attr}: 无法访问 - {e}")
        
        # 测试不同的回复方式
        print(f"\n🔧 测试回复方式:")
        
        # 方式1: reply()
        try:
            await message.reply("测试回复1")
            print("   ✅ reply() 成功")
        except Exception as e:
            print(f"   ❌ reply() 失败: {e}")
        
        # 方式2: reply() 无参数
        try:
            reply_msg = await message.reply()
            print(f"   ✅ reply() 无参数成功: {type(reply_msg)}")
        except Exception as e:
            print(f"   ❌ reply() 无参数失败: {e}")
        
        # 方式3: 检查是否有send方法
        if hasattr(message, 'send'):
            try:
                await message.send("测试send方法")
                print("   ✅ send() 成功")
            except Exception as e:
                print(f"   ❌ send() 失败: {e}")
        else:
            print("   ❌ 没有send方法")
        
        # 方式4: 通过API发送消息
        try:
            # 获取群ID和用户ID
            group_openid = getattr(message, 'group_openid', None)
            if group_openid:
                print(f"   群ID: {group_openid}")
                # 这里可以尝试通过API直接发送消息
        except Exception as e:
            print(f"   获取群ID失败: {e}")
        
        print("=" * 50)

def main():
    print("🔍 QQ群消息对象结构探索")
    print("=" * 30)
    
    try:
        bot = GroupMessageTestBot()
        bot.run(appid=bot.config["appid"], secret=bot.config["secret"])
    except KeyboardInterrupt:
        print("\n👋 探索结束")
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main()

