"""Search local literature with keyword matching or TF-IDF."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from common import NO_LOCAL_SOURCE, load_index, normalize_space, split_fragments


@dataclass
class SearchResult:
    score: float
    document: dict
    fragment: str
    keywords: list[str]


def query_terms(query: str) -> list[str]:
    """Extract useful Chinese sequences and alphanumeric words."""
    raw = re.findall(r"[\u4e00-\u9fff]{2,}|[A-Za-z0-9_-]{2,}", query)
    terms: list[str] = []
    for token in raw:
        lowered = token.casefold()
        if lowered not in terms:
            terms.append(lowered)
        if re.fullmatch(r"[\u4e00-\u9fff]{4,}", token):
            for size in (2, 3):
                terms.extend(
                    token[index : index + size]
                    for index in range(len(token) - size + 1)
                    if token[index : index + size] not in terms
                )
    return terms


def keyword_search(documents: list[dict], query: str, limit: int) -> list[SearchResult]:
    """Rank text fragments by transparent term occurrence counts."""
    terms = query_terms(query)
    results: list[SearchResult] = []
    for document in documents:
        for fragment in split_fragments(document.get("text", "")):
            lowered = fragment.casefold()
            counts = Counter({term: lowered.count(term) for term in terms})
            matched = [term for term, count in counts.items() if count]
            score = float(sum(counts.values()))
            if score:
                results.append(SearchResult(score, document, fragment, matched))
    return sorted(results, key=lambda item: item.score, reverse=True)[:limit]


def tfidf_search(documents: list[dict], query: str, limit: int) -> list[SearchResult]:
    """Rank fragments with character n-gram TF-IDF for Chinese-friendly search."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    rows: list[tuple[dict, str]] = []
    for document in documents:
        rows.extend((document, fragment) for fragment in split_fragments(document.get("text", "")))
    if not rows:
        return []
    corpus = [fragment for _, fragment in rows]
    vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(2, 4), min_df=1)
    matrix = vectorizer.fit_transform(corpus + [query])
    scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
    terms = query_terms(query)
    ranked = scores.argsort()[::-1]
    results: list[SearchResult] = []
    for index in ranked:
        if scores[index] <= 0:
            continue
        document, fragment = rows[int(index)]
        matches = [term for term in terms if term in fragment.casefold()]
        results.append(SearchResult(float(scores[index]), document, fragment, matches))
        if len(results) >= limit:
            break
    return results


def render_results(results: list[SearchResult], query: str, method: str) -> str:
    if not results:
        return NO_LOCAL_SOURCE
    lines = [f"# 本地文献检索结果", "", f"- 查询：{query}", f"- 方法：{method}", ""]
    for number, result in enumerate(results, start=1):
        document = result.document
        keywords = "、".join(result.keywords) if result.keywords else "语义相似片段"
        lines.extend(
            [
                f"## {number}. {document.get('file_name', '【待补充】')}",
                f"- 所属文件夹：{document.get('direction', '【待补充】')}",
                f"- 文件路径：{document.get('relative_path', '【待补充】')}",
                f"- 命中关键词：{keywords}",
                f"- 相关度：{result.score:.4f}",
                f"- 相关片段：{normalize_space(result.fragment)}",
                "- 简短解释：该片段与查询词存在直接命中或文本相似性；是否支持具体论断仍需核对原文上下文。",
                "",
            ]
        )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="检索本地文献索引。")
    parser.add_argument("query", help="问题或关键词。")
    parser.add_argument("--index", type=Path, default=None, help="自定义索引路径。")
    parser.add_argument("--limit", type=int, default=5, help="返回片段数量。")
    parser.add_argument(
        "--method",
        choices=("keyword", "tfidf"),
        default="tfidf",
        help="检索方法，默认 tfidf。",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = load_index(args.index) if args.index else load_index()
    documents = data["documents"]
    search = tfidf_search if args.method == "tfidf" else keyword_search
    results = search(documents, args.query, max(1, args.limit))
    print(render_results(results, args.query, args.method))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
