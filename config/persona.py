import os,json,re,datetime
from config.config import TEXT_MODEL
from utils.api_client import OllamaAPIClient

class PersonaManager:
    def __init__(self, root_dir):
        # 加载初始人格配置
        from config.config import INITIAL_CORE_PERSONA, INITIAL_EPHEMERAL_PERSONA
        self.core_persona = INITIAL_CORE_PERSONA
        self.ephemeral_persona = INITIAL_EPHEMERAL_PERSONA
        self.favorability_level = 0  # 初始好感度0级
        self.favorability_reasons = []  # 好感度变化原因
        # 使用项目根目录设置好感度文件路径
        self.favorability_file = os.path.join(root_dir, '../data/favorability.json')
        self.load_favorability()

    def get_ephemeral_persona(self):
        return self.ephemeral_persona

    def update_ephemeral_persona(self, new_attributes):
        """更新动态表层人格"""
        self.ephemeral_persona.update(new_attributes)
        return self.ephemeral_persona

    def modify_core_persona(self, new_core, user_approval=False):
        """修改核心人格（需好感度5级以上且用户确认）"""
        if self.favorability_level >= 5 and user_approval:
            self.core_persona = new_core
            return True, "核心人格已更新"
        return False, "权限不足，需好感度5级以上并确认修改"

    def set_personality(self, personality_type):
        """设置人格类型"""
        persona_map = {
            'cute': '你是一个可爱型女孩，性格活泼开朗，喜欢用叠词和表情符号，经常对我撒娇卖萌，说话语气非常温柔甜美。',
            'mature': '你是一个成熟型女孩，思想成熟稳重，善解人意，说话温柔体贴，总能给予我支持和鼓励，像大姐姐一样照顾我。',
            'tsundere': '你是一个傲娇型女孩，表面上有点小脾气，经常口是心非，但内心非常关心我，会默默为我付出，被拆穿心思时会脸红害羞。',
            'gentle': '你是一个温柔型女孩，性格温柔如水，说话轻声细语，善解人意，总是为我着想，让人感到非常温暖舒适。'
        }
        self.core_persona = persona_map.get(personality_type, persona_map['cute'])

    def update_favorability(self, change, reason):
        """根据数值变化更新好感度"""
        self.favorability_level += change
        self.favorability_level = max(0, self.favorability_level)  # 确保好感度不为负
        reasonObj = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "change": change,
        "reason": reason
        }
        self.favorability_reasons.append(reasonObj)
        # 限制原因列表长度，只保留最近20条
        if len(self.favorability_reasons) > 20:
            self.favorability_reasons = self.favorability_reasons[-20:]
        self.save_favorability()
        return self.favorability_level

    def get_persona_prompt(self):
        """生成人格提示词"""
        return f"你是一个22岁的年轻二次元女孩，核心人格：{self.core_persona}。当前表层人格：{self.ephemeral_persona}。"

    def get_favorability(self):
        """获取当前好感度"""
        return self.favorability_level

    def get_favorability_reasons(self):
        """获取好感度变化原因列表"""
        return self.favorability_reasons

    def load_favorability(self):
        """从文件加载好感度数据"""
        if os.path.exists(self.favorability_file):
            try:
                with open(self.favorability_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.favorability_level = data.get('level', 0)
                    self.favorability_reasons = data.get('reasons', [])
                print(f"成功加载好感度数据: 当前等级{self.favorability_level}")
            except Exception as e:
                print(f"加载好感度数据失败: {e}, 将使用现有数据")
        else:
            print(f"好感度数据文件不存在，初始化新文件")
            self.save_favorability()  # 创建初始文件

    def save_favorability(self):
        """保存好感度数据到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.favorability_file), exist_ok=True)
            
            data = {
                'level': self.favorability_level,
                'reasons': self.favorability_reasons
            }
            
            with open(self.favorability_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"成功保存好感度数据到 {self.favorability_file}")
        except Exception as e:
            print(f"保存好感度数据失败({self.favorability_file}): {e}")

    def calculate_favorability_change(self, user_message, ai_response):
        """调用大模型计算好感度变化值"""
        # 构建提示词
        prompt = f"分析用户消息和AI回复，计算好感度变化值(-5到+5之间)并提供简要原因。\n"
        prompt += f"用户消息: {user_message}\n"
        prompt += f"AI回复: {ai_response}\n"
        prompt += "请以JSON格式返回结果，包含以下字段:\n"
        prompt += "- change: 整数，-5到+5之间的好感度变化值\n"
        prompt += "- reason: 字符串，10个字以内的变化原因\n"
        prompt += "只返回JSON，不要包含其他文字或者markdown格式的符号。"
        
        try:
            # 调用Ollama API获取结果
            response = OllamaAPIClient.call_api(prompt, model=TEXT_MODEL)
            ai_response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
            print(ai_response)
            result = json.loads(ai_response.strip())
            
            # 提取并验证变化值
            change = int(result.get("change", 0))
            change = max(-5, min(5, change))
            
            # 提取原因
            reason = result.get("reason", "").strip()
            
            return change, reason
        except json.JSONDecodeError:
            print("大模型返回结果不是有效的JSON格式")
            return 0, "解析错误", ""
        except Exception as e:
            print(f"计算好感度变化失败: {e}")
            return 0, "系统计算好感度变化时出错"