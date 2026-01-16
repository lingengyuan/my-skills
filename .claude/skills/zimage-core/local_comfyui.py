"""
Local ComfyUI Generator - 本地 ComfyUI 连接模块
连接本地 ComfyUI 服务器进行图像生成
"""

import os
import json
import time
import uuid
import urllib.request
import urllib.parse
from pathlib import Path
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()


class LocalComfyUIGenerator:
    """本地 ComfyUI 生成器"""

    DEFAULT_SERVER = "127.0.0.1:8188"

    # 风格配置
    STYLES = {
        "hojo": {
            "name": "北条司风格 (Hojo Tsukasa)",
            "description": "80年代《城市猎人》风格，黑白漫画，网点纸效果",
            "trigger": "",
            "lora": "90s anime.safetensors",
            "lora_strength": -2.0,
            "style_prompt": "manga style, monochrome, greyscale, screentone, high contrast, ink lines, 1980s style",
            "negative": "color, colorful, low quality, blurry, messy lines, 3d render, modern",
            "cfg": 8.0,
            "steps": 25,
        },
        "satoshi": {
            "name": "漆原智志风格 (Urushihara Satoshi)",
            "description": "90年代OVA风格，彩色动漫，光泽质感",
            "trigger": "",
            "lora": "90s anime.safetensors",
            "lora_strength": 2.0,
            "style_prompt": "anime style, vibrant colors, glossy, shiny skin, detailed, 90s anime aesthetic, retro anime",
            "negative": "monochrome, greyscale, low quality, dull colors, flat shading, modern style",
            "cfg": 7.0,
            "steps": 25,
        }
    }

    # 带 LoRA 的工作流模板
    LORA_WORKFLOW = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": 0,
                "steps": 30,
                "cfg": 7.5,
                "sampler_name": "euler_ancestral",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["10", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            }
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": "animagine-xl-3.1.safetensors"
            }
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": 768,
                "height": 768,
                "batch_size": 1
            }
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": "positive prompt",
                "clip": ["10", 1]
            }
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": "negative prompt",
                "clip": ["10", 1]
            }
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2]
            }
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": "ZImage",
                "images": ["8", 0]
            }
        },
        "10": {
            "class_type": "LoraLoader",
            "inputs": {
                "lora_name": "lora.safetensors",
                "strength_model": 0.8,
                "strength_clip": 0.8,
                "model": ["4", 0],
                "clip": ["4", 1]
            }
        }
    }

    def __init__(self, server_address=None, style="hojo"):
        """
        初始化本地 ComfyUI 生成器

        Args:
            server_address: ComfyUI 服务器地址 (默认 127.0.0.1:8188)
            style: 风格选择 ("hojo" 或 "satoshi")
        """
        self.server_address = server_address or os.getenv("COMFYUI_SERVER", self.DEFAULT_SERVER)

        if style not in self.STYLES:
            raise ValueError(f"未知风格: {style}，可选: {list(self.STYLES.keys())}")

        self.style = style
        self.style_config = self.STYLES[style]
        self.client_id = str(uuid.uuid4())

        print(f"[LocalComfyUI] 服务器: {self.server_address}")
        print(f"[LocalComfyUI] 风格: {self.style_config['name']}")

    def check_server(self):
        """检查服务器是否可用"""
        try:
            url = f"http://{self.server_address}/system_stats"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read())
                print(f"[LocalComfyUI] 服务器在线")
                if "system" in data:
                    print(f"[LocalComfyUI] GPU: {data['system'].get('gpu_name', 'Unknown')}")
                return True
        except Exception as e:
            print(f"[LocalComfyUI] 服务器离线: {e}")
            return False

    def generate(self, prompt, width=768, height=768, seed=-1):
        """
        生成图像

        Args:
            prompt: 用户提示词
            width: 图像宽度
            height: 图像高度
            seed: 随机种子 (-1 为随机)

        Returns:
            PIL Image 对象
        """
        import random

        if seed == -1:
            seed = random.randint(0, 2147483647)

        full_prompt = self._build_prompt(prompt)
        negative = self.style_config["negative"]

        print(f"\n[生成] 提示词: {full_prompt[:80]}...")
        print(f"[生成] 分辨率: {width}x{height}")
        print(f"[生成] 种子: {seed}")

        workflow = self._build_lora_workflow(full_prompt, negative, width, height, seed)

        print("[生成] 提交任务到 ComfyUI...")
        prompt_id = self._queue_prompt(workflow)

        print("[生成] 等待生成完成...")
        images = self._wait_for_completion(prompt_id)

        if not images:
            raise Exception("生成失败：未返回图片")

        print("[生成] 完成!")
        return images[0]

    def _build_prompt(self, user_prompt):
        """构建完整提示词"""
        trigger = self.style_config["trigger"]
        style_prompt = self.style_config["style_prompt"]

        parts = [p for p in [trigger, user_prompt, style_prompt, "masterpiece, best quality, detailed"] if p]
        return ", ".join(parts)

    def _build_lora_workflow(self, prompt, negative, width, height, seed):
        """构建带 LoRA 的工作流"""
        import copy
        workflow = copy.deepcopy(self.LORA_WORKFLOW)

        workflow["3"]["inputs"]["seed"] = seed
        workflow["3"]["inputs"]["steps"] = self.style_config["steps"]
        workflow["3"]["inputs"]["cfg"] = self.style_config["cfg"]
        workflow["5"]["inputs"]["width"] = width
        workflow["5"]["inputs"]["height"] = height
        workflow["6"]["inputs"]["text"] = prompt
        workflow["7"]["inputs"]["text"] = negative
        workflow["10"]["inputs"]["lora_name"] = self.style_config["lora"]
        workflow["10"]["inputs"]["strength_model"] = self.style_config["lora_strength"]
        workflow["10"]["inputs"]["strength_clip"] = self.style_config["lora_strength"]

        return workflow

    def _queue_prompt(self, workflow):
        """提交工作流到队列"""
        data = json.dumps({
            "prompt": workflow,
            "client_id": self.client_id
        }).encode('utf-8')

        url = f"http://{self.server_address}/prompt"
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            return result['prompt_id']

    def _wait_for_completion(self, prompt_id, timeout=300):
        """等待任务完成并获取图片"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            url = f"http://{self.server_address}/history/{prompt_id}"
            try:
                with urllib.request.urlopen(url) as response:
                    history = json.loads(response.read())

                    if prompt_id in history:
                        outputs = history[prompt_id].get("outputs", {})
                        images = []

                        for node_id, node_output in outputs.items():
                            if "images" in node_output:
                                for img_data in node_output["images"]:
                                    img = self._get_image(
                                        img_data["filename"],
                                        img_data.get("subfolder", ""),
                                        img_data.get("type", "output")
                                    )
                                    images.append(img)

                        if images:
                            return images

            except urllib.error.HTTPError:
                pass

            time.sleep(1)

        raise TimeoutError(f"生成超时 (>{timeout}秒)")

    def _get_image(self, filename, subfolder, folder_type):
        """从 ComfyUI 获取图片"""
        params = urllib.parse.urlencode({
            "filename": filename,
            "subfolder": subfolder,
            "type": folder_type
        })
        url = f"http://{self.server_address}/view?{params}"

        with urllib.request.urlopen(url) as response:
            return Image.open(BytesIO(response.read()))

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
