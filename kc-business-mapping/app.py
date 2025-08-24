from flask import Flask, render_template, jsonify, request
import sqlite3
import json
from typing import List, Dict, Optional
from contextlib import contextmanager

app = Flask(__name__)

# Database configuration
DATABASE = 'business_licenses.db'

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    try:
        yield conn
    finally:
        conn.close()

def dict_from_row(row):
    """Convert sqlite3.Row to dictionary"""
    return dict(zip(row.keys(), row))

def load_business_data() -> List[Dict]:
    """Load business data from SQLite database"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, business_name, dba_name, business_type, address, 
                       city, state, zipcode, license_valid_until, 
                       latitude, longitude, has_coordinates
                FROM businesses 
                WHERE has_coordinates = 1
                ORDER BY business_name
            ''')
            
            businesses = []
            for row in cursor.fetchall():
                business = dict_from_row(row)
                if business['latitude'] and business['longitude']:
                    business['coordinates'] = {
                        'lat': float(business['latitude']),
                        'lng': float(business['longitude'])
                    }
                    businesses.append(business)
            
            return businesses
    except Exception as e:
        print(f"Error loading data from database: {e}")
        return []

@app.route('/')
def index():
    """Main page with the map"""
    return render_template('index.html')

@app.route('/api/businesses')
def get_businesses():
    """API endpoint to get all businesses with coordinates"""
    try:
        businesses = load_business_data()
        print(f"Returning {len(businesses)} businesses with coordinates")
        return jsonify(businesses)
    except Exception as e:
        print(f"Error in get_businesses: {e}")
        return jsonify([])

@app.route('/api/businesses/search')
def search_businesses():
    """API endpoint to search businesses by name, type, or city"""
    query = request.args.get('q', '').lower()
    business_type = request.args.get('type', '').lower()
    city = request.args.get('city', '').lower()
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Build the SQL query dynamically
            sql = '''
                SELECT id, business_name, dba_name, business_type, address, 
                       city, state, zipcode, license_valid_until, 
                       latitude, longitude, has_coordinates
                FROM businesses 
                WHERE has_coordinates = 1
            '''
            params = []
            
            # Add search conditions
            if query:
                sql += ' AND (LOWER(business_name) LIKE ? OR LOWER(business_type) LIKE ?)'
                params.extend([f'%{query}%', f'%{query}%'])
            
            if business_type:
                sql += ' AND LOWER(business_type) LIKE ?'
                params.append(f'%{business_type}%')
            
            if city:
                sql += ' AND LOWER(city) LIKE ?'
                params.append(f'%{city}%')
            
            sql += ' ORDER BY business_name'
            
            cursor.execute(sql, params)
            
            businesses = []
            for row in cursor.fetchall():
                business = dict_from_row(row)
                if business['latitude'] and business['longitude']:
                    business['coordinates'] = {
                        'lat': float(business['latitude']),
                        'lng': float(business['longitude'])
                    }
                    businesses.append(business)
            
            return jsonify(businesses)
            
    except Exception as e:
        print(f"Error searching businesses: {e}")
        return jsonify([])

@app.route('/api/businesses/search_advanced')
def search_businesses_advanced():
    """Advanced search with multiple filters"""
    query = request.args.get('q', '').lower()
    business_type = request.args.get('type', '').lower()
    city = request.args.get('city', '').lower()
    state = request.args.get('state', '').lower()
    min_lat = request.args.get('min_lat')
    max_lat = request.args.get('max_lat')
    min_lng = request.args.get('min_lng')
    max_lng = request.args.get('max_lng')
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            sql = '''
                SELECT id, business_name, dba_name, business_type, address, 
                       city, state, zipcode, license_valid_until, 
                       latitude, longitude, has_coordinates
                FROM businesses 
                WHERE has_coordinates = 1
            '''
            params = []
            
            # Add search conditions
            if query:
                sql += ' AND (LOWER(business_name) LIKE ? OR LOWER(business_type) LIKE ?)'
                params.extend([f'%{query}%', f'%{query}%'])
            
            if business_type:
                sql += ' AND LOWER(business_type) LIKE ?'
                params.append(f'%{business_type}%')
            
            if city:
                sql += ' AND LOWER(city) LIKE ?'
                params.append(f'%{city}%')
            
            if state:
                sql += ' AND LOWER(state) LIKE ?'
                params.append(f'%{state}%')
            
            # Geographic bounds
            if min_lat and max_lat:
                sql += ' AND latitude BETWEEN ? AND ?'
                params.extend([float(min_lat), float(max_lat)])
            
            if min_lng and max_lng:
                sql += ' AND longitude BETWEEN ? AND ?'
                params.extend([float(min_lng), float(max_lng)])
            
            sql += ' ORDER BY business_name'
            
            cursor.execute(sql, params)
            
            businesses = []
            for row in cursor.fetchall():
                business = dict_from_row(row)
                if business['latitude'] and business['longitude']:
                    business['coordinates'] = {
                        'lat': float(business['latitude']),
                        'lng': float(business['longitude'])
                    }
                    businesses.append(business)
            
            return jsonify(businesses)
            
    except Exception as e:
        print(f"Error in advanced search: {e}")
        return jsonify([])

@app.route('/api/business-types')
def get_business_types():
    """API endpoint to get unique business types for filtering"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT business_type, count 
                FROM business_types 
                ORDER BY count DESC, business_type
            ''')
            
            types = [dict_from_row(row) for row in cursor.fetchall()]
            return jsonify(types)
    except Exception as e:
        print(f"Error loading business types: {e}")
        return jsonify([])

@app.route('/api/cities')
def get_cities():
    """API endpoint to get unique cities for filtering"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT city, state, count 
                FROM cities 
                ORDER BY count DESC, city
            ''')
            
            cities = [dict_from_row(row) for row in cursor.fetchall()]
            return jsonify(cities)
    except Exception as e:
        print(f"Error loading cities: {e}")
        return jsonify([])

