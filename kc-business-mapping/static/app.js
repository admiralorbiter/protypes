// Global variables
let map;
let markers = [];
let allBusinesses = [];
let currentMarkers = [];
let markerClusterGroup;
let isDataLoaded = false;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing application...');
    
    // Ensure map container is ready
    ensureMapContainerReady();
    
    initializeMap();
    loadBusinessData();
    setupEventListeners();
});

// Ensure map container is properly sized and ready
function ensureMapContainerReady() {
    const mapContainer = document.getElementById('map');
    console.log('Map container element:', mapContainer);
    console.log('Map container dimensions:', mapContainer.offsetWidth, 'x', mapContainer.offsetHeight);
    
    // Force container to be visible and sized
    mapContainer.style.display = 'block';
    mapContainer.style.height = '100%';
    mapContainer.style.width = '100%';
    mapContainer.style.position = 'relative';
    
    // Wait a bit for the container to be properly sized
    setTimeout(() => {
        console.log('Map container ready, dimensions:', mapContainer.offsetWidth, 'x', mapContainer.offsetHeight);
    }, 100);
}

// Initialize Leaflet map
function initializeMap() {
    console.log('Initializing map...');
    
    // Center on Kansas City area
    map = L.map('map', {
        zoomControl: true,
        doubleClickZoom: true,
        scrollWheelZoom: true,
        dragging: true,
        touchZoom: true,
        boxZoom: true,
        keyboard: true,
        tap: true,
        bounceAtZoomLimits: false,
        maxZoom: 18,
        minZoom: 8
    }).setView([39.0997, -94.5786], 10);
    
    console.log('Map created:', map);
    console.log('Map container:', document.getElementById('map'));
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18,
        updateWhenIdle: true,
        updateWhenZooming: false
    }).addTo(map);
    
    // Add scale control
    L.control.scale().addTo(map);
    
    // Initialize marker clustering with optimized settings
    markerClusterGroup = L.markerClusterGroup({
        chunkedLoading: true,
        chunkInterval: 100,  // Reduced from 200
        chunkDelay: 25,      // Reduced from 50
        maxClusterRadius: 60, // Reduced from 80 for better performance
        spiderfyOnMaxZoom: true,
        showCoverageOnHover: false, // Disabled for better performance
        zoomToBoundsOnClick: true,
        disableClusteringAtZoom: 15, // Reduced from 16
        chunkProgress: updateLoadingProgress, // Use our progress function
        animate: false, // Disable animations for better performance
        animateAddingMarkers: false
    });
    map.addLayer(markerClusterGroup);
    
    console.log('Marker cluster group added');
    
    // Test map interactions
    testMapInteractions();
    
    // Add performance monitoring
    map.on('zoomstart', function() {
        console.log('Zoom started');
    });
    
    map.on('zoomend', function() {
        console.log('Zoom ended at level:', map.getZoom());
    });
    
    map.on('movestart', function() {
        console.log('Map movement started');
    });
    
    map.on('moveend', function() {
        console.log('Map movement ended');
    });
    
    // Add click event to test if map is responsive
    map.on('click', function(e) {
        console.log('Map clicked at:', e.latlng);
    });
    
    console.log('Map initialization complete');
}

