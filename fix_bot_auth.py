#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQ机器人认证修复脚本
"""

import requests
import json
import base64
from botpy.ext.cog_yaml import read

def test_bot_auth_methods(appid, secret):
    """测试不同的认证方法"""
    
    print("🔧 测试不同的认证方法...")
    print()
    
    # 方法1: Bot Token格式
    print("1️⃣ 测试 Bot Token 格式")
    try:
        headers1 = {
            'Authorization': f'Bot {appid}.{secret}',
            'Content-Type': 'application/json',
            'User-Agent': 'BotNodeSDK/1.0.0'
        }
        
        response1 = requests.get(
            "https://api.sgroup.qq.com/users/@me",
            headers=headers1,
            timeout=10
        )
        
        print(f"   状态码: {response1.status_code}")
        if response1.status_code == 200:
            print("   ✅ 认证成功！")
            user_info = response1.json()
            print(f"   机器人信息: {user_info.get('username', 'N/A')}")
            return True
        else:
            error_data = response1.json() if response1.text else {}
            print(f"   ❌ 认证失败: {error_data}")
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
    
    print()
    
    # 方法2: QQBot Token格式
    print("2️⃣ 测试 QQBot Token 格式")
    try:
        headers2 = {
            'Authorization': f'QQBot {appid}.{secret}',
            'Content-Type': 'application/json',
            'User-Agent': 'BotNodeSDK/1.0.0'
        }
        
        response2 = requests.get(
            "https://api.sgroup.qq.com/users/@me",
            headers=headers2,
            timeout=10
        )
        
        print(f"   状态码: {response2.status_code}")
        if response2.status_code == 200:
            print("   ✅ 认证成功！")
            user_info = response2.json()
            print(f"   机器人信息: {user_info.get('username', 'N/A')}")
            return True
        else:
            error_data = response2.json() if response2.text else {}
            print(f"   ❌ 认证失败: {error_data}")
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
    
    print()
    
    # 方法3: Bearer Token格式
    print("3️⃣ 测试 Bearer Token 格式")
    try:
        token = base64.b64encode(f"{appid}.{secret}".encode()).decode()
        headers3 = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'User-Agent': 'BotNodeSDK/1.0.0'
        }
        
        response3 = requests.get(
            "https://api.sgroup.qq.com/users/@me",
            headers=headers3,
            timeout=10
        )
        
        print(f"   状态码: {response3.status_code}")
        if response3.status_code == 200:
            print("   ✅ 认证成功！")
            user_info = response3.json()
            print(f"   机器人信息: {user_info.get('username', 'N/A')}")
            return True
        else:
            error_data = response3.json() if response3.text else {}
            print(f"   ❌ 认证失败: {error_data}")
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
    
    print()
    
    # 方法4: 尝试获取access_token
    print("4️⃣ 测试获取 access_token")
    try:
        auth_url = "https://bots.qq.com/app/getAppAccessToken"
        auth_data = {
            "appId": appid,
            "clientSecret": secret
        }
        
        auth_response = requests.post(auth_url, json=auth_data, timeout=10)
        print(f"   状态码: {auth_response.status_code}")
        
        if auth_response.status_code == 200:
            auth_result = auth_response.json()
            if "access_token" in auth_result:
                access_token = auth_result["access_token"]
                print(f"   ✅ 获取access_token成功")
                
                # 使用access_token测试API
                headers4 = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json',
                    'User-Agent': 'BotNodeSDK/1.0.0'
                }
                
                api_response = requests.get(
                    "https://api.sgroup.qq.com/users/@me",
                    headers=headers4,
                    timeout=10
                )
                
                print(f"   API测试状态码: {api_response.status_code}")
                if api_response.status_code == 200:
                    print("   ✅ API访问成功！")
                    user_info = api_response.json()
                    print(f"   机器人信息: {user_info.get('username', 'N/A')}")
                    return True
                else:
                    error_data = api_response.json() if api_response.text else {}
                    print(f"   ❌ API访问失败: {error_data}")
            else:
                print(f"   ❌ 未获取到access_token: {auth_result}")
        else:
            error_data = auth_response.json() if auth_response.text else {}
            print(f"   ❌ 获取access_token失败: {error_data}")
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
    
    return False

def check_bot_status(appid):
    """检查机器人状态"""
    print("🤖 机器人状态检查")
    print(f"   AppID: {appid}")
    print("   建议检查项目：")
    print("   1. 登录 https://q.qq.com/")
    print("   2. 检查机器人应用状态是否为'开发中'或'已上线'")
    print("   3. 确认Secret没有重新生成")
    print("   4. 检查是否在沙盒环境还是正式环境")
    print()

def main():
    print("🔧 QQ机器人认证修复")
    print("=" * 40)
    
    try:
        config = read("config.yaml")
        appid = config["appid"]
        secret = config["secret"]
        
        print(f"AppID: {appid}")
        print(f"Secret: {secret[:10]}...")
        print()
        
        # 测试认证方法
        success = test_bot_auth_methods(appid, secret)
        
        if not success:
            print("❌ 所有认证方法都失败了")
            print()
            check_bot_status(appid)
            print("💡 可能的解决方案：")
            print("   1. 检查AppID和Secret是否正确")
            print("   2. 确认机器人应用状态正常")
            print("   3. 检查是否需要重新生成Secret")
            print("   4. 联系QQ开放平台技术支持")
        else:
            print("✅ 认证问题已解决！")
            print("   现在可以尝试重新启动机器人")
            
    except Exception as e:
        print(f"❌ 配置文件读取失败: {e}")

if __name__ == "__main__":
    main()
