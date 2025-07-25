from flask import Flask, render_template, request, jsonify, url_for
from flask_cors import CORS
import os
import time
import re
import threading
from werkzeug.utils import secure_filename
from config.persona import PersonaManager
from utils.api_client import OllamaAPIClient
from utils.emotion_analyzer import EmotionAnalyzer
from utils.image_processor import ImageProcessor
import json
from config.config import TEXT_MODEL, VISION_MODEL, SUMMARY_INTERVAL

# 初始化Flask应用
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# 设置文件处理
SETTINGS_FILE = 'config/settings.json'

# 加载设置
current_settings = {'personality': 'cute'}
if os.path.exists(SETTINGS_FILE):
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            current_settings = json.load(f)
    except Exception as e:
        print(f'加载设置失败: {e}')

# 保存设置

def save_current_settings():
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(current_settings, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f'保存设置失败: {e}')
        return False

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 存储聊天历史的文件路径
CHAT_HISTORY_FILE = os.path.join(app.root_path, 'data/chat_history.json')
# 存储记忆数据的文件路径
MEMORY_FILE = os.path.join(app.root_path, 'data/memory.json')

# 确保聊天历史文件存在
if not os.path.exists(CHAT_HISTORY_FILE):
    with open(CHAT_HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

# 加载聊天历史
def load_chat_history():
    try:
        with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

# 保存聊天历史
def save_chat_history(history):
    try:
        with open(CHAT_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f'保存聊天历史失败: {e}')

# 加载记忆数据
def load_memory():
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f'加载记忆数据失败: {e}')

# 保存记忆数据
def save_memory(memory):
    try:
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f'保存记忆数据失败: {e}')

# 生成上下文总结
def generate_context_summary(history):
    try:
        # 获取最近的SUMMARY_INTERVAL条对话
        recent_conversations = history[-SUMMARY_INTERVAL*2:]
        context = "\n".join([f"{msg['sender']}: {msg['content']}" for msg in recent_conversations if msg['type'] == 'text'])
        
        prompt = f"请简要总结以下对话内容，提取关键信息，作为记忆保存:\n{context}\n\n总结要求：简洁明了，突出重点，不超过100字"
        summary = api_client.generate_text_response(prompt, TEXT_MODEL)
        summary = re.sub(r'<think>.*?</think>', '', summary, flags=re.DOTALL)
        # 添加到记忆数据
        global memory_data
        memory_data.append({
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': summary,
            'conversation_count': conversation_counter
        })
        
        # 获取当前表层人格
        current_ephemeral = persona_manager.get_ephemeral_persona()
        
        # 获取最近聊天记录
        recent_history = history[-5:]
        formatted_history = "\n".join([f"{msg['sender']}: {msg['content']}" for msg in recent_history if msg['type'] == 'text'])
        
        # 创建人格更新提示
        prompt = f"基于以下当前表层人格和最近聊天记录，生成更新后的表层人格:\n当前表层人格: {current_ephemeral}\n最近聊天记录: {formatted_history}\n\n更新要求:\n1. 保持核心人格特质不变\n2. 根据聊天记录中的用户互动模式，调整语气、表达方式和话题偏好\n3. 输出应仅包含更新后的表层人格描述，不超过100字"
        
        # 调用大模型生成新的表层人格
        updated_ephemeral = api_client.generate_text_response(prompt, TEXT_MODEL)
        updated_ephemeral = re.sub(r'<RichMediaReference>.*?</RichMediaReference>', '', updated_ephemeral, flags=re.DOTALL).strip()
        
        # 更新表层人格
        persona_manager.update_ephemeral_persona({'ephemeral_persona': updated_ephemeral})
        
        # 保存记忆数据
        save_memory(memory_data)
        print(f'生成上下文总结成功: {summary}')
    except Exception as e:
        print(f'生成上下文总结失败: {str(e)}')

# 初始化核心组件
persona_manager = PersonaManager(app.root_path)
# 加载聊天历史
chat_history = load_chat_history()
# 加载记忆数据
memory_data = load_memory()
# 对话计数器
conversation_counter = len(chat_history) // 2  # 每条完整对话包含用户和AI两条消息
api_client = OllamaAPIClient()
emotion_analyzer = EmotionAnalyzer()
image_processor = ImageProcessor()

# 允许的图片扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html', chat_history=chat_history)