// Test map interactions
function testMapInteractions() {
    console.log('=== MAP INTERACTION TEST ===');
    console.log('Map object:', map);
    console.log('Map container element:', document.getElementById('map'));
    console.log('Map size:', map.getSize());
    console.log('Map zoom:', map.getZoom());
    console.log('Map center:', map.getCenter());
    console.log('Marker cluster group:', markerClusterGroup);
    console.log('Number of markers:', markerClusterGroup ? markerClusterGroup.getLayers().length : 'N/A');
    
    // Test if map is responsive to programmatic changes
    try {
        console.log('Testing programmatic zoom...');
        const currentZoom = map.getZoom();
        map.setZoom(currentZoom + 1);
        console.log('Zoom test: SUCCESS - zoom changed from', currentZoom, 'to', map.getZoom());
    } catch (error) {
        console.error('Zoom test: FAILED -', error);
    }
    
    try {
        console.log('Testing programmatic pan...');
        const currentCenter = map.getCenter();
        // Use setView instead of panTo to avoid triggering movement events
        map.setView([currentCenter.lat + 0.01, currentCenter.lng + 0.01], map.getZoom());
        console.log('Pan test: SUCCESS - center moved');
    } catch (error) {
        console.error('Pan test: FAILED -', error);
    }
    
    // Test if map container has proper dimensions
    const mapContainer = document.getElementById('map');
    const rect = mapContainer.getBoundingClientRect();
    console.log('Map container bounding rect:', rect);
    console.log('Map container computed styles:', {
        width: getComputedStyle(mapContainer).width,
        height: getComputedStyle(mapContainer).height,
        position: getComputedStyle(mapContainer).position,
        zIndex: getComputedStyle(mapContainer).zIndex
    });
    
    // Test if Leaflet controls are present
    const zoomControls = document.querySelectorAll('.leaflet-control-zoom');
    console.log('Zoom controls found:', zoomControls.length);
    
    // Test if map events are working
    console.log('Map event listeners:', {
        hasZoomStart: map.hasEventListeners('zoomstart'),
        hasMoveStart: map.hasEventListeners('movestart'),
        hasClick: map.hasEventListeners('click')
    });
    
    console.log('=== END MAP INTERACTION TEST ===');
}

// Load business data from API
async function loadBusinessData() {
    try {
        showLoading(true);
        
        // Load all data with progress indication
        console.log('Loading business data...');
        const startTime = performance.now();
        
        const response = await fetch('/api/businesses');
        allBusinesses = await response.json();
        
        const loadTime = performance.now() - startTime;
        console.log(`Loaded ${allBusinesses.length} businesses in ${loadTime.toFixed(2)}ms`);
        
        // Load filter options
        await loadFilterOptions();
        
        // Display businesses in chunks for better performance
        const displayStartTime = performance.now();
        displayBusinessesInChunks(allBusinesses);
        
        // Update statistics
        updateStatistics();
        
        isDataLoaded = true;
        showLoading(false);
        
        // Fit map to show all markers
        if (markerClusterGroup.getLayers().length > 0) {
            map.fitBounds(markerClusterGroup.getBounds().pad(0.1));
        }
        
        const totalTime = performance.now() - startTime;
        console.log(`Total initialization time: ${totalTime.toFixed(2)}ms`);
        
        // Force map refresh and test interactions
        setTimeout(() => {
            console.log('Forcing map refresh...');
            map.invalidateSize();
            
            // Test map interactions after data load
            console.log('Testing map interactions after data load...');
            console.log('Map zoom level:', map.getZoom());
            console.log('Map center:', map.getCenter());
            console.log('Map size:', map.getSize());
            
            // Try to programmatically move the map
            const currentCenter = map.getCenter();
            map.setView([currentCenter.lat + 0.01, currentCenter.lng + 0.01], map.getZoom());
            
            console.log('Map interaction test completed');
        }, 500);
        
    } catch (error) {
        console.error('Error loading business data:', error);
        showLoading(false);
        showError('Failed to load business data. Please try again.');
    }
}

// Performance monitoring function
function logPerformanceMetrics() {
    if (map && markerClusterGroup) {
        const zoom = map.getZoom();
        const center = map.getCenter();
        const markerCount = markerClusterGroup.getLayers().length;
        const clusterCount = markerClusterGroup.getVisibleParent().length;
        
        console.log(`Performance Metrics:
            - Zoom Level: ${zoom}
            - Center: ${center.lat.toFixed(4)}, ${center.lng.toFixed(4)}
            - Total Markers: ${markerCount}
            - Visible Clusters: ${clusterCount}
            - Map Size: ${map.getSize().x}x${map.getSize().y}
        `);
    }
}

