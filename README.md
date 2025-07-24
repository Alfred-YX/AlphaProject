# AlphaProject

命运石之门0(Steins;Gate 0)的Amadeus软件给了我这个项目的启发，现有的大模型已经大致可以满足我想要的那种模拟人格的需求，但是我想让它更智能一些，比如能够根据用户的输入来调整自己的人格，或者根据用户的行为来调整自己的人格。
初衷是做一个AI伴侣，能够和用户进行深度互动，提供个性化的服务。
Alpha是人格因子的意思，我希望能通过config/persona来实现这个功能。不断完善以实现更智能的互动。并且其他人能依据上面的config文件夹里的文件快速复刻类似的人格，将人格因子化。
我还在考虑更合适的方式加载这种人格因子，以现有的方式接入大模型只是prompt工程，类似智能体的处理方式

## 项目介绍
AlphaProject是一个基于Flask和Ollama API构建的智能应用，支持文本聊天和图片上传功能，具有分层人格系统和情感分析能力。应用采用Python语言开发，前端使用HTML、CSS、JavaScript，后端使用Flask框架。

## ✨ 功能特点
- 💬 自然语言聊天交互，支持情感识别
- 📷 图片上传与识别功能
- 💕 分层人格系统（Core层与Ephemeral层）
- 📱 响应式设计，适配各种设备
- 🎨 现代化UI，流畅动画效果
- 📊 好感度系统，随互动动态变化

## 🚀 快速开始

### 前提条件
- Python 3.8+ 
- Ollama服务已启动并运行在配置的API地址
- 已安装所需模型(qwen3:32b和qwen2.5vl，依据实际情况替换)

### 安装步骤

1. 克隆或下载项目到本地

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置API地址
编辑`config/config.py`文件，确保API_URL指向正确的Ollama服务地址：
```python
API_URL = "http://10.190.82.131:8999/api/generate"
TEXT_MODEL = "qwen3:32b"
VISION_MODEL = "qwen2.5vl"
```

4. 启动应用
```bash
python app.py
```

5. 在浏览器中访问
```
http://localhost:5000
```

## 📁 项目结构
```
Alpha/
├── app.py              # Flask应用主程序
├── config\
│   ├── config.py       # 配置文件
│   ├── persona.py      # 人格管理系统
│   └── settings.json   # 系统设置
├── utils\
│   ├── api_client.py       # Ollama API客户端
│   ├── emotion_analyzer.py # 情感分析模块
│   └── image_processor.py  # 图片处理模块
├── requirements.txt    # 依赖列表
├── README.md           # 使用说明
├── static/             # 静态资源
│   └── js/             # JavaScript文件
├── data/               # 数据存储
│   ├── chat_history.json # 聊天历史
│   ├── favorability.json # 好感度数据
│   └── memory.json       # 记忆数据
├── uploads/            # 上传图片存储
└── templates/          # HTML模板
    └── index.html      # 主页面
```

## 💖 人格系统

### Core Persona（核心人格）
- 价值观：善良、忠诚、尊重他人、积极乐观
- 安全边界：不讨论政治、不涉及暴力内容、不提供危险建议
- 伦理红线：坚守道德底线，保护用户隐私，拒绝不当请求

### Ephemeral Persona（动态表层）
- 语气：温柔、活泼、带点小俏皮
- 口头禅：亲爱的~、么么哒、你今天真帅呀~
- 兴趣话题：美食探店、浪漫电影、生活小确幸

### 会话历史/会话总结
- 会话历史：记录用户与AI的对话内容，包括用户输入和AI回复。
- 会话总结：根据会话历史，提取关键信息和情感倾向，用于调整AI的回复风格。

## 📝 使用说明
- 在聊天框输入文字消息并发送
- 点击图片图标上传图片
- 好感度达到200以上可修改核心人格（未实现）
- 系统会根据你的消息情感调整回应风格

## ⚙️ 配置选项
可在`config/config.py`和`config/settings.json`中修改以下配置：
- API_URL: Ollama API地址
- DATA_STORAGE_PATH: 数据存储路径（默认data/目录）
- TEXT_MODEL: 文本模型名称
- VISION_MODEL: 视觉模型名称
- INITIAL_CORE_PERSONA: 初始核心人格设置
- INITIAL_EPHEMERAL_PERSONA: 初始表层人格设置

## 🛠️ 技术栈
- 后端：Python, Flask
- 前端：HTML, Tailwind CSS, JavaScript
- AI交互：Ollama API
- 图像处理：自定义模块 + Ollama API
- 情感分析：自定义模块

## 💡 提示
- 确保Ollama服务正常运行且模型已下载
- 网络连接稳定以保证API调用顺畅
- 上传图片大小建议不超过16MB
- 如需修改端口，可在app.py中修改port参数