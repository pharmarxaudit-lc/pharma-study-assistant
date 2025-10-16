# Phase 2 Implementation Plan: Exam/Testing UI

**Last Updated**: 2025-10-16
**Target Exam**: Puerto Rico Pharm.D State Law Licensure Exam
**Exam Format**: Multiple choice only, 2-3 hours

---

## Overview

Phase 2 builds an exam preparation system that generates questions from extracted PDF content and provides an interactive testing experience with progress tracking and spaced repetition.

---

## Architecture Decisions (Confirmed)

### Content Strategy
✅ **Static deployment model** - All content and enrichment happens before Replit deployment
✅ **Primary content source** - PR pharmacy law exam review course (111 pages, processed)
  - Contains detailed laws, regulations, case studies, examples
  - Source for question generation
✅ **Secondary reference** - PR pharmacy study guide (`uploads/pr_pharmacy_study_guide.pdf`)
  - Official commission guidance on exam topics
  - Ensures comprehensive coverage of all required areas
  - Cross-reference to validate review course completeness
✅ **Enhancement phase** - Optional research/enrichment step after initial testing
✅ **Dynamic generation** - Hybrid approach (pre-generated + on-demand via API)

### Question Generation
✅ **Question type**: Multiple choice only
- Single correct answer (4 options: A-D)
- "Choose all that apply" (2-3 correct out of 4-5 options)

✅ **Generation strategy**: Hybrid approach
- Pre-generate 20-30 questions per topic during setup
- Store all in SQLite for offline access
- Use Anthropic API for additional variations on-demand
- Question variation system to prevent memorization

✅ **Distractor strategy**:
- Use exam review course content + Claude's pharmacy law knowledge
- Generate plausible incorrect answers based on common misconceptions
- Include numeric variations and similar-sounding terms

### Study Session Configuration
✅ **User configurable** - Settings accessible when starting a session
- **Default: 25-30 questions** per session (medium length)
- **Default: Mixed topics** to simulate exam conditions
- **User can change**:
  - Session length (short 10-15, medium 25-30, long 50+)
  - Topic mode (single topic focus vs mixed topics)
  - Difficulty filter (if desired)

### Mock Exam Configuration
✅ **User configurable** - Keep it simple and flexible
- **Defaults**:
  - 50-100 questions (user selects before starting)
  - 2-3 hour time limit (user selects: 30 min, 1 hr, 2 hrs, 3 hrs)
  - 70% passing score
- **Multiple sessions**: User can take unlimited mock exams with randomized questions
- **Session history**: Track all attempts for progress review

### Deployment & Data Management
✅ **No login system** - Keep it simple, single-user app
- **Database strategy**:
  - Build and populate database locally with pre-generated questions
  - Include populated SQLite file in deployment
  - Update locally, redeploy with changes as needed based on feedback
- **API key**: Store ANTHROPIC_API_KEY as Replit secret
- **Session tracking**: Full exam attempt logging with:
  - All questions asked
  - User answers
  - Correct/incorrect status
  - Timestamp, duration, score
- **Results reporting**:
  - Online results page after each exam
  - Downloadable PDF report with:
    - Full exam questions and answers
    - Correct answers highlighted in green
    - Incorrect answers highlighted in red
    - Score breakdown by topic
    - Timestamp and duration
- **Exam history**: Persistent log of all test attempts with results accessible in app

---

## Implementation Phases

### Phase 1: PDF Extraction & Analysis ✅ COMPLETE
**Status**: Complete
- PDF extraction working
- Analysis.json generation working
- Topic identification working
- Key terms and exam critical points extracted

---

### Phase 2A: Database & Question Generation ✅ COMPLETE
**Goal**: Build core data layer and question generation system

**Status**: Complete (2025-10-16)
**Prerequisites**:
- ✅ Phase 1 complete
- ✅ Analysis.json available
- ✅ Review analysis.json structure

#### Components:

**2.1 Database Schema Design**
- Define complete schema for 5 tables:
  - `documents` - Track processed documents
  - `questions` - Store all generated questions
  - `user_attempts` - Record each answer attempt
  - `study_sessions` - Track exam sessions
  - `spaced_repetition` - Track question mastery
