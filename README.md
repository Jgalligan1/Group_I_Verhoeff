# MRTD (Machine Readable Travel Document) Parser with Verhoeff Check Digit Validation

Authors: Jack Galligan, Zhuo Zhang, Vanshaj Tyagi

Repository URL
- https://github.com/jgalligan1/Group_I_Verhoeff

Important: Use Python 3.7
- Install Python 3.7.x from: https://www.python.org/downloads/release/python-379/
- The grading environment targets Python 3.7.

Note about requirements.txt
- requirements.txt lists modern packages that may not install on Python 3.7.
- For grading on Python 3.7, install only:
  - pip install coverage==5.5 MutPy==0.6.1
- For a newer Python (e.g., 3.10+), you can use:
  - pip install -r requirements.txt

---

## Table of Contents
- Overview
- Features
- Installation (Windows, Python 3.7)
- Usage
  - Decoding MRZ
  - Encoding MRZ
  - Verhoeff validation and mismatch reporting
- Testing (without MutPy)
- Code Coverage (without MutPy)
- Mutation Testing (with MutPy)
- Project Structure
- Requirements
- API Reference (MRTD.py)
- About the Tests (MRTDtest.py)
- Additional Tests Added (MutPy-driven)
- How to Export the PDF Report
- Troubleshooting
- Contributing
- License

---

## Overview
This project parses and generates TD3-format MRZ (2 lines x 44 characters), validates fields using the Verhoeff check digit algorithm, and reports mismatches. It includes stubs for scanning hardware and a database so tests can use mocks.

## Features
- MRZ decoding to structured fields (TD3 format)
- MRZ encoding from fields to two 44-character lines
- Verhoeff check digit computation and verification
- Report mismatches for passport number, birth date, expiration date, and personal number
- Hardware scan and DB query stubs (mockable in tests)
- Comprehensive unit tests targeting >80% coverage

---

## Installation (Windows, Python 3.7)
1) Verify Python 3.7:
- python --version  (expect 3.7.x)

2) Create and activate a venv:
- python -m venv .venv
- .venv\Scripts\activate

3) Install minimal grading deps (recommended):
- pip install coverage==5.5 MutPy==0.6.1

Optionally (newer Python only):
- pip install -r requirements.txt

---

## Usage

### Decoding MRZ
```python
from MRTD import decode_mrz

line1 = "P<USASMITH<<JOHN<JAMES<<<<<<<<<<<<<<<<<<<"
line2 = "1234567890USA9001011M2505015<<<<<<<<<<<08"

result = decode_mrz(line1, line2)
print(result["surname"], result["given_names"], result["passport_number"])
```

### Encoding MRZ
```python
from MRTD import encode_mrz

fields = {
    "type": "P",
    "country": "USA",
    "name": "SMITH<<JOHN",
    "passport_number": "123456789",
    "passport_check": "0",
    "nationality": "USA",
    "birth_date": "900101",
    "birth_check": "1",
    "sex": "M",
    "expiration_date": "250501",
    "expiration_check": "5",
    "personal_number": "12345678900000",
    "final_check": "8",
}
line1, line2 = encode_mrz(fields)
print(line1, len(line1))
print(line2, len(line2))
```

### Verhoeff validation and mismatch reporting
```python
from MRTD import verhoeff_check_digit, verify_field_with_verhoeff, report_check_digit_mismatches

digit = verhoeff_check_digit("123456789")
ok = verify_field_with_verhoeff("123456789", str(digit))

decoded = decode_mrz(line1, line2)
mismatches = report_check_digit_mismatches(decoded)
```

---

## Testing (without MutPy)
- Run all tests:
  - python -m unittest -v
- Run a specific suite or test:
  - python -m unittest MRTDtest.TestDecodeMRZ -v
  - python -m unittest MRTDtest.TestEncodeMRZ.test_encode_mrz_basic -v

What’s covered:
- Decoding: valid MRZs (USA, GBR, FRA), boundary lengths, names (single/multiple), gender, personal number normalization, exact 44-char and off-by-one errors.
- Encoding: padding and truncation, name formatting, structure and length checks, empty personal number handling.
- Verhoeff and verification helper: edge/pattern cases, correct/incorrect digits, types.
- Mismatch reporting: each field wrong alone, multiple wrong, all wrong, order, and perfect case.
- Stubs: hardware scan and DB return None (mockable).

---

## Code Coverage (without MutPy)
- Generate coverage:
  - coverage run -m unittest -v
  - coverage report -m
  - coverage html  (open htmlcov\index.html)
- Target: >80% on MRTD.py.

---

## Mutation Testing (with MutPy)
- Run:
  - mut.py --target MRTD --unit-test MRTDtest -m --report-html .mutpy-report
- Capture in your report:
  - Mutants generated
  - Killed vs survived
  - Mutation score (%)
  - Additional tests added to kill survivors (see next section)

---

