#!/usr/bin/env python3
"""
Convert Preguntas Examen de Leyes study guide into standardized exam questions.
Processes in batches to handle the large study guide (117 points).
"""

import json
import logging
import sys
import time
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


# Split the study guide into manageable chunks
STUDY_CHUNKS = [
    {
        "name": "Chunk 1: Questions 1-20",
        "content": """
1. Propósito creación de la junta de farmacia. (pág. 12, HO 1)
2. Quien nombra los miembros de la junta: Gobernador (pág. 13, HO 1)
3. Función del técnico de farmacia: no puede verificar, ni orientar. (pág. 20, HO 1)
4. Requisitos para ejercer como farmacéutico en PR. (pág. 21, HO 1)
5. Horas de practica de farmacéutico: 1,500 (pág. 24, HO 1)
6. Cual no es requisito para ejercer en PR por reciprocidad: cumplir con 1,500 horas (pág. 35, HO 1)
7. Colegiación: CFPR (pág. 39, HO 1)
8. Educación continua: farmacéutico 35, 10 deben de ser presenciales, 12 créditos con la siguientes: ética, control de inf, ley de farm., errores en meds (pág. 52, HO 1)
9. Quien tiene el poder/ejecuta decisiones en el colegio de farmacéuticos (CFPR): el comité ejecutivo. (pág. 44, HO 1)
10. Horas de técnico; 1000 horas (pág. 64, HO 1)
11. Quien puede quitar licencia, cese y desista, multa, suspender, cancelar, revocar licencia a los farm y técnicos: La junta de farmacia (pág. 80, HO 1)
12. Licencia de Establecimientos, cambian de dueño o lugar: licencia es nula. (pág. 7, HO 2)
13. Licencia de establecimientos: se renovará cada 2 años. (pág. 8, HO 2)
14. Quien deniega, suspende, cancela o revoca licencias de establecimientos: Secretario de Salud. (pág. 9, HO 2)
15. Cuantos farm se necesitan en una farmacia, institución o droguería: los razonablemente necesarios para proveer controles y servicios que se requieren para una actividad. (pág. 10, HO 2)
16. Falta de farmacéutico: dueño notificara a la división de med y farmacia dentro de 3 días laborables. (pág. 12, HO 2)
17. Ausencia de farmacéutico: break más de una hora aplica emergencia, menos de una hora no. (pág. 49, HO 2)
18. Ausencia de preceptor: interno no puede hacer nada en el proceso de dispensación. Proceso de dispensación incluye desde recibir hasta despachar. (pág. 50, HO 2)
19. Temperatura de productos biológicos: 12.5 grados centígrados o 55 grados Fahrenheit. (pág. 60, HO 2)
20. Conservación de expediente de vacunación del paciente: a perpetuidad (pág. 63, HO 2)
"""
    },
    {
        "name": "Chunk 2: Questions 21-40",
        "content": """
21. Vacunas que no necesitan receta: influenza, neumococo y td/tdap. Zoster necesita receta. (pág. 63, HO 2)
22. Licencia de botiquín: medicamentos para ensayos clínicos se exime de esta licencia. (pág. 68, HO 2)
23. Certificado de registro trienal: oficinas médicas, ambulancias, instituciones. (pág. 69, HO 2)
24. División de Meds y Farmacia: Dirigida por farmacéutico con no menos de 5 años de experiencia (pág. 84, HO 2)
25. Medicamentos para uso de animales, el veterinario no necesita licencia de registro trienal ni de botiquín. Necesita licencia de instalación veterinaria. (pág. 5, HO 3)
26. Información de receta que se le puede preguntar al paciente si falta: nombre, dirección y edad. (pág. 14, HO 3)
27. Para acelerar el proceso de receta. La original se adhiere a la copia, fax, o receta escrita oralmente, email. (pág. 17, HO 3)
28. En caso de emergencia se dispensa un suplido para 5 días (120 horas). La receta también tiene que llegar en esos 5 días. (pág. 19, HO 3)
29. Receta de EU, refills se pueden coger en PR, solo limitación de 3 meses. La original se tiene que despachar en estado de procedencia (pág. 21, HO 3)
30. Medicamentos intercambiados bioequivalentes. La farmacia no tiene el medicamento prescrito y solo se puede cambiar por un medicamento genérico bioequivalente. (pág. 22, HO 3)
31. Máximo de empleados que el farmacéutico puede supervisar: máximo de 5 personas (5 técnicos, 4 técnico y 1 interno sea técnico o PharmD). (pág. 24, HO 3)
32. Entregas de medicamentos al hogar/domicilio: debe de haber autorización expresa por escrito del paciente. (pág. 28, HO 3)
33. Evidencia de renuncia a entrega u orientación: debe de estar mínimo 2 años guardado en el expediente farmacéutico. (pág. 30, HO 3)
34. Medicamentos Bioequivalentes. Leer bien esta página. (pág. 35 y 36, HO 3)
35. Cuando se hace el cambio de Brand a bioequivalente, el label tiene que tener ambos nombres, por ejemplo, "simvastatin bioequivalente a Zocor". (pág. 41, HO 3)
36. Que no es necesario en el label del medicamento dispensado: edad de paciente. (pág. 42, HO 3)
37. Fecha expiración de los medicamentos; cuando se despachan. Beyond use date (pág. 47, HO 3)
38. Para intercambiar producto biológico: debe de ser producto biológico terapéuticamente intercambiable/biosimilar intercambiable. (pág. 60 y 61, HO 3)
39. Dispositivos médicos y/o artefactos: exentos del registro de departamento de salud. (pág. 69, HO 3)
40. Ley # 73 de 2007 – elimina jeringuillas de definición de parafernalia. (pág. 4, HO 4)
"""
    },
    {
        "name": "Chunk 3: Questions 41-60",
        "content": """
41. Requisito para dispensación de narcóticos: 2 días (48 horas) después de la expedición. (pág. 6, HO 4)
42. Inspector de sustancias controladas: nombrado por secretario de salud. (pág. 15, HO 4)
43. Autoridad y procedimientos para control y clasificación de sustancias: específicamente los días. (pág. 28, HO 4)
44. Medidas de seguridad controlados. (pág. 45, HO 4)
45. Denegación, suspensión, y revocación del registro de sustancia controladas: a cargo del secretario de salud. (pág. 49, HO 4)
46. Manufactureros y distribuidores: controlados II guardados en caja de seguridad de más de 750 lbs. empotrada en el piso. (pág. 54, HO 4)
47. Hojas oficiales de pedido de controlado: firmadas por persona encargada, a quien se le expidió el registro o persona autorizada por poder notarial. (pág. 58, HO 4)
48. Quien puede expedir controlados: tiene que tener licencia de registro profesional en PR, licencia de DEA y Estatal de ASSMCA (secretario de salud) o estar exento de los registros. (pág. 59, HO 4)
49. Dispensador que se prescribe así mismo y es el consumidor final: solo permitido cuando el secretario de salud lo establezca por reglamentos. (pág. 60, HO 4)
50. Cambios en la receta de controlados: no se le pueden hacer cambios al nombre, droga y firma del prescribiente. Otros cambios con autorización del médico, documentando su acción. (pág. 65, HO 4)
51. Despacho de narcóticos: no más de 2 días (48 horas). (pág. 67, HO 4)
52. Repetición de narcóticos, ya sean clasificación II, III, IV o V: no repetición
53. Repetición de no narcóticos II, III, IV o V: 5 refills en 6 meses. La receta dura 6 meses en vez de un año. (pág. 73, HO 4)
54. No orientar y facilitar al paciente un resumen impreso de controlados: infracción técnica y delito. (pág. 86, HO 4)
55. Infracciones técnicas e infracciones técnica graves. (pág. 94, HO 4)
56. Quien reclasifica controlados: secretario de salud. (pág. 104, HO 4)
57. Recomendación de cannabis medicinal: tiene que ser a pacientes con condiciones médicas debilitantes. (pág. 109, HO 4)
58. Cualquiera persona que quiera dispensar cannabis medicinal: tiene que tener una licencia ocupacional valida. (pág. 123, HO 4)
59. Ley del Buen samaritano: exoneración solo aplicable cuando los actos u omisiones no sean constitutivos de negligencia crasa, o con el propósito de causar daño.
60. Medicamentos con requisitos especiales para ser despachados: Radionucleares, Controlados, Biológicos
"""
    },
    {
        "name": "Chunk 4: Additional Questions 1-20 (from Section 2)",
        "content": """
1. Horas de internado de farmacéutico: 1,500 hrs
2. El técnico deberá cumplir con: 1,000 hrs de internado autorizadas por la Junta de Farmacia bajo la supervision directa de farmacéutico preceptor en una farmacia
3. Para operar una farmacia se tiene que contar con: La cantidad de farmacéuticos y técnicos que sean necesarios (1 farmacéutico + 5 técnicos de farmacia O 1 farmacéutico + 4 técnicos de farmacia + interno)
4. Ley del buen samaritano: Exención de responsabilidad civil excepto negligencia crasa
5. Los miembros de la junta son nombrados por: Gobernador
6. El encargado de autorizar, aprobar o denegar certificaciones del personas farmacéutico es: Junta de Farmacia
7. Quién puede suspender, revocar la licencia de la profesión de farmacia: Junta de Farmacia
8. Quién puede suspender, revocar la licencia del establecimiento: Secretario de Salud
9. Temperatura de los biológicos es no mayor de: 12.5 C o 55 F
10. Farmacéutico que no oriente al paciente: Negligencia profesional
11. Educación continua del farmacéutico: 35 horas totales, donde 25 pueden ser aisladas y 10 presenciales
12. Qué licencia deben sacar los veterinarios para almacenar, administrar medicamentos: Lic. Veterinario (Instalación Veterinaria)
13. Cuando se hace intercambio de medicamento por bioequivalente, documento al dorso de la receta, excepto: precio de venta del de marca. Debe incluir: nombre de marca/genérico, fecha, firma paciente, precio, firma farmacéutico
14. Cuando se hace intercambio, en el rótulo del producto debe incluir: Nombre farmacia, número serie receta, fecha dispensación, nombre marca/manufactura, nombre genérico/manufactura, bioequivalente a..., potencia, indicaciones, nombre paciente, nombre prescribiente, fecha expiración, número lote
15. Cuantas personas puede supervisar un farmacéutico: 5 personas máximo (5 técnicos O 4 técnicos + 1 interno)
16. Cuanto dura la licencia del establecimiento: 2 años
17. Si un farmacéutico empieza un nuevo empleo, notificar a división de medicamento y farmacia: 3 días
18. Cada cuanto se renueva el certificado de farmacéutico y técnico: 3 años
19. Certificado de registro trienal: para oficinas médicas
20. Artefactos se eximen de registro en el Departamento de Salud: Aprobados por FDA y registrados en su página electrónica
"""
    },
    {
        "name": "Chunk 5: Additional Questions 21-40 (from Section 2)",
        "content": """
21. Repeticiones de control II: No se repiten
22. Duración de recetas de controlados: 6 meses con máximo de 5 repeticiones
23. Para despachar un medicamento controlado, la vigencia es: de 2 días para cualquier narcótico de cualquier clasificación
24. Cuánto tiempo hay que guardar los informes y las recetas: 2 años
25. Cuánto tiempo hay que hacer el registro de narcóticos: Anualmente
26. MD registrado para recetar controlados: Registro del DEA y de las oficinas de Investigaciones del departamento de salud
27. Vacunas exentas de orden médicas, excepto: Culebrilla (ZOSTER). Exentas: Influenza, Neumococo, Td/Tdap
28. Cannabis: Para uso medicinal en condiciones debilitantes
29. Quién dispensa el cannabis: Licencia ocupacional válida
30. Qué ley dice que se necesita colegiación para ejercer como farmacéutico: Ley del colegio de farmacéuticos de Puerto Rico (Ley 243 de 1938)
31. Renovación de colegiación: Anual
32. Intercambio de biológicos: Biológicos biosimilares intercambiables
33. Para la certificación de vacuna se necesita, excepto: EC errores en medicación. Necesita: nombre/apellido, licencia farmacéutico, registro profesional, CFPR activo, 20 horas CDC, CPR, administración oxígeno, manejo patógenos en sangre. Renovación cada 3 años, solicitud ≥60 días antes, ≥1 hora EC cada año, CPR
34. Si hay un descuadre en la cantidad de controlados: Infracción técnica grave
35. El técnico de farmacia no podrá: Orientar al paciente ni verificar recetas
36. La licencia por reciprocidad aplica todo excepto: no hay que hacer 1,500 horas
37. Mal practice: Comunidad
38. El farmacéutico deberá cumplir con: un mínimo de 10 horas contacto presenciales (35 totales: 25 aisladas y 10 presenciales)
39. Para obtener el certificado de Vacunación NO es necesario: EC errores en medicación
40. El perfil de vacunación del paciente se guarda: a perpetuidad
"""
    },
    {
        "name": "Chunk 6: Additional Questions 41-57 (from Section 2)",
        "content": """
41. El perfil farmacéutico del paciente se guarda por: 2 años
42. La agencia gubernamental a quien se someten los errores en medicación: VAERS
43. La agencia que regula los establecimientos es: Departamento de Salud
44. De los siguientes medicamentos, cuál tiene requisitos en cuanto a su dispensación: Radioactivos, Vacunas, Controlados
45. Lo siguiente es requerido en el rótulo de un medicamento, excepto: Edad del paciente
46. Al evaluar una receta, el farmacéutico puede completar: nombre del paciente, fecha, indicación, forma de dosificación, potencia. NO puede completar: medicamento y firma del prescribiente
47. Recetas electrónicas con instrucciones incompletas: Llamar al médico y documentar en el Sistema
48. Almacenaje de controlados II: caja empotrada de 750 libras (manufactureros/distribuidores)
49. Según la ley de paraphernalia, NO está incluida: Jeringuillas (eliminadas por Ley 73 de 2007)
50. Los inspectores son nombrados por: Departamento de Salud
51. Durante la ausencia de un farmacéutico para tomar alimento: No se podrá entregar recetas, cerrar el recetario, colocar rótulo (si > 1 hora)
52. Durante la ausencia del farmacéutico preceptor: El técnico/interno no podrá realizar funciones relacionadas con la dispensación de medicamentos de receta
53. Orden de control II se pueden ser firmadas por: La persona a quien se le expidió el registro o autorizada por poder notarial (Federal). A nivel estatal solo el registrante
54. La fecha de expiración del medicamento es: Según la Pharmacopea
55. En caso de emergencia, se dispensará una cantidad que no excederá de: 120 horas (5 días)
56. Horas del técnico de farmacia para educación continua: 20 horas
57. Ausencia en recetario durante periodo de alimentos: Si ausencia < 1 hora, no requiere rótulo
"""
    }
]


