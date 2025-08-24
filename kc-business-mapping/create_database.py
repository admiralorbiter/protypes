#!/usr/bin/env python3
"""
Database Creation Script for KC Business License Mapper

This script processes the Business_License_Holders.csv file and creates an SQLite database
with proper indexing for efficient querying and filtering.
"""

import pandas as pd
import sqlite3
import re
import os
from typing import Optional, Dict, Tuple
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_gps_coordinates(location_str: str) -> Optional[Tuple[float, float]]:
    """
    Parse GPS coordinates from Location column string like 'POINT (-94.33846 39.12445)'
    Returns (latitude, longitude) tuple or None if invalid
    """
    if pd.isna(location_str) or location_str == '':
        return None
    
    # Extract coordinates using regex
    match = re.search(r'POINT \(([-\d.]+) ([\d.]+)\)', location_str)
    if match:
        longitude = float(match.group(1))
        latitude = float(match.group(2))
        return (latitude, longitude)
    return None

def clean_business_name(name: str, dba_name: str) -> str:
    """Clean and combine business name and DBA name"""
    if pd.notna(name) and name.strip():
        return name.strip()
    elif pd.notna(dba_name) and dba_name.strip():
        return dba_name.strip()
    return "Unknown Business"

def parse_license_date(date_str: str) -> Optional[str]:
    """Parse and validate license date"""
    if pd.isna(date_str) or date_str == '':
        return None
    
    try:
        # Handle various date formats
        if len(str(date_str)) == 8:  # Format: YYYYMMDD
            date_obj = datetime.strptime(str(date_str), '%Y%m%d')
            return date_obj.strftime('%Y-%m-%d')
        elif len(str(date_str)) == 4:  # Format: YYYY
            return f"{date_str}-01-01"
        else:
            # Try to parse as is
            date_obj = pd.to_datetime(date_str)
            return date_obj.strftime('%Y-%m-%d')
    except:
        return None

def create_database(csv_file: str, db_file: str = 'business_licenses.db'):
    """Create SQLite database from CSV data"""
    
    logger.info(f"Starting database creation from {csv_file}")
    
    # Check if CSV file exists
    if not os.path.exists(csv_file):
        logger.error(f"CSV file not found: {csv_file}")
        return False
    
    try:
        # Read CSV file
        logger.info("Reading CSV file...")
        df = pd.read_csv(csv_file)
        logger.info(f"Loaded {len(df)} records from CSV")
        
        # Create SQLite connection
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Create tables
        logger.info("Creating database tables...")
        
        # Main businesses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS businesses (
                id TEXT PRIMARY KEY,
                business_name TEXT,
                dba_name TEXT,
                business_type TEXT,
                address TEXT,
                city TEXT,
                state TEXT,
                zipcode TEXT,
                license_valid_until TEXT,
                latitude REAL,
                longitude REAL,
                has_coordinates BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Business types lookup table for better performance
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS business_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_type TEXT UNIQUE NOT NULL,
                count INTEGER DEFAULT 0
            )
        ''')
        
        # Cities lookup table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT UNIQUE NOT NULL,
                state TEXT NOT NULL,
                count INTEGER DEFAULT 0
            )
        ''')
        
        # States lookup table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                state_code TEXT UNIQUE NOT NULL,
                state_name TEXT,
                count INTEGER DEFAULT 0
            )
        ''')
        
        # Create indexes for better performance
        logger.info("Creating database indexes...")
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_business_type ON businesses(business_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_city ON businesses(city)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_state ON businesses(state)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_coordinates ON businesses(latitude, longitude)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_license_date ON businesses(license_valid_until)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_business_name ON businesses(business_name)')
        
        # Process data and insert into database
        logger.info("Processing and inserting data...")
        
        # Track statistics
        total_records = len(df)
        records_with_coordinates = 0
        records_inserted = 0
        
        # Prepare data for insertion
        business_types = set()
        cities = set()
        states = set()
        
        for index, row in df.iterrows():
            try:
                # Parse GPS coordinates
                coords = parse_gps_coordinates(row['Location'])
                has_coords = coords is not None
                
                if has_coords:
                    records_with_coordinates += 1
                    latitude, longitude = coords
                else:
                    latitude, longitude = None, None
                
                # Clean business name
                business_name = clean_business_name(row['Business Name'], row['DBA Name'])
                dba_name = row['DBA Name'] if pd.notna(row['DBA Name']) else ''
                
                # Parse license date
                license_date = parse_license_date(row['Valid License For'])
                
                # Collect unique values for lookup tables
                if pd.notna(row['Business Type']):
                    business_types.add(row['Business Type'].strip())
                if pd.notna(row['City']):
                    cities.add((row['City'].strip(), row['State'].strip()))
                if pd.notna(row['State']):
                    states.add(row['State'].strip())
                
                # Insert business record
                cursor.execute('''
                    INSERT OR REPLACE INTO businesses 
                    (id, business_name, dba_name, business_type, address, city, state, 
                     zipcode, license_valid_until, latitude, longitude, has_coordinates)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(row['ID']),
                    business_name,
                    dba_name,
                    row['Business Type'] if pd.notna(row['Business Type']) else '',
                    row['Address'] if pd.notna(row['Address']) else '',
                    row['City'] if pd.notna(row['City']) else '',
                    row['State'] if pd.notna(row['State']) else '',
                    row['Zipcode'] if pd.notna(row['Zipcode']) else '',
                    license_date,
                    latitude,
                    longitude,
                    has_coords
                ))
                
                records_inserted += 1
                
                # Progress indicator
                if (index + 1) % 1000 == 0:
                    logger.info(f"Processed {index + 1}/{total_records} records...")
                    
            except Exception as e:
                logger.warning(f"Error processing record {index}: {e}")
                continue
        
        # Populate lookup tables
        logger.info("Populating lookup tables...")
        
        # Business types
        for business_type in business_types:
            cursor.execute('''
                INSERT OR REPLACE INTO business_types (business_type, count)
                VALUES (?, (SELECT COUNT(*) FROM businesses WHERE business_type = ?))
            ''', (business_type, business_type))
        
        # Cities
        for city, state in cities:
            cursor.execute('''
                INSERT OR REPLACE INTO cities (city, state, count)
                VALUES (?, ?, (SELECT COUNT(*) FROM businesses WHERE city = ? AND state = ?))
            ''', (city, state, city, state))
        
        # States
        for state in states:
            cursor.execute('''
                INSERT OR REPLACE INTO states (state_code, count)
                VALUES (?, (SELECT COUNT(*) FROM businesses WHERE state = ?))
            ''', (state, state))
        
        # Commit changes
        conn.commit()
        
        # Get final statistics
        cursor.execute('SELECT COUNT(*) FROM businesses')
        total_in_db = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM businesses WHERE has_coordinates = 1')
        with_coords_in_db = cursor.fetchone()[0]
        
        logger.info("Database creation completed successfully!")
        logger.info(f"Total records processed: {total_records}")
        logger.info(f"Records inserted: {records_inserted}")
        logger.info(f"Records with coordinates: {records_with_coordinates}")
        logger.info(f"Total in database: {total_in_db}")
        logger.info(f"With coordinates in database: {with_coords_in_db}")
        logger.info(f"Database file: {db_file}")
        
        # Close connection
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        return False

