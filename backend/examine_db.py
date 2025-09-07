#!/usr/bin/env python3
"""
Script to examine the existing event management database structure and content.
"""
import sqlite3
from pathlib import Path
from typing import List, Tuple, Any

from config import settings


def examine_database(db_path: str) -> None:
    """Examine the database structure and content."""
    
    if not Path(db_path).exists():
        print(f"❌ Database file not found: {db_path}")
        return
    
    print(f"🔍 Examining database: {db_path}")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = cursor.fetchall()
        
        print(f"📊 Found {len(tables)} tables:")
        for table in tables:
            print(f"   • {table[0]}")
        
        print("\n" + "=" * 60)
        
        # Examine each table structure
        for table in tables:
            table_name = table[0]
            print(f"\n📋 Table: {table_name}")
            print("-" * 40)
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print("🏗️  Schema:")
            for col in columns:
                col_id, name, data_type, not_null, default_val, pk = col
                pk_str = " 🔑" if pk else ""
                not_null_str = " NOT NULL" if not_null else ""
                default_str = f" DEFAULT {default_val}" if default_val else ""
                print(f"   • {name}: {data_type}{not_null_str}{default_str}{pk_str}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"📈 Row count: {count}")
            
            # Show sample data (first 3 rows)
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                sample_data = cursor.fetchall()
                print("📄 Sample data:")
                for i, row in enumerate(sample_data, 1):
                    print(f"   Row {i}: {row}")
            
            print()
        
        conn.close()
        print("✅ Database examination completed successfully!")
        
    except Exception as e:
        print(f"❌ Error examining database: {e}")


def main():
    """Main function to run database examination."""
    db_path = settings.database_path
    examine_database(db_path)


if __name__ == "__main__":
    main()
