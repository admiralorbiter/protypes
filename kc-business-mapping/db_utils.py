#!/usr/bin/env python3
"""
Database Utility Script for KC Business License Mapper

This script provides utility functions for database maintenance, analysis, and common operations.
"""

import sqlite3
import pandas as pd
import os
from contextlib import contextmanager

DATABASE = 'business_licenses.db'

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def get_database_info():
    """Get basic information about the database"""
    if not os.path.exists(DATABASE):
        print(f"❌ Database file '{DATABASE}' not found!")
        return
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get table information
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            print("=" * 60)
            print("DATABASE INFORMATION")
            print("=" * 60)
            print(f"Database file: {DATABASE}")
            print(f"File size: {os.path.getsize(DATABASE) / (1024*1024):.2f} MB")
            print(f"Tables: {', '.join(tables)}")
            print()
            
            # Get record counts for each table
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{table}: {count:,} records")
            
            print()
            
            # Get business statistics
            cursor.execute("SELECT COUNT(*) FROM businesses")
            total_businesses = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM businesses WHERE has_coordinates = 1")
            with_coordinates = cursor.fetchone()[0]
            
            print(f"Total businesses: {total_businesses:,}")
            print(f"With coordinates: {with_coordinates:,}")
            print(f"Coverage: {(with_coordinates/total_businesses*100):.1f}%")
            
    except Exception as e:
        print(f"Error getting database info: {e}")

def export_to_csv(table_name, output_file=None):
    """Export a table to CSV format"""
    if not output_file:
        output_file = f"{table_name}_export.csv"
    
    try:
        with get_db_connection() as conn:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            df.to_csv(output_file, index=False)
            print(f"✅ Exported {table_name} to {output_file}")
            print(f"   Records: {len(df):,}")
            print(f"   Columns: {len(df.columns)}")
            
    except Exception as e:
        print(f"❌ Error exporting {table_name}: {e}")

def search_businesses(search_term, limit=20):
    """Search businesses by name or type"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT business_name, business_type, city, state, 
                       latitude, longitude, has_coordinates
                FROM businesses 
                WHERE (LOWER(business_name) LIKE ? OR LOWER(business_type) LIKE ?)
                ORDER BY business_name
                LIMIT ?
            ''', (f'%{search_term.lower()}%', f'%{search_term.lower()}%', limit))
            
            results = cursor.fetchall()
            
            if results:
                print(f"🔍 Search results for '{search_term}' (showing {len(results)}):")
                print("-" * 80)
                for row in results:
                    coords_status = "📍" if row['has_coordinates'] else "❌"
                    print(f"{coords_status} {row['business_name']}")
                    print(f"   Type: {row['business_type']}")
                    print(f"   Location: {row['city']}, {row['state']}")
                    if row['has_coordinates']:
                        print(f"   Coordinates: {row['latitude']:.6f}, {row['longitude']:.6f}")
                    print()
            else:
                print(f"❌ No businesses found matching '{search_term}'")
                
    except Exception as e:
        print(f"❌ Error searching businesses: {e}")

def get_business_types_summary(limit=20):
    """Get summary of business types"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT business_type, count 
                FROM business_types 
                ORDER BY count DESC 
                LIMIT ?
            ''', (limit,))
            
            results = cursor.fetchall()
            
            print(f"📊 Top {len(results)} Business Types:")
            print("-" * 60)
            for i, row in enumerate(results, 1):
                print(f"{i:2d}. {row['business_type']:<40} {row['count']:>8,}")
                
    except Exception as e:
        print(f"❌ Error getting business types summary: {e}")

def get_cities_summary(limit=20):
    """Get summary of cities"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT city, state, count 
                FROM cities 
                ORDER BY count DESC 
                LIMIT ?
            ''', (limit,))
            
            results = cursor.fetchall()
            
            print(f"🏙️  Top {len(results)} Cities:")
            print("-" * 50)
            for i, row in enumerate(results, 1):
                print(f"{i:2d}. {row['city']:<25} {row['state']:<5} {row['count']:>8,}")
                
    except Exception as e:
        print(f"❌ Error getting cities summary: {e}")

