#!/usr/bin/env python3
"""Build 159 independent chart profiles from the audited source manifest."""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "references" / "source-manifest.json"

FAMILY_RULES = [
    ("parameter_recovery", ["参数恢复"]),
    ("spatial_transcriptomics", ["空间转录组"]),
    ("scatter_pie", ["散点饼图"]),
    ("circular_sample_track", ["样本信息的环形图"]),
    ("dot_pie_composite", ["堆积点图", "内嵌饼图"]),
    ("differential_concordance", ["logfc-fc"]),
    ("swimmer", ["泳道图"]),
    ("forest", ["森林图"]),
    ("phylogenetic_tree", ["系统发育树"]),
    ("ordination", ["pcoa", "nmds", "umap"]),
    ("volcano", ["火山图"]),
    ("manhattan", ["曼哈顿图"]),
    ("sankey_alluvial", ["桑基图", "冲击图"]),
    ("upset_venn", ["upset", "venn"]),
    ("ternary", ["三元图"]),
    ("radar", ["雷达图"]),
    ("raincloud", ["云雨图", "小提琴图+箱式图"]),
    ("heatmap", ["热图"]),
    ("correlation_matrix", ["一维变量", "二维变量", "多维变量"]),
    ("network", ["网络"]),
    ("map", ["地图"]),
    ("time_series", ["时序图"]),
    ("ridge", ["山脊图"]),
    ("density_contour", ["等高线", "密度图"]),
    ("violin", ["小提琴图"]),
    ("boxplot", ["箱线图", "箱式图"]),
    ("bubble", ["气泡图"]),
    ("scatter", ["散点图"]),
    ("circular_bar", ["环状柱形图"]),
    ("bar", ["柱形图", "柱状图"]),
    ("line", ["折线图", "点线图", "趋势线", "平滑曲线", "线条路径"]),
    ("chord", ["和弦图", "circos"]),
]

ROLE_MAP = {
    "radar": ["sample", "axis", "value"],
    "raincloud": ["group", "value"],
    "violin": ["group", "value"],
    "boxplot": ["group", "value"],
    "heatmap": ["row", "column", "value"],
    "correlation_matrix": ["sample", "numeric_features"],
    "volcano": ["feature", "effect", "p_value"],
    "differential_concordance": ["feature", "effect_x", "effect_y"],
    "ordination": ["sample", "feature_matrix", "group"],
    "phylogenetic_tree": ["newick_tree", "tip_annotation"],
    "ternary": ["component_a", "component_b", "component_c"],
    "swimmer": ["subject", "start", "end", "event"],
    "forest": ["term", "estimate", "lower", "upper"],
    "map": ["longitude", "latitude", "crs"],
    "network": ["source", "target", "weight"],
    "sankey_alluvial": ["source", "target", "weight"],
    "upset_venn": ["set", "member"],
    "time_series": ["time", "value", "group"],
    "bar": ["category", "value"],
    "circular_bar": ["category", "value"],
    "bubble": ["x", "y", "size"],
    "scatter": ["x", "y"],
    "line": ["x", "y"],
    "ridge": ["group", "value"],
    "density_contour": ["x", "y"],
    "manhattan": ["feature", "position", "p_value", "group"],
    "chord": ["source", "target", "weight"],
    "spatial_transcriptomics": ["spatial_x", "spatial_y", "expression", "sample"],
    "scatter_pie": ["x", "y", "component", "proportion"],
    "parameter_recovery": ["parameter", "truth", "estimate", "lower", "upper"],
    "circular_sample_track": ["sample", "annotation_track"],
    "dot_pie_composite": ["category", "value", "component", "proportion"],
}

