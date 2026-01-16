# Z-Image API Skill

> 使用 Replicate 云端 API 生成北条司/漆原智志风格漫画图像

## 工作流程

```
用户提供图片 → Claude Code 分析图片 → 生成提示词 → Replicate API 生成 → 输出图片
```

**优势：**
- 图片分析由 Claude Code 直接完成，无需额外 API 费用
- 无需本地 GPU，适合没有显卡的用户

## 支持的风格

| 风格 | 特点 | 效果 |
|------|------|------|
| `hojo` | 北条司风格，黑白漫画，80年代《城市猎人》风格 | 黑白 |
| `satoshi` | 漆原智志风格，彩色动漫，90年代OVA风格 | 彩色 |

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
3. 调用 API 生成风格化图片

### 方式2：直接提供提示词

```bash
cd .claude/skills/zimage-api
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

## 环境配置

### 1. 获取 Replicate API Token

1. 访问 [Replicate](https://replicate.com/) 并注册账号
2. 进入 [API Tokens 页面](https://replicate.com/account/api-tokens)
3. 点击 "Create token" 创建新 Token
4. 复制生成的 Token

### 2. 配置环境变量

在项目根目录创建 `.env` 文件：

```env
# Replicate API Token (必需)
REPLICATE_API_TOKEN=r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

或者直接设置环境变量：

```bash
# Windows (PowerShell)
$env:REPLICATE_API_TOKEN="r8_your_token_here"

# Windows (CMD)
set REPLICATE_API_TOKEN=r8_your_token_here

# Linux/macOS
export REPLICATE_API_TOKEN=r8_your_token_here
```

### 3. 安装依赖

```bash
pip install -r .claude/skills/zimage-core/requirements.txt
```

**依赖列表：**
- `replicate` - Replicate API 客户端
- `Pillow` - 图像处理
- `requests` - HTTP 请求
- `python-dotenv` - 环境变量加载

## 输出

- 图像文件：`output/zimage_<风格>_<时间戳>.png`

## 费用参考

- 每张图片约 $0.003 - $0.009（取决于分辨率和步数）
- 图片分析由 Claude Code 完成，无额外费用

## 注意事项

- API 生成需要 30-60 秒
- 建议分辨率 768x768
- 需要网络连接
