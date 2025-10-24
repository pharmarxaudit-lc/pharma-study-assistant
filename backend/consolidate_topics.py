#!/usr/bin/env python3
"""
Topic Consolidation Script
Consolidates 147 topics into 15 major categories
"""

import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "pharma_exam.db"

# Consolidated topic mapping based on analysis
TOPIC_MAPPING = {
    "Licenciatura y Requisitos Profesionales": [
        "Requisitos para ejercer como Farmacéutico",
        "Requisitos de Licenciatura",
        "Requisitos para Ejercer - Farmacéutico",
        "Licenciatura por Reciprocidad",
        "Reciprocidad - Farmacéutico",
        "Renovación de Licencias",
        "Licencias Especializadas",
        "Licencias Farmacéuticas",
        "Licencias de Establecimientos",
        "Certificación Profesional",
        "Certificados Especiales",
        "Renovación de Certificados",
        "Horas de Práctica",
        "Horas de Práctica - Farmacéutico",
        "Certificación de Vacunas",
        "Administración de Vacunas",
        "Dispensación de Vacunas",
        "Vacunación sin Receta",
        "Registros de Vacunación",
    ],
    "Junta de Farmacia": [
        "Junta de Farmacia",
        "Junta de Farmacia - Composición",
        "Junta de Farmacia - Propósito y Funciones",
        "Composición de la Junta",
        "Cuerpos Regulatorios y División de Medicamentos",
        "División de Medicamentos y Farmacia",
        "Autoridad sobre Establecimientos",
        "Autoridad sobre Registros",
        "Poder Disciplinario",
        "Inspección Farmacéutica",
    ],
    "Colegio de Farmacéuticos": [
        "Colegio de Farmacéuticos de Puerto Rico",
        "Colegio de Farmacéuticos",
        "Colegio de Farmacéuticos - Administración",
        "Colegiación Profesional",
        "Colegiación",
        "Estructura CFPR",
    ],
    "Regulación de Establecimientos Farmacéuticos": [
        "Regulación de Establecimientos Farmacéuticos",
        "Operación de Farmacias",
        "Personal Farmacéutico",
        "Personal Requerido",
        "Notificaciones de Personal",
        "Supervisión Farmacéutica",
        "Supervisión de Personal",
        "Supervisión de Personal Técnico",
        "Supervisión de Internos",
    ],
    "Farmacéutico Regente y Funciones Profesionales": [
        "Farmacéutico Regente y Preceptor",
        "Funciones del Farmacéutico",
    ],
    "Técnicos de Farmacia": [
        "Técnico de Farmacia",
        "Técnico de Farmacia - Limitaciones",
        "Requisitos Técnico",
        "Requisitos de Técnicos",
        "Funciones del Técnico",
        "Educación Continua para Técnicos",
        "Horas de Práctica - Técnico",
    ],
    "Sustancias Controladas": [
        "Sustancias Controladas",
        "Medicamentos Controlados",
        "Clasificación de Controlados",
        "Control y Clasificación de Sustancias",
        "Reclasificación de Controlados",
        "Reclasificación de Sustancias Controladas",
        "Almacenaje de Medicamentos Controlados",
        "Almacenamiento de Controlados Clase II",
        "Conservación de Controlados",
        "Seguridad de Controlados",
        "Medidas de Seguridad para Controlados",
        "Registro de Sustancias Controladas",
        "Pedidos de Sustancias Controladas",
        "Hojas de Pedido",
        "Autorización para Órdenes de Controlados",
        "Requisitos para Expedir Controlados",
        "Orientación al Paciente sobre Controlados",
        "Inspección de Sustancias Controladas",
        "Inspectores de Controlados",
        "Dispensación de Narcóticos",
        "Despacho de Narcóticos",
        "Registros de Narcóticos",
        "Repetición de Narcóticos",
        "Repeticiones de Controlados",
        "Repetición de No Narcóticos Controlados",
        "Autoprescripción de Controlados",
        "Modificaciones en Recetas de Controlados",
        "Jeringuillas y Parafernalia",
        "Ley de Paraphernalia",
    ],
    "Cannabis Medicinal": [
        "Cannabis Medicinal",
        "Dispensación de Cannabis",
        "Dispensación de Cannabis Medicinal",
    ],
    "Dispensación y Procesamiento de Medicamentos": [
        "Medicamentos y su Dispensación",
        "Procesamiento de Recetas",
        "Evaluación y Completación de Recetas",
        "Información de Recetas",
        "Dispensación de Emergencia",
        "Suplidos de Emergencia",
        "Requisitos Especiales de Dispensación",
        "Entrega de Medicamentos",
        "Entregas a Domicilio",
        "Recetas Interestatales",
        "Recetas de Estados Unidos",
        "Manejo de Recetas Electrónicas",
        "Transmisión de Recetas",
        "Modificaciones de Recetas",
        "Prescribientes Autorizados",
        "Prescriptores Autorizados",
        "Medicamentos Veterinarios",
        "Industria Farmacéutica",
        "Dispositivos Médicos",
        "Registro de Dispositivos Médicos",
    ],
    "Intercambio y Sustitución de Medicamentos": [
        "Intercambio de Medicamentos",
        "Medicamentos Bioequivalentes",
        "Cambios a Bioequivalentes",
        "Productos Biológicos",
        "Intercambio de Biológicos",
        "Almacenamiento de Biológicos",
        "Medicamentos Especiales",
        "Medicamentos con Requisitos Especiales",
    ],
    "Etiquetado y Rotulación": [
        "Etiquetado de Medicamentos",
        "Requisitos de Etiquetado",
        "Requisitos de Rotulación",
        "Fechas de Expiración",
        "Fechas de Medicamentos",
        "Estabilidad y Expiración de Medicamentos",
        "Registro de Productos",
    ],
    "Documentación y Registros Farmacéuticos": [
        "Documentación Farmacéutica",
        "Documentación y Registros",
        "Documentación de Renuncias",
        "Mantenimiento de Registros Farmacéuticos",
        "Conservación de Expedientes",
        "Certificaciones de Salud",
        "Reporte de Errores en Medicación",
    ],
    "Ausencias del Farmacéutico": [
        "Ausencia del Farmacéutico",
        "Ausencias de Emergencia",
        "Ausencias por Alimentos",
        "Notificación de Ausencias",
        "Protocolos de Ausencia",
        "Excepciones en Ausencia del Farmacéutico",
    ],
    "Disciplina Profesional y Sanciones": [
        "Delitos y Conductas Prohibidas",
        "Denegación y Suspensión de Licencia",
        "Disciplina Profesional",
        "Infracciones y Sanciones",
        "Infracciones Técnicas",
        "Tipos de Infracciones",
        "Clasificación de Infracciones",
        "Protección Legal",
        "Limitaciones de la Ley del Buen Samaritano",
    ],
    "Responsabilidad Social y Obligaciones Profesionales": [
        "La Profesión de Farmacia - Responsabilidad Social",
        "Responsabilidad Profesional",
        "Responsabilidades Profesionales",
        "Obligaciones Profesionales",
        "Educación Continua",
    ],
}


