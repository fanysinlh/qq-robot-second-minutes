#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQ机器人连接诊断脚本
用于排查IP白名单和连接问题
"""

import requests
import socket
import json
import time
from datetime import datetime
from botpy.ext.cog_yaml import read

def get_public_ip():
    """获取公网IP"""
    try:
        response = requests.get("https://api.ipify.org", timeout=10)
        return response.text.strip()
    except Exception as e:
        return f"获取失败: {e}"

def test_dns_resolution():
    """测试DNS解析"""
    hosts = [
        "api.sgroup.qq.com",
        "sandbox.api.sgroup.qq.com",
        "q.qq.com"
    ]
    
    results = {}
    for host in hosts:
        try:
            ip = socket.gethostbyname(host)
            results[host] = f"✅ {ip}"
        except Exception as e:
            results[host] = f"❌ {e}"
    
    return results

def test_network_connectivity():
    """测试网络连通性"""
    urls = [
        "https://api.sgroup.qq.com",
        "https://sandbox.api.sgroup.qq.com", 
        "https://q.qq.com"
    ]
    
    results = {}
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            results[url] = f"✅ HTTP {response.status_code}"
        except requests.exceptions.Timeout:
            results[url] = "⏰ 超时"
        except requests.exceptions.ConnectionError:
            results[url] = "❌ 连接错误"
        except Exception as e:
            results[url] = f"❌ {e}"
    
    return results

def test_bot_api_access(config):
    """测试机器人API访问"""
    try:
        # 模拟botpy的请求
        headers = {
            'Authorization': f'Bot {config["appid"]}.{config["secret"]}',
            'Content-Type': 'application/json',
            'User-Agent': 'BotNodeSDK/1.0.0'
        }
        
        # 尝试获取机器人信息
        response = requests.get(
            "https://api.sgroup.qq.com/users/@me",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return "✅ API访问成功"
        elif response.status_code == 401:
            error_data = response.json() if response.text else {}
            if "白名单" in str(error_data):
                return f"❌ IP白名单问题: {error_data}"
            else:
                return f"❌ 认证失败: {error_data}"
        else:
            return f"❌ HTTP {response.status_code}: {response.text}"
            
    except Exception as e:
        return f"❌ 请求异常: {e}"

def check_config_file():
    """检查配置文件"""
    try:
        config = read("config.yaml")
        
        issues = []
        if not config.get("appid"):
            issues.append("❌ 缺少appid")
        elif len(str(config["appid"])) < 8:
            issues.append("⚠️ appid格式可能不正确")
        
        if not config.get("secret"):
            issues.append("❌ 缺少secret")
        elif len(config["secret"]) < 20:
            issues.append("⚠️ secret格式可能不正确")
        
        if issues:
            return {"status": "❌ 配置问题", "issues": issues, "config": None}
        else:
            return {"status": "✅ 配置正常", "issues": [], "config": config}
            
    except Exception as e:
        return {"status": f"❌ 配置文件读取失败: {e}", "issues": [], "config": None}

def main():
    print("🔍 QQ机器人连接诊断")
    print("=" * 50)
    print(f"诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. 检查公网IP
    print("1️⃣ 检查公网IP地址")
    public_ip = get_public_ip()
    print(f"   当前公网IP: {public_ip}")
    print()
    
    # 2. 检查配置文件
    print("2️⃣ 检查配置文件")
    config_result = check_config_file()
    print(f"   {config_result['status']}")
    if config_result['issues']:
        for issue in config_result['issues']:
            print(f"   {issue}")
    print()
    
    # 3. 测试DNS解析
    print("3️⃣ 测试DNS解析")
    dns_results = test_dns_resolution()
    for host, result in dns_results.items():
        print(f"   {host}: {result}")
    print()
    
    # 4. 测试网络连通性
    print("4️⃣ 测试网络连通性")
    network_results = test_network_connectivity()
    for url, result in network_results.items():
        print(f"   {result}: {url}")
    print()
    
    # 5. 测试机器人API访问
    if config_result['config']:
        print("5️⃣ 测试机器人API访问")
        api_result = test_bot_api_access(config_result['config'])
        print(f"   {api_result}")
        print()
    
    # 6. 提供解决建议
    print("💡 解决建议")
    print("-" * 30)
    
    if "白名单" in str(network_results) or "白名单" in str(api_result if 'api_result' in locals() else ""):
        print("🎯 IP白名单问题解决方案：")
        print(f"   1. 确认已将IP {public_ip} 添加到QQ开放平台白名单")
        print("   2. 等待5-15分钟让白名单生效")
        print("   3. 检查是否在正确的环境（沙盒/正式）添加了白名单")
        print("   4. 确认机器人应用状态是否正常")
        print()
        print("🔧 详细步骤：")
        print("   • 访问 https://q.qq.com/")
        print("   • 登录开发者账号")
        print("   • 选择你的机器人应用")
        print("   • 开发设置 -> 服务器配置 -> IP白名单")
        print(f"   • 确认 {public_ip} 在白名单中")
        print("   • 如果是沙盒环境，检查沙盒白名单设置")
    
    elif "认证失败" in str(api_result if 'api_result' in locals() else ""):
        print("🎯 认证问题解决方案：")
        print("   1. 检查appid和secret是否正确")
        print("   2. 确认机器人应用状态是否为'开发中'或'已上线'")
        print("   3. 检查是否使用了正确的环境（沙盒/正式）")
    
    else:
        print("🎯 通用解决方案：")
        print("   1. 检查网络连接是否正常")
        print("   2. 确认防火墙没有阻止相关连接")
        print("   3. 尝试使用VPN或更换网络环境")
        print("   4. 联系QQ开放平台技术支持")
    
    print()
    print("📞 如果问题持续存在，请联系QQ开放平台客服")
    print("   客服邮箱: q_developer@tencent.com")

if __name__ == "__main__":
    main()
