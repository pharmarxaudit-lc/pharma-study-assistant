# LLM-Based Topic Identification System

## Overview

The application uses a sophisticated LLM-based approach to intelligently identify and group topics from pharmacy law PDFs. This document explains how the system works.

## Architecture

### Why LLM Instead of Python Logic?

**Old Approach (Rule-Based):**
- Python code looked for headers to identify new topics
- Used arbitrary page limits (e.g., "max 3 pages per topic")
- Result: Generic topics like "Section 11" or topics split at wrong boundaries

**New Approach (LLM Semantic Analysis):**
- Claude analyzes actual content semantics
- Understands when topics genuinely start/end
- Groups pages by meaning, not structure
- Result: Meaningful topics like "Funciones del Farmacéutico y Administración de Medicamentos"

## Processing Flow

### Phase 1: PDF Extraction (Python)
```
111 pages → PyMuPDF extracts:
├── Headers (detected by font size)
├── Bullets (bullet point lists)
└── Body text (main content)
```

### Phase 2: Dynamic Chunking (Token-Based)

**Intelligent Chunk Creation:**
- Instead of fixed "10 pages per chunk", system estimates tokens per page
- Packs as many pages as possible without exceeding configured limit (default: 80,000 tokens)
- Adapts to content density (dense pages = fewer per chunk, sparse pages = more per chunk)

**Configuration** (`config.py`):
```python
MODEL_MAX_CONTEXT_TOKENS = 200_000  # Claude 3.5 Sonnet capacity
MAX_CHUNK_TOKENS = 80_000           # Target: 40% of capacity
ESTIMATED_TOKENS_PER_PAGE = 500     # Conservative estimate
```

**Example Output:**
```
Created 2 dynamic chunks (max 80,000 tokens each)
  Chunk 1: 65 pages, ~52,000 tokens
  Chunk 2: 46 pages, ~38,000 tokens
```

### Phase 3: LLM Topic Identification (Claude)

The system processes these **dynamic chunks** with context propagation:

#### Chunk 1 (Pages 1-10)

**Input to Claude:**
```json
{
  "pages": [
    {
      "page": 1,
      "content": "HEADERS: Repaso Reválida | La Profesión de Farmacia..."
    },
    {
      "page": 2,
      "content": "HEADERS: Responsabilidad social | Requisitos para ejercer..."
    },
    ...pages 3-10
  ]
}
```

**Prompt:**
```
Analyze these pharmacy law pages and identify distinct topics.
Group consecutive pages that discuss the same subject.

IMPORTANT: Keep all topic names in the ORIGINAL LANGUAGE (Spanish).

Return JSON:
{
  "topics": [
    {
      "topic_name": "Topic name in Spanish",
      "start_page": 1,
      "end_page": 3,
      "reasoning": "Why these pages belong together"
    }
  ]
}
```

**Claude's Response:**
```json
{
  "topics": [
    {
      "topic_name": "Introducción y Responsabilidad Social de la Profesión",
      "start_page": 1,
      "end_page": 2,
      "reasoning": "Introduces the profession and its social responsibility"
    },
    {
      "topic_name": "Requisitos de Licencia",
      "start_page": 3,
      "end_page": 4,
      "reasoning": "Academic requirements, internship, and licensing exam"
    },
    {
      "topic_name": "Colegiación y Recertificación",
      "start_page": 5,
      "end_page": 8,
      "reasoning": "Professional association membership and continuing education"
    }
  ]
}
```

#### Chunk 2 (Pages 11-20)

**Context Propagation:**

Before processing the next chunk, the system:
1. **Extracts last 2 topics** from previous chunk
2. **Generates a summary** of last 2-3 pages using Claude

**Input to Claude for Chunk 2:**
```
CONTEXT FROM PREVIOUS PAGES:
Topics identified in previous chunk:
- Pages 5-8: Colegiación y Recertificación
- Pages 9-10: Denegación, Suspensión y Reinstalación de Licencias

Content summary (ending at page 10):
Estas páginas discuten los requisitos de educación continua para
farmacéuticos, el procedimiento de recertificación profesional, y las
condiciones para la denegación, suspensión y reinstalación de licencias
farmacéuticas.

NOTE: If the first page(s) in the current batch continue the last topic
from the context, include them in a topic that starts from that earlier
page number.

CURRENT PAGES TO ANALYZE:
[pages 11-20]
```

This context allows Claude to:
- ✅ Detect if page 11 continues the topic from page 10
- ✅ Avoid creating duplicate topics
- ✅ Maintain consistent naming
- ✅ Understand the narrative flow

