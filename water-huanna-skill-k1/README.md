# Water-Huanna-Skill-K1

科研数据自动选图、缺项检查与分级复现 Skill。

详细介绍见 [INTRODUCTION.md](INTRODUCTION.md)。

## Quick start

```bash
python scripts/water_huanna.py inspect DATA.csv
python scripts/water_huanna.py recommend DATA.csv --goal "研究问题" --top 5
python scripts/water_huanna.py validate DATA.csv --style-id 79 --target-fidelity l1
python scripts/water_huanna.py render DATA.csv --style-id 79 --output figure.png
```

## Highlights

- 159 个独立 Style ID。
- 自动识别数据结构与科研问题。
- 硬约束过滤和缺项阻断。
- L1、L2、L3 复现等级。
- 地图合规闸门。
- 基础渲染器与专用 R、Python 扩展接口。

## Validation

```bash
python -m unittest discover -s tests -v
python path/to/quick_validate.py .
```

## License and references

仓库不分发来源指南中的参考图。`assets/demos/` 均为本项目原创示意图。
