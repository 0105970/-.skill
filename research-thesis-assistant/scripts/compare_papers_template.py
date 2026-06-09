"""Generate a Markdown comparison template for selected indexed papers."""

from __future__ import annotations

import argparse
from pathlib import Path

from common import (
    MISSING,
    NO_LOCAL_SOURCE,
    PROJECT_ROOT,
    load_index,
    markdown_escape,
    save_text,
    select_documents,
)

DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "paper_comparison.md"
FIELDS = [
    "文献名称",
    "研究对象",
    "核心方法",
    "实验条件",
    "数据或样品",
    "主要贡献",
    "局限性",
    "与光学方向关系",
    "与深度学习方向关系",
    "与实验室条件匹配度",
    "适合大论文 / 小论文",
    "可借鉴点",
]


def render_table(documents: list[dict]) -> str:
    if not documents:
        return NO_LOCAL_SOURCE
    lines = [
        "# 文献对比表",
        "",
        "> 除文献名称外，未由索引直接确认的字段均保留为【待补充】，需核对原文后填写。",
        "",
        "| " + " | ".join(FIELDS) + " |",
        "| " + " | ".join("---" for _ in FIELDS) + " |",
    ]
    for document in documents:
        name = document.get("title") or document.get("file_name") or MISSING
        direction = document.get("direction")
        optics = "所属本地 optics 目录；具体关系【待补充】" if direction == "optics" else MISSING
        deep_learning = (
            "所属本地 deep_learning 目录；具体关系【待补充】"
            if direction == "deep_learning"
            else MISSING
        )
        row = [
            name,
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            optics,
            deep_learning,
            MISSING,
            MISSING,
            MISSING,
        ]
        lines.append("| " + " | ".join(markdown_escape(value) for value in row) + " |")
    lines.extend(
        [
            "",
            "## 文献证据",
            "- 表中仅“文献名称”和所属目录来自本地索引。",
            "",
            "## 推断建议",
            "- 完成原文核对后，再比较方法、实验、贡献、局限和实验室匹配度。",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成多篇本地文献对比表模板。")
    parser.add_argument(
        "papers",
        nargs="*",
        help="索引 ID、文件名、路径或标题关键词；省略时选择全部文献。",
    )
    parser.add_argument("--index", type=Path, default=None, help="自定义索引路径。")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="输出路径。")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = load_index(args.index) if args.index else load_index()
    documents = select_documents(data["documents"], args.papers)
    content = render_table(documents)
    save_text(args.output, content)
    print(f"已保存 {len(documents)} 篇文献的对比模板：{args.output.resolve()}")
    return 0 if documents else 1


if __name__ == "__main__":
    raise SystemExit(main())

