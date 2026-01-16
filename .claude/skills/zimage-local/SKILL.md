# Z-Image Local Skill

> 使用本地 ComfyUI 生成北条司/漆原智志风格漫画图像

## 工作流程

```
用户提供图片 → Claude Code 分析图片 → 生成提示词 → 本地 ComfyUI 生成 → 输出图片
```

**优势：**
- 图片分析由 Claude Code 直接完成，无需 API 费用
- 图像生成在本地完成，无需云端 API 费用
- **完全免费使用**

## 支持的风格

| 风格 | 特点 | 效果 |
|------|------|------|
| `hojo` | 北条司风格，黑白漫画，80年代《城市猎人》风格 | 黑白 |
| `satoshi` | 漆原智志风格，彩色动漫，90年代OVA风格 | 彩色 |

## 前置要求

### 1. 安装 ComfyUI

```bash
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt
```

### 2. 下载模型

| 类型 | 文件 | 下载地址 | 存放位置 |
|------|------|---------|---------|
| Checkpoint | animagine-xl-3.1.safetensors | [HuggingFace](https://huggingface.co/cagliostrolab/animagine-xl-3.1) | `ComfyUI/models/checkpoints/` |
| LoRA | 90s anime.safetensors | [HuggingFace](https://huggingface.co/Norod78/90s-anime-style-lora) | `ComfyUI/models/loras/` |

### 3. 启动 ComfyUI 服务器

```bash
cd <ComfyUI目录>
python main.py --listen

# 6GB 显存用户使用:
python main.py --listen --lowvram
```

服务器启动后访问 http://127.0.0.1:8188 确认运行中。

## 使用方法

### 推荐方式：让 Claude Code 分析图片

直接告诉 Claude Code：

```
帮我把这张图片转成北条司风格
帮我把 input/photo.jpg 转成漆原智志风格
```

Claude Code 会自动：
1. 读取并分析图片内容
2. 生成漫画风格提示词
3. 调用本地 ComfyUI 生成图片

### 方式2：直接提供提示词

```bash
cd .claude/skills/zimage-local
python generate.py "1girl, solo, short hair, glasses, smile" hojo
python generate.py "1girl, portrait, anime style" satoshi
```

## 提示词格式

使用英文逗号分隔的标签格式：

```
1girl, solo, short brown hair, round glasses, gray sweater, smile, looking at viewer, indoor
```

**常用标签：**
- 人物：`1girl`, `1boy`, `solo`, `couple`
- 发型：`short hair`, `long hair`, `ponytail`, `bob cut`
- 表情：`smile`, `serious`, `looking at viewer`
- 构图：`portrait`, `upper body`, `full body`

## 环境配置（可选）

在项目根目录创建 `.env` 文件：

```env
COMFYUI_SERVER=127.0.0.1:8188
```

## 安装依赖

```bash
pip install -r .claude/skills/zimage-core/requirements.txt
```

## 硬件要求

| 组件 | 最低配置 | 推荐配置 |
|------|---------|---------|
| GPU | 4GB VRAM | 8GB+ VRAM |
| RAM | 16GB | 32GB |

**注意：** 6GB 显存的 GPU 需要使用 `--lowvram` 参数启动 ComfyUI。

## 性能参考

- 生成时间：~30-40秒/张 (768x768)
- 显存占用：~5GB (lowvram模式)

## 输出

- 图像文件：`outputs/zimage/zimage_<风格>_local_<时间戳>.png`

## 故障排除

### ComfyUI 服务器未运行

```
错误: ComfyUI 服务器未运行!
```

解决：启动 ComfyUI
```bash
cd <ComfyUI目录>
python main.py --listen --lowvram
```

### 显存不足

使用 `--lowvram` 参数启动 ComfyUI。

### 模型未找到

确保模型文件已下载到正确位置：
- Checkpoint: `ComfyUI/models/checkpoints/animagine-xl-3.1.safetensors`
- LoRA: `ComfyUI/models/loras/90s anime.safetensors`
