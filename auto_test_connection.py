#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动测试QQ机器人连接
每5分钟测试一次，直到连接成功
"""

import time
import requests
from datetime import datetime
from botpy.ext.cog_yaml import read

def test_connection():
    """测试连接"""
    try:
        config = read("config.yaml")
        
        # 测试API访问
        headers = {
            'Authorization': f'Bot {config["appid"]}.{config["secret"]}',
            'Content-Type': 'application/json',
            'User-Agent': 'BotNodeSDK/1.0.0'
        }
        
        response = requests.get(
            "https://api.sgroup.qq.com/users/@me",
            headers=headers,
            timeout=10
        )
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if response.status_code == 200:
            print(f"[{timestamp}] ✅ 连接成功！机器人可以正常运行了！")
            return True
        elif "白名单" in str(response.json()):
            print(f"[{timestamp}] ❌ 仍然是IP白名单问题")
            return False
        else:
            error_data = response.json() if response.text else {}
            print(f"[{timestamp}] ⚠️ 其他错误: {error_data}")
            return False
            
    except Exception as e:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] ❌ 连接异常: {e}")
        return False

def main():
    print("🔄 QQ机器人连接自动测试")
    print("每5分钟测试一次，按Ctrl+C停止")
    print("=" * 40)
    
    test_count = 0
    
    try:
        while True:
            test_count += 1
            print(f"\n第 {test_count} 次测试:")
            
            success = test_connection()
            
            if success:
                print("\n🎉 测试成功！现在可以启动完整的机器人了！")
                print("运行命令: python start_bot.py")
                break
            else:
                print("等待5分钟后重新测试...")
                print("💡 在等待期间，请检查QQ开放平台的白名单设置")
                
                # 等待5分钟 (300秒)
                for remaining in range(300, 0, -30):
                    print(f"   还需等待 {remaining//60}分{remaining%60}秒...", end='\r')
                    time.sleep(30)
                print()
                
    except KeyboardInterrupt:
        print(f"\n👋 测试已停止 (共测试了 {test_count} 次)")
        print("💡 建议继续检查QQ开放平台的白名单设置")

if __name__ == "__main__":
    main()

