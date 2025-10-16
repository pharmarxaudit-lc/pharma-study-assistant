import re
from collections import Counter
from typing import Dict, List


class TextProcessor:
    def clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = text.replace('', '•').replace('', '-')
        text = re.sub(r'\d+\s*$', '', text)
        return text.strip()

    def detect_repeated_elements(self, pages_data: List[Dict]) -> set:
        text_frequency: Counter = Counter()
        for page in pages_data:
            for item in page.get("content", []):
                text = item.get("text", "").strip()
                if len(text) > 5:
                    text_frequency[text] += 1
        threshold = len(pages_data) * 0.3
        return {text for text, count in text_frequency.items() if count > threshold}

    def remove_repeated_elements(self, pages_data: List[Dict], repeated: set) -> List[Dict]:
        cleaned_pages = []
        for page in pages_data:
            cleaned_content = [
                item for item in page.get("content", [])
                if item.get("text", "").strip() not in repeated
            ]
            page["content"] = cleaned_content
            cleaned_pages.append(page)
        return cleaned_pages

    def structure_page(self, page_data: Dict) -> Dict:
        structured = {
            "page": page_data["page"],
            "headers": [],
            "bullets": [],
            "body": []
        }

        for item in page_data.get("content", []):
            text = self.clean_text(item.get("text", ""))
            if not text:
                continue

            if item.get("is_header", False):
                structured["headers"].append(text)
            elif text.startswith(('•', '-', '*', '○')):
                structured["bullets"].append(text.lstrip('•-*○ '))
            else:
                structured["body"].append(text)

        return structured

    def group_by_topics(self, pages_data: List[Dict]) -> List[Dict]:
        topics = []
        current_topic = None

        for page in pages_data:
            structured = self.structure_page(page)

            if structured["headers"]:
                if current_topic and current_topic["content"]:
                    topics.append(current_topic)
                current_topic = {
                    "topic": structured["headers"][0],
                    "start_page": page["page"],
                    "end_page": page["page"],
                    "content": [structured]
                }
            elif current_topic:
                current_topic["end_page"] = page["page"]
                current_topic["content"].append(structured)
            else:
                current_topic = {
                    "topic": f"Section {page['page']}",
                    "start_page": page["page"],
                    "end_page": page["page"],
                    "content": [structured]
                }

        if current_topic and current_topic["content"]:
            topics.append(current_topic)

        return topics

    def process(self, pages_data: List[Dict]) -> List[Dict]:
        repeated = self.detect_repeated_elements(pages_data)
        cleaned_pages = self.remove_repeated_elements(pages_data, repeated)
        topics = self.group_by_topics(cleaned_pages)
        return topics
