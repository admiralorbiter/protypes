# KC Business License Mapper

A Flask web application for mapping and exploring business license holders in the Kansas City area. This application parses GPS coordinates from business license data and displays businesses on an interactive map using Leaflet.js.

## Features

- **Interactive Map**: Uses Leaflet.js to display businesses with GPS coordinates
- **Search & Filter**: Search by business name/type and filter by business type or city
- **Business Details**: Click on map markers or business list items to view detailed information
- **Responsive Design**: Modern, mobile-friendly interface with Bootstrap styling
- **Real-time Statistics**: Shows total and visible business counts
- **Performance Optimized**: Handles large datasets efficiently

## Data Source

The application reads from `Business_License_Holders.csv` which contains:
- Business information (name, type, address, etc.)
- GPS coordinates in the format: `POINT (-94.33846 39.12445)`
- License validity dates
- Business classifications

## Installation

1. **Clone or download** the project files to your local machine

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure the CSV file** `Business_License_Holders.csv` is in the project root directory

4. **Create the SQLite database** (recommended for better performance):
   ```bash
   python create_database.py
   ```

## Usage

1. **Start the Flask application**:
   ```bash
   python app.py
   ```

2. **Open your web browser** and navigate to:
   ```
   http://localhost:5000
   ```

3. **Use the application**:
   - The map will automatically load with all businesses that have GPS coordinates
   - Use the sidebar to search and filter businesses
   - Click on map markers to view business details
   - Use the business list to quickly navigate to specific businesses

## API Endpoints

- `GET /` - Main application page
- `GET /api/businesses` - Get all businesses with coordinates
- `GET /api/businesses/search` - Search businesses with filters
- `GET /api/businesses/search_advanced` - Advanced search with geographic bounds
- `GET /api/business-types` - Get unique business types with counts
- `GET /api/cities` - Get unique cities with counts
- `GET /api/states` - Get unique states with counts
- `GET /api/statistics` - Get comprehensive database statistics
- `GET /api/business/<id>` - Get detailed business information
- `GET /api/geographic_bounds` - Get geographic bounds of all businesses

## File Structure

```
kc-business-mapping/
├── app.py                 # Main Flask application (database-enabled)
├── create_database.py     # Script to create SQLite database from CSV
├── db_utils.py           # Database utility and analysis tools
├── Business_License_Holders.csv  # Business data source
├── business_licenses.db   # SQLite database (created by script)
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── static/
│   ├── style.css         # Custom CSS styling
│   └── app.js            # JavaScript functionality
└── templates/
    └── index.html        # Main HTML template
```

## Technical Details

### GPS Coordinate Parsing
The application parses GPS coordinates from the `Location` column using regex:
- Format: `POINT (longitude latitude)`
- Example: `POINT (-94.33846 39.12445)`
- Only businesses with valid coordinates are displayed on the map

### Map Features
- **Base Map**: OpenStreetMap tiles
- **Markers**: Each business with coordinates gets a clickable marker
- **Popups**: Quick business information on marker click
- **Auto-fit**: Map automatically adjusts to show all visible markers

### Performance Considerations
- Business list is limited to 50 items for performance
- Data is loaded once and filtered client-side when possible
- Map markers are efficiently managed and cleared as needed

## Database Features

### Database Creation
The `create_database.py` script:
- Parses GPS coordinates from the `Location` column
- Creates optimized SQLite tables with proper indexing
- Builds lookup tables for business types, cities, and states
- Handles data cleaning and validation
- Provides detailed progress and statistics

### Database Utilities
The `db_utils.py` script provides:
- Database information and statistics
- Business search functionality
- Coverage analysis by various dimensions
- Sample query execution
- Data export to CSV
- Interactive menu for database operations

### Performance Benefits
- **Faster queries**: Indexed database vs. CSV parsing
- **Better memory usage**: No need to load entire CSV into memory
- **Advanced filtering**: SQL-based search and filtering
- **Scalability**: Handles large datasets efficiently
- **Data integrity**: Proper data types and constraints

## Customization

### Adding New Data Sources
To use different data sources, modify the `load_business_data()` function in `app.py` to:
- Read from different file formats
- Parse different coordinate formats
- Handle additional business fields

### Database Schema Modifications
To modify the database schema:
1. Update the table creation SQL in `create_database.py`
2. Re-run the database creation script
3. Update the Flask app queries accordingly

### Styling Changes
- Modify `static/style.css` for visual changes
- Update `templates/index.html` for layout changes
- Customize map appearance in `static/app.js`

### Map Configuration
- Change default map center and zoom in `initializeMap()`
- Add different map tile providers
- Customize marker icons and popup content

## Troubleshooting

### Common Issues

1. **No businesses appear on map**:
   - Check that the CSV file is in the correct location
   - Verify the CSV has a `Location` column with GPS data
   - Check browser console for JavaScript errors

2. **Map doesn't load**:
   - Ensure internet connection (required for map tiles)
   - Check browser console for errors
   - Verify Leaflet.js is loading correctly

3. **Performance issues with large datasets**:
   - Consider implementing pagination
   - Add clustering for map markers
   - Implement server-side filtering

### Debug Mode
The application runs in debug mode by default. For production:
- Set `debug=False` in `app.py`
- Configure proper WSGI server
- Set environment variables for production settings

## Future Enhancements

- **Marker Clustering**: Group nearby businesses for better performance
- **Advanced Filtering**: Date ranges, license status, business size
- **Export Features**: Download filtered data as CSV/JSON
- **Heat Maps**: Visualize business density
- **Analytics Dashboard**: Business type distribution, geographic analysis
- **User Accounts**: Save favorite businesses, custom searches

## License

This project is open source and available under the MIT License.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review browser console for error messages
3. Verify data format and file locations
4. Check Python dependencies are correctly installed
