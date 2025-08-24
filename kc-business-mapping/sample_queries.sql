
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
