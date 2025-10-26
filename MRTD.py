#MRTD.py by Jack Galligan, Zhuo Zhang, and Vanshaj Tyagi

#Requirement 1 says to pass an empty function here
def scan_mrz_from_hardware():
    pass

#Requirement 2 wants a

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

