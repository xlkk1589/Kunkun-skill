#!/usr/bin/env python3
"""Create three original demonstration figures for the skill introduction."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "demos"
OUT.mkdir(parents=True, exist_ok=True)

available = {font.name for font in font_manager.fontManager.ttflist}
for candidate in ("Microsoft YaHei", "DengXian", "SimHei", "DejaVu Sans"):
    if candidate in available:
        plt.rcParams["font.sans-serif"] = [candidate]
        break
plt.rcParams["axes.unicode_minus"] = False

TEAL = "#0B7285"
ORANGE = "#E67700"
PURPLE = "#6741D9"
INK = "#1F2933"
MUTED = "#667085"
GRID = "#D9E2EC"
PAPER = "#F7FAFC"


def save(fig: plt.Figure, name: str) -> None:
    fig.savefig(OUT / f"{name}.png", dpi=220, bbox_inches="tight", facecolor="white")
    fig.savefig(OUT / f"{name}.svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def workflow() -> None:
    fig, ax = plt.subplots(figsize=(12, 4.6))
    ax.set_xlim(0, 12); ax.set_ylim(0, 4.6); ax.axis("off")
    ax.text(0.2, 4.18, "Water-Huanna-Skill-K1  自动选图闭环", fontsize=19, weight="bold", color=INK)
    ax.text(0.2, 3.83, "从数据画像到复现验收，每一步都有硬约束", fontsize=10.5, color=MUTED)
    labels = [
        ("01", "识别数据", "字段类型\n重复层级"),
        ("02", "理解问题", "比较、时间\n空间、效应"),
        ("03", "召回159型", "逐项档案\n候选排序"),
        ("04", "缺项闸门", "阻断误用\n列出缺失"),
        ("05", "渲染验收", "L1、L2、L3\n差异报告"),
    ]
    colors = [TEAL, "#157A8A", "#2A7FA0", PURPLE, ORANGE]
    for index, ((number, title, note), color) in enumerate(zip(labels, colors)):
        x = 0.25 + index * 2.35
        ax.add_patch(plt.Rectangle((x, 1.25), 1.95, 1.85, facecolor=PAPER, edgecolor=color, linewidth=1.8))
        ax.add_patch(plt.Rectangle((x, 2.7), 1.95, 0.4, facecolor=color, edgecolor=color))
        ax.text(x + 0.12, 2.88, number, color="white", fontsize=10, weight="bold", va="center")
        ax.text(x + 0.16, 2.34, title, color=INK, fontsize=13, weight="bold")
        ax.text(x + 0.16, 1.58, note, color=MUTED, fontsize=10.5, linespacing=1.55)
        if index < 4:
            ax.annotate("", xy=(x + 2.28, 2.18), xytext=(x + 1.98, 2.18), arrowprops={"arrowstyle": "->", "color": "#98A2B3", "lw": 1.5})
    ax.text(0.25, 0.55, "核心原则", color=TEAL, fontsize=10, weight="bold")
    ax.text(1.28, 0.55, "科学适配优先于视觉炫技；条件不足时，明确说明缺什么和为什么。", color=INK, fontsize=10.5)
    save(fig, "demo-01-workflow")


def distribution() -> None:
    rng = np.random.default_rng(42)
    groups = {
        "A 低水位": rng.normal(2.4, 0.35, 42),
        "B 过渡期": rng.normal(3.1, 0.48, 46),
        "C 高水位": np.r_[rng.normal(3.8, 0.38, 40), 5.2],
    }
    fig, ax = plt.subplots(figsize=(8.6, 5.6))
    ax.set_facecolor("white")
    values = list(groups.values())
    positions = np.arange(1, 4)
    violin = ax.violinplot(values, positions=positions, widths=0.78, showmedians=False, showextrema=False)
    colors = [TEAL, PURPLE, ORANGE]
    for body, color in zip(violin["bodies"], colors):
        body.set_facecolor(color); body.set_alpha(0.18); body.set_edgecolor(color); body.set_linewidth(1.4)
    box = ax.boxplot(values, positions=positions, widths=0.18, patch_artist=True, showfliers=False,
                     medianprops={"color": "white", "linewidth": 1.7}, whiskerprops={"color": INK}, capprops={"color": INK})
    for patch, color in zip(box["boxes"], colors):
        patch.set_facecolor(color); patch.set_edgecolor(color)
    for index, (group, vals) in enumerate(groups.items(), start=1):
        jitter = rng.normal(index, 0.055, len(vals))
        ax.scatter(jitter, vals, s=20, color=colors[index - 1], alpha=0.56, edgecolors="white", linewidths=0.35)
    ax.set_xticks(positions, list(groups))
    ax.set_ylabel("标准化植被响应")
    ax.set_title("示意图  分布、四分位数与原始观测同时呈现", loc="left", fontsize=15, weight="bold", color=INK, pad=16)
    ax.text(0.02, 0.96, "自动识别 group + value 后，优先推荐云雨图或小提琴图", transform=ax.transAxes, color=MUTED, fontsize=9.5, va="top")
    ax.grid(axis="y", color=GRID, linewidth=0.8, alpha=0.7)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "demo-02-distribution")


def forest() -> None:
    labels = ["水位", "水温", "总氮", "透明度", "风速", "沉水植被覆盖度"]
    estimate = np.array([0.42, -0.17, 0.29, 0.21, -0.08, 0.51])
    lower = np.array([0.18, -0.31, 0.10, 0.03, -0.22, 0.28])
    upper = np.array([0.66, -0.03, 0.48, 0.39, 0.06, 0.74])
    y = np.arange(len(labels))
    colors = np.where(estimate >= 0, TEAL, ORANGE)
    fig, ax = plt.subplots(figsize=(8.8, 5.4))
    for index in range(len(labels)):
        ax.plot([lower[index], upper[index]], [y[index], y[index]], color="#5D6B78", linewidth=2)
        ax.scatter(estimate[index], y[index], s=74, color=colors[index], zorder=3, edgecolors="white", linewidths=0.8)
        ax.text(0.78, y[index], f"{estimate[index]:+.2f}  [{lower[index]:+.2f}, {upper[index]:+.2f}]", va="center", fontsize=9.5, color=MUTED)
    ax.axvline(0, color="#98A2B3", linestyle="--", linewidth=1.2)
    ax.set_yticks(y, labels); ax.invert_yaxis()
    ax.set_xlim(-0.45, 1.18); ax.set_xlabel("标准化效应量及 95% 置信区间")
    ax.set_title("示意图  先验证 estimate、lower、upper，再绘制森林图", loc="left", fontsize=15, weight="bold", color=INK, pad=16)
    ax.grid(axis="x", color=GRID, linewidth=0.8, alpha=0.65)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    save(fig, "demo-03-forest")


if __name__ == "__main__":
    workflow(); distribution(); forest()
    print("created 3 PNG and 3 SVG demo figures")
