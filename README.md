# SciToolAgent · 统一知识图谱工作台（精简整合版）

本版本基于用户已有的 SciToolAgent 修改工程，**保留现有科学工具执行逻辑**，新增一个统一 Streamlit 前端：

> 本地 TXT/Markdown 上传 → 结构化分块 → DeepSeek 抽取实体关系 → 网页审核 → 增量更新 SciToolKG/BGE-M3 → 知识图谱浏览 / Jev + DeepSeek 智能问答。

无需手工编写 Excel。为了兼容已有 `incremental_from_excel.py`，系统仍在内部自动创建 `review.xlsx`，允许在网页修改和下载。

## 1. 项目主要文件

```text
SciToolAgent_Unified_Clean/
├── app_scitoolagent_with_evidence.py  # 统一网页入口（上传构图、问答、浏览）
├── unified_services.py              # 网页与抽取/增量/图谱问答的服务层
├── text_to_excel_kg.py              # 原命令行抽取入口（保留可选使用）
├── incremental_from_excel.py        # 原增量入库脚本（网页内部复用）
├── text_ingestion/                 # 文档分块、DeepSeek抽取、校验、Excel导出
├── scripts/
│   ├── retrieve_tool_info.py       # 原Agent：支持按请求选择图谱
│   ├── tool_registry.py            # 新增：从真实Python工具注册表校验工具名
│   ├── jev_tool_selector.py        # Jev off/shadow/rerank/filter
│   ├── custom_kg_retrievers.py     # 原知识图谱检索器
│   └── utils.py
├── app/                            # 原DeepSeek规划、工具安全等实现
├── ToolsAgent/                     # 真实科学工具服务
├── KG/storage_graph_bge_m3/        # 主BGE-M3图谱及向量索引
├── data/toxin_compound.csv         # 原工具安全检查数据，保留
├── data/toxin_protein.csv
├── data/ingestion_runs/            # 自动产生：上传、Chunk、审核表与缓存
├── import_scitoolkg_neo4j.py       # 可选：手动同步Neo4j
├── requirements.txt
├── requirements_agent.txt
├── requirements_unified.txt
├── example.env                     # 配置模板（已清空API密钥）
└── ToolsAgent/example.env          # ToolsAgent配置模板（已清空API密钥）
```

**没有打包**以前的 `.idea`、`.vscode`、`__pycache__`、旧图谱/备份图谱、`kgqa_test`、测试PDF/Excel、12工具Demo、API缓存、重复问答小脚本及旧测试代码；保留完整核心功能和原有工具实现。

## 2. 安装与配置（Windows / Anaconda）

**建议解压到独立的新目录，不要直接覆盖你原来已经跑通的工程**。若想沿用当前密钥配置，可从你自己的原工程复制 `example.env` 及 `ToolsAgent/example.env`；本压缩包中的相同文件已将 API 密钥字段清空，避免在文件分享中意外泄露。

```cmd
conda activate SciToolAgent
cd /d D:\gitwork\SciToolAgent_Unified_Clean
python -m pip install -r requirements_unified.txt
```

请先确认你此前跑通的 SciToolAgent 环境里已有 PyTorch、CUDA（按设备）、LlamaIndex、BAAI/bge-m3 及 ToolsAgent 所需的科学计算包。此增量 requirements 文件不重新安装所有旧依赖。

打开项目 `example.env`，至少设置：

```ini
OPENAI_API_BASE=https://api.deepseek.com
OPENAI_API_KEY=你的DeepSeek密钥
MODEL_NAME=deepseek-flash
EMBEDDING_MODEL_NAME=BAAI/bge-m3
PERSIST_DIR=KG/storage_graph_bge_m3

DEEPSEEK_API_KEY=你的DeepSeek密钥
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-flash

TYPESAFE_API_KEY=你的Jev密钥
JEV_MODEL=jev-latest
JEV_MODE=filter
JEV_THRESHOLD=0.55
```

模型名称和API基础地址以你此前已成功使用的配置为准。不要把实际密钥提交到Git仓库或上传到公开平台。部分ToolsAgent工具还需要各自的外部服务密钥。

## 3. 启动统一前端

先启动 ToolsAgent（用于计算和实际调用工具；如果只做图谱问答或构图，可以暂不启动）：

```cmd
conda activate SciToolAgent
cd /d D:\gitwork\SciToolAgent_Unified_Clean\ToolsAgent
python main.py
```

打开第二个终端，运行统一页面：

```cmd
conda activate SciToolAgent
cd /d D:\gitwork\SciToolAgent_Unified_Clean
python -m streamlit run app_scitoolagent_with_evidence.py
```

网页左侧选择当前知识图谱，**第一次建议选择“测试图谱”**，程序会从主图谱复制出一个 `KG/storage_graph_bge_m3_workspace`，不会触碰原始图谱。若选择正式图谱，写入前还需要额外确认，入库脚本自动备份。

