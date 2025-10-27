# MRTD (Machine Readable Travel Document) Parser with Verhoeff Check Digit Validation

**Authors:** Jack Galligan, Zhuo Zhang, and Vanshaj Tyagi

A Python library for parsing, encoding, and validating Machine Readable Travel Documents (MRTD) using the Verhoeff check digit algorithm as specified in ICAO Doc 9303.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Decoding MRZ](#decoding-mrz)
  - [Encoding MRZ](#encoding-mrz)
  - [Verhoeff Check Digit Validation](#verhoeff-check-digit-validation)
- [Testing](#testing)
- [Code Coverage](#code-coverage)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This project implements a complete MRTD (passport) MRZ (Machine Readable Zone) parser with Verhoeff check digit validation. It supports:

- Decoding 2-line MRZ data from passports
- Encoding travel document information into MRZ format
- Validating check digits using the Verhoeff algorithm
- Reporting mismatches in check digit validation

The implementation follows the ICAO Doc 9303 specifications for travel document standards.

---

## Features

✅ **MRZ Decoding**: Parse 44-character MRZ lines into structured data  
✅ **MRZ Encoding**: Convert structured data into ICAO-compliant MRZ format  
✅ **Verhoeff Check Digits**: Compute and verify check digits using the Verhoeff algorithm  
✅ **Mismatch Reporting**: Identify fields with incorrect check digits  
✅ **Multi-country Support**: Tested with USA, GBR, CAN, DEU, FRA passports  
✅ **Comprehensive Testing**: >80% code coverage with extensive test suite  
✅ **Type Hints**: Full type annotations for better IDE support

---

## Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd Group_I_Verhoeff
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Verify installation:**
```bash
python -m unittest MRTDtest.py
```

---

## Usage

### Decoding MRZ

```python
from MRTD import decode_mrz

# Example MRZ lines from a US passport
line1 = "P<USASMITH<<JOHN<JAMES<<<<<<<<<<<<<<<<<<"
line2 = "1234567890USA9001011M25050151234567890<<8"

# Decode the MRZ
result = decode_mrz(line1, line2)

print(f"Name: {result['given_names']} {result['surname']}")
print(f"Passport Number: {result['passport_number']}")
print(f"Nationality: {result['nationality']}")
print(f"Birth Date: {result['birth_date']}")
print(f"Expiration Date: {result['expiration_date']}")
```

**Output:**
```
Name: JOHN JAMES SMITH
Passport Number: 123456789
Nationality: USA
Birth Date: 900101
Expiration Date: 250501
```

### Encoding MRZ

```python
from MRTD import encode_mrz

# Create travel document fields
fields = {
    'type': 'P',
    'country': 'USA',
    'name': 'SMITH<<JOHN',
    'passport_number': '123456789',
    'passport_check': '0',
    'nationality': 'USA',
    'birth_date': '900101',
    'birth_check': '1',
    'sex': 'M',
    'expiration_date': '250501',
    'expiration_check': '5',
    'personal_number': '1234567890',
    'final_check': '8'
}

# Encode to MRZ format
line1, line2 = encode_mrz(fields)

print(f"Line 1: {line1}")
print(f"Line 2: {line2}")
```

### Verhoeff Check Digit Validation

```python
from MRTD import verhoeff_check_digit, verify_field_with_verhoeff, report_check_digit_mismatches

# Compute check digit
check = verhoeff_check_digit("123456789")
print(f"Check digit: {check}")

# Verify a field
is_valid = verify_field_with_verhoeff("123456789", "0")
print(f"Valid: {is_valid}")

# Check all fields in decoded MRZ
decoded = decode_mrz(line1, line2)
mismatches = report_check_digit_mismatches(decoded)

if mismatches:
    print(f"Fields with incorrect check digits: {mismatches}")
else:
    print("All check digits are valid!")
```

---

## Testing

The project includes comprehensive test coverage for all functions.

### Run All Tests

```bash
python -m unittest MRTDtest.py -v
```

### Run Specific Test Class

```bash
python -m unittest MRTDtest.TestDecodeMRZ -v
```

### Test Categories

- **TestScanMRZFromHardware**: Tests for hardware scanning stub
- **TestDecodeMRZ**: Tests for MRZ decoding (10 test cases)
- **TestEncodeMRZ**: Tests for MRZ encoding (3 test cases)
- **TestVerhoeffCheckDigit**: Tests for check digit computation (4 test cases)
- **TestVerifyFieldWithVerhoeff**: Tests for field verification (3 test cases)
- **TestReportCheckDigitMismatches**: Tests for mismatch reporting (6 test cases)
- **TestQueryTravelDocumentFromDB**: Tests for database query stub (2 test cases)

**Total: 29 test cases**

---

## Code Coverage

### Generate Coverage Report

```bash
# Run tests with coverage
coverage run -m unittest MRTDtest.py

# View coverage report in terminal
coverage report -m

# Generate HTML coverage report
coverage html
```

### View HTML Report

Open `htmlcov/index.html` in your browser to see detailed coverage analysis.

### Expected Coverage

- **MRTD.py**: >80% coverage
- **Statements**: High coverage of all executable lines
- **Branches**: Complete coverage of conditional logic
- **Functions**: All functions tested with multiple scenarios

---

## Project Structure

```
Group_I_Verhoeff/
│
├── MRTD.py                 # Main implementation
├── MRTDtest.py             # Test suite
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── 9303_p3_cons_en-1.pdf  # ICAO Doc 9303 specification
│
├── htmlcov/                # Coverage HTML reports
│   ├── index.html
│   ├── MRTD_py.html
│   └── ...
│
└── __pycache__/            # Python cache files
```

---

## Requirements

- Python 3.9+
- unittest (built-in)
- coverage (for code coverage reports)

See [requirements.txt](requirements.txt) for complete dependency list.

---

## API Reference

### Functions

#### `scan_mrz_from_hardware()`
**Description:** Stub function for hardware MRZ scanning.  
**Returns:** `None`  
**Status:** Not implemented (stub)

#### `decode_mrz(line1: str, line2: str) -> dict`
**Description:** Decodes two 44-character MRZ lines into structured data.  
**Parameters:**
- `line1` (str): First line of MRZ (44 characters)
- `line2` (str): Second line of MRZ (44 characters)

**Returns:** Dictionary with decoded fields  
**Raises:** `ValueError` if lines are not exactly 44 characters

**Returned Fields:**
- `document_type`, `issuing_country`, `surname`, `given_names`
- `passport_number`, `passport_check_digit`, `nationality`
- `birth_date`, `birth_check_digit`, `gender`
- `expiration_date`, `expiration_check_digit`
- `personal_number`, `personal_check_digit`, `final_check_digit`

#### `encode_mrz(fields: dict) -> tuple[str, str]`
**Description:** Encodes travel document fields into MRZ format.  
**Parameters:**
- `fields` (dict): Dictionary containing document fields

**Returns:** Tuple of (line1, line2) as 44-character strings

#### `verhoeff_check_digit(number: str) -> int`
**Description:** Computes Verhoeff check digit for a numeric string.  
**Parameters:**
- `number` (str): Numeric string

**Returns:** Check digit (0-9)

#### `verify_field_with_verhoeff(field: str, check_digit: str) -> bool`
**Description:** Verifies if a field matches its check digit.  
**Parameters:**
- `field` (str): Field value
- `check_digit` (str): Expected check digit

**Returns:** `True` if valid, `False` otherwise

#### `report_check_digit_mismatches(decoded_fields: dict) -> list[str]`
**Description:** Reports fields with incorrect check digits.  
**Parameters:**
- `decoded_fields` (dict): Decoded MRZ fields

**Returns:** List of field names with mismatches

#### `query_travel_document_from_db(document_id)`
**Description:** Stub function for database queries.  
**Returns:** `None`  
**Status:** Not implemented (stub)

---

## Examples

### Example 1: Validate UK Passport

```python
from MRTD import decode_mrz, report_check_digit_mismatches

line1 = "P<GBRJONES<<EMMA<CHARLOTTE<<<<<<<<<<<<<<<<"
line2 = "9876543210GBR8512312F30123141122334455<<7"

decoded = decode_mrz(line1, line2)
mismatches = report_check_digit_mismatches(decoded)

if not mismatches:
    print("✓ Passport is valid")
else:
    print(f"✗ Invalid fields: {', '.join(mismatches)}")
```

### Example 2: Handle Invalid MRZ Length

```python
from MRTD import decode_mrz

line1 = "P<USASMITH<<JOHN"  # Too short
line2 = "1234567890USA9001011M25050151234567890<<8"

try:
    result = decode_mrz(line1, line2)
except ValueError as e:
    print(f"Error: {e}")  # Output: Error: LengthError
```

### Example 3: Process Multiple Countries

```python
from MRTD import decode_mrz

passports = [
    ("USA", "P<USASMITH<<JOHN<JAMES<<<<<<<<<<<<<<<<<", "1234567890USA9001011M25050151234567890<<8"),
    ("GBR", "P<GBRJONES<<EMMA<CHARLOTTE<<<<<<<<<<<<<<<<", "9876543210GBR8512312F30123141122334455<<7"),
    ("FRA", "P<FRADUPONT<<MARIE<LOUISE<<<<<<<<<<<<<<<<<<<", "12FR1234567FRA7802285F27123011234567890<<3"),
]

for country, line1, line2 in passports:
    result = decode_mrz(line1, line2)
    print(f"{country}: {result['given_names']} {result['surname']}")
```

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Write tests for new functionality
4. Ensure >80% code coverage
5. Follow PEP 8 style guidelines
6. Submit a pull request

---

## License

This project is developed for educational purposes as part of SSW567 coursework at Stevens Institute of Technology.

---

## References

- [ICAO Doc 9303](https://www.icao.int/publications/Documents/9303_p3_cons_en.pdf) - Machine Readable Travel Documents
- [Verhoeff Algorithm](https://en.wikipedia.org/wiki/Verhoeff_algorithm) - Check digit algorithm

---

## Contact

For questions or issues, please contact:
- Jack Galligan
- Zhuo Zhang
- Vanshaj Tyagi

**Course:** SSW567 - Software Testing, Quality Assurance and Maintenance  
**Institution:** Stevens Institute of Technology