QUESTION_MAP = {
    "radar": "比较多个指标构成的样本或组别轮廓",
    "raincloud": "同时检查组间分布、四分位数与个体观测",
    "heatmap": "识别矩阵模式、聚类结构或关联强度",
    "volcano": "筛选同时满足效应阈值和显著性阈值的特征",
    "forest": "比较效应量及其不确定性",
    "map": "展示样点或区域属性的空间分布",
    "network": "刻画实体间关系及关联强度",
    "time_series": "比较随时间变化的水平、趋势与不确定性",
    "ternary": "比较三类闭合组成的相对结构",
    "ordination": "探索高维样本在低维空间中的结构",
}

PACKAGE_RULES = {
    "fmsb": "R:fmsb",
    "ggiraphExtra": "R:ggiraphExtra",
    "ggradar": "R:ggradar",
    "gghalves": "R:gghalves",
    "ggdist": "R:ggdist",
    "corrplot": "R:corrplot",
    "ComplexHeatmap": "R:ComplexHeatmap",
    "pheatmap": "R:pheatmap",
    "GGally": "R:GGally",
    "linkET": "R:linkET",
    "geom_tile": "R:ggplot2",
    "seaborn": "Python:matplotlib",
}

EXCEPTIONS = {
    56: "differential_concordance", 57: "differential_concordance",
    58: "differential_concordance", 59: "differential_concordance",
    76: "swimmer", 77: "swimmer", 78: "swimmer",
    79: "forest", 80: "forest", 81: "forest",
    104: "dot_pie_composite", 127: "circular_sample_track",
    130: "spatial_transcriptomics", 157: "heatmap",
    158: "scatter_pie", 159: "parameter_recovery",
}

SOURCE_CATEGORY_ERRORS = {76, 77, 78, 79, 80, 81, 130}
AMBIGUOUS_IDS = {35, 36, 52, 53, 56, 57, 58, 59, 72, 73, 83, 84, 89, 90, 91, 92, 93, 97, 98, 119, 120, 121}


def normalize(text: str) -> str:
    return unicodedata.normalize("NFKC", text).strip()


def family_for(item: dict) -> str:
    if item["id"] in EXCEPTIONS:
        return EXCEPTIONS[item["id"]]
    text = normalize(item["title"]).lower()
    for family, terms in FAMILY_RULES:
        if any(term.lower() in text for term in terms):
            return family
    return "manual"


def roles_for(family: str, title: str) -> tuple[list[str], list[str]]:
    required = list(ROLE_MAP.get(family, ["x", "y"]))
    optional = ["label", "color", "shape", "order"]
    if "分组" in title and "group" not in required:
        required.append("group")
    if "分面" in title and "facet" not in required:
        required.append("facet")
    if "误差" in title:
        required += [role for role in ("error_lower", "error_upper") if role not in required]
    if "配对" in title and "subject" not in required:
        required.append("subject")
    if any(term in title for term in ("显著性", "检验", "ANOVA", "Tukey", "LSD", "Dunnett")):
        optional += ["p_value", "adjusted_p", "significance_label"]
    return sorted(set(required)), sorted(set(optional) - set(required))


def stats_for(family: str, title: str) -> list[str]:
    out = []
    if family in {"raincloud", "violin", "ridge", "density_contour"}:
        out.append("kernel_density")
    if family == "correlation_matrix":
        out.append("correlation_method_and_missing_policy")
    if family == "forest":
        out.append("confidence_interval")
    if family == "ordination":
        out.append("distance_or_embedding_parameters")
    if "线性" in title:
        out.append("linear_model")
    if "对数" in title:
        out.append("log_transform_or_log_model")
    if "层次聚类" in title:
        out.append("distance_and_linkage")
    for token, name in [
        ("LMM-ANOVA", "linear_mixed_model_anova"),
        ("重复测量", "repeated_measures_anova"),
        ("Tukey", "tukey_multiple_comparison"),
        ("LSD", "lsd_posthoc"),
        ("Dunnett", "dunnett_posthoc"),
        ("RCS", "restricted_cubic_spline"),
        ("GSEA", "gene_set_enrichment_analysis"),
    ]:
        if token.lower() in title.lower():
            out.append(name)
    return sorted(set(out))


