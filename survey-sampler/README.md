
# Survey Sample Size & MOE Planner

A professional web application for planning survey sample sizes with comprehensive statistical analysis capabilities.

## Features

### 🎯 Single Group Planner
- Calculate required sample size for target margin of error
- Reverse calculation: find MOE for given sample size
- Finite population correction (FPC) support
- Design effect adjustments for complex sampling
- Response rate planning

### 👥 Multi-Group Planner
- Plan sample sizes across multiple population groups
- Multiple allocation strategies:
  - **Proportional**: Sample size proportional to group size
  - **Balanced**: Equal sample sizes per group
  - **Neyman**: Optimal allocation based on group variances
- Overall MOE targeting or per-group precision
- Dynamic group management

### 🔬 A/B Testing Power Analysis
- Sample size calculation for detecting differences in proportions
- Configurable confidence levels and statistical power
- Design effect support for both groups
- Optional finite population correction

## UI Improvements

### Enhanced User Experience
- **Tooltips & Help Text**: Hover over any field for detailed explanations
- **Example Values**: Practical examples for each input field
- **Visual Feedback**: Modern card-based design with hover effects
- **Responsive Layout**: Works seamlessly on desktop and mobile devices
- **Better Typography**: Inter font for improved readability

### Improved Results Display
- **Structured Results**: Clear, organized presentation of calculations
- **Color-Coded Output**: Success indicators and information boxes
- **Detailed Explanations**: Context for each result value
- **Smooth Scrolling**: Automatic focus on results when they appear

### Professional Styling
- **Dark Theme**: Easy on the eyes for extended use
- **Gradient Accents**: Modern visual appeal
- **Card Animations**: Subtle hover effects and transitions
- **Consistent Spacing**: Professional layout and alignment

## Technical Details

### Statistical Methods
- Normal approximation for proportions
- Finite population correction (FPC)
- Design effect adjustments
- Power analysis for hypothesis testing

### Technologies
- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Styling**: Custom CSS with CSS variables
- **Fonts**: Inter (Google Fonts)

## Getting Started

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python app.py
   ```

3. **Open in Browser**:
   Navigate to `http://localhost:5000`

## Usage Guide

### Single Group Planning
1. Enter your population size (or leave empty for infinite)
2. Select confidence level (95% is standard)
3. Estimate expected proportion (0.5 is most conservative)
4. Set design effect (1.0 for simple random sampling)
5. Specify expected response rate
6. Choose either:
   - Target MOE: Enter desired margin of error
   - Given n: Enter existing sample size to calculate MOE
7. Click "Calculate" to see results

### Multi-Group Planning
1. Configure confidence and planning mode
2. Set target MOE and allocation strategy
3. Add population groups with their parameters
4. Click "Plan Allocation" to see optimal distribution

### A/B Testing
1. Set confidence level and desired power
2. Specify detectable difference between groups
3. Enter expected proportions for both groups
4. Configure design effects if needed
5. Add population sizes for FPC (optional)
6. Calculate required sample sizes per group

## Best Practices

- **Sample Size**: Larger samples provide more precise estimates
- **Confidence Level**: 95% is standard; higher levels require larger samples
- **Design Effects**: Account for clustering, stratification, or other complex designs
- **Response Rates**: Plan for realistic completion rates
- **Proportions**: Use 0.5 when uncertain (most conservative estimate)

## Contributing

This tool is designed for researchers, survey professionals, and data scientists. Contributions to improve accuracy, usability, or add new statistical methods are welcome.

## License

Open source - feel free to use and modify for your research and professional needs.