def create_sample_queries(db_file: str = 'business_licenses.db'):
    """Create a file with sample SQL queries for the database"""
    
    queries = '''
-- Sample SQL Queries for KC Business License Database
-- File: business_licenses.db

-- 1. Get all businesses with coordinates
SELECT business_name, business_type, city, state, latitude, longitude
FROM businesses 
WHERE has_coordinates = 1
LIMIT 10;

-- 2. Count businesses by type
SELECT business_type, COUNT(*) as count
FROM businesses 
GROUP BY business_type 
ORDER BY count DESC 
LIMIT 20;

-- 3. Count businesses by city
SELECT city, state, COUNT(*) as count
FROM businesses 
GROUP BY city, state 
ORDER BY count DESC 
LIMIT 20;

-- 4. Find businesses in Kansas City, MO
SELECT business_name, business_type, address, latitude, longitude
FROM businesses 
WHERE city = 'KANSAS CITY' AND state = 'MO' AND has_coordinates = 1
LIMIT 20;

-- 5. Search for specific business types
SELECT business_name, city, state, latitude, longitude
FROM businesses 
WHERE business_type LIKE '%Software%' AND has_coordinates = 1
LIMIT 20;

-- 6. Get businesses by license expiration year
SELECT business_name, business_type, city, license_valid_until
FROM businesses 
WHERE license_valid_until LIKE '2025%'
LIMIT 20;

-- 7. Find businesses within a geographic area (approximate)
SELECT business_name, business_type, city, latitude, longitude
FROM businesses 
WHERE has_coordinates = 1
  AND latitude BETWEEN 39.0 AND 39.2
  AND longitude BETWEEN -94.7 AND -94.5
LIMIT 20;

-- 8. Count businesses with and without coordinates
SELECT 
    has_coordinates,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM businesses), 2) as percentage
FROM businesses 
GROUP BY has_coordinates;

-- 9. Get unique business types count
SELECT COUNT(DISTINCT business_type) as unique_business_types
FROM businesses;

-- 10. Get businesses with missing data
SELECT business_name, business_type, city, state
FROM businesses 
WHERE business_name = 'Unknown Business' OR city = '' OR state = ''
LIMIT 20;
'''
    
    with open('sample_queries.sql', 'w') as f:
        f.write(queries)
    
    logger.info("Sample queries saved to sample_queries.sql")

def main():
    """Main function"""
    csv_file = 'Business_License_Holders.csv'
    db_file = 'business_licenses.db'
    
    print("=" * 60)
    print("KC Business License Database Creator")
    print("=" * 60)
    
    # Check if CSV exists
    if not os.path.exists(csv_file):
        print(f"❌ Error: CSV file '{csv_file}' not found!")
        print("Please ensure the file is in the current directory.")
        return
    
    # Create database
    print(f"📁 Processing CSV file: {csv_file}")
    print(f"🗄️  Creating database: {db_file}")
    print()
    
    success = create_database(csv_file, db_file)
    
    if success:
        print("✅ Database created successfully!")
        print()
        
        # Create sample queries
        print("📝 Creating sample SQL queries...")
        create_sample_queries(db_file)
        print("✅ Sample queries saved to sample_queries.sql")
        print()
        
        print("🎉 Setup complete! You can now:")
        print("  1. Use the database with your Flask app")
        print("  2. Run sample queries from sample_queries.sql")
        print("  3. Modify app.py to use the database instead of CSV")
        
    else:
        print("❌ Failed to create database. Check the logs above for errors.")

if __name__ == '__main__':
    main()
