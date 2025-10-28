# MRTD.py by Jack Galligan, Zhuo Zhang, and Vanshaj Tyagi
from typing import Tuple, List, Optional

# Requirement 1: stub for hardware scanning
def scan_mrz_from_hardware():
    # Stub: hardware not available
    return None


# Requirement 2: decode two 44-char MRZ lines into fields (ICAO TD3 format)
def decode_mrz(line1: str, line2: str) -> dict:
    if len(line1) != 44 or len(line2) != 44:
        raise ValueError("LengthError")

    # Line 1
    document_type = line1[0:2]
    issuing_country = line1[2:5]
    names_raw = line1[5:44]

    # Names format: Surname<<Given<Given2...
    parts = names_raw.split("<<", 1)
    surname_raw = parts[0]
    given_raw = parts[1] if len(parts) > 1 else ""

    def normalize_name(s: str) -> str:
        # Replace filler '<' with spaces, collapse multiple spaces
        s = s.replace("<", " ")
        return " ".join(s.split()).strip()

    surname = normalize_name(surname_raw)
    given_names = normalize_name(given_raw)

    # Line 2 fields (positions are inclusive ranges described by ICAO)
    passport_number = line2[0:9]
    passport_check_digit = line2[9]
    nationality = line2[10:13]
    birth_date = line2[13:19]
    birth_check_digit = line2[19]
    gender = line2[20]
    expiration_date = line2[21:27]
    expiration_check_digit = line2[27]
    personal_number_raw = line2[28:42]
    personal_check_digit = line2[42]
    final_check_digit = line2[43]

    # Normalize personal number for consumers (replace filler with zero)
    personal_number = personal_number_raw.replace("<", "0")

    return {
        "document_type": document_type,
        "issuing_country": issuing_country,
        "surname": surname,
        "given_names": given_names,
        "passport_number": passport_number,
        "passport_check_digit": passport_check_digit,
        "nationality": nationality,
        "birth_date": birth_date,
        "birth_check_digit": birth_check_digit,
        "gender": gender,
        "expiration_date": expiration_date,
        "expiration_check_digit": expiration_check_digit,
        "personal_number": personal_number,
        "personal_check_digit": personal_check_digit,
        "final_check_digit": final_check_digit,
    }


# Requirement 3: encode fields into two 44-char MRZ lines
def encode_mrz(fields: dict) -> Tuple[str, str]:
    # Line 1: type + '<' + country (3) + name (surname<<given...) padded/truncated to 44
    doc_type = (fields.get("type") or "P").upper()[0]
    country = (fields.get("country") or "XXX").upper().ljust(3, "<")[:3]

    # Name is expected as 'SURNAME<<GIVEN<OTHER', replace spaces with '<'
    name = (fields.get("name") or "").upper().replace(" ", "<")
    line1_raw = f"{doc_type}<{country}{name}"
    line1 = (line1_raw + "<" * 44)[:44]

    # Line 2 structure
    def pad_or_trunc(val: Optional[str], size: int, fill: str = "<") -> str:
        s = (val or "")
        s = s[:size]
        if len(s) < size:
            s = s + (fill * (size - len(s)))
        return s

    passport_number = pad_or_trunc(fields.get("passport_number"), 9)
    passport_check = pad_or_trunc(fields.get("passport_check"), 1, "<")
    nationality = pad_or_trunc(fields.get("nationality"), 3).upper()
    birth_date = pad_or_trunc(fields.get("birth_date"), 6)
    birth_check = pad_or_trunc(fields.get("birth_check"), 1, "<")
    sex = pad_or_trunc(fields.get("sex"), 1, "<").upper()
    expiration_date = pad_or_trunc(fields.get("expiration_date"), 6)
    expiration_check = pad_or_trunc(fields.get("expiration_check"), 1, "<")
    personal_number = pad_or_trunc(fields.get("personal_number"), 14, "<")
    personal_check = pad_or_trunc(fields.get("personal_check"), 1, "<")
    final_check = pad_or_trunc(fields.get("final_check"), 1, "<")

    line2_raw = (
        passport_number
        + passport_check
        + nationality
        + birth_date
        + birth_check
        + sex
        + expiration_date
        + expiration_check
        + personal_number
        + personal_check
        + final_check
    )

    # Ensure exact length
    if len(line2_raw) < 44:
        line2 = line2_raw + "<" * (44 - len(line2_raw))
    else:
        line2 = line2_raw[:44]

    return line1, line2


# Requirement 1/DB stub: query function
def query_travel_document_from_db(document_id):
    # Stub: database not available
    return None


# Verhoeff algorithm tables
_d_table = [
    [0,1,2,3,4,5,6,7,8,9],
    [1,2,3,4,0,6,7,8,9,5],
    [2,3,4,0,1,7,8,9,5,6],
    [3,4,0,1,2,8,9,5,6,7],
    [4,0,1,2,3,9,5,6,7,8],
    [5,9,8,7,6,0,4,3,2,1],
    [6,5,9,8,7,1,0,4,3,2],
    [7,6,5,9,8,2,1,0,4,3],
    [8,7,6,5,9,3,2,1,0,4],
    [9,8,7,6,5,4,3,2,1,0],
]

_p_table = [
    [0,1,2,3,4,5,6,7,8,9],
    [1,5,7,6,2,8,3,0,9,4],
    [5,8,0,3,7,9,6,1,4,2],
    [8,9,1,6,0,4,3,5,2,7],
    [9,4,5,3,1,2,6,8,7,0],
    [4,2,8,6,5,7,3,9,0,1],
    [2,7,9,3,8,0,6,4,1,5],
    [7,0,4,6,9,1,3,2,5,8],
]

_inv_table = [0,4,3,2,1,5,6,7,8,9]


def verhoeff_check_digit(number: str) -> int:
    # Compute Verhoeff check digit for a numeric string
    c = 0
    digits = [int(ch) for ch in reversed(number or "")]
    for i, d in enumerate(digits):
        c = _d_table[c][_p_table[i % 8][d]]
    return _inv_table[c]


def verify_field_with_verhoeff(field: str, check_digit: str) -> bool:
    try:
        calc = verhoeff_check_digit(field)
    except Exception:
        return False
    return str(calc) == str(check_digit)


def report_check_digit_mismatches(decoded_fields: dict) -> List[str]:
    mismatches: List[str] = []

    # Normalize personal number input for calculation (replace filler with zeros)
    pn_raw = (decoded_fields.get("personal_number") or "").replace("<", "0")

    checks = [
        ("passport_number", "passport_check_digit", decoded_fields.get("passport_number") or ""),
        ("birth_date", "birth_check_digit", decoded_fields.get("birth_date") or ""),
        ("expiration_date", "expiration_check_digit", decoded_fields.get("expiration_date") or ""),
        ("personal_number", "personal_check_digit", pn_raw),
    ]

    for field_name, check_key, value in checks:
        provided = decoded_fields.get(check_key)
        if provided is None:
            continue  # skip if not provided
        try:
            expected = str(verhoeff_check_digit(value))
        except Exception:
            mismatches.append(field_name)
            continue
        if str(provided) != expected:
            mismatches.append(field_name)

    return mismatches