### Phase 3: Topic Aggregation

After processing all ~11 chunks (111 pages / 10 per chunk):
- Each chunk returns 3-5 topics
- System aggregates all topics
- **Total: 41 topics identified** (for 111-page document)

### Phase 4: Content Analysis & Formatting

For each of the 41 topics, Claude performs:

**Analysis:**
```python
{
  "main_topic": "Funciones del Farmacéutico",
  "subtopics": ["Dispensación", "Administración de Medicamentos"],
  "key_terms": [
    {"term": "Dispensar", "definition": "...", "importance": "high"}
  ],
  "exam_critical_points": [
    {"point": "1500 horas de internado requeridas", "category": "requirement"}
  ],
  "difficulty_level": "intermediate"
}
```

**Formatting:**
```markdown
---
topic: Funciones del Farmacéutico
pages: 11-13
difficulty: intermediate
---

# Funciones del Farmacéutico

⚖️ **Ley 247 de 2004** establece las funciones principales...
```

## Code Architecture

### Key Files

**`backend/text_processor.py`:**
- `identify_topics_with_llm()` - Main LLM topic identification
- Handles chunking (10 pages at a time)
- Manages context propagation
- Generates summaries for next chunk

**`backend/content_analyzer.py`:**
- Analyzes each topic's content
- Extracts key terms, critical points
- Spanish language preservation

**`backend/llm_formatter.py`:**
- Formats topics into clean markdown
- Preserves Spanish language
- Adds visual elements (emojis, structure)

## Language Preservation

All prompts explicitly instruct:
```
IMPORTANT: Keep all content in its ORIGINAL LANGUAGE (Spanish if the
input is in Spanish). Do NOT translate.
```

This ensures:
- ✅ Topic names in Spanish
- ✅ Key terms in Spanish
- ✅ Summaries in Spanish
- ✅ No unwanted translation to English

## Benefits of LLM Approach

### Intelligent Boundaries
```
❌ Old: "Page has 3 pages? New topic"
✅ New: "These pages discuss the same regulatory concept"
```

### Meaningful Names
```
❌ Old: "Section starting at page 11"
✅ New: "Funciones del Farmacéutico y Administración de Medicamentos"
```

### Context Awareness
```
❌ Old: Each chunk independent
✅ New: Chunk 2 knows what Chunk 1 discussed
```

### Semantic Understanding
```
❌ Old: Looks for headers only
✅ New: Understands content themes and relationships
```

## Performance Considerations

### API Calls
For 111 pages:
- **Topic Identification**: ~11 chunks × 2 calls/chunk = ~22 calls
  - 11 for topic identification
  - 11 for summary generation
- **Analysis & Formatting**: 41 topics × 2 calls/topic = 82 calls
- **Total**: ~104 API calls

### Processing Time
- Topic identification: ~2-3 minutes
- Analysis & formatting: ~10-15 minutes
- **Total**: ~12-18 minutes for 111-page document

### Rate Limits
With 50 requests/minute limit:
- Topic identification uses ~22 calls
- Well within rate limits
- Main bottleneck: Analysis phase (1 topic at a time)

## Example Output

For the Puerto Rico pharmacy law PDF (111 pages):
- **Input**: 111 pages of Spanish pharmacy law
- **Output**: 41 intelligently grouped topics with Spanish names
- **Quality**: Topics accurately reflect content boundaries

Sample topics generated:
1. "Introducción y Responsabilidad Social de la Profesión de Farmacia"
2. "Requisitos de Licencia para Farmacéuticos"
3. "Colegiación y Recertificación"
4. "Denegación, Suspensión y Reinstalación de Licencias"
5. "Funciones del Farmacéutico y Administración de Medicamentos"
6. "Farmacéutico Regente"
...and 35 more

## Future Enhancements

Potential improvements:
1. **Adaptive chunk size**: Larger chunks for simple content, smaller for complex
2. **Topic merging**: Post-process to merge very small topics
3. **Hierarchical topics**: Main topics with sub-topics
4. **Cross-references**: Identify related topics

## Testing

To verify the system is working:

```bash
# Check logs for topic identification
grep "Identified.*topics" logs/backend.log

# Check for Spanish language preservation
grep "topic_name" logs/backend.log | head -5

# Verify context propagation
grep "CONTEXT FROM PREVIOUS" logs/backend.log | head -1
```

Expected output:
```
Identified 41 topics
"topic_name": "Funciones del Farmacéutico"
CONTEXT FROM PREVIOUS PAGES: Topics identified in previous chunk...
```