## 4. 从上传文本到知识图谱

在 **“上传文本与构建图谱”** 页面：

1. 选择本地 `.txt`、`.md`、`.markdown`（可以多选；每份不超过10MB，单批最多20份）。
2. 点击 **① 预览Chunk**，检查段落与章节切割；本步骤不调用API。
3. 点击 **② DeepSeek抽取并生成审核表**，查看 `Tools`、`Triples`、`Evidence` 和 `Review`。系统复用历史相同Chunk的响应缓存。
4. 如有必要，在 `Tools` 或 `Triples` 的网页表格中修改内容，点击“保存网页审核调整”。对 `Review` 中被拒绝的项，只有人工校正后才可正常入库。
5. 点击 **③ 对当前图谱进行增量预检**，确认新增工具、三元组和所需Embedding数量（只读）。
6. 检查对应确认框，点击 **④ 写入选定知识图谱并更新BGE-M3索引**。后续问答会从所选目录**重新读取最新索引**。

**重要：**

- 科学工具信息由 `Tools` 生成 `is a`、`inputs`、`outputs`、`has the functionality that` 等关系；通用科研实体关系可在 `Triples` 中使用受控谓词（如 `uses`、`produces`、`depends on` 等）。
- 工具记录必须包含 `Category, Name, Function, Input, Output, Safety, Source` 七个字段。`Safety=Yes` 在原系统中**表示无需额外安全检查**，并非“已进行安全审计”；原文缺少安全信息时不能随意填 `Yes`。
- 未通过证据校验或字段不足的项目会进入 `Review`，不会自动变为Tools。对于网页人工修改的数据，需要自行核实真实性。
- 已存在工具的 `Tools` 行将被原增量脚本跳过；不会自动覆盖现有工具的描述与Embedding。
- 新的通用事实三元组可写入本地图谱，但目前**只建立图关系，不为每条通用事实建立BGE-M3语义向量**。
- 如果正在更新图谱，其他问答操作应在写入结束后再进行；网页写入使用锁文件防止并发写入同一图谱。
- 当前不支持直接读取 PDF/DOCX；请先转为UTF-8文本或Markdown。图表/扫描PDF识别暂未集成。

## 5. 统一问答

在 **“智能问答”** 页签选择：

**A. 科学工具Agent（BGE-M3 → Jev → DeepSeek → ToolsAgent）**

保留原来的工具链执行。左侧可切换 Jev 的 `off`、`shadow`、`rerank`、`filter`。页面展示实际执行结果及对应一阶工具图谱证据。例：

```text
What is the exact molecular weight of ethanol?
```

只有在 `ToolsAgent/ToolsFuns/*/tool_name_dict.py` **实际注册**的工具才允许进入Planner；从文档提取出的新工具没有Python实现时，虽然可保存其知识关系，但不会冒充可执行函数。

**B. 图谱证据问答（本地KG → DeepSeek）**

用于问新加入实体及关系，不运行任何工具；页面展示具体的三元组和图结构。例：

```text
NameToSMILES 输出什么？
NameToSMILES的输出可以连接到哪些工具的输入？
```

图谱事实问答使用**实体名称/关键词匹配及至多三跳的局部关系扩展**，并非面向任意自然语言的完整语义RAG；如果问题没有明确实体或图谱证据不足，可能无法回答。这条流程**不会调用Jev**，因为Jev目前负责的是工具候选筛选，不是自由文本知识的通用检索。

在 **“图谱浏览”** 可以输入实体名，直观看到关联边。

## 6. Neo4j可视化（可选）

原来的 `import_scitoolkg_neo4j.py` 仍然保留。它从本地 `graph_store.json` 手动同步Neo4j，**不是**在线问答必需的数据库。测试图谱写入后不会自动同步Neo4j。

## 7. 命令行方式仍可使用

```cmd
python text_to_excel_kg.py --input data/raw_documents --preview
python text_to_excel_kg.py --input data/raw_documents --output data/new_tools.xlsx
python incremental_from_excel.py --excel data/new_tools.xlsx --kg-dir KG/storage_graph_bge_m3 --dry-run
```

这些CLI入口保留，方便独立测试和排错。但日常操作无需手工运行它们。

## 8. 已知限制和测试情况

- 本包完成了Python语法检查及**离线**单元级烟雾测试：上传切块、Tool/Triple规范化、已有KG读取、局部图谱检索和增量`--dry-run`。尚未在你的真实密钥、真实GPU及Streamlit浏览器环境执行端到端在线API测试。
- 原始工具函数本身还有第三方密钥、模型和软件依赖，并不因统一前端而自动安装。
- 索引更新脚本保留备份机制，写入中断后请检查备份及索引一致性再恢复。
- 图谱边只能证明文档声明的关系，不代表某工具已成功执行。
- 本包移除了调试数据和旧版索引备份；**你原电脑上的原工程不受影响**。
