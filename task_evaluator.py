import requests
import json
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class TaskEvaluator:
    def __init__(self, api_key: str = "", api_base: str = "https://api.deepseek.com/v1", model: str = "deepseek-chat"):
        """
        初始化任务评估器
        
        Args:
            api_key: API密钥（如果为空则使用免费评估）
            api_base: API基础URL
            model: 使用的模型名称
        """
        self.api_key = api_key
        self.api_base = api_base.rstrip('/')
        self.model = model
        self.use_ai = bool(api_key)
    
    def evaluate_task_value(self, task_name: str, deadline: datetime) -> int:
        """
        评估任务价值并转换为代币数量
        
        Args:
            task_name: 任务名称
            deadline: 截止时间
            
        Returns:
            代币数量（10-100之间）
        """
        if self.use_ai:
            return self._ai_evaluate_task(task_name, deadline)
        else:
            return self._simple_evaluate_task(task_name, deadline)
    
    def _ai_evaluate_task(self, task_name: str, deadline: datetime) -> int:
        """使用AI评估任务价值"""
        try:
            now = datetime.now()
            time_diff = deadline - now
            days_left = time_diff.days
            hours_left = time_diff.seconds // 3600
            
            prompt = f"""
请评估以下任务的价值和难度，并给出一个10-100之间的代币奖励分数。

任务名称：{task_name}
截止时间：{deadline.strftime('%Y-%m-%d %H:%M')}
剩余时间：{days_left}天{hours_left}小时

评估标准：
1. 任务复杂度和工作量（40%权重）
2. 任务的重要性和紧急程度（30%权重）
3. 时间压力（剩余时间越少，奖励越高）（20%权重）
4. 任务类型的价值（学习、工作、健康等）（10%权重）

请直接返回一个10-100之间的整数，不要解释。
"""

            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.model,
                'messages': [
                    {'role': 'system', 'content': '你是一个任务价值评估专家，专门为番茄钟系统评估任务的代币价值。'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 10,
                'temperature': 0.3
            }
            
            response = requests.post(
                f'{self.api_base}/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                
                # 提取数字
                numbers = re.findall(r'\d+', content)
                if numbers:
                    tokens = int(numbers[0])
                    return max(10, min(100, tokens))  # 确保在10-100范围内
            
        except Exception as e:
            print(f"AI评估失败: {e}")
        
        # AI评估失败时使用简单评估
        return self._simple_evaluate_task(task_name, deadline)
    
    def _simple_evaluate_task(self, task_name: str, deadline: datetime) -> int:
        """简单的任务价值评估算法"""
        base_tokens = 20
        
        # 根据任务名称关键词调整分数
        task_lower = task_name.lower()
        
        # 工作学习类任务
        work_keywords = ['工作', '学习', '项目', '代码', '编程', '报告', '文档', '会议', '培训', '考试']
        if any(keyword in task_lower for keyword in work_keywords):
            base_tokens += 20
        
        # 健康生活类任务
        health_keywords = ['运动', '健身', '锻炼', '跑步', '瑜伽', '冥想', '睡眠', '休息']
        if any(keyword in task_lower for keyword in health_keywords):
            base_tokens += 15
        
        # 创作类任务
        creative_keywords = ['写作', '创作', '设计', '绘画', '音乐', '视频', '博客']
        if any(keyword in task_lower for keyword in creative_keywords):
            base_tokens += 25
        
        # 社交类任务
        social_keywords = ['聚会', '约会', '拜访', '电话', '聊天', '社交']
        if any(keyword in task_lower for keyword in social_keywords):
            base_tokens += 10
        
        # 根据任务长度调整（更详细的任务描述可能意味着更复杂）
        if len(task_name) > 20:
            base_tokens += 10
        elif len(task_name) > 10:
            base_tokens += 5
        
        # 根据时间压力调整
        now = datetime.now()
        time_diff = deadline - now
        hours_left = time_diff.total_seconds() / 3600
        
        if hours_left < 1:
            base_tokens += 30  # 1小时内截止
        elif hours_left < 6:
            base_tokens += 20  # 6小时内截止
        elif hours_left < 24:
            base_tokens += 15  # 1天内截止
        elif hours_left < 72:
            base_tokens += 10  # 3天内截止
        elif hours_left > 168:  # 超过一周
            base_tokens -= 5
        
        # 根据截止时间是否在工作时间调整
        if 9 <= deadline.hour <= 18 and deadline.weekday() < 5:  # 工作日工作时间
            base_tokens += 5
        
        return max(10, min(100, base_tokens))
    
    def get_task_difficulty_description(self, tokens: int) -> str:
        """根据代币数量返回任务难度描述"""
        if tokens >= 80:
            return "极高难度 🔥🔥🔥"
        elif tokens >= 60:
            return "高难度 🔥🔥"
        elif tokens >= 40:
            return "中等难度 🔥"
        elif tokens >= 20:
            return "简单任务 ⭐"
        else:
            return "轻松任务 ✨"
    
    def suggest_task_optimization(self, task_name: str, tokens: int) -> str:
        """根据任务评估结果提供优化建议"""
        suggestions = []
        
        if tokens < 20:
            suggestions.append("💡 考虑将多个类似的小任务合并成一个更有价值的任务")
        elif tokens > 80:
            suggestions.append("💡 考虑将这个大任务拆分成几个小任务，更容易完成")
        
        if '学习' in task_name:
            suggestions.append("📚 学习类任务建议设置具体的学习目标和时长")
        
        if '运动' in task_name or '锻炼' in task_name:
            suggestions.append("🏃‍♂️ 运动类任务建议记录具体的运动类型和时长")
        
        return '\n'.join(suggestions) if suggestions else "✅ 任务设置合理！"

# 配置管理
class TaskEvaluatorConfig:
    """任务评估器配置"""
    
    def __init__(self, config_dict: dict = None):
        """
        初始化配置
        
        Args:
            config_dict: 从config.yaml读取的配置字典
        """
        self.config = config_dict or {}
    
    def get_evaluator(self, service: str = "simple") -> TaskEvaluator:
        """
        获取任务评估器实例
        
        Args:
            service: 服务类型 ("deepseek", "openai", "zhipu", "simple")
        """
        if service == "deepseek":
            deepseek_config = self.config.get("deepseek", {})
            api_key = deepseek_config.get("api_key", "")
            if api_key and api_key != "你的DeepSeek API Key":
                api_base = deepseek_config.get("api_base", "https://api.deepseek.com/v1")
                model = deepseek_config.get("model", "deepseek-chat")
                return TaskEvaluator(api_key, api_base, model)
        
        elif service == "openai":
            openai_config = self.config.get("openai", {})
            api_key = openai_config.get("api_key", "")
            if api_key and api_key != "你的OpenAI API Key":
                api_base = openai_config.get("api_base", "https://api.openai.com/v1")
                model = openai_config.get("model", "gpt-3.5-turbo")
                return TaskEvaluator(api_key, api_base, model)
        
        elif service == "zhipu":
            zhipu_config = self.config.get("zhipu", {})
            api_key = zhipu_config.get("api_key", "")
            if api_key and api_key != "你的智谱AI API Key":
                api_base = zhipu_config.get("api_base", "https://open.bigmodel.cn/api/paas/v4")
                model = zhipu_config.get("model", "glm-4")
                return TaskEvaluator(api_key, api_base, model)
        
        # 使用简单评估（不需要API密钥）
        return TaskEvaluator()

# 保持向后兼容的静态配置类
class StaticTaskEvaluatorConfig:
    """静态任务评估器配置（向后兼容）"""
    
    # DeepSeek配置（推荐）
    DEEPSEEK_API_KEY = ""  # 在这里填入你的API密钥
    DEEPSEEK_API_BASE = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL = "deepseek-chat"
    
    # OpenAI配置（备选）
    OPENAI_API_KEY = ""
    OPENAI_API_BASE = "https://api.openai.com/v1"
    OPENAI_MODEL = "gpt-3.5-turbo"
    
    # 智谱AI配置
    ZHIPU_API_KEY = ""
    ZHIPU_API_BASE = "https://open.bigmodel.cn/api/paas/v4"
    ZHIPU_MODEL = "glm-4"
    
    @classmethod
    def get_evaluator(cls, service: str = "simple") -> TaskEvaluator:
        """
        获取任务评估器实例
        
        Args:
            service: 服务类型 ("deepseek", "openai", "zhipu", "simple")
        """
        if service == "deepseek" and cls.DEEPSEEK_API_KEY:
            return TaskEvaluator(cls.DEEPSEEK_API_KEY, cls.DEEPSEEK_API_BASE, cls.DEEPSEEK_MODEL)
        elif service == "openai" and cls.OPENAI_API_KEY:
            return TaskEvaluator(cls.OPENAI_API_KEY, cls.OPENAI_API_BASE, cls.OPENAI_MODEL)
        elif service == "zhipu" and cls.ZHIPU_API_KEY:
            return TaskEvaluator(cls.ZHIPU_API_KEY, cls.ZHIPU_API_BASE, cls.ZHIPU_MODEL)
        else:
            # 使用简单评估（不需要API密钥）
            return TaskEvaluator()
