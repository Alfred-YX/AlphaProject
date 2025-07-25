import re
from typing import Literal


class EmotionAnalyzer:
    def __init__(self):
        # 情感词库 - 可根据需要扩展
        self.positive_words = {
            '开心', '高兴', '喜欢', '爱', '好', '棒', '优秀', '不错', '支持', '赞美',
            '幸福', '满足', '兴奋', '惊喜', '温暖', '甜蜜', '愉快', '感谢', '感恩'
        }
        self.negative_words = {
            '难过', '伤心', '讨厌', '恨', '坏', '差', '糟糕', '失望', '生气', '愤怒',
            '痛苦', '悲伤', '遗憾', '烦躁', '无聊', '厌恶', '拒绝', '批评', '指责'
        }
        # 情感增强词
        self.intensifiers = {'很', '非常', '特别', '极其', '太', '十分', '超级', '尤其'}

    def analyze(self, text: str) -> Literal['positive', 'negative', 'neutral']:
        """分析文本情感，返回'positive'、'negative'或'neutral'"""
        text = text.lower().strip()
        if not text:
            return 'neutral'

        # 提取词语（简单分词）
        words = re.findall(r'\b\w+\b', text)
        word_count = len(words)
        if word_count == 0:
            return 'neutral'

        # 情感分数计算
        positive_score = 0
        negative_score = 0

        for i, word in enumerate(words):
            if word in self.positive_words:
                # 检查是否有增强词修饰
                if i > 0 and words[i - 1] in self.intensifiers:
                    positive_score += 2
                else:
                    positive_score += 1
            elif word in self.negative_words:
                if i > 0 and words[i - 1] in self.intensifiers:
                    negative_score += 2
                else:
                    negative_score += 1

        # 计算情感倾向
        if positive_score > negative_score:
            return 'positive'
        elif negative_score > positive_score:
            return 'negative'
        else:
            # 中性或无明显情感
            return 'neutral'
