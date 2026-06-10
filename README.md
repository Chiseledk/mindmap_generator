# AI 思维导图生成器

一个基于 Flask 的文本转思维导图工具。项目强调“思维导图是图”：后端会把文本转换为语义树，再生成图节点、边、权重和布局坐标；前端直接渲染 SVG 图形。

## 当前架构

```text
mindmap_generator/
├── backend/
│   ├── main.py                         # Flask 入口和 API
│   ├── services/
│   │   ├── ai_processor.py             # 外部大模型调用
│   │   ├── data_parser.py              # AI JSON 解析和 Pydantic 校验
│   │   ├── graph_algorithms.py         # NLP 关键词提取和图布局算法
│   │   └── mindmap_generator.py        # 生成流程编排
│   └── utils/
│       ├── logger.py                   # 日志工具
│       └── schema.py                   # 语义树和图数据模型
├── templates/
│   └── index.html                      # SVG 思维导图界面
├── requirements.txt
└── README.md
```

根目录是唯一推荐运行入口。`mindmap_generator/` 子目录是旧副本，确认无用后可以删除。

## 功能

- 文本生成思维导图
- AI 二次优化语义树
- SVG 可视化渲染
- SVG / JSON 导出
- 节点拖拽编辑
- 双击节点改名
- 项目保存、打开、删除
- 自动保存最近生成历史记录

项目和历史记录目前保存在浏览器 `localStorage` 中，适合单机演示和个人使用。

## 算法说明

当前算法由三部分组成：

1. 关键词提取

中文文本使用 `jieba.analyse`：

- `TextRank`：基于词共现图排序关键词
- `TF-IDF`：补充高区分度关键词
- 两者融合打分后去重

英文或依赖不可用时，会使用轻量词频兜底。

2. 图布局

后端会把语义树转换成：

- `graph.nodes`
- `graph.edges`
- `graph.layout`

布局使用 `radial-tidy-tree`：

- 先为叶子节点分配稳定顺序
- 内部节点角度取子节点角度均值
- 按深度映射到半径
- 最终生成每个节点的 `x/y` 坐标

3. AI 结构优化（可选）

如果配置了 `SPARK_API_PASSWORD`，系统会先生成一个本地算法初稿，再调用 AI 对语义树做二次优化：

- 合并重复或相近分支
- 将泛化节点改成更具体的短标签
- 补足遗漏的关键词
- 调整层级为“段落主题 -> 关键词 -> 关键句/支撑点”

AI 只优化语义树，不生成坐标。优化后的树会再次经过后端图布局算法生成 `nodes`、`edges` 和 `x/y`。

## 生成流程

```text
用户文本
  -> 本地 NLP 算法生成初稿
  -> 可选 AI 二次优化语义树
  -> 解析和 Pydantic 校验
  -> 失败时保留本地算法初稿
  -> 生成 graph.nodes / graph.edges / graph.layout
  -> 前端 SVG 渲染并支持 SVG/JSON 导出
```

## 本地运行

```powershell
cd C:\Users\25495\PycharmProjects\mindmap_generator
py -m pip install -r requirements.txt
py -m backend.main
```

打开：

```text
http://127.0.0.1:5000
```

## 环境变量

如果需要调用讯飞星火 API，在项目根目录 `.env` 中配置：

```env
SPARK_API_PASSWORD=your_api_password_here
SPARK_API_URL=https://spark-api-open.xf-yun.com/v1/chat/completions
SPARK_MODEL=4.0Ultra
FLASK_SECRET_KEY=your_secret_here
```

`SPARK_API_PASSWORD` 对应讯飞控制台“鉴权信息”里的 `APIPassword`。代码会以如下形式调用：

```http
Authorization: Bearer your_api_password_here
```

不配置 `SPARK_API_PASSWORD` 时，项目会自动使用本地 NLP 算法生成思维导图。

## API

`POST /api/generate_mindmap`

请求：

```json
{
  "text": "需要转换为思维导图的文本"
}
```

响应核心字段：

```json
{
  "success": true,
  "mindmap": {
    "title": "中心主题",
    "nodes": [],
    "graph": {
      "nodes": [],
      "edges": [],
      "layout": "radial-tidy-tree"
    }
  },
  "graph_data": {
    "nodes": [],
    "edges": [],
    "layout": "radial-tidy-tree"
  },
  "generation_source": "ai_optimized"
}
```

`generation_source` 可能的值：

- `ai_optimized`：本地算法初稿已被 AI 二次优化
- `ai_direct`：本地算法无法生成时，由 AI 直接生成
- `algorithm_only`：未调用 AI 或 AI 优化失败，使用本地算法结果
