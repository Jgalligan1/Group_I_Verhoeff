import json
import time
import csv
from MRTD import encode_mrz, decode_mrz, verhoeff_check_digit

def convert_to_numeric_for_check(value):
    """
    Convert alphanumeric MRZ field to numeric string for check digit calculation.
    ICAO 9303: A=10, B=11, ..., Z=35, 0-9=0-9, <=0
    """
    result = []
    for char in value.upper():
        if char.isdigit():
            result.append(char)
        elif char == '<':
            result.append('0')
        elif char.isalpha():
            # A=10, B=11, ..., Z=35
            result.append(str(ord(char) - ord('A') + 10))
    return ''.join(result)

def encode_record_from_decoded(record):
    """
    Convert a decoded record from JSON into MRZ format.
    Returns tuple (line1, line2) as strings.
    """
    line1_data = record.get('line1', {})
    line2_data = record.get('line2', {})
    
    # Extract and normalize fields
    issuing_country = line1_data.get('issuing_country', '').upper().strip()
    last_name = line1_data.get('last_name', '').upper().strip()
    given_name = line1_data.get('given_name', '').upper().strip()
    
    # Format name: SURNAME<<GIVEN<NAMES
    name = f"{last_name}<<{given_name.replace(' ', '<')}"
    
    # Extract line2 fields
    passport_raw = line2_data.get('passport_number', '').upper().strip()
    if len(passport_raw) > 9:
        passport_number = passport_raw[:9]
    else:
        passport_number = passport_raw.ljust(9, '<')
    
    country_code = line2_data.get('country_code', '').upper().strip()
    birth_date = line2_data.get('birth_date', '').strip()
    sex = line2_data.get('sex', '').upper().strip()
    expiration_date = line2_data.get('expiration_date', '').strip()
    personal_raw = line2_data.get('personal_number', '').upper().strip()
    
    # Pad personal number to exactly 14 characters
    personal_number = personal_raw.ljust(14, '<')[:14]
    
    # Calculate check digits using Verhoeff with alphanumeric conversion
    passport_check = str(verhoeff_check_digit(convert_to_numeric_for_check(passport_number)))
    birth_check = str(verhoeff_check_digit(birth_date))
    expiration_check = str(verhoeff_check_digit(expiration_date))
    personal_check = str(verhoeff_check_digit(convert_to_numeric_for_check(personal_number)))
    
    # Calculate final check digit from concatenated fields
    final_check_data = (
        passport_number + passport_check + 
        birth_date + birth_check + 
        expiration_date + expiration_check + 
        personal_number + personal_check
    )
    final_check = str(verhoeff_check_digit(convert_to_numeric_for_check(final_check_data)))
    
    # Build the fields dict for encode_mrz
    fields = {
        'type': 'P',
        'country': issuing_country,
        'name': name,
        'passport_number': passport_number,
        'passport_check': passport_check,
        'nationality': country_code,
        'birth_date': birth_date,
        'birth_check': birth_check,
        'sex': sex,
        'expiration_date': expiration_date,
        'expiration_check': expiration_check,
        'personal_number': personal_number,
        'personal_check': personal_check,
        'final_check': final_check
    }
    
    return encode_mrz(fields)

def encode_record_with_tests(record):
    """
    Encode a record with additional test assertions.
    """
    # Pre-condition: validate input
    if not isinstance(record, dict):
        raise ValueError("Record must be a dictionary")
    
    line1, line2 = encode_record_from_decoded(record)
    
    # Post-condition: validate output
    if len(line1) != 44 or len(line2) != 44:
        raise ValueError(f"Invalid MRZ length: line1={len(line1)}, line2={len(line2)}")
    
    return line1, line2

def main():
    """
    Main function to process records and measure execution times.
    Generates timing_results.csv and records_encoded.json
    """
    # Load all records
    with open('records_decoded.json', 'r') as f:
        data = json.load(f)
        all_records = data['records_decoded']
    
    print(f"Loaded {len(all_records)} records")
    
    # Prepare results storage
    timing_results = []
    k_values = [100, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]
    
    # Also encode all records for output file
    all_encoded = []
    
    for k in k_values:
        print(f"\nProcessing k={k} records...")
        records_subset = all_records[:k]
        
        # Execution without tests: encode and decode
        start_time = time.time()
        for record in records_subset:
            try:
                line1, line2 = encode_record_from_decoded(record)
                decoded = decode_mrz(line1, line2)
            except Exception as e:
                print(f"Error without tests: {str(e)[:100]}")
                continue
        time_without_tests = time.time() - start_time
        
        # Execution with tests: encode and decode with validation
        start_time = time.time()
        for record in records_subset:
            try:
                line1, line2 = encode_record_with_tests(record)
                decoded = decode_mrz(line1, line2)
                # Additional validation
                if not isinstance(decoded, dict):
                    raise ValueError("Decoded result must be dict")
            except Exception as e:
                print(f"Error with tests: {str(e)[:100]}")
                continue
        time_with_tests = time.time() - start_time
        
        timing_results.append({
            'num_records': k,
            'time_without_tests': time_without_tests,
            'time_with_tests': time_with_tests
        })
        
        print(f"  Without tests: {time_without_tests:.3f}s | With tests: {time_with_tests:.3f}s")
    
    # Save timing results to CSV
    with open('timing_results.csv', 'w', newline='') as csvfile:
        fieldnames = ['Number of lines read from the beginning of the file', 
                      'Execution time without tests (seconds)', 
                      'Execution time with unit tests (seconds)']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in timing_results:
            writer.writerow({
                'Number of lines read from the beginning of the file': result['num_records'],
                'Execution time without tests (seconds)': result['time_without_tests'],
                'Execution time with unit tests (seconds)': result['time_with_tests']
            })
    
    print(f"\nTiming results saved to timing_results.csv")
    
    # Encode all 10,000 records for output file
    print(f"\nEncoding all {len(all_records)} records for records_encoded.json...")
    error_count = 0
    error_details = []
    
    for idx, record in enumerate(all_records):
        try:
            line1, line2 = encode_record_from_decoded(record)
            mrz_string = f"{line1};{line2}"
            all_encoded.append(mrz_string)
        except Exception as e:
            error_count += 1
            if len(error_details) < 10:  # Keep first 10 errors for reporting
                error_details.append(f"Record {idx}: {str(e)[:100]}")
    
    # Save encoded records
    with open('records_encoded.json', 'w') as f:
        json.dump(all_encoded, f, indent=2)
    
    print(f"Encoded {len(all_encoded)} records successfully")
    if error_count > 0:
        print(f"Encountered {error_count} errors during encoding")
        print("First few errors:")
        for err in error_details:
            print(f"  {err}")
    
    print("\nProcessing complete!")
    print(f"  - timing_results.csv: {len(timing_results)} rows")
    print(f"  - records_encoded.json: {len(all_encoded)} records")

if __name__ == '__main__':
    main()