## Project Structure
- MRTD.py: Implementation (decode, encode, Verhoeff, mismatch report) + stubs.
- MRTDtest.py: Unit tests (incl. additional tests to kill mutants).
- docs/REPORT.md: Project report (export to PDF).
- README.md: This file.
- requirements.txt: Optional full dev stack (best on newer Python).

---

## Requirements
- Python 3.7 (grading)
- unittest (built-in)
- coverage==5.5 (grading)
- MutPy==0.6.1 (grading)

If using the full stack on a newer Python, see requirements.txt.

---

## API Reference (MRTD.py)
- scan_mrz_from_hardware() -> None
  - Stub; returns None (hardware not available).
- decode_mrz(line1: str, line2: str) -> dict
  - Validates both lines are exactly 44 chars; raises ValueError("LengthError") on failure.
  - Line 1: document_type[0:2], issuing_country[2:5], names[5:44] (Surname<<Given<...).
  - Line 2: passport_number[0:9], passport_check_digit[9], nationality[10:13],
    birth_date[13:19], birth_check_digit[19], gender[20], expiration_date[21:27],
    expiration_check_digit[27], personal_number[28:42], personal_check_digit[42], final_check_digit[43].
  - Names: '<' replaced with spaces and collapsed.
  - Personal number returned with filler '<' normalized to '0'.
- encode_mrz(fields: dict) -> (str, str)
  - Line 1: "P<" + country(3) + NAME (SURNAME<<GIVEN<...), spaces -> '<', pad/truncate to 44.
  - Line 2: exact 44 chars = 9+1+3+6+1+1+6+1+14+1+1; pads/truncates each field; personal_number forced to 14 chars (pads with '<').
- query_travel_document_from_db(document_id) -> None
  - Stub; returns None (DB not available).
- verhoeff_check_digit(number: str) -> int
  - Standard Verhoeff algorithm using d/p/inv tables.
- verify_field_with_verhoeff(field: str, check_digit: str) -> bool
  - Computes and compares as strings.
- report_check_digit_mismatches(decoded_fields: dict) -> list[str]
  - Returns names of fields whose provided check digit mismatches computed (order: passport_number, birth_date, expiration_date, personal_number). Treats personal_number filler '<' as zeros for verification.

---

## About the Tests (MRTDtest.py)
- TestScanMRZFromHardware: validates the stub returns None.
- TestDecodeMRZ:
  - Valid examples (USA, GBR, FRA).
  - Names: single surname, multiple given names.
  - Boundary: exactly 44 chars for each line; too short/too long variants.
  - Gender extraction; personal number normalization and length 14.
- TestEncodeMRZ:
  - Basic build; padding and truncation; structure and formats; spaces replaced with '<'; empty personal number padded to 14.
- TestVerhoeffCheckDigit:
  - Simple, single-digit, zeros, long, known values, lengths, same-digit patterns, sequential and alternating patterns.
- TestVerifyFieldWithVerhoeff:
  - Correct/incorrect digits, zero checks, string comparison, boolean return type.
- TestReportCheckDigitMismatches:
  - No mismatches (all correct).
  - Each individual mismatch.
  - Multiple mismatches, all fields mismatch, expected order.

Run without MutPy:
- python -m unittest -v
- coverage run -m unittest -v
- coverage report -m
- coverage html

---

## Additional Tests Added (MutPy-driven)
Added to strengthen coverage and kill common mutants:
- Decoding:
  - test_decode_mrz_all_fields_extracted
  - test_decode_mrz_exactly_44_chars_line1
  - test_decode_mrz_exactly_44_chars_line2
  - test_decode_mrz_line1_43_chars
  - test_decode_mrz_line2_45_chars
  - test_decode_mrz_gender_extraction
  - test_decode_mrz_male_gender
  - test_decode_mrz_personal_number_field
- Encoding:
  - test_encode_mrz_line1_format
  - test_encode_mrz_line2_structure
  - test_encode_mrz_space_replacement
  - test_encode_mrz_truncation_at_44
  - test_encode_mrz_empty_personal_number

Record updated coverage and mutation score in docs/REPORT.md.

---

## How to Export the PDF Report
- Create/update docs/REPORT.md with your coverage and mutation results.
- VS Code method:
  - Install “Markdown PDF”.
  - Open docs/REPORT.md → “Markdown PDF: Export (pdf)”.
- Pandoc (Windows):
  - choco install pandoc
  - pandoc docs\REPORT.md -o docs\REPORT.pdf

---

## Troubleshooting
- ValueError("LengthError") in decode_mrz:
  - Both MRZ lines must be exactly 44 chars.
- encode_mrz line2 not 44 chars:
  - Ensure personal_number is 14 chars; encoder pads with '<' if short.
- Low coverage:
  - Run coverage run -m unittest -v and verify boundary/error-path tests run.
- MutPy not found:
  - pip install MutPy==0.6.1 (on Python 3.7).

---

## Contributing
- Fork, create a feature branch, add tests, ensure >80% coverage, follow PEP 8, then open a PR.

## License
Educational use for SSW567 (Stevens Institute of Technology).