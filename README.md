# SciToolAgent · 精简整合版（2026-11-11）

本版基于上传的 `SciToolAgent_Unified_Clean.zip` 整理，**保留当前正式图谱、测试图谱及全部核心功能**：

- 文本上传（TXT/Markdown）→ Chunk → DeepSeek实体与关系抽取 → Excel审核
- **增量知识融合**：已有工具差异比较、关系补充、来源人工审核、新工具和三元组入库
- **图谱管理**：浏览、删除单条关系、删除实体及其相关关系，删除前自动备份
- **问答**：BGE-M3 + KG检索 + Jev筛选 + DeepSeek Planner + ToolsAgent计算；图谱证据问答
- 命令行入口与Neo4j手动导入脚本

## 目录

```text
SciToolAgent_Clean_20261111/
├── app_scitoolagent_with_evidence.py   # Streamlit统一前端
├── unified_services.py                # 页面后端与图谱证据查询
├── text_ingestion/                   # 文本抽取、校验、审核Excel
├── kg_fusion/                        # 增量知识融合规划
├── kg_management/                    # 实体/关系删除与备份
├── incremental_from_excel.py         # 实际增量写入图谱
├── fusion_from_excel.py              # 融合命令行
├── graph_manage.py                   # 删除命令行
├── scripts/ + app/                   # BGE-M3/Jev/DeepSeek Agent
├── ToolsAgent/                       # 科研函数与HTTP服务
├── KG/
│   ├── storage_graph_bge_m3/          # 当前正式图谱（保留）
│   └── storage_graph_bge_m3_workspace/# 当前测试图谱（保留）
├── data/                              # 毒性检查数据、融合示例
├── tests/                             # 融合和图谱删除单元测试
├── example.env.template               # 主程序配置模板（无密钥）
└── ToolsAgent/example.env.template    # 工具服务配置模板（无密钥）
```

**保留了当前测试图谱的修改记录**，历史备份因体积较大单独提供，不包含在主运行包。

## 一、配置环境

建议解压到独立目录，先用原来已跑通的Conda环境。

```cmd
conda activate SciToolAgent
cd /d D:\gitwork\SciToolAgent_Clean_20261111
python -m pip install -r requirements_unified.txt
copy example.env.template example.env
copy ToolsAgent\example.env.template ToolsAgent\example.env
```

按需在两个 `example.env` 中填写自己的API密钥及本机路径（文件本身没有打包）。
主配置至少配置 `OPENAI_API_KEY`、`DEEPSEEK_API_KEY`、`TYPESAFE_API_KEY`（若启用Jev）、`PERSIST_DIR`；ToolsAgent还可能需要其他第三方服务凭据。

**不要把 `example.env` 提交到GitHub。** 模型名、Base URL、GPU环境和部分工具的本地软件依赖，以你此前运行成功的环境为准。

## 二、启动

终端A（ToolsAgent服务）：

```cmd
conda activate SciToolAgent
cd /d D:\gitwork\SciToolAgent_Clean_20261111\ToolsAgent
python main.py
```

终端B（Streamlit统一前端）：

```cmd
conda activate SciToolAgent
cd /d D:\gitwork\SciToolAgent_Clean_20261111
python -m streamlit run app_scitoolagent_with_evidence.py
```

## 三、网页使用

1. **上传文本与构建图谱**：预览Chunk → DeepSeek抽取 → 审核Excel → 知识融合预检 → 审核来源补充 → 正式写入。
2. **智能问答**：选择“科学工具Agent”或“图谱证据问答”，Jev支持 `off/shadow/rerank/filter`。
3. **图谱浏览与管理**：查看实体及关系 → 选择关系/实体删除 → 预览影响 → 二次确认 → 自动生成 `KG/<图谱名>_backup_delete_<时间>`。
4. 图谱变更优先在 `storage_graph_bge_m3_workspace`（测试图谱）操作；新文档中的工具如无注册函数，**不会自动变成可执行工具**。

## 四、测试与常用命令

```cmd
python -m unittest discover -s tests -p test_kg_fusion.py -v
python -m unittest discover -s tests -p test_graph_management.py -v
python fusion_from_excel.py --help
python graph_manage.py --help
python incremental_from_excel.py --help
```

手动Neo4j同步：`import_scitoolkg_neo4j.py`（需单独配置服务）。

## 五、精简说明及注意事项

- 已清理 `.git`、IDE配置、`__pycache__`、历史上传缓存Excel、示例PDF与重复脚本。**这些从分发ZIP删除，不影响你本地原项目。**
- 原ZIP里 `ToolsAgent/example.env` 的 `OPENAI_API_KEY` 字段有非空值，因此**没有保留原配置文件**，只提供空密钥模板；请核对本地密钥是否真实，必要时更换。
- 原ZIP根目录没有 `example.env`，新包提供 `example.env.template`，需复制为 `example.env` 后配置。
- 包内保留正式图谱和当前测试图谱，不含删除前备份。历史备份会另行提供归档。
- 本包是精简整理，**没有替你在线重新执行DeepSeek、Jev或GPU工具链**。
- 如果要继续使用原目录的Git提交历史，**不要用新包覆盖原项目的 `.git` 文件夹**；在Git仓库中替换源文件时保留原有 `.git` 即可。