- Document relationships and constraints
- Create database initialization script
- Create sample data for testing

**2.2 Question Generator** (`backend/question_generator.py`)
- **Input**: analysis.json from Phase 1
- **Process**:
  - Load topic data with key terms and exam critical points
  - Generate 20-30 questions per topic
  - Create multiple choice questions (single answer)
  - Create "choose all that apply" questions (2-3 correct)
  - Generate high-quality distractors using:
    - Common misconceptions
    - Similar terms from topic
    - Numeric variations within legal ranges
  - Add regulatory citations to explanations
- **Output**: Store questions in database with metadata
- **Progress tracking**: Stream progress via SSE
- **Error handling**: Validate and retry failed generations

**2.3 Question Variation System** (`backend/question_variator.py`)
- Build variation strategies:
  - Rephrase question text (different wording, same concept)
  - Create scenario-based variations
  - Rotate distractor combinations
  - Vary numeric values (within legal bounds)
- Track previously seen questions per session
- Prioritize unseen variations
- Generate new variations on-demand via API when needed

**2.4 Question Validator** (`backend/question_validator.py`)
- Validate question format and structure
- Check for duplicate questions
- Verify correct_answer matches options array
- Validate difficulty levels
- Check for ambiguous wording
- Ensure explanations are clear

**2.5 API Endpoints - Questions**
- `POST /api/questions/generate/<file_id>` - Generate questions from document
- `GET /api/questions/<file_id>` - Retrieve all questions (with pagination/filtering)
- `GET /api/questions/<file_id>/stats` - Question counts by topic/difficulty/type
- `GET /api/questions/<question_id>` - Get single question details

**2.6 API Endpoints - Sessions**
- `POST /api/sessions/start` - Start new study session
- `POST /api/sessions/<session_id>/answer` - Submit answer
- `GET /api/sessions/<session_id>/results` - Get session results
- `GET /api/sessions/history` - Get all past sessions
- `GET /api/sessions/<session_id>/pdf` - Download PDF report

**Deliverable**: ✅ Working database with question generation and API

---

### Phase 2B: Basic Exam Flow ✅ COMPLETE
**Goal**: Build minimal working exam experience

**Status**: Complete (2025-10-16)
**What was built**:
- ✅ Complete exam flow (config → questions → results)
- ✅ All session API endpoints functional
- ✅ Basic UI for taking exams (10/25/50/100 questions)
- ✅ Immediate feedback with explanations
- ✅ Results page with score and topic breakdown
- ✅ 325 questions loaded in database
- ⚠️ Minor frontend bug on results display (topic_breakdown.map undefined)

**Deliverable**: ✅ Working end-to-end exam flow

---

### Phase 3: UI Polish & Features (NEXT)
**Goal**: Enhance user experience and add missing features

**Prerequisites**:
- ✅ Phase 2B complete
- ✅ Basic exam flow working
- ✅ API endpoints functional

#### UI Architecture:

**Navigation Structure**:
- Simple navigation menu/sidebar with routes:
  - `/process` - Process PDFs (existing Phase 1 UI - no changes)
  - `/exam` - Exam Prep (new Phase 2 UI)
  - `/progress` - Progress Dashboard
- Each section independent, accessible anytime
- Clean separation between processing and testing functionality

**Phase 1 UI (Unchanged)**:
- FileUpload.vue
- ProcessingStatus.vue
- ResultViewer.vue

**Phase 2 UI (New)**:
- All exam prep functionality below

#### Priority Tasks (Phase 3A - Immediate):

**3.1 Fix Results Display Bug** 🔴 HIGH PRIORITY
- Debug and fix `topic_breakdown.map` undefined error
- Ensure results page displays correctly
- Test with multiple sessions

**3.2 Polish Results Summary**
- Create proper `ResultsSummary.vue` component
- Display final score prominently
- Show pass/fail indicator (70% threshold)
- Add topic breakdown visualization
- Show time spent and duration
- Make it visually appealing

**3.3 Add Session History**
- Create `ExamHistory.vue` component
- List all past sessions with scores and dates
- Allow viewing past results
- Filter by session type

**3.4 Add Question Review**
- Create `QuestionReview.vue` component
- Show all questions from a session
- Highlight correct (green) / incorrect (red)
- Display explanations for all questions
- Allow filtering by correct/incorrect

