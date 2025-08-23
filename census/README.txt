Kansas City Industry Landscape Builder — Extended ABS Insights
=============================================================
Pulls ABS Company Summary, Characteristics of Businesses, Characteristics of Business Owners,
ABS Module Business Characteristics, and CBP — all at the metro level (default: Kansas City CBSA 28140).

OUTPUTS
-------
- kc_industry_landscape.xlsx → Multi-sheet workbook with all extended ABS data:
    • combined_industry_view - Core industry landscape (ABSCs + CBP)
    • abs_company_summary - ABS Company Summary data
    • cbp - County Business Patterns data
    • abs_business_chars - Business characteristics (innovation, remote work, franchise, family-owned)
    • abs_owner_chars - Owner demographics (sex, race, ethnicity, veteran status, age, education)
    • abs_module_chars - Specialized business characteristics (COVID, technology adoption, etc.)

INSTALL
-------
pip install requests pandas openpyxl

RUN
---
# Default Kansas City pull
python kc_industry_landscape_extended.py --api-key YOUR_CENSUS_API_KEY

# Different metro
python kc_industry_landscape_extended.py --cbsa 12060

# Limit to some sectors (Manufacturing + NAICS 54)
python kc_industry_landscape_extended.py --naics 31-33 54

HEADER NOTES
------------
- The script renames raw Census codes to descriptive titles before saving.
- All data is organized in Excel sheets for easy analysis.
- Key fields in combined_industry_view:
    Geography, NAICS_2digit, NAICS_Code, Industry_Sector,
    Employer_Firms_ABS, Employment_ABS, Annual_Payroll_ABS, Receipts_ABS,
    Establishments_CBP, Employment_CBP, Q1_Payroll_CBP, Annual_Payroll_CBP,
    Geo_ID, Dataset_ABS_CS, Year_ABS_CS, Dataset_CBP, Year_CBP
