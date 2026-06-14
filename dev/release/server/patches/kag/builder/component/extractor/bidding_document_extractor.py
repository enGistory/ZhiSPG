# -*- coding: utf-8 -*-
import re
from typing import List, Type

from kag.builder.model.chunk import Chunk
from kag.builder.model.sub_graph import SubGraph
from kag.common.utils import generate_hash_id
from kag.interface import ExtractorABC
from knext.common.base.runnable import Input, Output
from knext.schema.client import CHUNK_TYPE


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _dedupe_key(text: str) -> str:
    text = _clean_text(text).lower()
    text = re.sub(r"^[（(]?\s*[\d一二三四五六七八九十]+[）).、]\s*", "", text)
    text = re.sub(r"[\s，,。；;：:、（）()【】\[\]《》\"'“”‘’]", "", text)
    return text


def _project_name(chunk: Chunk) -> str:
    name = re.sub(r"#.*$", "", chunk.name or "").strip()
    return name or "未命名项目"


def _sentences(text: str) -> List[str]:
    normalized = re.sub(r"[ \t]+", " ", text or "")
    parts = re.split(r"[\n。；;]", normalized)
    return [_clean_text(part) for part in parts if _clean_text(part)]


def _matches(text: str, keywords: List[str], limit: int = 6) -> List[str]:
    matched = []
    for sentence in _sentences(text):
        if any(keyword in sentence for keyword in keywords):
            matched.append(sentence[:500])
        if len(matched) >= limit:
            break
    return matched


def _meaningful_sentences(text: str, keywords: List[str], limit: int = 12) -> List[str]:
    skip_words = ["目录", "第 页共 页", "合 计", "小计", "备注", "序号"]
    rows = []
    for sentence in _sentences(text):
        if len(sentence) < 8:
            continue
        if any(word in sentence for word in skip_words) and not any(
            keyword in sentence for keyword in keywords
        ):
            continue
        if any(keyword in sentence for keyword in keywords):
            rows.append(sentence[:500])
        if len(rows) >= limit:
            break
    return list(dict.fromkeys(rows))


def _amounts(text: str, limit: int = 5) -> List[str]:
    values = re.findall(r"(?:人民币)?\s*\d+(?:\.\d+)?\s*(?:万元|元)", text or "")
    return list(dict.fromkeys([_clean_text(value) for value in values]))[:limit]


def _regulations(text: str, limit: int = 6) -> List[str]:
    values = re.findall(r"《[^》]{2,60}》", text or "")
    for sentence in _sentences(text):
        if any(keyword in sentence for keyword in ["法律", "法规", "条例", "办法", "规定"]):
            values.append(sentence[:300])
    return list(dict.fromkeys([_clean_text(value) for value in values]))[:limit]


def _units(text: str, limit: int = 6) -> List[str]:
    units = []
    patterns = [
        r"(?:招标人|建设单位|采购人|发包人|投标人|施工单位|监理单位|设计单位)[：:]\s*([^\n，,；;。]{2,80})",
        r"([^\n，,；;。]{2,80}(?:有限公司|集团|委员会|局|中心|单位|公司))",
    ]
    for pattern in patterns:
        units.extend(re.findall(pattern, text or ""))
    ignored = ["须知", "资格", "文件", "格式", "目录", "正文"]
    cleaned = [
        _clean_text(unit)
        for unit in units
        if _clean_text(unit) and not any(word in _clean_text(unit) for word in ignored)
    ]
    return list(dict.fromkeys(cleaned))[:limit]


def _add_chunk(graph: SubGraph, chunk: Chunk):
    graph.add_node(
        id=chunk.id,
        name=chunk.name,
        label=CHUNK_TYPE,
        properties={
            "id": chunk.id,
            "name": chunk.name,
            "content": f"{chunk.name}\n{chunk.content}",
            **chunk.kwargs,
        },
    )
    graph.id = chunk.id


