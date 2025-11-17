import json
import time
import csv
from MRTD import encode_mrz, decode_mrz

INPUT_FILE = "records_decoded.json"
OUTPUT_CSV = "timing_results.csv"

# -----------------------------
# Step 1: Load and flatten records
# -----------------------------
with open(INPUT_FILE, "r") as f:
    data = json.load(f)

records_raw = data["records_decoded"]  # list of records

def flatten_record(record):
    """
    Converts JSON record to format expected by encode_mrz()
    """
    line1 = record.get("line1", {})
    line2 = record.get("line2", {})
    return {
        "type": "P",
        "country": line1.get("issuing_country", "XXX"),
        "name": f'{line1.get("last_name","")}<<{line1.get("given_name","")}',
        "passport_number": line2.get("passport_number", ""),
        "passport_check": "0",   # placeholder; replace with Verhoeff if needed
        "nationality": line2.get("country_code", "XXX"),
        "birth_date": line2.get("birth_date", ""),
        "birth_check": "0",
        "sex": line2.get("sex", "X"),
        "expiration_date": line2.get("expiration_date", ""),
        "expiration_check": "0",
        "personal_number": line2.get("personal_number", ""),
        "personal_check": "0",
        "final_check": "0"
    }

records = [flatten_record(r) for r in records_raw]

# -----------------------------
# Step 2: Timing functions
# -----------------------------
TEST_SIZES = [100] + list(range(1000, 10001, 1000))

def run_encode(records_slice):
    for rec in records_slice:
        encode_mrz(rec)

def run_decode(records_slice):
    for rec in records_slice:
        l1, l2 = encode_mrz(rec)
        decode_mrz(l1, l2)

def measure(func, records_slice):
    """
    Measure execution time of func(records_slice)
    Assumes Python -O flag is used externally to disable assertions if desired
    """
    start = time.perf_counter()
    func(records_slice)
    end = time.perf_counter()
    return end - start

# -----------------------------
# Step 3: Write CSV results
# -----------------------------
with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["NumRecords", "EncodeTime(s)", "DecodeTime(s)"])

    for n in TEST_SIZES:
        sample = records[:n]
        print(f"Processing {n} records...")

        enc_time = measure(run_encode, sample)
        dec_time = measure(run_decode, sample)

        writer.writerow([n, enc_time, dec_time])
        print(f"Done: {n} records")

print(f"All timing results written to {OUTPUT_CSV}")
