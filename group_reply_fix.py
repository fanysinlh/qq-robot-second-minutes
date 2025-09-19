#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQ群聊回复修复方案
基于常见的QQ机器人实现模式
"""

import asyncio
import botpy
from botpy.ext.cog_yaml import read
from botpy.message import GroupMessage
import logging

logging.basicConfig(level=logging.INFO)

class GroupReplyBot(botpy.Client):
    def __init__(self):
        config = read("config.yaml")
        intents = botpy.Intents.default()
        super().__init__(intents=intents, is_sandbox=True)
        self.config = config
    
    async def on_ready(self):
        print("🤖 群聊回复修复机器人已启动！")
        print("📝 请在群中@机器人测试各种回复方式")
    
    async def on_group_at_message_create(self, message):
        print(f"\n📨 收到群聊@消息: {message.content}")
        
        # 安全获取用户信息
        try:
            # 尝试不同的用户名属性
            user_attrs = ['username', 'nick', 'name', 'user_openid', 'member_openid']
            author_name = "未知用户"
            
            for attr in user_attrs:
                if hasattr(message.author, attr):
                    value = getattr(message.author, attr)
                    if value:
                        author_name = str(value)
                        print(f"👤 用户 ({attr}): {author_name}")
                        break
            
        except Exception as e:
            print(f"❌ 获取用户信息失败: {e}")
            author_name = "未知用户"
        
        # 尝试各种回复方式
        await self._try_all_reply_methods(message, author_name)
    
    async def _try_all_reply_methods(self, message, author_name: str):
        """尝试所有可能的回复方式"""
        reply_text = f"🍅 你好 {author_name}！群聊机器人收到消息：{message.content}"
        
        # 方式1: 标准reply方法
        print("🔧 尝试方式1: message.reply()")
        try:
            await message.reply(reply_text)
            print("✅ 方式1成功: message.reply()")
            return
        except Exception as e:
            print(f"❌ 方式1失败: {e}")
        
        # 方式2: reply无参数
        print("🔧 尝试方式2: message.reply()无参数")
        try:
            result = await message.reply()
            print(f"✅ 方式2调用成功，返回: {type(result)} - {result}")
        except Exception as e:
            print(f"❌ 方式2失败: {e}")
        
        # 方式3: 通过API发送群消息
        print("🔧 尝试方式3: 通过API发送群消息")
        try:
            # 获取群相关ID
            group_openid = getattr(message, 'group_openid', None)
            if group_openid:
                print(f"📍 群ID: {group_openid}")
                
                # 尝试使用api发送消息
                if hasattr(self, 'api') and hasattr(self.api, 'post_group_message'):
                    await self.api.post_group_message(
                        group_openid=group_openid,
                        msg_type=0,
                        content=reply_text
                    )
                    print("✅ 方式3成功: API发送群消息")
                    return
                else:
                    print("❌ 方式3失败: 没有post_group_message方法")
            else:
                print("❌ 方式3失败: 无法获取group_openid")
        except Exception as e:
            print(f"❌ 方式3失败: {e}")
        
        # 方式4: 检查消息对象是否有send方法
        print("🔧 尝试方式4: message.send()")
        try:
            if hasattr(message, 'send'):
                await message.send(reply_text)
                print("✅ 方式4成功: message.send()")
                return
            else:
                print("❌ 方式4失败: 没有send方法")
        except Exception as e:
            print(f"❌ 方式4失败: {e}")
        
        # 方式5: 通过频道消息方式（如果群聊被当作频道处理）
        print("🔧 尝试方式5: 频道消息方式")
        try:
            channel_id = getattr(message, 'channel_id', None)
            if channel_id and hasattr(self, 'api'):
                await self.api.post_message(
                    channel_id=channel_id,
                    msg_type=0,
                    content=reply_text
                )
                print("✅ 方式5成功: 频道消息方式")
                return
            else:
                print("❌ 方式5失败: 没有channel_id或api")
        except Exception as e:
            print(f"❌ 方式5失败: {e}")
        
        # 打印调试信息
        print("\n🔍 调试信息:")
        print(f"消息对象类型: {type(message)}")
        print(f"消息对象属性: {[attr for attr in dir(message) if not attr.startswith('_')]}")
        
        if hasattr(self, 'api'):
            print(f"API对象属性: {[attr for attr in dir(self.api) if not attr.startswith('_')]}")
        else:
            print("没有API对象")
        
        print("❌ 所有回复方式都失败了")

def main():
    print("🔧 QQ群聊回复修复测试")
    print("=" * 30)
    
    try:
        bot = GroupReplyBot()
        bot.run(appid=bot.config["appid"], secret=bot.config["secret"])
    except KeyboardInterrupt:
        print("\n👋 测试结束")
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main()
