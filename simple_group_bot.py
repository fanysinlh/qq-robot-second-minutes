#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的QQ群聊机器人测试
专门测试群聊回复功能
"""

import asyncio
import botpy
from botpy.ext.cog_yaml import read
import logging

logging.basicConfig(level=logging.INFO)

class SimpleGroupBot(botpy.Client):
    def __init__(self):
        config = read("config.yaml")
        intents = botpy.Intents.default()
        super().__init__(intents=intents, is_sandbox=True)
        self.config = config
    
    async def on_ready(self):
        print("🤖 简化群聊机器人已启动！")
        print("📝 请在群中@机器人测试")
    
    async def on_group_at_message_create(self, message):
        print(f"\n📨 收到群聊@消息: {message.content}")
        
        # 获取用户信息
        try:
            author_name = getattr(message.author, 'username', 
                                getattr(message.author, 'nick', 
                                       getattr(message.author, 'name', '未知用户')))
            print(f"👤 用户: {author_name}")
        except Exception as e:
            print(f"❌ 获取用户信息失败: {e}")
        
        # 尝试多种回复方式
        reply_success = False
        
        # 方式1: 直接reply（可能需要无参数）
        if not reply_success:
            try:
                # 检查reply方法的签名
                import inspect
                sig = inspect.signature(message.reply)
                print(f"🔍 reply方法签名: {sig}")
                
                # 如果reply方法不接受参数，可能需要先调用reply()获取回复对象
                if len(sig.parameters) == 0:
                    reply_obj = await message.reply()
                    print(f"✅ reply()调用成功，返回对象: {type(reply_obj)}")
                    # 然后可能需要通过其他方式发送内容
                else:
                    await message.reply("🍅 群聊回复测试成功！")
                    print("✅ reply(content)调用成功")
                    reply_success = True
                    
            except Exception as e:
                print(f"❌ reply方法失败: {e}")
        
        # 方式2: 通过API直接发送群消息
        if not reply_success:
            try:
                # 获取群ID
                group_openid = getattr(message, 'group_openid', None)
                if group_openid:
                    print(f"📍 群ID: {group_openid}")
                    
                    # 尝试通过api发送消息
                    if hasattr(self, 'api'):
                        await self.api.post_group_message(
                            group_openid=group_openid,
                            msg_type=0,  # 文本消息
                            content="🍅 通过API发送的群聊回复！"
                        )
                        print("✅ API发送成功")
                        reply_success = True
                    else:
                        print("❌ 没有api对象")
                else:
                    print("❌ 无法获取群ID")
                    
            except Exception as e:
                print(f"❌ API发送失败: {e}")
        
        # 方式3: 检查消息对象的其他方法
        if not reply_success:
            print("🔍 检查消息对象的所有方法:")
            for attr in dir(message):
                if 'send' in attr.lower() or 'reply' in attr.lower():
                    print(f"   发现方法: {attr}")
                    try:
                        method = getattr(message, attr)
                        if callable(method):
                            print(f"     方法签名: {inspect.signature(method)}")
                    except:
                        pass
        
        if not reply_success:
            print("❌ 所有回复方式都失败了")
        
        print("-" * 50)

def main():
    print("🔍 简化群聊机器人测试")
    print("=" * 30)
    
    try:
        bot = SimpleGroupBot()
        bot.run(appid=bot.config["appid"], secret=bot.config["secret"])
    except KeyboardInterrupt:
        print("\n👋 测试结束")
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main()