def convert_chunk_to_questions(chunk_text: str, chunk_name: str) -> List[Dict]:
    """Convert a chunk of study points into exam questions."""
    logger.info(f"Processing {chunk_name}...")

    client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)

    prompt = f"""You are creating pharmacy exam questions based on study guide material.

Convert EACH study point below into 1 exam question following this EXACT format:

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
- Create ONE question per study point
- Create challenging, realistic exam questions
- Use "choose_all" for points with multiple correct components
- Mix difficulty levels appropriately
- Make distractors plausible but clearly wrong
- Explanations should teach why answer is correct
- Use proper regulatory references (Ley 247 de 2004, Ley 243 de 1938, Reglamento 156, etc.)

**STUDY POINTS:**

{chunk_text}

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
        logger.info(f"✓ Generated {len(questions)} questions from {chunk_name}")

        return questions

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse response for {chunk_name}: {e}")
        logger.error(f"Response: {response_text[:500]}...")
        return []
    except Exception as e:
        logger.error(f"Error processing {chunk_name}: {e}", exc_info=True)
        return []


def save_markdown_files(study_text: str, file_id: str, questions: List[Dict]):
    """Save raw and cleaned markdown files."""
    import os

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
        f.write(f"Total Study Points: 117\n\n")
        f.write("---\n\n")
        f.write(study_text)

    logger.info(f"Saved raw markdown to: {raw_file}")

    # Save cleaned markdown
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
    parser.add_argument('--output', default='/tmp/preguntas_examen_all_questions.json',
                       help='Output file for all generated questions')
    parser.add_argument('--document-id', type=int, default=1,
                       help='Document ID to associate questions with')
    parser.add_argument('--execute', action='store_true',
                       help='Actually add questions to database')
    parser.add_argument('--file-id', default='preguntas_examen_leyes',
                       help='File ID for organizing output files')
    parser.add_argument('--delay', type=int, default=2,
                       help='Delay in seconds between API calls')
    args = parser.parse_args()

    logger.info("="*80)
    logger.info("PREGUNTAS EXAMEN DE LEYES - BATCHED QUESTION CONVERTER")
    logger.info("="*80)
    logger.info(f"Total chunks to process: {len(STUDY_CHUNKS)}")
    logger.info(f"Delay between chunks: {args.delay} seconds")
    logger.info("="*80)

    # Process all chunks
    all_questions = []

    for idx, chunk in enumerate(STUDY_CHUNKS, 1):
        logger.info(f"\n[{idx}/{len(STUDY_CHUNKS)}] {chunk['name']}")

        questions = convert_chunk_to_questions(chunk['content'], chunk['name'])

        if questions:
            all_questions.extend(questions)
            logger.info(f"Running total: {len(all_questions)} questions")

        # Add delay between API calls to avoid rate limiting
        if idx < len(STUDY_CHUNKS):
            logger.info(f"Waiting {args.delay} seconds before next chunk...")
            time.sleep(args.delay)

    logger.info("\n" + "="*80)
    logger.info(f"TOTAL QUESTIONS GENERATED: {len(all_questions)}")
    logger.info("="*80)

    if not all_questions:
        logger.error("No questions generated")
        return 1

    # Combine all study text for markdown
    full_study_text = "\n\n".join([
        f"# {chunk['name']}\n{chunk['content']}"
        for chunk in STUDY_CHUNKS
    ])

    # Save markdown files
    save_markdown_files(full_study_text, args.file_id, all_questions)

    # Save to JSON file
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, indent=2, ensure_ascii=False)
    logger.info(f"\nSaved {len(all_questions)} questions to: {args.output}")

    # Deduplicate
    importer = TestQuestionImporter(
        pdf_path="",
        document_id=args.document_id
    )

    logger.info("\n" + "="*80)
    logger.info("DEDUPLICATION")
    logger.info("="*80)

    new_questions, duplicates = importer.deduplicate_questions(all_questions)

    logger.info(f"\nDeduplication results:")
    logger.info(f"  Total generated: {len(all_questions)}")
    logger.info(f"  Duplicates: {len(duplicates)}")
    logger.info(f"  New questions: {len(new_questions)}")

    # Add to database
    dry_run = not args.execute
    added = importer.add_questions_to_database(new_questions, dry_run=dry_run)

    logger.info("\n" + "="*80)
    logger.info("FINAL SUMMARY")
    logger.info("="*80)
    logger.info(f"Questions generated: {len(all_questions)}")
    logger.info(f"Duplicates found: {len(duplicates)}")
    logger.info(f"New questions: {len(new_questions)}")
    logger.info(f"Questions added: {added if not dry_run else 0}")
    logger.info("="*80)

    return 0


if __name__ == '__main__':
    sys.exit(main())
