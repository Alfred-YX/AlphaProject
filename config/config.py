# Ollama API配置
API_URL = "http://10.190.82.131:8999/api/generate"
# 模型配置
TEXT_MODEL = "qwen3:32b"
VISION_MODEL = "qwen2.5vl"

# 人格配置
PERSONALITY = "tsundere"

# 上下文总结配置
SUMMARY_INTERVAL = 5  # 每5步对话生成一次上下文总结

# 初始核心人格
INITIAL_CORE_PERSONA = "你是一个可爱型的女孩，性格活泼开朗，喜欢用叠词和表情符号，经常对我撒娇卖萌，说话语气非常温柔甜美。"

# 初始表层人格
INITIAL_EPHEMERAL_PERSONA = {}