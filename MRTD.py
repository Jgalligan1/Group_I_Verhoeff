#MRTD.py by Jack Galligan, Zhuo Zhang, and Vanshaj Tyagi

#Requirement 1 says to pass an empty function here
def scan_mrz_from_hardware():
    pass

#Requirement 2 wants to be able to decode 2 strings for all the relevant information

def decode_mrz(line1: str, line2: str) -> dict:
    if len(line1) != 44 or len(line2) != 44:
        #The value should be exactly 44 characters long
        raise ValueError("LengthError")
     
    document_type = line1[0:2]
    issuing_country = line1[2:5]
    names_raw = line1[5:44]
    names_clean = names_raw.replace('<', ' ').strip()
    name_parts = names_clean.split('  ')
    surname = name_parts[0]
    given_names = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

    passport_number = line2[0:9]
    passport_check = line2[9]
    nationality = line2[10:13]
    birth_date = line2[13:19]
    birth_check = line2[19]
    gender = line2[20]
    expiration_date = line2[21:27]
    expiration_check = line2[27]
    personal_number = line2[28:42]
    personal_check = line2[42]
    final_check = line2[43]

    return {
        "document_type": document_type,
        "issuing_country": issuing_country,
        "surname": surname,
        "given_names": given_names,
        "passport_number": passport_number,
        "passport_check_digit": passport_check,
        "nationality": nationality,
        "birth_date": birth_date,
        "birth_check_digit": birth_check,
        "gender": gender,
        "expiration_date": expiration_date,
        "expiration_check_digit": expiration_check,
        "personal_number": personal_number,
        "personal_check_digit": personal_check,
        "final_check_digit": final_check
    }

#Requirement 3 wants to be able to encode information into two strings.
def encode_mrz(fields: dict) -> tuple[str, str]:
    line1 = f"{fields['type']}<{fields['country']}{fields['name']:<39}".replace(" ", "<")
    line2 = (
        f"{fields['passport_number']}{fields['passport_check']}"
        f"{fields['nationality']}{fields['birth_date']}{fields['birth_check']}"
        f"{fields['sex']}{fields['expiration_date']}{fields['expiration_check']}"
        f"{fields['personal_number']:<14}{fields['final_check']}"
    ).replace(" ", "<")
    return line1[:44], line2[:44]

def query_travel_document_from_db(document_id):
    """Stub for querying travel document fields from a database."""
    pass  # No implementation needed for now

#Requirement 4 wants us to report mismatchs
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
    [9,8,7,6,5,4,3,2,1,0]
]

_p_table = [
    [0,1,2,3,4,5,6,7,8,9],
    [1,5,7,6,2,8,3,0,9,4],
    [5,8,0,3,7,9,6,1,4,2],
    [8,9,1,6,0,4,3,5,2,7],
    [9,4,5,3,1,2,6,8,7,0],
    [4,2,8,6,5,7,3,9,0,1],
    [2,7,9,3,8,0,6,4,1,5],
    [7,0,4,6,9,1,3,2,5,8]
]

_inv_table = [0,4,3,2,1,5,6,7,8,9]

def verhoeff_check_digit(number: str) -> int:
    """
    Computes Verhoeff check digit for a numeric string.
    """
    c = 0
    reversed_digits = map(int, reversed(number))
    for i, item in enumerate(reversed_digits):
        c = _d_table[c][_p_table[(i + 1) % 8][item]]
    return _inv_table[c]


def verify_field_with_verhoeff(field: str, check_digit: str) -> bool:
    """
    Verifies that field matches its Verhoeff check digit.
    """
    expected = verhoeff_check_digit(field)
    return str(expected) == check_digit

def report_check_digit_mismatches(decoded_fields: dict) -> list[str]:
    mismatches = []
    if not verify_field_with_verhoeff(decoded_fields['passport_number'], decoded_fields['passport_check_digit']):
        mismatches.append('passport_number')
    if not verify_field_with_verhoeff(decoded_fields['birth_date'], decoded_fields['birth_check_digit']):
        mismatches.append('birth_date')
    if not verify_field_with_verhoeff(decoded_fields['expiration_date'], decoded_fields['expiration_check_digit']):
        mismatches.append('expiration_date')
    if not verify_field_with_verhoeff(decoded_fields['personal_number'], decoded_fields['personal_check_digit']):
        mismatches.append('personal_number')
    return mismatches