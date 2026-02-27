#!/usr/bin/env python3
"""
{skill_name} Document Analyzer with DeepSeek Integration
Cost-optimized analysis of documents and references.

Usage:
    python scripts/{script_name}_analyzer.py summarize "topic"
    python scripts/{script_name}_analyzer.py analyze "topic"
    python scripts/{script_name}_analyzer.py compare "item1 vs item2"
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum

# Add DeepSeek router to path
DEEPSEEK_PATH = Path("/home/ubuntu/skills/deepseek-router/scripts")
sys.path.insert(0, str(DEEPSEEK_PATH))

from task_router import TaskRouter

SKILL_ROOT = Path(__file__).parent.parent

# Document paths - customize for your skill
DOCUMENTS = {{
    # "doc_name": SKILL_ROOT / "references/doc_name.md",
}}


class AnalysisType(Enum):
    SUMMARIZE = "summarize"
    ANALYZE = "analyze"
    COMPARE = "compare"
    EXTRACT = "extract"
    EXPLAIN = "explain"


ANALYSIS_PROMPTS = {{
    AnalysisType.SUMMARIZE: """Create a clear, structured summary.
STRUCTURE: Executive Summary, Key Points, Technical Details, Takeaways.""",
    
    AnalysisType.ANALYZE: """Provide deep analysis of the specified aspect.
STRUCTURE: Overview, How it works, Strengths/Weaknesses, Recommendations.""",
    
    AnalysisType.COMPARE: """Compare and contrast the specified elements.
STRUCTURE: Overview of each, Similarities, Differences, Trade-offs.""",
    
    AnalysisType.EXTRACT: """Extract specific information from the document.
STRUCTURE: Direct quotes, Related information, Implications, Gaps.""",
    
    AnalysisType.EXPLAIN: """Explain the concept clearly.
STRUCTURE: Simple definition, How it works, Why it matters, Example.""",
}}


class {class_name}Analyzer:
    """Cost-optimized document analyzer."""
    
    def __init__(self, force_deepseek: bool = True):
        self.router = TaskRouter()
        self.force_deepseek = force_deepseek
        self.documents = self._load_documents()
    
    def _load_documents(self) -> Dict[str, str]:
        """Load all available documents."""
        loaded = {{}}
        for name, path in DOCUMENTS.items():
            if path.exists():
                try:
                    loaded[name] = path.read_text()
                except Exception as e:
                    loaded[name] = f"[Error loading {{name}}: {{e}}]"
        return loaded
    
    def _get_document_context(
        self,
        doc_names: List[str],
        max_chars: int = 15000
    ) -> str:
        """Get document context, truncating if necessary."""
        contexts = []
        remaining = max_chars
        
        for name in doc_names:
            if name in self.documents:
                doc = self.documents[name]
                if len(doc) <= remaining:
                    contexts.append(f"## {{name.upper()}}\\n{{doc}}")
                    remaining -= len(doc)
                else:
                    truncated = doc[:remaining]
                    contexts.append(f"## {{name.upper()}} (truncated)\\n{{truncated}}\\n[...truncated...]")
                    break
        
        return "\\n\\n".join(contexts)
    
    def analyze(
        self,
        analysis_type: AnalysisType,
        topic: str,
        documents: Optional[List[str]] = None,
        custom_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform analysis on documents."""
        if documents is None:
            documents = list(self.documents.keys())[:2]
        
        system = ANALYSIS_PROMPTS[analysis_type]
        context = self._get_document_context(documents)
        
        if custom_context:
            context += f"\\n\\n## ADDITIONAL CONTEXT\\n{{custom_context}}"
        
        prompt = f"""Based on the following documents, {{analysis_type.value}} the topic: "{{topic}}"

{{context}}

---

Now, {{analysis_type.value}} "{{topic}}" based on the above documents."""
        
        result = self.router.route(
            prompt=prompt,
            system=system,
            force_deepseek=self.force_deepseek,
            max_tokens=3000
        )
        
        result["analysis_type"] = analysis_type.value
        result["documents_used"] = documents
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cumulative usage statistics."""
        return self.router.get_stats()


def main():
    """CLI interface for document analysis."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Analyze documents with DeepSeek cost optimization"
    )
    parser.add_argument(
        "action",
        choices=["summarize", "analyze", "compare", "extract", "explain"],
        help="Analysis action"
    )
    parser.add_argument("topic", help="Topic to analyze")
    parser.add_argument(
        "--docs", "-d",
        nargs="+",
        help="Documents to include"
    )
    parser.add_argument(
        "--stats", "-s",
        action="store_true",
        help="Show usage statistics"
    )
    
    args = parser.parse_args()
    
    analyzer = {class_name}Analyzer()
    
    if args.stats:
        stats = analyzer.get_stats()
        print(json.dumps(stats, indent=2))
        return
    
    analysis_type = AnalysisType(args.action)
    result = analyzer.analyze(
        analysis_type=analysis_type,
        topic=args.topic,
        documents=args.docs
    )
    
    print(f"Analysis Type: {{result['analysis_type'].upper()}}")
    print(f"Documents: {{', '.join(result['documents_used'])}}")
    print(f"Cost: ${{result['cost']:.6f}}")
    print("=" * 60)
    print(f"\\n{{result['content']}}")


if __name__ == "__main__":
    main()