// Load filter options (business types and cities)
async function loadFilterOptions() {
    try {
        // Load business types
        const typesResponse = await fetch('/api/business-types');
        const businessTypes = await typesResponse.json();
        
        const typeSelect = document.getElementById('businessTypeFilter');
        businessTypes.forEach(type => {
            const option = document.createElement('option');
            option.value = type;
            option.textContent = type;
            typeSelect.appendChild(option);
        });
        
        // Load cities
        const citiesResponse = await fetch('/api/cities');
        const cities = await citiesResponse.json();
        
        const citySelect = document.getElementById('cityFilter');
        cities.forEach(city => {
            const option = document.createElement('option');
            option.value = city;
            option.textContent = city;
            citySelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading filter options:', error);
    }
}

// Display businesses on the map in chunks for better performance
function displayBusinessesInChunks(businesses) {
    // Clear existing markers
    clearMarkers();
    
    // Filter businesses with valid coordinates
    const validBusinesses = businesses.filter(business => business.coordinates);
    console.log(`Displaying ${validBusinesses.length} businesses with coordinates`);
    
    // Process in smaller chunks for better performance
    const chunkSize = 500; // Reduced from 1000
    let currentIndex = 0;
    
    function processChunk() {
        const chunk = validBusinesses.slice(currentIndex, currentIndex + chunkSize);
        
        chunk.forEach(business => {
            if (business.coordinates) {
                // Create marker with minimal popup content for better performance
                const marker = L.marker([business.coordinates.lat, business.coordinates.lng], {
                    title: business.business_name || business.dba_name || 'Business'
                });
                
                // Only bind popup on click for better performance
                marker.on('click', () => {
                    marker.bindPopup(createPopupContent(business)).openPopup();
                    showBusinessDetails(business);
                });
                
                markerClusterGroup.addLayer(marker);
                currentMarkers.push(marker);
            }
        });
        
        currentIndex += chunkSize;
        
        // Update progress
        const progress = Math.min((currentIndex / validBusinesses.length) * 100, 100);
        updateLoadingProgress(progress);
        
        // Continue with next chunk or finish
        if (currentIndex < validBusinesses.length) {
            // Use requestAnimationFrame for better performance
            requestAnimationFrame(() => {
                setTimeout(processChunk, 5); // Reduced delay from 10ms
            });
        } else {
            console.log(`Finished displaying ${currentMarkers.length} markers`);
            updateBusinessList(businesses);
            document.getElementById('visibleBusinesses').textContent = currentMarkers.length;
            
            // Force a map refresh after all markers are added
            map.invalidateSize();
            
            // Update debug info
            updateDebugInfo();
        }
    }
    
    // Start processing chunks
    processChunk();
}

// Display businesses on the map (legacy function for compatibility)
function displayBusinesses(businesses) {
    displayBusinessesInChunks(businesses);
}

// Create popup content for map markers
function createPopupContent(business) {
    return `
        <div class="popup-content">
            <h5>${business.name || business.dba_name}</h5>
            <p><strong>Type:</strong> ${business.business_type}</p>
            <p><strong>Address:</strong> ${business.address}</p>
            <p><strong>City:</strong> ${business.city}, ${business.state} ${business.zipcode}</p>
            <button class="btn btn-sm btn-primary mt-2" onclick="showBusinessDetails(${JSON.stringify(business).replace(/"/g, '&quot;')})">
                View Details
            </button>
        </div>
    `;
}

// Show business details in modal
function showBusinessDetails(business) {
    const modal = new bootstrap.Modal(document.getElementById('businessModal'));
    const modalTitle = document.getElementById('businessModalTitle');
    const modalBody = document.getElementById('businessModalBody');
    
    modalTitle.textContent = business.name || business.dba_name;
    
    modalBody.innerHTML = `
        <div class="business-detail-grid">
            <div class="business-detail-item">
                <div class="business-detail-label">Business Name</div>
                <div class="business-detail-value">${business.name || 'N/A'}</div>
            </div>
            <div class="business-detail-item">
                <div class="business-detail-label">DBA Name</div>
                <div class="business-detail-value">${business.dba_name || 'N/A'}</div>
            </div>
            <div class="business-detail-item">
                <div class="business-detail-label">Business Type</div>
                <div class="business-detail-value">${business.business_type}</div>
            </div>
            <div class="business-detail-item">
                <div class="business-detail-label">Address</div>
                <div class="business-detail-value">${business.address}</div>
            </div>
            <div class="business-detail-item">
                <div class="business-detail-label">City</div>
                <div class="business-detail-value">${business.city}, ${business.state} ${business.zipcode}</div>
            </div>
            <div class="business-detail-item">
                <div class="business-detail-label">License Valid Until</div>
                <div class="business-detail-value">${business.valid_license_for}</div>
            </div>
            <div class="business-detail-item">
                <div class="business-detail-label">Coordinates</div>
                <div class="business-detail-value">${business.coordinates.lat.toFixed(6)}, ${business.coordinates.lng.toFixed(6)}</div>
            </div>
            <div class="business-detail-item">
                <div class="business-detail-label">Business ID</div>
                <div class="business-detail-value">${business.id}</div>
            </div>
        </div>
    `;
    
    modal.show();
}

// Update business list in sidebar
function updateBusinessList(businesses) {
    const businessList = document.getElementById('businessList');
    businessList.innerHTML = '';
    
    businesses.slice(0, 50).forEach(business => { // Limit to first 50 for performance
        const businessItem = document.createElement('div');
        businessItem.className = 'business-item fade-in';
        businessItem.innerHTML = `
            <h6>${business.name || business.dba_name}</h6>
            <p>${business.business_type}</p>
            <p>${business.city}, ${business.state}</p>
        `;
        
        businessItem.addEventListener('click', () => {
            // Center map on this business
            if (business.coordinates) {
                map.setView([business.coordinates.lat, business.coordinates.lng], 15);
                
                // Find and open popup for this marker
                currentMarkers.forEach(marker => {
                    const markerLatLng = marker.getLatLng();
                    if (markerLatLng.lat === business.coordinates.lat && 
                        markerLatLng.lng === business.coordinates.lng) {
                        marker.openPopup();
                    }
                });
            }
        });
        
        businessList.appendChild(businessItem);
    });
    
    if (businesses.length > 50) {
        const moreItem = document.createElement('div');
        moreItem.className = 'business-item text-center text-muted';
        moreItem.innerHTML = `<p>... and ${businesses.length - 50} more businesses</p>`;
        businessList.appendChild(moreItem);
    }
}

// Clear all markers from the map
function clearMarkers() {
    markerClusterGroup.clearLayers();
    currentMarkers = [];
}

// Update statistics
function updateStatistics() {
    document.getElementById('totalBusinesses').textContent = allBusinesses.length;
    document.getElementById('visibleBusinesses').textContent = allBusinesses.length;
}

// Search and filter businesses
async function searchBusinesses() {
    const searchQuery = document.getElementById('searchInput').value;
    const businessType = document.getElementById('businessTypeFilter').value;
    const city = document.getElementById('cityFilter').value;
    
    try {
        const params = new URLSearchParams();
        if (searchQuery) params.append('q', searchQuery);
        if (businessType) params.append('type', businessType);
        if (city) params.append('city', city);
        
        const response = await fetch(`/api/businesses/search?${params}`);
        const filteredBusinesses = await response.json();
        
        displayBusinesses(filteredBusinesses);
    } catch (error) {
        console.error('Error searching businesses:', error);
        showError('Failed to search businesses. Please try again.');
    }
}

// Clear all filters
function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('businessTypeFilter').value = '';
    document.getElementById('cityFilter').value = '';
    
    // Display all businesses
    displayBusinesses(allBusinesses);
}

// Setup event listeners
function setupEventListeners() {
    // Search button
    document.getElementById('searchBtn').addEventListener('click', searchBusinesses);
    
    // Search input (search on Enter key)
    document.getElementById('searchInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchBusinesses();
        }
    });
    
    // Filter changes
    document.getElementById('businessTypeFilter').addEventListener('change', searchBusinesses);
    document.getElementById('cityFilter').addEventListener('change', searchBusinesses);
    
    // Clear filters button
    document.getElementById('clearFilters').addEventListener('click', clearFilters);
    
    // Test map button
    document.getElementById('testMapBtn').addEventListener('click', testMapInteractions);
    
    // Add map performance optimizations
    if (map) {
        // Remove suspend/resume calls that don't exist in this version
        // Just log the events for debugging
        map.on('zoomstart', function() {
            console.log('Zoom started');
        });
        
        map.on('zoomend', function() {
            console.log('Zoom ended at level:', map.getZoom());
            updateDebugInfo();
        });
        
        map.on('movestart', function() {
            console.log('Map movement started');
        });
        
        map.on('moveend', function() {
            console.log('Map movement ended');
            updateDebugInfo();
        });
    }
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+D to toggle debug panel
        if (e.ctrlKey && e.key === 'd') {
            e.preventDefault();
            toggleDebugPanel();
        }
        
        // Ctrl+P to log performance metrics
        if (e.ctrlKey && e.key === 'p') {
            e.preventDefault();
            logPerformanceMetrics();
        }
    });
}

