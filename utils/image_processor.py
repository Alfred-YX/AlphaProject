import base64
from PIL import Image
from io import BytesIO
import os

class ImageProcessor:
    @staticmethod
    def encode_image(image_path: str) -> str:
        """将图片文件编码为base64字符串"""
        # 验证文件是否存在
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")

        # 验证文件格式
        valid_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
        ext = os.path.splitext(image_path)[1].lower()
        if ext not in valid_formats:
            raise ValueError(f"不支持的图片格式: {ext}，支持格式: {valid_formats}")

        try:
            # 打开并处理图片
            with Image.open(image_path) as img:
                # 转换为RGB模式（处理透明背景）
                if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else img.info['transparency'])
                    img = background
                else:
                    img = img.convert('RGB')

                # 调整图片大小（如果过大）
                max_size = (1024, 1024)
                img.thumbnail(max_size)

                # 编码为base64
                buffered = BytesIO()
                img.save(buffered, format="JPEG")
                return base64.b64encode(buffered.getvalue()).decode('utf-8')

        except Exception as e:
            raise RuntimeError(f"图片处理失败: {str(e)}")

    @staticmethod
    def is_image_file(file_path: str) -> bool:
        """检查文件是否为图片"""
        valid_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
        ext = os.path.splitext(file_path)[1].lower()
        return ext in valid_formats