**3.5 Enhance Session Configuration**
- Add topic filter dropdown
- Add difficulty filter dropdown
- Add session type selection (study/practice/mock)
- Add time limit option
- Improve UI/UX

**Deliverable**: Polished exam experience ready for testing

---

#### Future Tasks (Phase 3B - Later):

**Practice Mode Enhancements**
- Timer display with warnings
- Question navigation sidebar
- Mark for review functionality
- Pause/resume session

**Mock Exam Mode**
- Strict timer enforcement
- No feedback during exam
- Randomized question order
- Final results only after completion

**Question Bank**
- View all generated questions
- Filter by topic/difficulty/type
- Preview questions
- Search functionality

---

### Phase 4: Progress & Analytics
**Goal**: Track learning progress and optimize review

**Prerequisites**:
- ✅ Phase 3 complete
- ✅ Users can take exams
- ✅ Session data being recorded

#### Components:

**4.1 Spaced Repetition System**
- `backend/spaced_repetition.py` - SM-2 algorithm
  - Track question mastery (ease factor)
  - Calculate next review dates
  - Adjust difficulty based on performance
  - Get questions due for review
- Integration with session manager:
  - Update after each answer
  - Balance new questions vs review questions

**4.2 Progress Dashboard**
- `ProgressDashboard.vue` - Analytics overview
  - Overall statistics card:
    - Total questions attempted
    - Overall accuracy rate
    - Average score
  - Study streak calendar
  - Performance trends chart (scores over time)
  - Topic strength analysis:
    - Strong topics (>80% accuracy)
    - Weak topics (<60% accuracy)
  - Spaced repetition queue (questions due)

**4.3 Exam History**
- `ExamHistory.vue` - Past sessions log
  - List all past sessions with:
    - Date and time
    - Session type
    - Score and percentage
    - Duration
  - Filter by session type
  - View details button
  - Delete session option

**4.4 PDF Report Generation**
- Choose PDF library (reportlab/weasyprint/fpdf)
- `backend/pdf_report_generator.py` - Generate reports
  - Design professional report template
  - Header with score, date, duration
  - List all questions with:
    - Question number
    - Question text
    - User's answer
    - Correct answer
    - Explanation
    - Color coding (green=correct, red=incorrect)
  - Topic breakdown section
  - Summary statistics
- API endpoint for download

**Deliverable**: Complete analytics and progress tracking system

---

### Phase 5: Deployment & Testing
**Goal**: Deploy to Replit and validate with real user

**Prerequisites**:
- ✅ Phase 2, 3, 4 complete
- ✅ All features tested locally
- ✅ Database populated with questions

#### Tasks:

**5.1 Database Preparation**
- Generate all questions locally (20-30 per topic)
- Run validation on all questions
- Remove duplicates
- Test database integrity
- Optimize database (indexes, vacuum)
- Create backup

**5.2 Replit Configuration**
- Set up Replit project
- Configure environment variables
- Add ANTHROPIC_API_KEY as secret
- Update requirements.txt
- Update start script for Replit
- Test deployment locally first

**5.3 Deployment**
- Deploy to Replit
- Test on Replit environment
- Verify database persistence
- Test API endpoints
- Test all UI components
- Test PDF generation

**5.4 User Acceptance Testing**
- Test with real user (your wife)
- Take multiple practice exams
- Try all session types
- Test on multiple devices (desktop, mobile)
- Collect feedback:
  - Question quality
  - UI/UX issues
  - Missing features
  - Performance issues
  - Bugs

**5.5 Bug Fixes & Refinements**
- Fix identified bugs
- Refine question quality
- Adjust UI based on feedback
- Performance optimizations

**Deliverable**: Production-ready app deployed on Replit

---

### Phase 6: Content Enrichment (OPTIONAL - POST-DEPLOYMENT)
**Goal**: Enhance question quality and coverage if needed

**Prerequisites**:
- ✅ Phase 5 complete
- ✅ Initial testing completed
- ✅ Feedback collected
- ✅ Decision made: Enhancement needed