def renderer_for(family: str, title: str) -> dict:
    engine = "python"
    if "R版" in title or "包" in title or family in {"phylogenetic_tree", "ternary", "chord"}:
        engine = "r"
    if "Python版" in title:
        engine = "python"
    coord = "cartesian"
    if family in {"radar", "circular_bar", "circular_sample_track", "chord"} or "环" in title or "扇形" in title:
        coord = "polar"
    elif family == "map":
        coord = "geo"
    elif family == "ternary":
        coord = "ternary"
    elif family in {"network", "phylogenetic_tree", "sankey_alluvial"}:
        coord = "graph"
    layout = []
    for token, value in [("分面", "facet"), ("边缘", "marginal"), ("内嵌", "inset"), ("组合", "composite"), ("+", "composite")]:
        if token in title:
            layout.append(value)
    package = None
    for token, value in PACKAGE_RULES.items():
        if token.lower() in title.lower():
            package = value
            break
    return {"engine": engine, "coordinate": coord, "layout": sorted(set(layout)), "package": package}


def risks_for(family: str, title: str, width: int | None, height: int | None, ambiguous: bool) -> list[str]:
    risks = []
    if family in {"map", "network", "phylogenetic_tree", "sankey_alluvial", "chord"} or "环" in title:
        risks.append("layout_sensitive")
    if any(x in title for x in ("渐变", "彩虹", "配色")):
        risks.append("color_scale_sensitive")
    if any(x in title for x in ("误差", "显著性", "检验", "ANOVA", "Tukey", "LSD", "Dunnett")):
        risks.append("statistical_annotation_required")
    if any(x in title for x in ("分面", "内嵌", "多层", "外围", "外圈", "+")):
        risks.append("alignment_and_clipping")
    if "动态交互" in title:
        risks.append("static_export_loses_interaction")
    if width and height and (width / height > 2 or width / height < 0.5):
        risks.append("extreme_aspect_ratio")
    if ambiguous:
        risks.append("title_insufficient_use_style_id")
    if family == "map":
        risks += ["boundary_provenance_required", "projection_required", "map_compliance_gate"]
    if family in {"volcano", "forest", "ordination", "parameter_recovery"}:
        risks.append("model_outputs_required")
    return sorted(set(risks))


def layers_for(family: str, title: str) -> list[str]:
    base = {
        "radar": ["angular_axes", "radial_scale", "series_path"],
        "raincloud": ["density", "box_summary", "raw_points"],
        "violin": ["density", "median_or_box", "raw_points_optional"],
        "boxplot": ["box", "median", "whiskers", "outliers_optional"],
        "heatmap": ["matrix_tiles", "color_legend"],
        "correlation_matrix": ["correlation_matrix", "color_or_glyph_legend"],
        "volcano": ["effect_significance_points", "threshold_lines", "feature_labels_optional"],
        "forest": ["point_estimates", "confidence_intervals", "null_reference"],
        "map": ["compliant_boundary_or_basemap", "spatial_marks", "legend"],
        "network": ["nodes", "weighted_edges", "labels_optional"],
        "sankey_alluvial": ["nodes_or_strata", "weighted_flows", "labels"],
        "time_series": ["time_path", "observations", "uncertainty_optional"],
        "bar": ["bars", "axis", "labels_optional"],
        "circular_bar": ["polar_bars", "radial_scale", "labels"],
        "scatter": ["points", "fit_optional", "uncertainty_optional"],
        "bubble": ["points", "area_scale", "color_scale_optional"],
        "ridge": ["stacked_density", "group_labels"],
        "density_contour": ["density_estimate", "contours_or_fill", "legend"],
        "phylogenetic_tree": ["tree_branches", "tip_labels", "annotation_tracks_optional"],
        "ternary": ["ternary_axes", "composition_points", "group_legend_optional"],
        "ordination": ["embedding_points", "group_encoding", "marginals_optional"],
        "chord": ["sectors", "weighted_chords", "outer_track_optional"],
        "parameter_recovery": ["truth_reference", "estimates", "uncertainty_intervals"],
    }.get(family, ["primary_marks", "scales", "annotations_optional"])
    layers = list(base)
    for token, layer in [
        ("分面", "facets"), ("误差", "error_bars"), ("显著性", "significance_annotations"),
        ("背景", "background_encoding"), ("外圈", "outer_track"), ("外围", "outer_track"),
        ("边缘", "marginal_distribution"), ("内嵌", "inset_panel"), ("网络", "network_overlay"),
        ("饼图", "pie_glyphs"), ("柱形图", "bar_layer"), ("热图", "heatmap_layer"),
    ]:
        if token in title:
            layers.append(layer)
    return sorted(set(layers))


