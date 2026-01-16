"""
Z-Image Core - 共享核心模块
支持北条司/漆原智志风格漫画生成
"""

__version__ = "3.0.0"

from .presets import PRESETS, QualityMode
from .lora_generator import LoraGenerator
from .local_comfyui import LocalComfyUIGenerator

__all__ = [
    "PRESETS",
    "QualityMode",
    "LoraGenerator",
    "LocalComfyUIGenerator",
]
