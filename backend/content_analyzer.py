from typing import Dict
from anthropic import Anthropic
from config import Config
import json

class PharmacyContentAnalyzer:
    def __init__(self):
        self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.model = Config.ANTHROPIC_MODEL

    def analyze_topic(self, topic_data: Dict) -> Dict:
        content_text = self._prepare_content(topic_data)

        prompt = f"""Analyze this pharmacy law content and return ONLY valid JSON:

{content_text}

Return this exact structure:
{{
  "main_topic": "topic name",
  "subtopics": ["sub1", "sub2"],
  "content_type": "regulation",
  "key_terms": [{{"term": "name", "definition": "def", "importance": "high"}}],
  "exam_critical_points": [{{"point": "fact", "category": "requirement"}}],
  "question_potential": {{"multiple_choice": "high", "true_false": "medium", "scenario_based": "high", "calculation": "low"}},
  "difficulty_level": "intermediate",
  "regulatory_context": "DEA"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )

            analysis_text = response.content[0].text
            if "```json" in analysis_text:
                analysis_text = analysis_text.split("```json")[1].split("```")[0]

            analysis = json.loads(analysis_text.strip())
            analysis["pages"] = f"{topic_data['start_page']}-{topic_data['end_page']}"
            return analysis

        except Exception as e:
            print(f"Analysis error: {e}")
            return self._fallback_analysis(topic_data)

    def _prepare_content(self, topic_data: Dict) -> str:
        lines = [f"TOPIC: {topic_data['topic']}", ""]
        for page in topic_data['content']:
            if page['headers']:
                lines.append("## " + " / ".join(page['headers']))
            for bullet in page['bullets']:
                lines.append(f"• {bullet}")
            for body_text in page['body']:
                lines.append(body_text)
            lines.append("")
        return "\n".join(lines)[:3000]  # Limit for speed

    def _fallback_analysis(self, topic_data: Dict) -> Dict:
        return {
            "main_topic": topic_data['topic'],
            "subtopics": [],
            "content_type": "mixed",
            "key_terms": [],
            "exam_critical_points": [],
            "question_potential": {"multiple_choice": "medium", "true_false": "medium", "scenario_based": "low", "calculation": "low"},
            "difficulty_level": "intermediate",
            "regulatory_context": "Mixed",
            "pages": f"{topic_data['start_page']}-{topic_data['end_page']}"
        }
