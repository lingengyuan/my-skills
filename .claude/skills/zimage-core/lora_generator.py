"""
LoRA Style Generator - 使用 Replicate API 生成风格图像
支持北条司风格和漆原智志风格
"""

import os
import time
from pathlib import Path
from PIL import Image
import requests
from io import BytesIO
from dotenv import load_dotenv
import replicate

load_dotenv()


class LoraGenerator:
    """LoRA 风格生成器 - 支持北条司和漆原智志风格"""

    # 风格配置
    STYLES = {
        "hojo": {
            "name": "北条司风格 (Hojo Tsukasa)",
            "description": "80年代《城市猎人》风格，黑白漫画，网点纸效果，高对比度线条",
            "trigger": "Zanshou_kin_Hojo",
            "style_prompt": "manga style, monochrome, greyscale, screentone, high contrast, ink lines, 80s manga aesthetic",
            "negative": "color, colorful, low quality, blurry, messy lines, 3d render",
            "cfg": 8.0,
            "steps": 30,
        },
        "satoshi": {
            "name": "漆原智志风格 (Urushihara Satoshi)",
            "description": "90年代OVA风格，彩色动漫，光泽质感，鲜艳色彩",
            "trigger": "sato",
            "style_prompt": "anime style, vibrant colors, glossy, shiny skin, detailed, 90s anime aesthetic, high saturation",
            "negative": "monochrome, greyscale, low quality, dull colors, flat shading",
            "cfg": 7.0,
            "steps": 28,
        }
    }

    MODEL_OPTIONS = {
        "sdxl": "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
        "flux_schnell": "black-forest-labs/flux-schnell",
    }

    def __init__(self, style="hojo", model="sdxl"):
        """
        初始化生成器

        Args:
            style: "hojo" (北条司) 或 "satoshi" (漆原智志)
            model: 基础模型选择
        """
        self.token = os.getenv("REPLICATE_API_TOKEN")
        if not self.token:
            raise ValueError("未找到 REPLICATE_API_TOKEN，请在 .env 中配置")

        if style not in self.STYLES:
            raise ValueError(f"未知风格: {style}，可选: {list(self.STYLES.keys())}")

        self.style = style
        self.style_config = self.STYLES[style]
        self.model = model

        print(f"[LoraGenerator] 风格: {self.style_config['name']}")

    def generate(self, prompt, width=768, height=768, seed=-1, timeout=300):
        """
        生成风格图像

        Args:
            prompt: 用户提示词 (来自图片分析)
            width: 图像宽度
            height: 图像高度
            seed: 随机种子 (-1 为随机)
            timeout: 超时时间（秒）

        Returns:
            PIL Image 对象
        """
        full_prompt = self._build_prompt(prompt)
        negative = self.style_config["negative"]

        print(f"\n[生成] 提示词: {full_prompt[:100]}...")
        print(f"[生成] 分辨率: {width}x{height}")
        print(f"[生成] 正在调用 API...")

        try:
            if self.model == "flux_schnell":
                output = self._generate_with_flux(full_prompt, width, height, seed)
            else:
                output = self._generate_with_sdxl(full_prompt, negative, width, height, seed)

            if not output:
                raise Exception("API 未返回图片")

            # 处理不同的返回类型
            if isinstance(output, list):
                image_url = output[0]
            elif hasattr(output, 'url'):
                image_url = output.url
            elif hasattr(output, '__iter__'):
                image_url = next(iter(output))
            else:
                image_url = str(output)

            print(f"[生成] 下载图片...")

            response = requests.get(str(image_url), timeout=60)
            response.raise_for_status()

            image = Image.open(BytesIO(response.content))
            print("[生成] 完成!")

            return image

        except Exception as e:
            print(f"[错误] 生成失败: {e}")
            raise

    def _generate_with_sdxl(self, prompt, negative, width, height, seed):
        """使用 SDXL 生成"""
        import random

        if seed == -1:
            seed = random.randint(0, 2147483647)

        width = min(max(width, 512), 1024)
        height = min(max(height, 512), 1024)
        width = (width // 64) * 64
        height = (height // 64) * 64

        output = replicate.run(
            self.MODEL_OPTIONS["sdxl"],
            input={
                "prompt": prompt,
                "negative_prompt": negative,
                "width": width,
                "height": height,
                "num_inference_steps": self.style_config["steps"],
                "guidance_scale": self.style_config["cfg"],
                "scheduler": "K_EULER_ANCESTRAL",
                "seed": seed,
                "num_outputs": 1,
            },
        )

        return output

    def _generate_with_flux(self, prompt, width, height, seed):
        """使用 Flux Schnell 生成"""
        import random

        if seed == -1:
            seed = random.randint(0, 2147483647)

        output = replicate.run(
            self.MODEL_OPTIONS["flux_schnell"],
            input={
                "prompt": prompt,
                "seed": seed,
                "num_outputs": 1,
                "aspect_ratio": "1:1",
                "output_format": "png",
                "output_quality": 90,
            },
        )

        return output

    def _build_prompt(self, user_prompt):
        """构建完整的风格提示词"""
        trigger = self.style_config["trigger"]
        style_prompt = self.style_config["style_prompt"]

        parts = [
            trigger,
            user_prompt,
            style_prompt,
            "masterpiece, best quality, detailed"
        ]

        return ", ".join(parts)

    def save(self, image, output_path):
        """保存图片"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path)
        print(f"[保存] {output_path}")
        return output_path

    @classmethod
    def list_styles(cls):
        """列出可用风格"""
        print("\n可用风格:\n")
        for key, config in cls.STYLES.items():
            print(f"  {key}: {config['name']}")
            print(f"       {config['description']}")
            print()
