#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQ群机器人测试
专门测试QQ群消息处理
"""

import asyncio
import botpy
from botpy.ext.cog_yaml import read
from botpy.message import Message
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GroupTestBot(botpy.Client):
    def __init__(self):
        # 读取配置
        self.config = read("config.yaml")
        
        # 初始化父类 - 专注于QQ群支持
        intents = botpy.Intents(
            public_guild_messages=True,    # 频道消息
            guild_messages=True,           # 私域频道消息
            direct_message=True,           # 私信消息
            group_at_message_create=True,  # QQ群@消息 (关键)
            c2c_message_create=True        # 单聊消息
        )
        super().__init__(intents=intents, is_sandbox=True)
    
    async def on_ready(self):
        """机器人就绪事件"""
        print("✅ QQ群测试机器人已启动！")
        print("🏖️ 运行在沙盒环境")
        print("👥 支持的消息类型:")
        print("   • 频道@消息")
        print("   • QQ群@消息")
        print("   • 私信消息")
        print("   • 单聊消息")
        print()
        print("💡 请在QQ群中@机器人发送 'test' 来测试")
    
    async def on_at_message_create(self, message: Message):
        """处理频道@消息"""
        logging.info(f"收到频道@消息: {message.content}")
        await message.reply("🏛️ 频道消息收到！这是来自代币番茄钟机器人的回复。")
    
    async def on_group_at_message_create(self, message: Message):
        """处理QQ群@消息"""
        logging.info(f"收到QQ群@消息: {message.content} (来自用户: {message.author.username})")
        
        content = message.content.strip().lower()
        
        if "test" in content:
            await message.reply("🍅 QQ群消息测试成功！代币番茄钟机器人正常工作！")
        elif "help" in content or "帮助" in content:
            help_text = """🍅 代币番茄钟机器人 - QQ群版本

📝 基本命令：
• @机器人 \\help - 查看帮助
• @机器人 \\cr 任务名称 截止时间 - 创建任务
• @机器人 \\ch - 查看任务列表
• @机器人 \\fi 任务ID - 完成任务

🎯 示例：
@机器人 \\cr 完成作业 明天 18:00
@机器人 \\ch
@机器人 \\fi 1

💡 当前运行在测试环境中"""
            await message.reply(help_text)
        else:
            await message.reply(f"👋 你好！我是代币番茄钟机器人。\n收到消息: {message.content}\n发送 'help' 查看使用说明。")
    
    async def on_direct_message_create(self, message: Message):
        """处理私信消息"""
        logging.info(f"收到私信: {message.content}")
        await message.reply("📧 私信消息收到！")
    
    async def on_c2c_message_create(self, message: Message):
        """处理单聊消息"""
        logging.info(f"收到单聊消息: {message.content}")
        await message.reply("💬 单聊消息收到！")

def main():
    print("👥 QQ群机器人测试")
    print("=" * 30)
    
    try:
        bot = GroupTestBot()
        print(f"📋 配置信息:")
        print(f"   AppID: {bot.config['appid']}")
        print(f"   环境: 沙盒环境")
        print()
        print("🚀 启动中...")
        
        bot.run(appid=bot.config["appid"], secret=bot.config["secret"])
        
    except KeyboardInterrupt:
        print("\n👋 测试停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print()
        print("💡 可能的问题:")
        print("1. 机器人未获得QQ群消息权限")
        print("2. 需要在QQ开放平台申请群消息权限")
        print("3. 沙盒环境可能不支持群消息")

if __name__ == "__main__":
    main()

