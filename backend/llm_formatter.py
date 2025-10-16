from typing import Dict
from anthropic import Anthropic
from config import Config

class ClaudeFormatter:
    def __init__(self):
        self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.model = Config.ANTHROPIC_MODEL

    def format_topic(self, topic_data: Dict, analysis: Dict) -> str:
        content_text = self._prepare_input(topic_data)

        prompt = f"""Format this pharmacy content as clean markdown with YAML frontmatter:

{content_text}

Use this structure:
---
topic: {analysis['main_topic']}
pages: {analysis['pages']}
difficulty: {analysis['difficulty_level']}
exam_focus: high
---

# {analysis['main_topic']}

[Format with proper headers, bold key terms, use ⚠️ for critical points, 💊 for drugs, ⚖️ for laws]"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except Exception as e:
            print(f"Format error: {e}")
            return self._basic_format(topic_data, analysis)

    def _prepare_input(self, topic_data: Dict) -> str:
        lines = []
        for page in topic_data['content']:
            if page['headers']:
                lines.append("HEADERS: " + " | ".join(page['headers']))
            for bullet in page['bullets']:
                lines.append(f"  • {bullet}")
            for body in page['body']:
                lines.append(f"  {body}")
        return "\n".join(lines)[:2000]

    def _basic_format(self, topic_data: Dict, analysis: Dict) -> str:
        lines = ["---", f"topic: {analysis['main_topic']}", f"pages: {analysis['pages']}", "---", "", f"# {topic_data['topic']}", ""]
        for page in topic_data['content']:
            if page['headers']:
                for h in page['headers']:
                    lines.append(f"## {h}")
            for bullet in page['bullets']:
                lines.append(f"• {bullet}")
            for body in page['body']:
                lines.append(body)
            lines.append("")
        return "\n".join(lines)
