"""
Presets and configuration for Z-Image generation
"""

class StylePresets:
    """风格预设配置"""

    PRESETS = {
        # 黑白漫画
        "hojo_manga": {
            "name": "黑白漫画 (Hojo Manga Style)",
            "description": "北条司风格，网点纸效果、高对比度线条，80年代漫画风格",
            "style_keywords": "Zanshou_kin_Hojo, z-image style, manga style, monochrome, screentone, ink lines",
            "quality_keywords": "high contrast, detailed lineart, sharp lines, masterpiece",
            "negative": "color, low quality, blurry, messy lines",
            "steps": 35,
            "cfg": 8.0,
            "workflow": "hojo_manga",
            "lora": "z-image-hojo.safetensors",
            "lora_strength": 0.85,
        },

        # 彩色动漫
        "satoshi_anime": {
            "name": "彩色动漫 (Satoshi Anime Style)",
            "description": "漆原智志风格，鲜艳色彩、光泽质感，90年代动漫风格",
            "style_keywords": "sato, z-image style, anime style, vibrant colors, glossy, shiny skin",
            "quality_keywords": "detailed, high saturation, professional illustration, masterpiece",
            "negative": "monochrome, low quality, dull colors, flat",
            "steps": 30,
            "cfg": 7.0,
            "workflow": "satoshi_anime",
            "lora": "z-image-satoshi.safetensors",
            "lora_strength": 0.80,
        },
    }

    @classmethod
    def get_preset(cls, key):
        """获取预设配置"""
        return cls.PRESETS.get(key)

    @classmethod
    def list_presets(cls):
        """列出所有预设"""
        return list(cls.PRESETS.keys())


class QualityMode:
    """质量模式配置"""

    MODES = {
        "quick": {
            "name": "快速模式 (Quick)",
            "resolution": (768, 768),
            "steps": 20,
            "cost": "~$0.003",
            "time": "~20秒",
            "description": "适合快速预览和测试",
        },

        "standard": {
            "name": "标准模式 (Standard)",
            "resolution": (1024, 1024),
            "steps": 30,
            "cost": "~$0.006",
            "time": "~30-40秒",
            "description": "平衡质量和速度，日常使用",
        },

        "high": {
            "name": "高质量模式 (High Quality)",
            "resolution": (1024, 1024),
            "steps": 45,
            "cost": "~$0.009",
            "time": "~50-60秒",
            "description": "最佳质量，适合最终作品",
        },
    }

    @classmethod
    def get_mode(cls, key):
        """获取模式配置"""
        return cls.MODES.get(key, cls.MODES["standard"])


# 导出
PRESETS = StylePresets.PRESETS