def acceptance_for(family: str, title: str) -> list[str]:
    checks = ["required_roles_resolved", "scientific_question_matches", "canvas_aspect_checked"]
    if family in {"forest", "volcano", "parameter_recovery"} or any(token in title for token in ("ANOVA", "检验", "显著性", "误差")):
        checks.append("statistics_recomputed_or_verified")
    if family in {"network", "sankey_alluvial", "chord", "phylogenetic_tree"}:
        checks.append("layout_and_node_order_recorded")
    if family == "map":
        checks += ["boundary_and_projection_recorded", "map_compliance_passed"]
    if any(token in title for token in ("分面", "内嵌", "外圈", "外围", "+")):
        checks.append("panel_alignment_checked")
    return sorted(set(checks))


def aliases_for(item: dict, family: str) -> list[str]:
    title = normalize(item["title"])
    stripped = re.sub(r"[（(].*?(?:包|库|R版|Python版).*?[）)]", "", title, flags=re.I)
    aliases = {title, stripped.strip(), family, f"style-{item['id']:03d}", f"id:{item['id']:03d}"}
    return sorted(x for x in aliases if x)


def build(manifest_path: Path = DEFAULT_MANIFEST) -> list[dict]:
    items = json.loads(manifest_path.read_text(encoding="utf-8"))
    profiles = []
    styles_dir = ROOT / "references" / "styles"
    styles_dir.mkdir(parents=True, exist_ok=True)
    for item in items:
        family = family_for(item)
        required, optional = roles_for(family, item["title"])
        profile = {
            "id": item["id"],
            "title": normalize(item["title"]),
            "family": family,
            "source_category": item.get("category"),
            "source_category_audited": item["id"] not in SOURCE_CATEGORY_ERRORS,
            "scientific_question": QUESTION_MAP.get(family, "依据字段角色、研究设计和目标解释该图形编码"),
            "required_roles": required,
            "optional_roles": optional,
            "statistical_requirements": stats_for(family, item["title"]),
            "renderer_hint": renderer_for(family, item["title"]),
            "visual_layers": layers_for(family, item["title"]),
            "acceptance_checks": acceptance_for(family, item["title"]),
            "reference_canvas": {"width": item.get("width"), "height": item.get("height")},
            "fidelity_risks": risks_for(family, item["title"], item.get("width"), item.get("height"), item["id"] in AMBIGUOUS_IDS),
            "aliases": aliases_for(item, family),
            "fidelity_policy": {
                "l1_scientific_equivalence": "requires all required_roles and statistical prerequisites",
                "l2_visual_high_fidelity": "also requires theme, fonts, exact annotations and layout parameters",
                "l3_pixel_level": "also requires original code, data, versions, fonts, random seeds and output device",
            },
        }
        profiles.append(profile)
        (styles_dir / f"{item['id']:03d}.json").write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "references" / "chart-catalog.json").write_text(json.dumps(profiles, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return profiles


if __name__ == "__main__":
    profiles = build()
    print(json.dumps({"profiles": len(profiles), "ids": [profiles[0]["id"], profiles[-1]["id"]]}, ensure_ascii=False))
