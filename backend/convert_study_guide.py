#!/usr/bin/env python3
"""
Convert study guide points into standardized exam questions.

This script reads the Repaso_Ley_D.pdf study guide and converts each
study point into properly formatted exam questions matching the existing
database format.
"""

import json
import logging
import sys
from datetime import datetime
from typing import List, Dict

import anthropic
from config import Config
from database import get_database
from database_models import Question
from import_test_questions import TestQuestionImporter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


STUDY_GUIDE_TEXT = """
Repaso Examen de Ley-D - 60 Study Points

1. Propósito de la creación de la Junta de Farmacia: Responsable de salvaguardar la salud del pueblo, con poder exclusivo para reglamentar la admisión, suspensión o separación del ejercicio de la profesión de farmacia y de la ocupación de técnico de farmacia.

2. ¿Quién nombra los miembros de la Junta? El Gobernador de Puerto Rico de lista sometida por el CFPR o por la Junta de Farmacia o no incluido en la lista.

3. Función del técnico de farmacia: Podrá desempeñar, bajo supervisión directa del farmacéutico, funciones técnicas o administrativas relacionadas con la dispensación de medicamentos y artefactos mediante receta que le delegue el farmacéutico y que NO requieran juicio farmacéutico. NO podrá verificar recetas, ni orientar al paciente sobre medicamentos recetados.

4. Requisitos para ejercer como Farmacéutico en Puerto Rico: Licencia (Junta de Farmacia), Colegiación (CFPR, $144 anuales), Recertificación (ORCPS, Departamento de Salud)

5. Horas de práctica de farmacéutico: Completar un mínimo de 1,500 horas de práctica, previamente autorizadas por la Junta, bajo la supervisión de un farmacéutico preceptor.

6. ¿Cuál NO es requisito para ejercer en PR por reciprocidad? Cumplir con 1,500 horas de práctica.

7. Colegiación: Uno de los requisitos para ejercer en PR es ser miembro de CFPR. La cuota anual (2018-2019) es $144. El CFPR fue creado por la Ley Núm. 243 de 15 de mayo de 1938.

8. Educación continua: Farmacéutico total 35 hrs. 10 horas presenciales. 12 créditos (3 c/u) obligados en: Control de infecciones, errores en medicación, ética, ley de farmacia.

9. ¿Quién tiene el poder/ejecutar decisiones en el colegio de farmacéuticos? El comité ejecutivo.

10. Horas de práctica de técnico de farmacia: Completar mínimo de 1000 horas de internado autorizado por la Junta de Farmacia bajo supervisión directa de farmacéutico preceptor.

11. ¿Quién puede quitar la licencia, cese y desista, multa, suspender, cancelar, revocar licencia a los farmacéuticos y técnicos de farmacia? La Junta de Farmacia según establecido en la Ley 247 de 2004 y por el Reglamento de la Junta.

12. ¿Qué ocurre con la Licencia de establecimientos al cambiar de dueño o lugar? La licencia será nula y se entregará al Departamento de Salud para proveerse de una nueva.

13. Licencia de establecimientos: Según Reglamento 156, se renovarán cada 2 años. Solicitud debe estar en SARAFS no más tarde de 45 días calendarios anteriores a la fecha de vencimiento.

14. ¿Quién deniega, suspende, cancela o revoca licencias de establecimientos? El Secretario de Salud según Reglamento 156.

15. ¿Cuántos farmacéuticos se necesitan en una farmacia? Los establecimientos contarán con el número de farmacéuticos que razonablemente sean necesarios para proveer los controles y servicios requeridos.

16. Falta de farmacéutico - Cambio o cese de empleo: Notificar por escrito a la División de Medicamentos y Farmacia dentro de 3 días laborables.

17. Ausencia de Farmacéutico en Industria: Notificar dentro de 24 horas a la División de Medicamentos y Farmacia.

18. Ausencia en Recetario: Solo en emergencia. Farmacéutico tiene 24 horas para completar registro. Colocar rótulo "RECETARIO CERRADO POR EMERGENCIA DE FARMACÉUTICO".

19. Ausencia en Recetario durante periodo de alimentos: Si ausencia < 1 hora, no requiere rótulo.

20. Ausencia de preceptor: Durante ausencia, el interno no podrá realizar funciones relacionadas con dispensación de medicamentos.

21. Temperatura de productos biológicos: 12.5°C o 55°F

22. Conservación de expediente de vacunación: Conservar a perpetuidad en lugar seguro del recetario.

23. Vacunas que no necesitan receta: Neumococos, Influenza, Td/Tdap

24. División de Medicamentos y Farmacia: Dirigida por farmacéutico con no menos de 5 años de experiencia.

25. Medicamentos para uso de animales: Veterinario necesita licencia de instalación veterinaria. Medicamentos pueden ser dispensados en Centro Agrícola.

26. Información de receta que se le puede preguntar al paciente si falta: Nombre, Dirección, Edad.

27. Transmisión de receta: Puede transmitirse por medio oral, fax, imagen digitalizada o comunicación electrónica. La receta original se entregará antes de entregar medicamentos.

28. Suplido de Emergencia: En emergencia se despacharán suplidos para 5 días. Prescribiente debe enviar receta en 5 días (120 horas).

29. Receta en EE.UU: Se permite repetición de recetas de EU si original fue dispensado en estado de procedencia. Rx no puede tener más de 3 meses.

30. Medicamentos intercambios bioequivalentes: Se permite intercambio a menos que prescribiente escriba "No intercambie".

31. Máximo de empleados que el farmacéutico puede supervisar: 5 personas total (5 técnicos O 4 técnicos + 1 interno).

32. Entregas de medicamentos al hogar: Paciente puede renunciar a que sea farmacéutico quien entrega, con autorización expresa por escrito.

33. Evidencia de renuncia: Documentar fecha, hora, nombre. Archivar durante 2 años en expediente farmacéutico.

34. Medicamentos Bioequivalentes: Requiere firma del paciente para cambiar a bioequivalente. Si médico indicó "NO INTERCAMBIO" y paciente desea bioequivalente, comunicarse con médico.

35. Cambio de Brand a bioequivalente: Label debe contener nombre de marca o genérico + manufacturero, potencia, indicaciones, nombres, fecha exp, número lote.

36. ¿Qué NO es necesario en el label? Edad del paciente.

37. Fecha de expiración (Beyond Use Date): Medicamentos en mismo envase: fecha del manufacturero o 1 año, lo que sea menor. Compounding sólido/líquido no acuoso: 6 meses. Con agua: 14 días en nevera. Otras formulaciones: 30 días.

38. Intercambio biológico por biosimilar: Permitido si producto aprobado como intercambiable (Purple/Orange Book) y médico no indica "No intercambiable". Informar al médico en 2 días.

39. Dispositivos médicos: Todo dispositivo FDA aprobado está exento de registro ante Departamento de Salud.

40. Ley #73 de 2007: Elimina jeringuillas de parafernalia de sustancias controladas.

41. Requisito para dispensación de narcóticos: 2 días desde expedición de receta.

42. Inspector de sustancias controladas: Agente del orden público nombrado por Departamento de Salud, adiestrado por Departamento de Justicia/Policía PR.

43. Autoridad para clasificación de sustancias: Secretario de Salud mediante Reglamento u Orden Declarativa. Publicar en 2 periódicos dentro de 30 días. Entra en vigor 30 días después.

44. Medidas de seguridad de controlados: Rejas, alarmas, cámaras en recetario, área de recibo y almacén.

45. Denegación/suspensión/revocación de registro: Estatal: Secretario de Salud. Federal: DEA.

46. Conservación de controlados - Manufactureros: CI y CII en caja de seguridad >750 lbs empotrada al piso (Federal). Profesionales: CII-CV en gabinete cerrado (Federal).

47. Hojas oficiales de pedido: DEA Form 222. Conservar copia por 2 años.

48. Quién puede expedir controlados: Médicos, dentistas, veterinarios, podiatras registrados por Secretario de Salud y DEA.

49. Cambios en receta de controlados (Federal): Farmacéutico puede añadir/cambiar forma, concentración, instrucciones, fecha. NO puede cambiar nombre paciente, sustancia, firma prescribiente.

50. Despacho de narcóticos: No despachar transcurridos 2 días después de expedición.

51. Repetición de narcóticos: No tienen repetición (CII, III, IV, V).

52. Repetición de controlados NO narcóticos: 5 refills en 6 meses.

53. Orientación e información escrita: No facilitar resumen impreso con advertencias/efectos secundarios es infracción técnica grave.

54. Infracciones técnicas graves: Falta de seguridad, falta/exceso en inventarios, movimiento sin autorización, no notificar cambios, no fijar rótulo, no facilitar medguide, etc.

55. ¿Quién reclasifica controlados? Secretario de Salud mediante órdenes administrativas.

56. Recomendación cannabis medicinal: Justificada para condición médica debilitante. Suministro max 30 días. Nuevas condiciones: Depresión, Glaucoma, PTSD, Trastorno Bipolar.

57. Persona que dispensa cannabis: Necesita licencia ocupacional válida.

58. Ley del Buen Samaritano: Exención de responsabilidad civil por servicios voluntarios de emergencia, excepto negligencia crasa.

59. Medicamentos con requisitos especiales: Radionucleares, Controlados, Biológicos.
"""


