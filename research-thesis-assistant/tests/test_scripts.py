from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PROJECT_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from compare_papers_template import render_table
from ingest_literature import build_index
from recommend_topic_template import render_recommendations
from search_literature import keyword_search, render_results
from summarize_paper_template import render_summary


def sample_document() -> dict:
    return {
        "id": "abc123",
        "file_name": "sample.tex",
        "relative_path": "literature/optics/sample.tex",
        "file_type": "tex",
        "direction": "optics",
        "title": "光场重建测试",
        "abstract": "本文研究光场重建方法。",
        "text": "本文研究光场重建方法。实验使用真实采集数据进行比较。",
        "warnings": [],
    }


class ScriptTests(unittest.TestCase):
    def test_build_index_extracts_tex_and_records_error_free_result(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            optics = root / "literature" / "optics"
            deep_learning = root / "literature" / "deep_learning"
            optics.mkdir(parents=True)
            deep_learning.mkdir(parents=True)
            (optics / "paper.tex").write_text(
                r"""
                \title{基于物理模型的光场重建}
                \begin{abstract}
                本文讨论光场重建的基础方法。
                \end{abstract}
                \section{方法}
                使用可核验的本地文本。
                """,
                encoding="utf-8",
            )

            index = build_index(root)

            self.assertEqual(index["document_count"], 1)
            self.assertEqual(index["error_count"], 0)
            document = index["documents"][0]
            self.assertEqual(document["direction"], "optics")
            self.assertEqual(document["title"], "基于物理模型的光场重建")
            self.assertIn("光场重建", document["abstract"])
            self.assertEqual(document["relative_path"], "literature/optics/paper.tex")

    def test_build_index_keeps_errors_without_stopping(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            optics = root / "literature" / "optics"
            deep_learning = root / "literature" / "deep_learning"
            optics.mkdir(parents=True)
            deep_learning.mkdir(parents=True)
            (optics / "broken.docx").write_bytes(b"not-a-docx")
            (deep_learning / "valid.tex").write_text("有效文献内容", encoding="utf-8")

            index = build_index(root)

            self.assertEqual(index["document_count"], 1)
            self.assertEqual(index["error_count"], 1)
            self.assertEqual(
                index["errors"][0]["path"], "literature/optics/broken.docx"
            )

    def test_keyword_search_returns_real_fragment_and_empty_marker(self) -> None:
        document = sample_document()
        results = keyword_search([document], "光场重建", 3)
        self.assertTrue(results)
        self.assertIn("光场重建", results[0].fragment)
        self.assertIn("sample.tex", render_results(results, "光场重建", "keyword"))
        self.assertEqual(
            render_results([], "不存在的主题", "keyword"),
            "【本地文献库未检索到来源】",
        )

    def test_summary_and_comparison_keep_missing_markers(self) -> None:
        document = sample_document()
        summary = render_summary(document)
        comparison = render_table([document])
        self.assertIn("## 5. 主要结果", summary)
        self.assertIn("【待补充】", summary)
        self.assertIn("光场重建测试", comparison)
        self.assertIn("【待补充】", comparison)

    def test_topic_recommendations_do_not_invent_local_references(self) -> None:
        content = render_recommendations([], "lab", "scope")
        self.assertGreaterEqual(content.count("## "), 5)
        self.assertIn("【本地文献库未检索到来源】", content)
        self.assertIn("高度可行", content)

    def test_index_shape_is_json_serializable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "literature" / "optics").mkdir(parents=True)
            (root / "literature" / "deep_learning").mkdir(parents=True)
            encoded = json.dumps(build_index(root), ensure_ascii=False)
            self.assertIn('"schema_version": 1', encoded)


if __name__ == "__main__":
    unittest.main()
