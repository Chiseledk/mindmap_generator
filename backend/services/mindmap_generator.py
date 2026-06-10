from typing import Literal, Optional, Tuple

from backend.services.ai_processor import generate_structured_mindmap, optimize_mindmap_with_ai
from backend.services.data_parser import parse_and_validate_mindmap
from backend.services.graph_algorithms import build_algorithmic_mindmap
from backend.utils.schema import MindMap


GenerationSource = Literal["ai_optimized", "ai_direct", "algorithm_only"]


def generate_mindmap_content(source_text: str) -> Tuple[Optional[MindMap], Optional[str], Optional[GenerationSource]]:
    """Generate a mind map with deterministic algorithms, then refine it with AI when available."""
    print("\n--- Mind map generation started ---")

    draft_map = build_algorithmic_mindmap(source_text)
    if not (draft_map.nodes and draft_map.graph and draft_map.graph.nodes):
        return _generate_directly_with_ai(source_text)

    optimized_json = optimize_mindmap_with_ai(source_text, draft_map)
    if optimized_json:
        optimized_map = parse_and_validate_mindmap(optimized_json)
        if optimized_map:
            print("--- Algorithmic draft optimized by AI and graph layout regenerated ---")
            return optimized_map, None, "ai_optimized"
        print("--- AI optimization could not be parsed; using algorithmic draft ---")

    print("--- Using algorithmic draft without AI optimization ---")
    return draft_map, None, "algorithm_only"


def _generate_directly_with_ai(source_text: str) -> Tuple[Optional[MindMap], Optional[str], Optional[GenerationSource]]:
    raw_json = generate_structured_mindmap(source_text)
    if raw_json:
        validated_map = parse_and_validate_mindmap(raw_json)
        if validated_map:
            print("--- AI mind map validated and graph layout generated ---")
            return validated_map, None, "ai_direct"

    return None, "无法从输入文本中提取可用的思维导图结构。", None
