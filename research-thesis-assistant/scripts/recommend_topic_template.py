"""Generate five evidence-aware topic recommendation templates."""

from __future__ import annotations

import argparse
from pathlib import Path

from common import MISSING, NO_LOCAL_SOURCE, PROJECT_ROOT, load_index, save_text

DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "topic_recommendations.md"
TOPICS = [
    {
        "title": "微图文阵列制备误差与成像质量关系研究",
        "keywords": ("微图文", "阵列", "光刻", "成像"),
        "problem": "分析结构与制备误差如何影响成像质量，并建立可验证的评价关系。",
        "feasibility": "高度可行",
        "equipment": "直写/灰度光刻、光刻胶、显微镜、表征光路、图像处理。",
        "route": "结构设计与仿真 -> 小规模制备 -> 显微/光学表征 -> 图像质量评价。",
        "deep_learning": "可用于缺陷检测、误差预测或成像质量增强，但应保留传统基线。",
        "paper_type": "适合作为大论文主线，也可拆分工艺或评价小论文。",
        "risk": "设备分辨率、加工一致性与表征精度仍需核实。",
        "rating": "5/5",
    },
    {
        "title": "物理模型约束的光场图像重建方法研究",
        "keywords": ("光场", "重建", "物理", "深度学习"),
        "problem": "在有限采样或退化观测下，利用物理先验提升光场重建可信度。",
        "feasibility": "简化后可行",
        "equipment": "计算仿真、深度学习训练、图像处理、简化光路与成像采集。",
        "route": "建立退化模型 -> 仿真数据训练 -> 公开数据基准 -> 少量实验数据验证。",
        "deep_learning": "作为核心重建模块，并通过物理约束、消融和传统方法对比验证。",
        "paper_type": "适合大论文主线或算法型小论文。",
        "risk": "GPU、真实光场数据来源与仿真到实验的域差异需核实。",
        "rating": "5/5",
    },
    {
        "title": "灰度光刻参数与微结构轮廓质量优化研究",
        "keywords": ("灰度光刻", "微结构", "曝光", "工艺"),
        "problem": "建立曝光与工艺参数对微结构轮廓和一致性的影响规律。",
        "feasibility": "高度可行",
        "equipment": "灰度光刻设备、光刻胶、显微镜及可用表征仪器。",
        "route": "参数矩阵设计 -> 预实验 -> 制备与表征 -> 误差建模 -> 工艺窗口分析。",
        "deep_learning": "可作为参数预测或缺陷分类的辅助模块，不宜在数据量不足时作为核心。",
        "paper_type": "适合工艺型小论文或大论文中的制备章节。",
        "risk": "结构高度、轮廓测量能力和材料参数尚未确认。",
        "rating": "4/5",
    },
    {
        "title": "光学表征图像的去噪与超分辨率联合增强",
        "keywords": ("表征", "图像", "去噪", "超分辨率"),
        "problem": "提升低质量表征图像的可用性，并验证增强是否保留真实结构。",
        "feasibility": "简化后可行",
        "equipment": "显微镜、表征光路、图像采集、图像处理和深度学习训练。",
        "route": "采集退化数据 -> 构建基线 -> 训练增强模型 -> 结构保真与下游评价。",
        "deep_learning": "可作为核心算法，但必须设置物理保真、传统方法和无参考指标限制。",
        "paper_type": "适合作为小论文或大论文算法章节。",
        "risk": "真实干净标签难获得，模型可能产生不存在的细节。",
        "rating": "4/5",
    },
    {
        "title": "液晶光学响应建模与神经网络辅助校正",
        "keywords": ("液晶", "响应", "建模", "校正"),
        "problem": "建立液晶样品输入条件与光学响应之间的模型并评估校正方法。",
        "feasibility": "困难但可尝试",
        "equipment": "液晶材料、光学平台、表征光路、采集设备和计算能力。",
        "route": "确认器件与驱动条件 -> 响应采集 -> 物理/统计建模 -> 网络校正验证。",
        "deep_learning": "可用于响应拟合和误差校正，但依赖稳定、覆盖充分的实验数据。",
        "paper_type": "适合小论文或大论文中的器件建模章节。",
        "risk": "液晶盒、驱动、温控和材料参数未确认，可能需要外部条件。",
        "rating": "3/5",
    },
]


def matching_documents(documents: list[dict], keywords: tuple[str, ...]) -> list[str]:
    matches: list[str] = []
    for document in documents:
        haystack = " ".join(
            str(document.get(field, ""))
            for field in ("file_name", "title", "abstract", "text")
        ).casefold()
        if any(keyword.casefold() in haystack for keyword in keywords):
            matches.append(document.get("file_name", MISSING))
    return matches[:5]


def render_recommendations(documents: list[dict], lab_text: str, scope_text: str) -> str:
    config_status = (
        "已读取 config/lab_profile.md 与 config/research_scope.md。"
        if lab_text.strip() and scope_text.strip()
        else MISSING
    )
    lines = [
        "# 研究选题推荐模板",
        "",
        f"> 配置状态：{config_status}",
        "> 候选题目来自已有研究范围与实验室条件配置；本地文献仅按关键词建立候选关联，使用前必须核对原文。",
        "",
    ]
    for number, topic in enumerate(TOPICS, start=1):
        references = matching_documents(documents, topic["keywords"])
        reference_text = "、".join(references) if references else NO_LOCAL_SOURCE
        lines.extend(
            [
                f"## {number}. {topic['title']}",
                f"1. **题目名称**：{topic['title']}",
                f"2. **研究背景**：依据研究范围配置，该方向属于光学与计算/深度学习交叉候选方向；更具体背景【缺少可靠引用】。",
                f"3. **核心科学或工程问题**：{topic['problem']}",
                f"4. **可参考的本地文献**：{reference_text}",
                f"5. **实验室可行性**：{topic['feasibility']}",
                f"6. **需要的设备和材料**：{topic['equipment']}",
                f"7. **可能的实验路线**：{topic['route']}",
                f"8. **深度学习是否可以参与**：{topic['deep_learning']}",
                f"9. **适合作为大论文还是小论文**：{topic['paper_type']}",
                f"10. **风险点**：{topic['risk']}",
                f"11. **推荐指数**：{topic['rating']}",
                "",
                "### 文献证据",
                f"- 本地候选文献：{reference_text}",
                "",
                "### 推断建议",
                f"- 当前可行性为模板级判断：{topic['feasibility']}。执行前需用真实文献、设备参数和预实验复核。",
                "",
            ]
        )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成五个研究选题推荐模板。")
    parser.add_argument("--index", type=Path, default=None, help="自定义索引路径。")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="输出路径。")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = load_index(args.index) if args.index else load_index()
    lab_path = PROJECT_ROOT / "config" / "lab_profile.md"
    scope_path = PROJECT_ROOT / "config" / "research_scope.md"
    lab_text = lab_path.read_text(encoding="utf-8") if lab_path.exists() else ""
    scope_text = scope_path.read_text(encoding="utf-8") if scope_path.exists() else ""
    content = render_recommendations(data["documents"], lab_text, scope_text)
    save_text(args.output, content)
    print(f"已保存 {len(TOPICS)} 个候选方向：{args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