@app.route('/api/states')
def get_states():
    """API endpoint to get unique states for filtering"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT state_code, count 
                FROM states 
                ORDER BY count DESC, state_code
            ''')
            
            states = [dict_from_row(row) for row in cursor.fetchall()]
            return jsonify(states)
    except Exception as e:
        print(f"Error loading states: {e}")
        return jsonify([])

@app.route('/api/statistics')
def get_statistics():
    """API endpoint to get database statistics"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Total businesses
            cursor.execute('SELECT COUNT(*) FROM businesses')
            total_businesses = cursor.fetchone()[0]
            
            # Businesses with coordinates
            cursor.execute('SELECT COUNT(*) FROM businesses WHERE has_coordinates = 1')
            with_coordinates = cursor.fetchone()[0]
            
            # Unique business types
            cursor.execute('SELECT COUNT(*) FROM business_types')
            unique_types = cursor.fetchone()[0]
            
            # Unique cities
            cursor.execute('SELECT COUNT(*) FROM cities')
            unique_cities = cursor.fetchone()[0]
            
            # Top business types
            cursor.execute('''
                SELECT business_type, count 
                FROM business_types 
                ORDER BY count DESC 
                LIMIT 10
            ''')
            top_types = [dict_from_row(row) for row in cursor.fetchall()]
            
            # Top cities
            cursor.execute('''
                SELECT city, state, count 
                FROM cities 
                ORDER BY count DESC 
                LIMIT 10
            ''')
            top_cities = [dict_from_row(row) for row in cursor.fetchall()]
            
            stats = {
                'total_businesses': total_businesses,
                'with_coordinates': with_coordinates,
                'unique_business_types': unique_types,
                'unique_cities': unique_cities,
                'top_business_types': top_types,
                'top_cities': top_cities,
                'coverage_percentage': round((with_coordinates / total_businesses * 100), 2) if total_businesses > 0 else 0
            }
            
            return jsonify(stats)
            
    except Exception as e:
        print(f"Error loading statistics: {e}")
        return jsonify({})

@app.route('/api/business/<business_id>')
def get_business_details(business_id):
    """API endpoint to get detailed information for a specific business"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM businesses WHERE id = ?
            ''', (business_id,))
            
            row = cursor.fetchone()
            if row:
                business = dict_from_row(row)
                if business['latitude'] and business['longitude']:
                    business['coordinates'] = {
                        'lat': float(business['latitude']),
                        'lng': float(business['longitude'])
                    }
                return jsonify(business)
            else:
                return jsonify({'error': 'Business not found'}), 404
                
    except Exception as e:
        print(f"Error loading business details: {e}")
        return jsonify({'error': 'Database error'}), 500

@app.route('/api/geographic_bounds')
def get_geographic_bounds():
    """API endpoint to get the geographic bounds of all businesses"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    MIN(latitude) as min_lat,
                    MAX(latitude) as max_lat,
                    MIN(longitude) as min_lng,
                    MAX(longitude) as max_lng
                FROM businesses 
                WHERE has_coordinates = 1
            ''')
            
            bounds = dict_from_row(cursor.fetchone())
            return jsonify(bounds)
            
    except Exception as e:
        print(f"Error loading geographic bounds: {e}")
        return jsonify({})

if __name__ == '__main__':
    # Check if database exists
    import os
    if not os.path.exists(DATABASE):
        print(f"❌ Database file '{DATABASE}' not found!")
        print("Please run 'python create_database.py' first to create the database.")
    else:
        print(f"✅ Database found: {DATABASE}")
        print("🚀 Starting Flask application...")
        app.run(debug=True, host='0.0.0.0', port=5000)