def consolidate_topics():
    """Execute topic consolidation in database"""

    print("=" * 80)
    print("TOPIC CONSOLIDATION SCRIPT")
    print("=" * 80)
    print(f"Database: {DB_PATH}")
    print()

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Show current state
        cursor.execute("SELECT COUNT(DISTINCT topic_name) FROM questions WHERE topic_name IS NOT NULL")
        original_count = cursor.fetchone()[0]
        print(f"Original unique topics: {original_count}")

        cursor.execute("SELECT COUNT(*) FROM questions")
        total_questions = cursor.fetchone()[0]
        print(f"Total questions: {total_questions}")
        print()

        # Execute consolidation
        total_updated = 0

        for consolidated_topic, original_topics in TOPIC_MAPPING.items():
            print(f"Consolidating to: {consolidated_topic}")
            print(f"  Original topics: {len(original_topics)}")

            # Build UPDATE statement with all original topics
            placeholders = ','.join(['?'] * len(original_topics))
            update_sql = f"""
                UPDATE questions
                SET topic_name = ?
                WHERE topic_name IN ({placeholders})
            """

            # Execute update
            params = [consolidated_topic] + original_topics
            cursor.execute(update_sql, params)
            updated = cursor.rowcount
            total_updated += updated

            print(f"  Updated: {updated} questions")
            print()

        # Commit changes
        conn.commit()

        # Verify results
        print("=" * 80)
        print("CONSOLIDATION RESULTS")
        print("=" * 80)

        cursor.execute("SELECT COUNT(DISTINCT topic_name) FROM questions WHERE topic_name IS NOT NULL")
        new_count = cursor.fetchone()[0]
        print(f"New unique topics: {new_count}")
        print(f"Total questions updated: {total_updated}")
        print()

        # Show distribution of new topics
        print("Topic Distribution:")
        print("-" * 80)
        cursor.execute("""
            SELECT topic_name, COUNT(*) as count
            FROM questions
            WHERE topic_name IS NOT NULL
            GROUP BY topic_name
            ORDER BY count DESC
        """)

        for topic, count in cursor.fetchall():
            percentage = (count / total_questions) * 100
            print(f"  {topic:<50} {count:>3} questions ({percentage:>5.1f}%)")

        print()
        print("=" * 80)
        print("CONSOLIDATION COMPLETE!")
        print("=" * 80)

    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    consolidate_topics()
