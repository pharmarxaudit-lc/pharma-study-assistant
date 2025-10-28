#!/usr/bin/env python3
"""
Apply key_terms standardization to database.
Uses the reviewed JSON file from generate_keyterms_preview.py

⚠️  WARNING: This modifies the database. Backup is created automatically.
"""

import json
import sqlite3
import shutil
import time
from datetime import datetime

DB_PATH = '/Users/luiscotto/Code/pharma-study-assistant/backend/pharma_exam.db'
JSON_INPUT = 'keyterms_standardization_preview.json'

def create_backup():
    """Create database backup before applying changes."""

    timestamp = int(time.time())
    backup_path = f'/Users/luiscotto/Code/pharma-study-assistant/backend/pharma_exam_backup_keyterms_{timestamp}.db'

    print(f"\n📦 Creating backup: {backup_path}")
    shutil.copy2(DB_PATH, backup_path)
    print(f"   ✅ Backup created successfully")

    return backup_path

def load_preview_data():
    """Load the reviewed preview data."""

    print(f"\n📂 Loading preview data from: {JSON_INPUT}")

    try:
        with open(JSON_INPUT, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"   ✅ Loaded {data['total_conversions']} conversions")
        print(f"   📅 Generated: {data['generated_at']}")

        return data['conversions']

    except FileNotFoundError:
        print(f"\n❌ Error: {JSON_INPUT} not found!")
        print(f"   Please run generate_keyterms_preview.py first")
        return None
    except Exception as e:
        print(f"\n❌ Error loading preview data: {e}")
        return None

def apply_conversions(conversions):
    """Apply the conversions to the database."""

    print(f"\n🔧 Applying {len(conversions)} conversions to database...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    success_count = 0
    error_count = 0

    for idx, conversion in enumerate(conversions, 1):
        q_id = conversion['question_id']
        new_terms = conversion['after']

        print(f"   Processing {idx}/{len(conversions)}: Question {q_id}...", end='\r')

        try:
            # Convert to JSON string
            new_terms_json = json.dumps(new_terms, ensure_ascii=False)

            # Update database
            cursor.execute("""
                UPDATE questions
                SET key_terms_json = ?
                WHERE id = ?
            """, (new_terms_json, q_id))

            success_count += 1

        except Exception as e:
            print(f"\n   ❌ Error updating question {q_id}: {e}")
            error_count += 1

    conn.commit()
    conn.close()

    print(f"\n\n✅ Conversion complete!")
    print(f"   Success: {success_count}")
    print(f"   Errors: {error_count}")

    return success_count, error_count

def verify_conversions():
    """Verify that conversions were applied correctly."""

    print(f"\n🔍 Verifying conversions...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Count questions with object format
    cursor.execute("""
        SELECT COUNT(*)
        FROM questions
        WHERE key_terms_json LIKE '%"term":%'
        AND key_terms_json LIKE '%"definition":%'
    """)

    object_format_count = cursor.fetchone()[0]

    # Count questions with string array format
    cursor.execute("""
        SELECT COUNT(*)
        FROM questions
        WHERE key_terms_json NOT LIKE '%"term":%'
        AND LENGTH(key_terms_json) > 2
    """)

    string_format_count = cursor.fetchone()[0]

    conn.close()

    print(f"\n📊 Database Status:")
    print(f"   Object format: {object_format_count}")
    print(f"   String format: {string_format_count}")

    if string_format_count == 0:
        print(f"\n   ✅ All questions now use object format!")
        return True
    else:
        print(f"\n   ⚠️  Still {string_format_count} questions with string format")
        return False

def main():
    """Main execution flow."""

    print("\n" + "="*80)
    print("KEY TERMS STANDARDIZATION - APPLY TO DATABASE")
    print("="*80)

    print("\n⚠️  WARNING: This will modify the database!")
    print("   A backup will be created automatically.")

    # Ask for confirmation
    response = input("\n❓ Continue with database update? (yes/no): ").strip().lower()

    if response not in ['yes', 'y']:
        print("\n❌ Operation cancelled by user")
        return False

    # Load preview data
    conversions = load_preview_data()
    if not conversions:
        return False

    # Create backup
    backup_path = create_backup()

    # Apply conversions
    success_count, error_count = apply_conversions(conversions)

    # Verify
    all_converted = verify_conversions()

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\n✅ Conversions applied: {success_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📦 Backup: {backup_path}")

    if all_converted:
        print(f"\n🎉 SUCCESS! All key_terms now use consistent object format.")
        print(f"\n📝 Next Steps:")
        print(f"   1. Test the application to verify everything works")
        print(f"   2. If issues occur, restore from backup")
        print(f"   3. Deploy the updated database to production")
    else:
        print(f"\n⚠️  Some questions still need conversion")
        print(f"   Check the logs above for details")

    print("\n" + "="*80)

    return all_converted

if __name__ == '__main__':
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
