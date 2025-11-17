from MRTD import encode_mrz, decode_mrz

# Example fields to encode
fields = {
    "type": "P",
    "country": "USA",
    "name": "DOE<<JOHN",
    "passport_number": "123456789",
    "passport_check": "0",
    "nationality": "USA",
    "birth_date": "900101",
    "birth_check": "7",
    "sex": "M",
    "expiration_date": "300101",
    "expiration_check": "2",
    "personal_number": "987654321",
    "personal_check": "1",
    "final_check": "9"
}

line1, line2 = encode_mrz(fields)

print("MRZ Line 1:", line1)
print("MRZ Line 2:", line2)
print("Line1 length:", len(line1))
print("Line2 length:", len(line2))
