# Supplier EIB — Error Fixes (Submit Supplier V6)

Source: `~/Downloads/Submit supplier V6 with errors.xlsx`
Total errors: 3,751 across 2,955 suppliers (out of 6,733 total)

---

## [ ] 1. Phone — 1,893 errors (50.5%)

**Error messages:**
- `Invalid number: The number length does not match valid numbers for this region.`
- `Invalid number: The number is not valid for this region.`

**Root cause:**
3+ manually re-entered phone numbers from the xlsm Supplier Phone tab, stripping leading zeros (numbers stored as integers in their EIB). The SQL/UDF parsing in `workday_supplier_phone.sql` is correct — the xlsm Supplier Phone tab has the right values (`44 | 20 | 76370656 | Landline`). The problem is in the manual transcription step.

Additionally, the xlsm macro (`SubmitSuppliers`) has the Area Code line commented out, so even if the macro had been used, the area code would not have been written to the EIB.

**Fix:**
- Uncomment the Area Code line in the xlsm VBA macro (`SubmitSuppliers`, line ~2371)
- Ensure 3+ uses the macro output rather than manually transcribing phone data

---

## [ ] 2. Bank Settlement / Payment Type — 516 errors (13.8%)

**Error messages:**
- `All electronic payment types accepted for this Supplier must be assigned to an active Settlement Bank Account`
- `Ensure the supplier has only 1 active settlement bank account with no payment types and no accepted currencies`

**Root cause:**
Two sub-patterns:
1. Supplier has `Payment Types Accepted = BACS/Wire/SEPA` but no Settlement Bank Account linked
2. Supplier has multiple bank accounts; Workday requires exactly one with no payment types as a catch-all default

**Fix:**
- Review `workday_supplier_settlement_account.sql` — ensure payment types are correctly linked to bank accounts
- Review logic for suppliers with multiple bank accounts

---

## [ ] 3. EMAIL as PO Issue Option with no Email Address — 416 errors (11.1%)

**Error messages:**
- `Email cannot be chosen as a PO Issue Option if no Email Address is specified.`
- `Submit an Email Address to also submit the Change Order Issue Option.`

**Root cause:**
`PO Issue Option = EMAIL` and `Change Order Issue Option = EMAIL` set in the EIB but the `Email Address` field is blank for those suppliers.

**Fix:**
- In the supplier payment/procurement SQL, default PO Issue Option and Change Order Issue Option to a non-email method (e.g. `Print`) when no email address exists for the supplier

---

## [ ] 4. Invoice Specific Suppliers Data Missing — 363 errors (9.7%)

**Error message:**
- `Element Content 'Additional_Suppliers_for_Sending_Invoices_Data' is required on internal element 'Invoice Specific Suppliers Widget Data'`

**Root cause:**
EIB structural issue — the `Invoice Specific Suppliers Widget Data` block is triggered but `Additional_Suppliers_for_Sending_Invoices_Data` is not populated. Not a source data problem.

**Fix:**
- Review the EIB template configuration with 3+ — either populate the required element or suppress the block when data is absent

---

## [ ] 5. Region Code Invalid for Country — 303 errors (8.1%)

**Error messages:**
- `Region Name must be valid for the specified Country.`
- `Validation error occurred. Region Name must be valid for the specified Country.`

**Root cause:**
Two sub-patterns:
1. "Manchester" in source data resolves to `JAM-12` (Jamaica's Manchester parish) instead of a valid GB region — collision in the region lookup
2. Other GB region codes (e.g. `GBR-POST-LON`) not recognised by the Workday tenant

**Fix:**
- Review `workday_supplier_address.sql` region mapping logic
- Fix the Manchester → `JAM-12` collision in the region reference data
- Validate all region codes against the Workday tenant's configured regions

---

## [ ] 6. Postal Code Invalid Format — 131 errors (3.5%)

**Error messages:**
- `Enter a postal code in the valid format: Royal Mail UK format (A# #AA)`
- `Enter a postal code in the valid format: Postal code must be 5 digits`
- `Enter a postal code in the valid format: Irish Eircode format`

**Root cause:**
Three sub-patterns:
1. **UK**: Letter `O` used instead of digit `0` in source data (e.g. `RH6 ODW`, `L34 OHF`, `CB25 OHJ`)
2. **EU (FR/ES/DE/IT/US)**: Spaces embedded in 5-digit codes (e.g. `35 018`, `75 003`) — numeric storage artefact
3. **UAE**: Postal code submitted but UAE does not use postal codes

**Fix:**
- In `src_fin_supplier_raw.sql` or `workday_supplier_address.sql`: add `O` → `0` substitution in UK postal codes
- Strip spaces from numeric postal codes for EU/US countries
- Suppress postal code for countries that do not use them (e.g. UAE)

---

## [ ] 7. Bank BIC / IBAN / Routing Format Errors — 73 errors (2.0%)

**Error messages:**
- `The Bank Identification Code (BIC) entry is not following a standard format.`
- `IBAN is required for this country.`
- `SWIFT BIC is required for this Country.`
- `Routing Transit or Institution Number is required for this country.`
- `Bank Sort Code must be 6 numeric digits.`

**Root cause:**
- UK sort codes entered in the SWIFT/BIC field (e.g. `821974`)
- IBAN missing for France and Portugal (required by Workday)
- Routing number missing for US suppliers
- Sort codes with only 5 digits (e.g. `40003`) — source data truncation

**Fix:**
- Review `workday_supplier_settlement_account.sql` — add country-specific validation/nulling of BIC when it looks like a sort code
- Flag suppliers in FR/PT with no IBAN — either source or exclude from upload
- Ensure US routing numbers are correctly mapped

---

## [ ] 8. Supplier Category ID Invalid — 25 errors (0.7%)

**Error message:**
- `'Government & Charities' is not a valid ID value for type = 'Supplier_Category_ID'`

**Root cause:**
The display name `'Government & Charities'` is passed as the category ID but Workday expects the internal ID value (e.g. `Government_and_Charities` or a tenant-specific code). Affects charity/community trust suppliers.

**Fix:**
- Add mapping in `elt_ingest_excel/config/data/ref_supplier_category` (or the relevant reference table) to translate `Government & Charities` to the correct Workday `Supplier_Category_ID`