def convert_study_points_to_questions() -> List[Dict]:
    """Use Claude to convert study points into exam questions."""
    logger.info("Converting study guide points into exam questions...")

    client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)

    prompt = f"""You are creating pharmacy exam questions based on study guide material.

Convert each study point below into 1-3 exam questions following this EXACT format:

{{
  "question_text": "Question in Spanish",
  "question_type": "single_answer" or "choose_all",
  "difficulty": "basic" or "intermediate" or "advanced",
  "options": {{
    "A": "Option text",
    "B": "Option text",
    "C": "Option text",
    "D": "Option text"
  }},
  "correct_answer": "A" (single) or "A,B,C" (multiple, sorted),
  "explanation": "Detailed explanation in Spanish",
  "key_terms": ["term1", "term2"],
  "regulatory_context": "Ley 247 de 2004" or relevant law,
  "topic_name": "Topic name"
}}

**RULES:**
- Create challenging, realistic exam questions
- For facts with multiple components, create "choose_all" questions
- Mix difficulty levels appropriately
- Make distractors plausible but clearly wrong
- Explanations should teach why answer is correct
- Use proper regulatory references (Ley 247 de 2004, Reglamento 156, Reglamento 153, etc.)

**STUDY GUIDE:**

{STUDY_GUIDE_TEXT}

**OUTPUT (JSON array only, no markdown):**"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=16000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.content[0].text.strip()

        # Remove markdown if present
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            response_text = '\n'.join(
                line for line in lines
                if not line.strip().startswith('```')
            )

        questions = json.loads(response_text)
        logger.info(f"Successfully generated {len(questions)} questions from study guide")

        return questions

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse response: {e}")
        logger.error(f"Response: {response_text[:500]}...")
        return []
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return []


def save_markdown_files(study_text: str, file_id: str, questions: List[Dict]):
    """Save raw and cleaned markdown files like main document processing."""
    import os

    # Create output directory structure
    output_dir = os.path.join(Config.OUTPUT_FOLDER, file_id)
    raw_dir = os.path.join(output_dir, 'study_guide_raw')
    cleaned_dir = os.path.join(output_dir, 'study_guide_cleaned')
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(cleaned_dir, exist_ok=True)

    # Save raw markdown
    raw_file = os.path.join(raw_dir, 'study_guide_raw.md')
    with open(raw_file, 'w', encoding='utf-8') as f:
        f.write(f"# Study Guide - Raw Content\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        f.write(study_text)

    logger.info(f"Saved raw markdown to: {raw_file}")

    # Save cleaned/structured markdown (questions in readable format)
    cleaned_file = os.path.join(cleaned_dir, 'study_guide_questions.md')
    with open(cleaned_file, 'w', encoding='utf-8') as f:
        f.write(f"# Study Guide - Converted Questions\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Total Questions: {len(questions)}\n\n")
        f.write("---\n\n")

        for idx, q in enumerate(questions, 1):
            f.write(f"## Question {idx}\n\n")
            f.write(f"**Type**: {q['question_type']} | **Difficulty**: {q['difficulty']} | **Topic**: {q['topic_name']}\n\n")
            f.write(f"**Question**: {q['question_text']}\n\n")
            f.write("**Options**:\n")
            for letter, text in q['options'].items():
                marker = "✓" if letter in q['correct_answer'].split(',') else " "
                f.write(f"- [{marker}] {letter}. {text}\n")
            f.write(f"\n**Correct Answer**: {q['correct_answer']}\n\n")
            f.write(f"**Explanation**: {q['explanation']}\n\n")
            f.write(f"**Key Terms**: {', '.join(q.get('key_terms', []))}\n\n")
            f.write(f"**Regulatory Context**: {q.get('regulatory_context', 'N/A')}\n\n")
            f.write("---\n\n")

    logger.info(f"Saved cleaned markdown to: {cleaned_file}")

    return raw_file, cleaned_file


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='/tmp/study_guide_questions.json',
                       help='Output file for generated questions')
    parser.add_argument('--document-id', type=int, default=1,
                       help='Document ID to associate questions with')
    parser.add_argument('--execute', action='store_true',
                       help='Actually add questions to database')
    parser.add_argument('--file-id', default='study_guide',
                       help='File ID for organizing output files')
    args = parser.parse_args()

    logger.info("="*80)
    logger.info("STUDY GUIDE TO QUESTIONS CONVERTER")
    logger.info("="*80)

    # Generate questions
    questions = convert_study_points_to_questions()

    if not questions:
        logger.error("No questions generated")
        return 1

    # Save markdown files (raw and cleaned)
    save_markdown_files(STUDY_GUIDE_TEXT, args.file_id, questions)

    # Save to file
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {len(questions)} questions to: {args.output}")

    # Use existing importer for deduplication and adding
    importer = TestQuestionImporter(
        pdf_path="",  # Not needed since we have questions already
        document_id=args.document_id
    )

    # Deduplicate
    new_questions, duplicates = importer.deduplicate_questions(questions)

    logger.info(f"\nDeduplication results:")
    logger.info(f"  Total generated: {len(questions)}")
    logger.info(f"  Duplicates: {len(duplicates)}")
    logger.info(f"  New questions: {len(new_questions)}")

    # Add to database
    dry_run = not args.execute
    added = importer.add_questions_to_database(new_questions, dry_run=dry_run)

    logger.info("\n" + "="*80)
    logger.info("SUMMARY")
    logger.info("="*80)
    logger.info(f"Questions generated: {len(questions)}")
    logger.info(f"Duplicates found: {len(duplicates)}")
    logger.info(f"New questions: {len(new_questions)}")
    logger.info(f"Questions added: {added if not dry_run else 0}")
    logger.info("="*80)

    return 0


if __name__ == '__main__':
    sys.exit(main())