// Toggle debug panel
function toggleDebugPanel() {
    const debugPanel = document.getElementById('debugPanel');
    if (debugPanel.style.display === 'none') {
        debugPanel.style.display = 'block';
        updateDebugInfo();
        console.log('Debug panel enabled. Use Ctrl+D to hide, Ctrl+P for performance log.');
    } else {
        debugPanel.style.display = 'none';
    }
}

// Update debug information
function updateDebugInfo() {
    if (map && markerClusterGroup) {
        document.getElementById('debugZoom').textContent = map.getZoom();
        document.getElementById('debugMarkers').textContent = markerClusterGroup.getLayers().length;
        
        // Fix the getVisibleParent call - use a safer method
        try {
            const visibleClusters = markerClusterGroup.getLayers().filter(layer => 
                layer._icon && layer._icon.style.display !== 'none'
            ).length;
            document.getElementById('debugClusters').textContent = visibleClusters;
        } catch (error) {
            document.getElementById('debugClusters').textContent = 'N/A';
        }
        
        // Update performance status
        const markerCount = markerClusterGroup.getLayers().length;
        const performanceStatus = document.getElementById('performanceStatus');
        
        if (performanceStatus) {
            if (markerCount < 1000) {
                performanceStatus.textContent = 'Good';
                performanceStatus.className = 'stat-value good';
            } else if (markerCount < 5000) {
                performanceStatus.textContent = 'OK';
                performanceStatus.className = 'stat-value warning';
            } else {
                performanceStatus.textContent = 'Slow';
                performanceStatus.className = 'stat-value poor';
            }
        }
    }
}

// Show/hide loading spinner
function showLoading(show) {
    const spinner = document.getElementById('loadingSpinner');
    if (show) {
        spinner.classList.remove('hidden');
        // Reset progress
        updateLoadingProgress(0);
    } else {
        spinner.classList.add('hidden');
    }
}

// Update loading progress
function updateLoadingProgress(progress) {
    const progressBar = document.getElementById('loadingProgress');
    if (progressBar) {
        progressBar.style.width = progress + '%';
        progressBar.textContent = Math.round(progress) + '%';
    }
}

// Show error message
function showError(message) {
    // Create a simple alert for now
    alert(message);
}

// Export functions to global scope for HTML onclick handlers
window.showBusinessDetails = showBusinessDetails;
