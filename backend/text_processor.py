import json
import logging
import re
from collections import Counter
from typing import Dict, List, Optional

from anthropic import Anthropic
from config import Config


class TextProcessor:
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.client: Optional[Anthropic] = None
        if Config.ANTHROPIC_API_KEY:
            self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
            self.model = Config.ANTHROPIC_MODEL
        # Use provided logger or create default
        self.logger = logger or logging.getLogger(__name__)
    def clean_text(self, text: str) -> str:
        # Only remove flowchart artifacts if the text has the specific pattern
        # Pattern: repeated sequences of dash-bullet-dash between single characters
        # Example: -•-D-•-o-•-m-•-a-•-n-•-i-•-
        if re.search(r'(-•-[A-Za-z0-9\s]){3,}', text):
            # Remove the -•- separators between characters
            text = re.sub(r'-•-', '', text)

        # Normalize whitespace (collapse multiple spaces/newlines)
        text = re.sub(r'\s+', ' ', text)

        # Remove trailing page numbers
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

    def group_by_topics(self, pages_data: List[Dict], max_pages_per_topic: int = 3) -> List[Dict]:
        """
        Group pages into topics with better control over topic size.

        Args:
            pages_data: List of page dictionaries
            max_pages_per_topic: Maximum pages to include in a single topic (default: 3)
        """
        topics = []
        current_topic = None
        pages_in_current_topic = 0

        for page in pages_data:
            structured = self.structure_page(page)

            # Create new topic if we find a header OR if current topic has too many pages
            should_create_new_topic = (
                structured["headers"] or
                (current_topic and pages_in_current_topic >= max_pages_per_topic) or
                current_topic is None
            )

            if should_create_new_topic and current_topic and current_topic["content"]:
                # Save the current topic before starting a new one
                topics.append(current_topic)
                current_topic = None
                pages_in_current_topic = 0

            if structured["headers"]:
                # Start new topic with header
                current_topic = {
                    "topic": structured["headers"][0],
                    "start_page": page["page"],
                    "end_page": page["page"],
                    "content": [structured]
                }
                pages_in_current_topic = 1
            elif current_topic:
                # Add to existing topic
                current_topic["end_page"] = page["page"]
                current_topic["content"].append(structured)
                pages_in_current_topic += 1
            else:
                # No current topic and no header - create generic section
                current_topic = {
                    "topic": f"Section starting at page {page['page']}",
                    "start_page": page["page"],
                    "end_page": page["page"],
                    "content": [structured]
                }
                pages_in_current_topic = 1

        # Don't forget the last topic
        if current_topic and current_topic["content"]:
            topics.append(current_topic)

        return topics

    def estimate_tokens(self, pages: List[Dict]) -> int:
        """
        Estimate token count for a set of pages.
        Uses a simple heuristic: ~1 token per 4 characters.
        """
        total_chars = 0
        for page in pages:
            structured = self.structure_page(page)
            # Count all text content
            total_chars += sum(len(h) for h in structured['headers'])
            total_chars += sum(len(b) for b in structured['bullets'])
            total_chars += sum(len(t) for t in structured['body'])
        # Rough estimate: 1 token ≈ 4 characters
        return total_chars // 4

    def create_dynamic_chunks(self, pages_data: List[Dict], max_tokens: int) -> List[List[Dict]]:
        """
        Dynamically create chunks based on token count, not fixed page count.
        Tries to pack as many pages as possible without exceeding max_tokens.
        """
        chunks = []
        current_chunk = []
        current_tokens = 0

        for page in pages_data:
            page_tokens = self.estimate_tokens([page])

            # If adding this page would exceed limit, start new chunk
            if current_chunk and (current_tokens + page_tokens > max_tokens):
                chunks.append(current_chunk)
                current_chunk = [page]
                current_tokens = page_tokens
            else:
                current_chunk.append(page)
                current_tokens += page_tokens

        # Don't forget last chunk
        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def identify_topics_with_llm(self, pages_data: List[Dict]) -> List[Dict]:
        """
        Use LLM to intelligently identify topic boundaries and group pages.
        Processes in dynamic chunks based on token count to optimize API usage.
        """
        if not self.client:
            # Fall back to basic grouping if no LLM available
            return self.group_by_topics(pages_data)

        # Create dynamic chunks based on token limit
        max_tokens = Config.MAX_CHUNK_TOKENS
        chunks = self.create_dynamic_chunks(pages_data, max_tokens)

        self.logger.info(f"Created {len(chunks)} dynamic chunks (max {max_tokens} tokens each)")
        for i, chunk in enumerate(chunks):
            estimated = self.estimate_tokens(chunk)
            self.logger.info(f"  Chunk {i+1}: {len(chunk)} pages, ~{estimated:,} tokens")

        all_topics = []
        previous_context = ""

        for chunk_idx, chunk in enumerate(chunks):
            chunk_start = chunk[0]['page']
            chunk_end = chunk[-1]['page']
            self.logger.info(f"Processing chunk {chunk_idx+1}/{len(chunks)}: pages {chunk_start}-{chunk_end}")

            # Prepare content summary for LLM
            pages_summary = []
            for page in chunk:
                structured = self.structure_page(page)
                page_text = []
                if structured['headers']:
                    page_text.append("HEADERS: " + " | ".join(structured['headers']))
                if structured['bullets']:
                    page_text.append("BULLETS: " + "; ".join(structured['bullets'][:5]))  # First 5 bullets
                if structured['body']:
                    page_text.append("CONTENT: " + " ".join(structured['body'][:3])[:200])  # First 3 body items, limited

                pages_summary.append({
                    "page": page['page'],
                    "content": "\n".join(page_text)
                })

            # Build context section from previous chunk's topics
            context_section = ""
            if previous_context:
                context_section = f"""
CONTEXT FROM PREVIOUS PAGES:
{previous_context}

NOTE: If the first page(s) in the current batch continue the last topic from the context, include them in a topic that starts from that earlier page number.
"""

            # Ask LLM to identify topic boundaries
            prompt = f"""Analyze these pharmacy law pages and identify distinct topics. Group consecutive pages that discuss the same subject.

IMPORTANT: Keep all topic names in the ORIGINAL LANGUAGE (Spanish if the content is Spanish).
{context_section}
CURRENT PAGES TO ANALYZE:
{json.dumps(pages_summary, indent=2, ensure_ascii=False)}

Return ONLY valid JSON in this format:
{{
  "topics": [
    {{
      "topic_name": "Topic name in original language",
      "start_page": 1,
      "end_page": 3,
      "reasoning": "Brief explanation"
    }}
  ]
}}"""

            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt}]
                )

                response_text = response.content[0].text
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0]

                result = json.loads(response_text.strip())

                # Convert LLM response to our topic format
                chunk_topics = []
                for topic_info in result.get('topics', []):
                    topic_pages = [
                        p for p in chunk
                        if topic_info['start_page'] <= p['page'] <= topic_info['end_page']
                    ]

                    if topic_pages:
                        topic = {
                            "topic": topic_info['topic_name'],
                            "start_page": topic_info['start_page'],
                            "end_page": topic_info['end_page'],
                            "content": [self.structure_page(p) for p in topic_pages]
                        }
                        all_topics.append(topic)
                        chunk_topics.append(topic)

                # Generate rich context for next chunk: both summary AND topic list
                if chunk_topics:
                    # Build topic list
                    context_topics = chunk_topics[-2:] if len(chunk_topics) > 1 else chunk_topics
                    topic_lines = [f"- Pages {t['start_page']}-{t['end_page']}: {t['topic']}" for t in context_topics]
                    topic_list = "\n".join(topic_lines)

                    # Get last 2-3 pages from this chunk for summary
                    last_pages = chunk[-3:] if len(chunk) > 2 else chunk
                    summary_prompt = f"""Briefly summarize what these pages discuss (1-2 sentences max). Keep the summary in the ORIGINAL LANGUAGE.

Pages:
{json.dumps([pages_summary[i] for i in range(len(pages_summary)) if i >= len(pages_summary) - len(last_pages)], indent=2, ensure_ascii=False)}

Summary:"""

                    try:
                        summary_response = self.client.messages.create(
                            model=self.model,
                            max_tokens=150,
                            temperature=0.1,
                            messages=[{"role": "user", "content": summary_prompt}]
                        )
                        summary = summary_response.content[0].text.strip()
                        previous_context = f"""Topics identified in previous chunk:
{topic_list}

Content summary (ending at page {chunk[-1]['page']}):
{summary}"""
                    except:
                        # Fallback to just topic list if summary fails
                        previous_context = f"""Topics identified in previous chunk:
{topic_list}"""

            except Exception as e:
                self.logger.error(f"LLM topic identification error for chunk {chunk_start}-{chunk_end}: {e}")
                # Fall back to basic grouping for this chunk
                fallback_topics = self.group_by_topics(chunk, max_pages_per_topic=3)
                all_topics.extend(fallback_topics)

                # Update context from fallback topics too
                if fallback_topics:
                    last_topic = fallback_topics[-1]
                    previous_context = f"- Pages {last_topic['start_page']}-{last_topic['end_page']}: {last_topic['topic']}"

        return all_topics

    def process(self, pages_data: List[Dict]) -> List[Dict]:
        repeated = self.detect_repeated_elements(pages_data)
        cleaned_pages = self.remove_repeated_elements(pages_data, repeated)

        # Use LLM-based topic identification
        topics = self.identify_topics_with_llm(cleaned_pages)

        return topics
