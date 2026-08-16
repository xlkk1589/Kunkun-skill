---
name: water-huanna-skill-k1
description: This skill should be used when users request scientific plotting, automatic chart selection, data-to-figure conversion, reproduction of one of 159 audited SciDraw-style chart cases, publication-quality figure export, or a precise explanation of why a requested figure cannot yet be reproduced and which data or visual specifications are missing.
---

# Water-Huanna-Skill-K1

## Purpose

将用户数据与科研问题映射到 159 个独立 Style ID。优先保证科学解释、统计设计和数据契约，再匹配视觉结构。禁止用近似基础图冒充高保真复现。

## Mandatory workflow

1. 识别用户目标：探索、比较、分布、关联、时间变化、空间格局、效应汇总、组成、网络或组学分析。
2. 读取 `references/data-contracts.md`，检查分析单元、字段角色、重复层级、配对关系、时间、空间参考和缺失机制。
3. 对用户数据运行：

```bash
python scripts/water_huanna.py inspect DATA
python scripts/water_huanna.py recommend DATA --goal "RESEARCH QUESTION" --top 5
```

4. 将首选候选与 `references/styles/NNN.json` 对照。逐项验证必填角色、统计前提、坐标系统、布局与复现风险。
5. 对指定样式运行：

```bash
python scripts/water_huanna.py validate DATA --style-id N --target-fidelity l1
```

6. 仅在验证结果为 `ready` 时绘图。基础图族可运行：

```bash
python scripts/water_huanna.py render DATA --style-id N --output figure.png
```

7. 复杂图族被基础渲染器阻断时，依据该 Style ID 的 `renderer_hint` 编写专用 R 或 Python 实现。保留阻断结果，禁止更换成视觉上相近但科学语义不同的图。
8. 按 `references/fidelity-standard.md` 完成科学正确性、视觉结构和差异报告验收。
9. 涉及地图时，先加载地图合规能力，并执行 `references/map-compliance.md`。缺少合法边界、投影或审核条件时停止生成公开发布版。

## Automatic selection rules

按以下顺序选图：

1. 数据画像：连续、分类、时间、空间、闭合组成、矩阵、网络、树结构或模型输出。
2. 科研问题：比较、分布、关联、预测、时间、空间、效应、组成、流向或组学。
3. 硬约束：字段角色、样本量、重复观测、配对 ID、置信区间、边表、树文件、坐标系。
4. 多目标排序：科学适配优先，其后为数据完备性、可解释性、复现条件和发表场景。
5. 输出首选和两个备选。解释推荐理由、未选原因和误读风险。

在下列典型结构中优先召回：

- `group + value + 原始重复观测`：云雨图、小提琴图或箱线图。
- `time + value + subject`：重复测量时间序列图。
- `estimate + lower + upper`：森林图。
- `source + target + weight`：网络、桑基或和弦图，依据关系与流量语义区分。
- 三列非负且逐行总和固定：三元图。
- `effect + p_value`：火山图或差异图。
- 经纬度、几何或栅格：地图及空间图，进入合规闸门。

## Missing-data gate

无法满足以下条件时停止绘图并报告：

- 缺少原始重复观测、配对 ID、时间字段或统计模型输出。
- 缺少效应量、置信区间、P 值或 FDR。
- 缺少网络边表、流量、Newick 树、叶节点注释或组成约束。
- 缺少坐标系、合法边界、投影、底图来源或地图审核条件。
- L2 缺少字体、精确配色、主题、标注规则或画布规格。
- L3 缺少原代码、原数据、包版本、字体文件、随机种子或输出设备。

缺项报告固定包含：缺少字段或材料、必要性、当前影响、可接受补充示例。

## Fidelity levels

- L1 科学等价：变量映射、数据处理、统计结果和图形语义一致。
- L2 视觉高保真：增加图层、布局、配色、字体、比例、标签和导出规格一致。
- L3 像素级：增加原代码、原数据、依赖版本、字体、随机种子和图形设备一致。

只承诺现有材料允许的最高等级。明确写出限制，禁止将 L1 或 L2 标记为“完美复现”。

## Output contract

每次完整任务优先交付：

- PNG 预览图。
- SVG 或 PDF 矢量图。
- 600 dpi TIFF，期刊需要时生成。
- 完整 R 或 Python 代码及环境信息。
- 数据完整性报告与字段映射。
- 风格推荐评分、备选方案及未选原因。
- 统计方法、样本量、误差类型和图注建议。
- 目标复现等级、已达到等级和差异说明。

## Resources

- `references/chart-catalog.json`：159 项总目录。
- `references/styles/001.json` 至 `159.json`：逐图独立档案。
- `references/data-contracts.md`：字段角色与硬约束。
- `references/fidelity-standard.md`：验收规则。
- `references/map-compliance.md`：地图合规闸门。
- `scripts/water_huanna.py`：数据识别、推荐、验证和基础渲染。
- `scripts/build_catalog.py`：从经审读清单重新生成 159 个档案。
- `tests/`：目录完整性、推荐与阻断测试。
