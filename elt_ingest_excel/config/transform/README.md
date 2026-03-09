
# Finance Data Migration: Customer & Supplier Data Preparation

This document outlines the automated rules and logic applied to prepare legacy Finance Customer and Supplier data for migration into Workday. The goal of this process is to ensure data quality, consistency, and compliance with Workday's strict requirements.

## 1. Executive Summary

We have implemented an automated data preparation pipeline that consolidates data from multiple legacy systems (FA, NFC, WNSL). This process fixes common data quality issues—such as messy addresses, duplicate records, and inconsistent naming—before the data is loaded into the Workday migration workbooks. This ensures a "clean" start in the new system.

## 2. Key Data Improvements

### 2.1. Customer Data Cleaning
*   **Duplicate Removal:** We identify and merge duplicate customer records (e.g., "Acme Ltd" vs. "Acme Limited") using smart name matching, ensuring a single, golden record for each customer.
*   **Name Standardization:** All customer names are standardized to a consistent format (uppercase, standard suffixes like "LTD", "PLC", "INC").
*   **Address Quality:**
    *   Addresses are parsed and formatted into clear lines.
    *   **Postcodes:** We apply rigorous checks to fix spacing errors (e.g., "SW1A1AA" becomes "SW1A 1AA") and remove invalid characters.
    *   **Geographic Mapping:** Postcodes are automatically mapped to their correct County, District, and Region to ensure accurate reporting.
*   **Dates:** Transaction and creation dates are harmonized into a single standard format.

### 2.2. Supplier Data Cleaning
*   **Duplicate Management:** Similar to customers, suppliers are de-duplicated to prevent multiple payments or records for the same vendor.
*   **Banking Information:**
    *   **Sort Codes & Account Numbers:** We strip out dashes, spaces, and typos to ensure payment files will be accepted by the bank.
    *   **IBAN Validation:** International Bank Account Numbers (IBANs) are cleaned and formatted correctly.
*   **Categorization:** Legacy supplier categories are mapped to the new, standardized Workday Supplier Categories (e.g., "Consulting Services", "Professional Fees").
*   **Payment Terms:** Historical payment terms are translated into the corresponding Workday definitions to ensure continuity of credit agreements.

## 3. How We Conform to Workday Standards

Workday requires data to be in specific formats that often differ from legacy systems. Our process handles this translation automatically:

*   **Region/County Mapping:** Workday requires specific codes for regions (e.g., "GB-ENG" for England). We automatically derive these from the legacy address data.
*   **Tax IDs:** Tax registration numbers are validated and formatted to meet country-specific requirements.
*   **Contact Information:** Phone numbers and email addresses are cleaned to ensure valid contact channels are migrated.

## 4. Business Benefits

*   **Reduced Manual Effort:** Eliminates the need for Finance teams to manually fix thousands of rows in Excel spreadsheets.
*   **Higher Data Accuracy:** Automated rules are consistent and catch errors that human review might miss.
*   **Smoother Migration:** Providing clean, pre-validated data significantly reduces the risk of errors during the actual Workday load process.
