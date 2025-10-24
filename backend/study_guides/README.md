# Study Guides Directory

This directory contains the source PDF documents used to generate additional exam questions for the Pharma Study Assistant.

## Contents

### 1. Repaso_Ley_D.pdf
- **Size:** 315 KB
- **Pages:** 10
- **Study Points:** 60
- **Format:** Numbered study guide covering pharmacy law fundamentals
- **Questions Generated:** 57
- **Processing Script:** `../convert_study_guide.py`
- **Status:** ✅ Fully processed and added to database

**Topics Covered:**
- Junta de Farmacia creation and purpose
- Pharmacist and pharmacy technician licensing requirements
- Continuing education requirements
- Establishment licenses and regulations
- Pharmacist absences and emergency procedures
- Biological products storage
- Vaccination administration
- Controlled substances basics

**Date Added to Project:** October 23, 2025

---

### 2. Preguntas_Examen_de_Leyes__Examen_de_Agosto_.docx.pdf
- **Size:** 767 KB
- **Pages:** 9
- **Study Points:** 117 (split into two sections)
- **Format:** Comprehensive exam question review guide
- **Questions Generated:** 117 (105 new, 12 duplicates)
- **Processing Script:** `../convert_preguntas_examen_batched.py`
- **Status:** ✅ Fully processed and added to database

**Structure:**
- **Section 1:** Questions 1-60 (regulatory framework, licensing, facilities)
- **Section 2:** Additional Questions 1-57 (controlled substances, cannabis, bioequivalents)

**Topics Covered:**
- Internship hours and requirements
- Good Samaritan Law
- Pharmacy board authority
- Biological product storage temperatures
- Continuing education specifics
- Veterinary licenses
- Prescription information requirements
- Emergency dispensing
- Bioequivalent medication interchange
- Controlled substances regulations (Classes II-V)
- Cannabis medicinal regulations
- Narcotic dispensing and repetition rules
- Technical infractions
- Medical device registration exemptions
- Paraphernalia law
- Professional malpractice jurisdiction

**Date Added to Project:** October 23, 2025

---

## Processing History

| PDF | Study Points | Questions Generated | Duplicates | Added to DB | Database Total After |
|-----|--------------|---------------------|------------|-------------|---------------------|
| Repaso_Ley_D.pdf | 60 | 57 | 0 | 57 | 294 |
| Preguntas_Examen_de_Leyes.pdf | 117 | 117 | 12 | 105 | 399 |
| **TOTAL** | **177** | **174** | **12** | **162** | **399** |

---

## Original Source

These PDFs were originally located at:
- `/Users/luiscotto/Library/CloudStorage/OneDrive-Personal/Personal/Repaso_Ley_D.pdf`
- `/Users/luiscotto/Library/CloudStorage/OneDrive-Personal/Personal/Preguntas_Examen_de_Leyes__Examen_de_Agosto_.docx.pdf`

They have been copied to this project directory to preserve them as part of the codebase.

---

## Usage

To reprocess these PDFs or process new similar documents:

### For Repaso_Ley_D.pdf format:
```bash
cd ..
python convert_study_guide.py --output /tmp/questions.json --file-id study_guide_name [--execute]
```

### For Preguntas_Examen_de_Leyes.pdf format (recommended for large study guides):
```bash
cd ..
python convert_preguntas_examen_batched.py --output /tmp/questions.json --file-id study_guide_name --delay 3 [--execute]
```

---

## Generated Outputs

Each PDF has corresponding output files in:
- `../outputs/repaso_ley_d/`
  - `study_guide_raw/study_guide_raw.md` - Original study text
  - `study_guide_cleaned/study_guide_questions.md` - Formatted questions

- `../outputs/preguntas_examen_leyes/`
  - `study_guide_raw/study_guide_raw.md` - Original study text
  - `study_guide_cleaned/study_guide_questions.md` - Formatted questions (117 questions)

---

## Notes

- All questions are in Spanish
- Questions follow standardized format with difficulty levels (basic/intermediate/advanced)
- Automatic deduplication ensures no duplicate questions in database
- All questions include regulatory context (Ley 247 de 2004, Reglamento 156, etc.)
- Questions are mapped to relevant topics for study organization

---

## Maintenance

**Last Updated:** October 23, 2025
**Location:** `/Users/luiscotto/Code/pharma-study-assistant/backend/study_guides/`
**Related Documentation:** `../STUDY_GUIDE_IMPORT_README.md`
