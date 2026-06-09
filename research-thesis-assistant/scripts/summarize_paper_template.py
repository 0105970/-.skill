"""Generate a cautious Markdown summary template for one indexed paper."""

from __future__ import annotations

import argparse
from pathlib import Path

from common import MISSING, load_index, save_text, select_documents


def render_summary(document: dict) -> str:
    """Render known metadata and leave unsupported analytical fields explicit."""
    title = document.get("title") or MISSING
    abstract = document.get("abstract") or MISSING
    if abstract == MISSING:
        abstract_note = MISSING
    else:
        abstract_note = f"候选摘要（需核对原文）：{abstract}"
    warnings = "；".join(document.get("warnings", [])) or "无"
    return f"""# 单篇文献结构化总结

> 本模板仅填入索引可确认的信息。正文分析项必须回到原文核对，不得据此虚构结论。

## 1. 文献信息
- 索引 ID：{document.get("id", MISSING)}
- 文件名：{document.get("file_name", MISSING)}
- 文件路径：{document.get("relative_path", MISSING)}
- 所属方向：{document.get("direction", MISSING)}
- 文件类型：{document.get("file_type", MISSING)}
- 可能的标题：{title}
- 可能的摘要：{abstract_note}
- 提取警告：{warnings}

## 2. 研究问题
{MISSING}

## 3. 核心方法
{MISSING}

## 4. 实验设计
{MISSING}

## 5. 主要结果
{MISSING}

## 6. 创新点
{MISSING}

## 7. 局限性
{MISSING}

## 8. 与我的研究方向的关系
### 文献证据
{MISSING}

### 推断建议
{MISSING}

## 9. 与实验室条件的匹配度
- 可行性等级：{MISSING}
- 已满足条件：{MISSING}
- 待核实条件：{MISSING}
- 缺失条件：{MISSING}

## 10. 可作为毕业论文或小论文参考的部分
- 适合毕业论文：{MISSING}
- 适合小论文：{MISSING}
- 可借鉴内容：{MISSING}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成单篇文献中文总结模板。")
    parser.add_argument("paper", help="索引 ID、文件名、路径或标题关键词。")
    parser.add_argument("--index", type=Path, default=None, help="自定义索引路径。")
    parser.add_argument("--output", type=Path, default=None, help="保存 Markdown 的路径。")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = load_index(args.index) if args.index else load_index()
    matches = select_documents(data["documents"], [args.paper])
    if not matches:
        print("【本地文献库未检索到来源】")
        return 1
    if len(matches) > 1:
        names = "、".join(document["file_name"] for document in matches[:10])
        print(f"匹配到多篇文献，请使用更精确的文件名或索引 ID：{names}")
        return 2
    content = render_summary(matches[0])
    if args.output:
        save_text(args.output, content)
        print(f"已保存：{args.output.resolve()}")
    else:
        print(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

