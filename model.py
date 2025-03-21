from transformers import AutoModel, AutoTokenizer
import sys
import os
import torch


class UIEModel:
    def __init__(self):

        # 检测可用的设备，优先级：CUDA > MPS > CPU
        if torch.cuda.is_available():
            self.device = torch.device('cuda')
        elif torch.backends.mps.is_available():
            self.device = torch.device('mps')
        else:
            self.device = torch.device('cpu')
        print(f"Using device: {self.device}")

        model_path = 'xusenlin/uie-base'
        
        # 加载模型和tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        self.model = AutoModel.from_pretrained(model_path, trust_remote_code=True)
        
        # 将模型迁移到指定设备
        self.model = self.model.to(self.device)
 
    def predict(self, text: str, schema: list) -> dict:
        """执行模型推理
        
        Args:
            text: 输入文本
            schema: 信息抽取模式列表
            
        Returns:
            dict: 抽取结果
        """
        return self.model.predict(self.tokenizer, text, schema=schema)

# 全局模型实例
_model = None

def get_model():
    """获取全局模型实例，确保模型只被加载一次"""
    global _model
    if _model is None:
        _model = UIEModel()
    return _model