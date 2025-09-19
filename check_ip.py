#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IP地址监控脚本
用于监控公网IP变化并提醒用户更新白名单
"""

import requests
import json
import time
import os
from datetime import datetime

class IPMonitor:
    def __init__(self, ip_file: str = "current_ip.txt"):
        self.ip_file = ip_file
        self.current_ip = self.load_current_ip()
    
    def get_public_ip(self) -> str:
        """获取当前公网IP"""
        try:
            response = requests.get("https://api.ipify.org", timeout=10)
            return response.text.strip()
        except Exception as e:
            print(f"获取IP失败: {e}")
            return ""
    
    def load_current_ip(self) -> str:
        """从文件加载当前记录的IP"""
        if os.path.exists(self.ip_file):
            try:
                with open(self.ip_file, "r", encoding="utf-8") as f:
                    return f.read().strip()
            except:
                pass
        return ""
    
    def save_current_ip(self, ip: str):
        """保存当前IP到文件"""
        try:
            with open(self.ip_file, "w", encoding="utf-8") as f:
                f.write(ip)
        except Exception as e:
            print(f"保存IP失败: {e}")
    
    def check_ip_change(self) -> bool:
        """检查IP是否发生变化"""
        new_ip = self.get_public_ip()
        if not new_ip:
            return False
        
        if new_ip != self.current_ip:
            print(f"🚨 IP地址已变化！")
            print(f"旧IP: {self.current_ip}")
            print(f"新IP: {new_ip}")
            print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            print("📝 请更新QQ机器人白名单：")
            print(f"1. 访问 https://q.qq.com/")
            print(f"2. 登录开发者账号")
            print(f"3. 找到你的机器人应用")
            print(f"4. 进入安全设置 -> IP白名单")
            print(f"5. 添加新IP: {new_ip}")
            print(f"6. 删除旧IP: {self.current_ip}")
            print()
            
            self.current_ip = new_ip
            self.save_current_ip(new_ip)
            return True
        
        return False
    
    def get_current_status(self) -> dict:
        """获取当前状态"""
        current_ip = self.get_public_ip()
        return {
            "current_ip": current_ip,
            "recorded_ip": self.current_ip,
            "ip_changed": current_ip != self.current_ip,
            "timestamp": datetime.now().isoformat()
        }

def main():
    print("🔍 IP监控脚本")
    print("=" * 40)
    
    monitor = IPMonitor()
    
    # 获取当前状态
    status = monitor.get_current_status()
    print(f"当前公网IP: {status['current_ip']}")
    print(f"记录的IP: {status['recorded_ip']}")
    
    if status['ip_changed']:
        print("⚠️ IP地址已发生变化，需要更新白名单！")
        monitor.check_ip_change()
    else:
        print("✅ IP地址未发生变化")
        
        # 如果没有记录IP，保存当前IP
        if not status['recorded_ip']:
            monitor.save_current_ip(status['current_ip'])
            print(f"📝 已记录当前IP: {status['current_ip']}")
    
    print()
    print("💡 提示：")
    print("- 可以定期运行此脚本检查IP变化")
    print("- 建议将此脚本加入定时任务")
    print("- IP变化时会自动提醒更新白名单")

if __name__ == "__main__":
    main()