**When to implement**: Only proceed if testing reveals:
- Insufficient question variety
- Missing important topics from official study guide
- Need for more detailed legal citations
- Gaps in edge cases or exceptions
- Request for more difficult questions

#### Components:

**6.1 Gap Analysis**
- Cross-reference exam review course with official study guide
- Identify missing topics or under-represented areas
- Review user feedback for weak areas
- Prioritize topics needing enhancement

**6.2 Content Enrichment** (if needed)
- `backend/content_enricher.py`
  - Analyze existing topics from analysis.json
  - Use WebSearch to fetch Puerto Rico pharmacy laws:
    - Law 247 of 2004 (full text)
    - Recent amendments
    - Official regulations
    - Case examples
  - Extract specific regulation numbers, requirements, penalties
  - Find edge cases and exceptions
  - Gather numeric values (timeframes, limits, fees)
- Store enrichment data in database:
  - Add `content_enrichment` table if needed
  - Link enrichment to topics

**6.3 Question Regeneration**
- Re-run question generator with enriched content
- Generate additional questions for weak areas
- Improve distractor quality with real legal alternatives
- Add detailed regulation citations to explanations
- Validate all new questions

**6.4 Redeployment**
- Update database with enhanced questions
- Redeploy to Replit
- Notify user of updates
- Collect feedback on improvements

**Deliverable**: Enhanced database with comprehensive question coverage

---

## Technical Stack

- **Backend**: Flask, SQLite, Claude API (Sonnet 3.5)
- **Frontend**: Vue 3, Axios
- **Question Generation**: Claude API with structured prompts
- **PDF Generation**: reportlab/weasyprint/fpdf (TBD)
- **Deployment**: Replit (with secrets for API key)
- **Database**: SQLite (single file, included in deployment)
- **Content Enhancement**: WebSearch API (if Phase 6 needed)

---

## Success Criteria

### Phase 2 Success:
- Database schema complete and tested
- 20-30 questions generated per topic
- All API endpoints working
- Questions validated and stored

### Phase 3 Success:
- All three study modes functional
- Timer working correctly
- Question navigation smooth
- Results display accurately

### Phase 4 Success:
- Spaced repetition algorithm working
- Progress dashboard displays correctly
- PDF reports generate and download
- Exam history tracks all sessions

### Phase 5 Success:
- App deployed on Replit
- User can complete full exam
- No critical bugs
- Performance acceptable
- User satisfied with functionality

### Phase 6 Success (if needed):
- Gaps identified and filled
- Question quality improved
- User reports better coverage
- Exam readiness increased

---

## Risk Mitigation

### Risk: Question Quality Issues
- **Mitigation**: Implement thorough validation, manual review of samples, user feedback loop

### Risk: API Costs for On-Demand Generation
- **Mitigation**: Pre-generate maximum questions, set budget alerts, monitor usage

### Risk: Database Size
- **Mitigation**: Optimize queries, add indexes, regular vacuum, pagination for large lists

### Risk: PDF Generation Performance
- **Mitigation**: Generate PDFs asynchronously, cache common reports, optimize template

### Risk: Browser Compatibility
- **Mitigation**: Test on multiple browsers, use standard web APIs, responsive design

---

## Next Steps (Updated 2025-10-16)

**Phase 2B Complete! ✅**
1. ✅ Planning complete
2. ✅ Database schema designed and implemented
3. ✅ Question generation working (325 questions)
4. ✅ All API endpoints functional
5. ✅ Basic exam flow working end-to-end

**Phase 3A - Immediate Priorities:**
1. 🔴 Fix results page display bug (topic_breakdown.map undefined)
2. Polish results summary component
3. Add session history view
4. Add question review component
5. Enhance session configuration UI

**Phase 3B - Future Enhancements:**
- Timer functionality
- Question navigation
- Mock exam mode
- Question bank view

---

## Notes

**Phase 2B Milestone (2025-10-16)**
- ✅ Complete exam flow implemented and tested
- ✅ 325 questions loaded from analysis.json
- ✅ All core API endpoints working
- ✅ Backend datetime parsing bug fixed
- ⚠️ Minor frontend display issue on results page (needs fix)
- 📊 Overall progress: 45% complete (86/190 tasks)
- 🎯 Next focus: Phase 3A UI polish and bug fixes