def get_coverage_analysis():
    """Analyze coordinate coverage by different dimensions"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            print("📊 COORDINATE COVERAGE ANALYSIS")
            print("=" * 50)
            
            # Overall coverage
            cursor.execute("SELECT COUNT(*) FROM businesses")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM businesses WHERE has_coordinates = 1")
            with_coords = cursor.fetchone()[0]
            
            print(f"Overall coverage: {with_coords:,}/{total:,} ({(with_coords/total*100):.1f}%)")
            print()
            
            # Coverage by state
            cursor.execute('''
                SELECT state, 
                       COUNT(*) as total,
                       SUM(CASE WHEN has_coordinates = 1 THEN 1 ELSE 0 END) as with_coords,
                       ROUND(SUM(CASE WHEN has_coordinates = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as coverage
                FROM businesses 
                GROUP BY state 
                ORDER BY total DESC
                LIMIT 10
            ''')
            
            print("Coverage by State:")
            print("-" * 50)
            for row in cursor.fetchall():
                print(f"{row['state']:<5} {row['with_coords']:>6,}/{row['total']:<6,} ({row['coverage']:>5.1f}%)")
            
            print()
            
            # Coverage by business type
            cursor.execute('''
                SELECT business_type, 
                       COUNT(*) as total,
                       SUM(CASE WHEN has_coordinates = 1 THEN 1 ELSE 0 END) as with_coords,
                       ROUND(SUM(CASE WHEN has_coordinates = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as coverage
                FROM businesses 
                GROUP BY business_type 
                HAVING total > 10
                ORDER BY total DESC
                LIMIT 10
            ''')
            
            print("Coverage by Business Type (top 10):")
            print("-" * 60)
            for row in cursor.fetchall():
                print(f"{row['business_type'][:40]:<40} {row['with_coords']:>6,}/{row['total']:<6,} ({row['coverage']:>5.1f}%)")
                
    except Exception as e:
        print(f"❌ Error analyzing coverage: {e}")

def run_sample_queries():
    """Run some sample queries to test the database"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            print("🔍 SAMPLE QUERIES RESULTS")
            print("=" * 50)
            
            # Query 1: Businesses in Kansas City, MO
            cursor.execute('''
                SELECT business_name, business_type, address
                FROM businesses 
                WHERE city = 'KANSAS CITY' AND state = 'MO' AND has_coordinates = 1
                LIMIT 5
            ''')
            
            results = cursor.fetchall()
            print(f"1. Businesses in Kansas City, MO (showing {len(results)}):")
            for row in results:
                print(f"   • {row['business_name']} - {row['business_type']}")
            print()
            
            # Query 2: Software companies
            cursor.execute('''
                SELECT business_name, city, state
                FROM businesses 
                WHERE business_type LIKE '%Software%' AND has_coordinates = 1
                LIMIT 5
            ''')
            
            results = cursor.fetchall()
            print(f"2. Software companies (showing {len(results)}):")
            for row in results:
                print(f"   • {row['business_name']} - {row['city']}, {row['state']}")
            print()
            
            # Query 3: Geographic distribution
            cursor.execute('''
                SELECT 
                    CASE 
                        WHEN latitude BETWEEN 39.0 AND 39.2 AND longitude BETWEEN -94.7 AND -94.5 
                        THEN 'Kansas City Metro'
                        WHEN latitude BETWEEN 38.5 AND 40.0 AND longitude BETWEEN -95.0 AND -94.0 
                        THEN 'Greater KC Area'
                        ELSE 'Other'
                    END as region,
                    COUNT(*) as count
                FROM businesses 
                WHERE has_coordinates = 1
                GROUP BY region
                ORDER BY count DESC
            ''')
            
            results = cursor.fetchall()
            print("3. Geographic distribution:")
            for row in results:
                print(f"   • {row['region']}: {row['count']:,} businesses")
                
    except Exception as e:
        print(f"❌ Error running sample queries: {e}")

def main():
    """Main function with menu"""
    while True:
        print("\n" + "=" * 60)
        print("KC BUSINESS LICENSE DATABASE UTILITIES")
        print("=" * 60)
        print("1. Database Information")
        print("2. Search Businesses")
        print("3. Business Types Summary")
        print("4. Cities Summary")
        print("5. Coverage Analysis")
        print("6. Run Sample Queries")
        print("7. Export Table to CSV")
        print("0. Exit")
        print("-" * 60)
        
        choice = input("Enter your choice (0-7): ").strip()
        
        if choice == '0':
            print("👋 Goodbye!")
            break
        elif choice == '1':
            get_database_info()
        elif choice == '2':
            search_term = input("Enter search term: ").strip()
            if search_term:
                search_businesses(search_term)
        elif choice == '3':
            get_business_types_summary()
        elif choice == '4':
            get_cities_summary()
        elif choice == '5':
            get_coverage_analysis()
        elif choice == '6':
            run_sample_queries()
        elif choice == '7':
            print("Available tables: businesses, business_types, cities, states")
            table = input("Enter table name: ").strip()
            if table in ['businesses', 'business_types', 'cities', 'states']:
                export_to_csv(table)
            else:
                print("❌ Invalid table name")
        else:
            print("❌ Invalid choice. Please enter 0-7.")
        
        input("\nPress Enter to continue...")

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        print(f"❌ Database file '{DATABASE}' not found!")
        print("Please run 'python create_database.py' first to create the database.")
    else:
        main()
