
# Detailed Data Transformation Specifications

This document details the specific business rules and logic applied to transform legacy Customer and Supplier data into the Workday-conformed format.

## 1. Address & Geography Transformation

### 1.1. Postcode Cleaning & Validation
We enforce strict UK Postcode formatting to ensure high-quality matching with geographic reference data.

**Logic:**
1.  **Format Validation:** We use regex pattern matching to extract valid postcodes from free-text fields, strictly adhering to the standard UK formats (MRS standards):
    *   **AN NAA** (e.g., `M1 1AA`)
    *   **ANN NAA** (e.g., `M60 1NW`)
    *   **AAN NAA** (e.g., `CR2 6XH`)
    *   **AANN NAA** (e.g., `DN55 1PT`)
    *   **ANA NAA** (e.g., `W1A 1HQ`)
    *   **AANA NAA** (e.g., `EC1A 1BB`)
    *   *(Where A=Alpha, N=Numeric)*
2.  **Normalization:**
    *   All postcodes are converted to **UPPERCASE**.
    *   Commas (`,`) and hyphens (`-`) are replaced with spaces (e.g., `W1A-1HQ` -> `W1A 1HQ`).
    *   Multiple spaces are collapsed into a single space.
    *   Values like `UNKNOWN`, `[NOT KNOWN]` are explicitly converted to `NULL`.
3.  **Extraction:** If a field contains extra text (e.g., `AL5 2LG, UK`), we extract only the valid postcode portion.

### 1.2. Geographic Enrichment (County, Town, Region)
Once a clean postcode is established, we derive the correct administrative hierarchy.

**Logic:**
1.  **District/City Lookup:** We map the "Outcode" (first half of postcode) or full postcode to the official **Postal District** to derive the `City` or `Town`.
2.  **County & Region:** We map the District to its official **County** and **Region**.
3.  **Workday Conformance:**
    *   We map the derived Region/County to the specific **Workday Region IDs** (e.g., `GB-ENG`, `GB-LND`).
    *   If a direct match isn't found, we fallback to Country-level defaults.

### 1.3. Address Line Cleaning
**Logic:**
1.  **Special Character Removal:** We strip invalid characters (`"`, `<`, `>`, `|`, `;`, `{`, `}`) that cause integration failures.
2.  **Deduplication:** We remove duplicate lines (e.g., if Line 1 and Line 2 are identical).
3.  **Consolidation:** Empty lines are removed, and remaining lines are shifted up to ensure no gaps (e.g., if Line 2 is empty, Line 3 becomes Line 2).

---

## 2. Banking Transformation (Suppliers)

### 2.1. Bank Details
**Logic:**
1.  **Bank Name Derivation:** We use the **Sort Code** (first 2 digits) to look up the official **Bank Name** (e.g., `20-xx-xx` -> `Barclays`).
2.  **Account Number Cleaning:**
    *   Spaces and hyphens are stripped.
    *   We validate the length based on country rules (e.g., UK accounts must be 8 digits).
3.  **Routing Numbers:** For international suppliers, we format the routing code based on the country (e.g., US ABA Routing Numbers vs. UK Sort Codes).

### 2.2. IBAN
**Logic:**
*   Spaces and hyphens are removed.
*   Format is standardized to uppercase.

---

## 3. Name Standardization & Deduplication

### 3.1. Name Cleaning
**Logic:**
1.  **Standardization:**
    *   `WOMENS` -> `WOMEN`
    *   `FOOTBALL CLUB` -> `FC`
    *   Remove trailing legal entity suffixes (`LIMITED`, `LTD`, `PLC`, `LLP`, `INC`) for the "Clean Name" used in matching.
2.  **Phonetic Encoding:** We generate **Soundex** and **Double Metaphone** codes to identify similar sounding names (e.g., `Smith` vs `Smyth`) for duplicate detection.

### 3.2. Deduplication Strategy
**Logic:**
*   We group records that share the same **Clean Name** or **Phonetic Code**.
*   **Golden Record Selection:** We pick the "best" record based on:
    1.  Recency of transaction (Last Payment Date).
    2.  Completeness of data (Has Bank Details?).
    3.  Account creation date.

---

## 4. Financial & Regulatory Data

### 4.1. Tax IDs
**Logic:**
*   **Validation:** Tax IDs are checked against country-specific formats.
*   **Mapping:** We map legacy Tax Schedule codes to Workday Tax Categories.

### 4.2. Supplier Categories
**Logic:**
*   Legacy categories (often free-text or obsolete codes) are mapped to the defined **Workday Supplier Category** hierarchy (e.g., `IT Services`, `Professional Fees`). Unmapped categories default to a general bucket (e.g., `Consulting Services`).

### 4.3. Payment Terms
**Logic:**
*   Legacy payment term codes are translated to Workday Payment Term IDs (e.g., `Net 30`, `Immediate`).

---

## 5. Contact & Payment Grouping (Consolidation)

When multiple source records are identified as the same entity (e.g., duplicate suppliers with different addresses), we don't just pick one row and discard the rest. Instead, we **aggregate** valuable contact and payment information into the single "Golden Record".

### 5.1. Address & Contact Consolidation
**Logic:**
*   **Addresses:** We collect all **unique** addresses associated with the entity into a list. This ensures that if a supplier has a "Billing" address on one record and a "Shipping" address on another, both are preserved and migrated.
*   **Emails & Phones:** All unique phone numbers and email addresses are aggregated into semi-colon separated lists (e.g., `sales@acme.com; billing@acme.com`). This preserves all valid communication channels.

### 5.2. Bank Account Aggregation
**Logic:**
*   We collect all **unique** valid bank account details found across the duplicate records.
*   These are stored as a list of payment methods attached to the supplier.
*   This prevents payment failures by ensuring the active bank account is migrated even if it wasn't on the specific "primary" row selected during deduplication.
