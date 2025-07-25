import requests
import json
from config.config import API_URL

class OllamaAPIClient:
    @staticmethod
    def call_api(prompt, model, images=None):
        """调用Ollama API，支持文本和图片输入"""
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }

        # 如果有图片，添加图片数据
        if images:
            payload["images"] = images

        try:
            response = requests.post(
                API_URL,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload)
            )

            if response.status_code == 200:
                return response.json().get("response", "我没太明白你的意思呢~")
            elif response.status_code == 405:
                raise Exception("API请求方法错误，请确认端点是否支持POST请求")
            else:
                raise Exception(f"API调用失败: {response.status_code} {response.text}")
        except Exception as e:
            return f"接口通信错误: {str(e)}"

    def generate_text_response(self, prompt, model):
        """生成文本响应"""
        return self.call_api(prompt, model)

    def analyze_image(self, image_data, model):
        """分析图片内容"""
        return self.call_api("描述这张图片的内容并分析情感", model, [image_data])