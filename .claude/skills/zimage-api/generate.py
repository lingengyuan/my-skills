#!/usr/bin/env python3
"""
Z-Image API Generator - 使用 Replicate API 生成风格化图像
"""

import sys
import time
from pathlib import Path

# 添加核心模块路径
SKILL_DIR = Path(__file__).parent
CORE_DIR = SKILL_DIR.parent / "zimage-core"
sys.path.insert(0, str(CORE_DIR))

from lora_generator import LoraGenerator


def generate(prompt, style="hojo", output_dir=None):
    """
    生成风格化图像

    Args:
        prompt: 提示词（英文逗号分隔的标签）
        style: 风格 (hojo/satoshi)
        output_dir: 输出目录

    Returns:
        输出图片路径
    """
    print(f"[Z-Image API] 风格: {style}")
    print(f"[Z-Image API] 提示词: {prompt}")

    generator = LoraGenerator(style=style)
    image = generator.generate(prompt, width=768, height=768)

    # 保存
    if output_dir is None:
        output_dir = SKILL_DIR.parent.parent.parent / "outputs" / "zimage"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = int(time.time())
    output_path = output_dir / f"zimage_{style}_{timestamp}.png"
    generator.save(image, output_path)

    print(f"\n完成! 输出: {output_path}")
    return output_path


def main():
    """
    用法:
        python generate.py "<提示词>" [风格]

    参数:
        提示词: 英文逗号分隔的标签
        风格: hojo (北条司/黑白) 或 satoshi (漆原智志/彩色)

    示例:
        python generate.py "1girl, solo, glasses, smile" hojo
        python generate.py "1girl, portrait, anime style" satoshi
    """
    if len(sys.argv) < 2:
        print(main.__doc__)
        return

    prompt = sys.argv[1]
    style = sys.argv[2] if len(sys.argv) > 2 else "hojo"

    if style not in ["hojo", "satoshi"]:
        print(f"未知风格: {style}, 使用默认 hojo")
        style = "hojo"

    generate(prompt, style)


if __name__ == "__main__":
    main()