@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.form.get('message', '').strip()
    image_file = request.files.get('image')
    response_data = {'status': 'error', 'message': ''}

    if not user_message and not image_file:
        response_data['message'] = '请输入消息或上传图片'
        return jsonify(response_data)

    # 处理用户输入
    user_input_type = 'text'
    image_path = None
    image_base64 = None

    # 处理图片上传
    if image_file and allowed_file(image_file.filename):
        filename = secure_filename(f"{int(time.time())}_{image_file.filename}")
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(image_path)
        user_input_type = 'image'

        # 生成可访问的图片URL
        image_url = url_for('uploaded_file', filename=filename)

    # 添加用户消息到历史
    chat_history.append({
        'sender': 'user',
        'type': user_input_type,
        'content': user_message,
        'image_path': image_url,
        'timestamp': time.strftime('%H:%M:%S')
    })

    # 生成AI响应
    try:
        if user_input_type == 'text':
            # 文本消息处理
            emotion = emotion_analyzer.analyze(user_message)
            prompt = f"{persona_manager.get_persona_prompt()}用户说：{user_message}。用户情感：{emotion}。请以女友身份回应。"
            ai_response = api_client.generate_text_response(prompt, TEXT_MODEL)
        else:
            # 图片消息处理
            try:
                image_data = image_processor.encode_image(image_path)
            except (FileNotFoundError, ValueError) as e:
                return jsonify({'error': str(e)}), 400
            content = api_client.analyze_image(image_data, VISION_MODEL)
            
            # 结合用户文本和图片内容生成提示
            combined_content = f"用户说：{user_message}" if user_message else ""
            combined_content += f"\n用户发送了一张图片，内容描述：{content}"
            
            prompt = f"{persona_manager.get_persona_prompt()}{combined_content}。请结合文本和图片内容回应。"
            ai_response = api_client.generate_text_response(prompt, TEXT_MODEL)

        # 移除返回数据中的标签内容
        ai_response = re.sub(r'<think>.*?</think>', '', ai_response, flags=re.DOTALL)

        # 计算并更新好感度
        # 获取当前时间
        result = persona_manager.calculate_favorability_change(user_message, ai_response)
        if len(result) == 2:
            change, reason = result
        elif len(result) >= 2:
            change, reason = result[:2]
        else:
            change, reason = 0, '解析返回结果出错'
        if change != 0:
            persona_manager.update_favorability(change, reason)

        # 添加AI响应到历史
        chat_history.append({
            'sender': 'ai',
            'type': 'text',
            'content': ai_response,
            'timestamp': time.strftime('%H:%M:%S')
        })
        
        # 保存聊天历史到文件
        save_chat_history(chat_history)

        # 检查是否需要生成上下文总结
        global conversation_counter
        conversation_counter += 1
        if conversation_counter % SUMMARY_INTERVAL == 0:
            # 在后台线程中生成上下文总结
            threading.Thread(target=generate_context_summary, args=(chat_history,)).start()

        response_data = {
            'status': 'success',
            'ai_response': ai_response if ai_response is not None else '未能生成响应',
            'timestamp': time.strftime('%H:%M:%S'),
            'favorability': persona_manager.get_favorability()
        }

    except Exception as e:
        response_data['message'] = f'处理消息时出错: {str(e)}'

    return jsonify(response_data)


@app.route('/save_settings', methods=['POST'])
def save_settings():
    try:
        data = request.get_json()
        personality = data.get('personality')
        if not personality:
            return jsonify({'status': 'error', 'message': '无效的人格设置'})
        
        current_settings['personality'] = personality
        # 保存到文件
        if save_current_settings():
            # 更新当前应用的人格设置
            persona_manager.set_personality(personality)
            return jsonify({'status': 'success', 'message': '人格设置已保存'})
        else:
            return jsonify({'status': 'error', 'message': '保存设置失败'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'保存设置失败: {str(e)}'})

@app.route('/get_settings', methods=['GET'])
def get_settings():
    try:
        # 从current_settings获取当前人格设置
        personality = current_settings.get('personality', 'cute')
        return jsonify({
            'status': 'success',
            'personality': personality
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取设置失败: {str(e)}'})


@app.route('/get_favorability', methods=['GET'])
def get_favorability():
    try:
        favorability = persona_manager.get_favorability()
        reasons = persona_manager.get_favorability_reasons()
        return jsonify({
            'status': 'success',
            'favorability': favorability,
            'reasons': reasons
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取好感度失败: {str(e)}'})


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/get_chat_history', methods=['GET'])
def get_chat_history():
    try:
        history = load_chat_history()
        return jsonify({
            'status': 'success',
            'history': history
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取聊天历史失败: {str(e)}'})


if __name__ == '__main__':
    # 确保静态文件夹和上传文件夹存在
    os.makedirs(os.path.join(app.root_path, 'uploads'), exist_ok=True)
    os.makedirs(os.path.join(app.root_path, 'templates'), exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
