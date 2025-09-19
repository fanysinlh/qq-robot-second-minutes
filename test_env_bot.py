#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试环境QQ机器人
专门用于"测试中"状态的机器人
"""

import asyncio
import botpy
from botpy.ext.cog_yaml import read
from botpy.message import Message
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)

class TestEnvBot(botpy.Client):
    def __init__(self):
        # 读取配置
        self.config = read("config.yaml")
        
        # 测试环境需要使用沙盒intents
        intents = botpy.Intents(
            public_guild_messages=True,
            guild_messages=True,
            direct_message=True
        )
        
        # 初始化父类 - 指定使用沙盒环境
        super().__init__(
            intents=intents,
            is_sandbox=True  # 重要：指定使用沙盒环境
        )
    
    async def on_ready(self):
        """机器人就绪事件"""
        print(f"✅ 测试环境机器人已成功登录!")
        print(f"🤖 机器人ID: {self.user.id}")
        print(f"📛 机器人名称: {self.user.username}")
        print(f"🏷️ 运行环境: 沙盒测试环境")
        print("🎉 测试连接成功！现在可以进行功能测试了")
    
    async def on_at_message_create(self, message: Message):
        """处理@机器人的消息"""
        content = message.content.strip()
        
        if "test" in content.lower():
            await message.reply("🍅 代币番茄钟机器人 (测试版) 连接正常！\n\n可用测试命令:\n• \\help - 查看帮助\n• \\cr 测试任务 1小时后 - 创建测试任务")
        elif content.startswith("\\help"):
            help_text = """
🍅 代币番茄钟机器人 (测试版)

📝 测试命令：
\\cr <任务名称> <截止时间> - 创建任务
\\fi <任务ID> - 完成任务  
\\ch - 查看任务列表
\\stats - 查看统计信息

⚠️ 注意：当前为测试环境，数据不会保留到正式版本
"""
            await message.reply(help_text)
    
    async def on_direct_message_create(self, message: Message):
        """处理私信消息"""
        if message.author.bot:
            return
            
        await message.reply("👋 你好！我是代币番茄钟机器人的测试版本。\n请在群聊中@我使用功能哦！")

def main():
    print("🧪 QQ机器人测试环境启动")
    print("=" * 40)
    print("⚠️ 注意：这是专门为'测试中'状态机器人设计的版本")
    print("📋 特点：")
    print("• 使用沙盒环境连接")
    print("• 适用于未审核上线的机器人")
    print("• 功能可能有限制")
    print()
    
    try:
        bot = TestEnvBot()
        print(f"📋 使用配置:")
        print(f"   AppID: {bot.config['appid']}")
        print(f"   Secret: {bot.config['secret'][:10]}...")
        print(f"   环境: 沙盒测试环境")
        print()
        print("🚀 尝试连接测试环境...")
        
        # 运行机器人
        bot.run(appid=bot.config["appid"], secret=bot.config["secret"])
        
    except KeyboardInterrupt:
        print("\n👋 测试机器人已停止")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print()
        print("💡 测试环境连接失败的可能原因:")
        print("1. 沙盒环境的IP白名单未设置")
        print("2. 测试机器人权限不足")
        print("3. 需要申请测试用户权限")
        print()
        print("🔗 解决方案:")
        print("• 在QQ开放平台的'沙盒环境'中设置IP白名单")
        print("• 添加测试用户QQ号")
        print("• 确认测试权限已开启")

if __name__ == "__main__":
    main()