@ExtractorABC.register("tender_document_extractor")
class TenderDocumentExtractor(ExtractorABC):
    @property
    def input_types(self) -> Type[Input]:
        return Chunk

    @property
    def output_types(self) -> Type[Output]:
        return SubGraph

    def _invoke(self, input: Input, **kwargs) -> List[Output]:
        chunk = input
        text = f"{chunk.name}\n{chunk.content}"
        project = _project_name(chunk)
        graph = SubGraph([], [])

        amounts = _amounts(text)
        regulations = _regulations(text)
        units = _units(text)
        project_code_match = re.search(
            r"(?:项目编号|招标编号|标段编号)[：:\s]*([A-Za-z0-9_\-（）()号包]+)",
            text or "",
        )
        project_code = _clean_text(project_code_match.group(1) if project_code_match else "")
        scoring_lines = _meaningful_sentences(
            text,
            ["评分", "得分", "分值", "评审因素", "评分标准", "评标办法", "加分", "扣分"],
            limit=10,
        )

        has_document_info = bool(project_code or amounts or regulations or units)
        if not has_document_info and not scoring_lines:
            return []

        _add_chunk(graph, chunk)

        doc_id = generate_hash_id(f"tender-document::{project}")
        if has_document_info:
            graph.add_node(
                id=doc_id,
                name=project,
                label="TenderDocumentInfo",
                properties={
                    "content": _clean_text(chunk.content)[:1000],
                    "projectName": project,
                    "projectCode": project_code,
                    "unit": "；".join(units),
                    "amount": "；".join(amounts),
                    "regulation": "；".join(regulations),
                },
            )
            graph.add_edge(doc_id, "TenderDocumentInfo", "sourceChunk", chunk.id, CHUNK_TYPE)

        seen_item_ids = set()
        for line in scoring_lines:
            item_id = generate_hash_id(f"tender-scoring::{doc_id}::{_dedupe_key(line)}")
            if item_id in seen_item_ids:
                continue
            seen_item_ids.add(item_id)
            graph.add_node(
                id=item_id,
                name=line[:80],
                label="TenderScoringItem",
                properties={
                    "itemName": line[:120],
                    "scoringPoint": line,
                    "regulation": "；".join(regulations),
                    "amount": "；".join(amounts),
                    "unit": "；".join(units),
                    "content": line,
                },
            )
            graph.add_edge(item_id, "TenderScoringItem", "sourceChunk", chunk.id, CHUNK_TYPE)
            if has_document_info:
                graph.add_edge(doc_id, "TenderDocumentInfo", "hasScoringItem", item_id, "TenderScoringItem")
                graph.add_edge(item_id, "TenderScoringItem", "belongsTo", doc_id, "TenderDocumentInfo")

        return [graph]


@ExtractorABC.register("bid_document_extractor")
class BidDocumentExtractor(ExtractorABC):
    @property
    def input_types(self) -> Type[Input]:
        return Chunk

    @property
    def output_types(self) -> Type[Output]:
        return SubGraph

    def _invoke(self, input: Input, **kwargs) -> List[Output]:
        chunk = input
        text = f"{chunk.name}\n{chunk.content}"
        project = _project_name(chunk)
        graph = SubGraph([], [])

        units = _units(text)
        features = _meaningful_sentences(text, ["项目特色", "技术方案", "先进", "亮点", "优势"], limit=6)
        design_parts = _meaningful_sentences(
            text,
            ["施工组织设计", "施组", "施工方案", "进度计划", "质量保证", "安全文明", "环保措施"],
            limit=10,
        )

        if not units and not features and not design_parts:
            return []

        _add_chunk(graph, chunk)

        doc_id = generate_hash_id(f"bid-document::{project}")
        graph.add_node(
            id=doc_id,
            name=project,
            label="BidDocumentInfo",
            properties={
                "content": _clean_text(chunk.content)[:1000],
                "projectFeature": "；".join(features),
                "technicalAdvancement": "；".join([line for line in features if "先进" in line or "技术方案" in line]),
                "constructionDesignSplit": "；".join(design_parts),
                "unit": "；".join(units),
            },
        )
        graph.add_edge(doc_id, "BidDocumentInfo", "sourceChunk", chunk.id, CHUNK_TYPE)

        seen_part_ids = set()
        for line in design_parts:
            part_id = generate_hash_id(f"construction-design::{doc_id}::{_dedupe_key(line)}")
            if part_id in seen_part_ids:
                continue
            seen_part_ids.add(part_id)
            graph.add_node(
                id=part_id,
                name=line[:80],
                label="ConstructionDesignPart",
                properties={
                    "partName": line[:120],
                    "content": line,
                    "unit": "；".join(units),
                },
            )
            graph.add_edge(part_id, "ConstructionDesignPart", "sourceChunk", chunk.id, CHUNK_TYPE)
            graph.add_edge(doc_id, "BidDocumentInfo", "hasConstructionDesign", part_id, "ConstructionDesignPart")
            graph.add_edge(part_id, "ConstructionDesignPart", "belongsTo", doc_id, "BidDocumentInfo")

        return [graph]
