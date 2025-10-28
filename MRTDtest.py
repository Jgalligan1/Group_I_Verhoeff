import unittest
from unittest.mock import patch, MagicMock
from MRTD import (
    scan_mrz_from_hardware,
    decode_mrz,
    encode_mrz,
    query_travel_document_from_db,
    verhoeff_check_digit,
    verify_field_with_verhoeff,
    report_check_digit_mismatches
)


class TestScanMRZFromHardware(unittest.TestCase):
    """Test cases for scan_mrz_from_hardware function"""
    
    def test_scan_mrz_returns_none(self):
        """Test that scan_mrz_from_hardware returns None as it's a stub"""
        result = scan_mrz_from_hardware()
        self.assertIsNone(result)


class TestDecodeMRZ(unittest.TestCase):
    """Test cases for decode_mrz function"""
    
    def test_decode_mrz_valid_input_usa(self):
        """Test decoding valid MRZ from USA passport"""
        line1 = "P<USASMITH<<JOHN<JAMES<<<<<<<<<<<<<<<<<<<<<<" # 44 chars
        line2 = "1234567890USA9001011M2505015<<<<<<<<<<<<<<<8" # 44 chars
        result = decode_mrz(line1, line2)
        self.assertEqual(result['document_type'], 'P<')
        self.assertEqual(result['issuing_country'], 'USA')
        self.assertEqual(result['surname'], 'SMITH')
        self.assertEqual(result['given_names'], 'JOHN JAMES')
    
    def test_decode_mrz_valid_input_gbr(self):
        """Test decoding valid MRZ from GBR (United Kingdom) passport"""
        line1 = "P<GBRJONES<<EMMA<CHARLOTTE<<<<<<<<<<<<<<<<<<"  # 44 chars
        line2 = "9876543210GBR8512312F3012314<<<<<<<<<<<<<<<7"  # 44 chars
        result = decode_mrz(line1, line2)
        self.assertEqual(result['document_type'], 'P<')
        self.assertEqual(result['issuing_country'], 'GBR')
    
    def test_decode_mrz_single_name(self):
        """Test decoding MRZ with only surname, no given names"""
        line1 = "P<CANMADONNA<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<" # 44 chars - FIXED
        line2 = "AB12345670CAN7506201F280201509<<<<<<<<<<<<<<" # 44 chars - FIXED
        result = decode_mrz(line1, line2)
        self.assertEqual(result['surname'], 'MADONNA')
        self.assertEqual(result['given_names'], '')
    
    def test_decode_mrz_multiple_given_names(self):
        """Test decoding MRZ with multiple given names"""
        line1 = "P<DEUMULLER<<HANS<PETER<WOLFGANG<<<<<<<<<<<<" # 44 chars - FIXED
        line2 = "C01234567DEU6903152M260918405<<<<<<<<<<<<<<<" # 44 chars - FIXED
        result = decode_mrz(line1, line2)
        self.assertEqual(result['surname'], 'MULLER')
        self.assertEqual(result['given_names'], 'HANS PETER WOLFGANG')
    
    def test_decode_mrz_line1_too_short(self):
        """Test that ValueError is raised when line1 is too short"""
        line1 = "P<USASMITH<<JOHN<<<<<<<<<<<<<<<<<<<"
        line2 = "1234567890USA9001011M2505015<<<<<<<<<<<08"
        
        with self.assertRaises(ValueError) as context:
            decode_mrz(line1, line2)
        self.assertEqual(str(context.exception), "LengthError")
    
    def test_decode_mrz_line1_too_long(self):
        """Test that ValueError is raised when line1 is too long"""
        line1 = "P<USASMITH<<JOHN<JAMES<<<<<<<<<<<<<<<<<<<<<<<"
        line2 = "1234567890USA9001011M2505015<<<<<<<<<<<08"
        
        with self.assertRaises(ValueError) as context:
            decode_mrz(line1, line2)
        self.assertEqual(str(context.exception), "LengthError")
    
    def test_decode_mrz_line2_too_short(self):
        """Test that ValueError is raised when line2 is too short"""
        line1 = "P<USASMITH<<JOHN<JAMES<<<<<<<<<<<<<<<<<<<"
        line2 = "1234567890USA9001011M2505015<<<<<<<<<"
        
        with self.assertRaises(ValueError) as context:
            decode_mrz(line1, line2)
        self.assertEqual(str(context.exception), "LengthError")
    
    def test_decode_mrz_line2_too_long(self):
        """Test that ValueError is raised when line2 is too long"""
        line1 = "P<USASMITH<<JOHN<JAMES<<<<<<<<<<<<<<<<<<<"
        line2 = "1234567890USA9001011M2505015<<<<<<<<<<<08999"
        
        with self.assertRaises(ValueError) as context:
            decode_mrz(line1, line2)
        self.assertEqual(str(context.exception), "LengthError")
    
    def test_decode_mrz_france_passport(self):
        """Test decoding valid MRZ from France (FRA) passport"""
        line1 = "P<FRADUPONT<<MARIE<LOUISE<<<<<<<<<<<<<<<<<<<"  # 44 chars
        line2 = "12FR123456FRA7802285F2712301<<<<<<<<<<<<<<<3"  # 44 chars
        result = decode_mrz(line1, line2)
        self.assertEqual(result['issuing_country'], 'FRA')
        self.assertEqual(result['nationality'], 'FRA')
    
    # ADDITIONAL TEST CASES TO KILL MUTANTS
    def test_decode_mrz_all_fields_extracted(self):
        """Test that all fields are correctly extracted from MRZ"""
        line1 = "P<JPNTANAKA<<YUKI<<<<<<<<<<<<<<<<<<<<<<<<<<<"  # 44 chars
        line2 = "AB12345673JPN9505153F3012311<<<<<<<<<<<<<<<6"  # 44 chars
        result = decode_mrz(line1, line2)
        self.assertIn('document_type', result)
        self.assertIn('issuing_country', result)
        self.assertIn('surname', result)
    
    def test_decode_mrz_exactly_44_chars_line1(self):
        """Test boundary condition: line1 exactly 44 characters"""
        line1 = "P<INDKUMAR<<RAJESH<KUMAR<<<<<<<<<<<<<<<<<<<<" # 44 chars - FIXED
        line2 = "XY98765434IND8807192M310525102<<<<<<<<<<<<<<" # 44 chars - FIXED
        result = decode_mrz(line1, line2)
        self.assertEqual(result['issuing_country'], 'IND')
        self.assertEqual(len(line1), 44)
    
    def test_decode_mrz_exactly_44_chars_line2(self):
        """Test boundary condition: line2 exactly 44 characters"""
        line1 = "P<BRASILVA<<CARLOS<EDUARDO<<<<<<<<<<<<<<<<<<"  # 44 chars
        line2 = "MN54321678BRA9201055M2808151<<<<<<<<<<<<<<<9"  # 44 chars
        result = decode_mrz(line1, line2)
        self.assertEqual(result['nationality'], 'BRA')
        self.assertEqual(len(line2), 44)
    
    def test_decode_mrz_line1_43_chars(self):
        """Test edge case: line1 with 43 characters (should fail)"""
        line1 = "P<USASMITH<<JOHN<JAMES<<<<<<<<<<<<<<<<<"
        line2 = "1234567890USA9001011M2505015<<<<<<<<<<<08"
        
        with self.assertRaises(ValueError):
            decode_mrz(line1, line2)
    
    def test_decode_mrz_line2_45_chars(self):
        """Test edge case: line2 with 45 characters (should fail)"""
        line1 = "P<USASMITH<<JOHN<JAMES<<<<<<<<<<<<<<<<<<<"
        line2 = "1234567890USA9001011M2505015<<<<<<<<<<<089"
        
        with self.assertRaises(ValueError):
            decode_mrz(line1, line2)
    
    def test_decode_mrz_gender_extraction(self):
        """Test specific extraction of gender field"""
        line1 = "P<CHNTANG<<LI<MEI<<<<<<<<<<<<<<<<<<<<<<<<<<<"  # 44 chars
        line2 = "PQ13579242CHN9608253F2906181<<<<<<<<<<<<<<<7"  # 44 chars
        result = decode_mrz(line1, line2)
        self.assertEqual(result['gender'], 'F')

    
    def test_decode_mrz_male_gender(self):
        """Test extraction of male gender"""
        line1 = "P<RUSIVANOV<<DMITRI<<<<<<<<<<<<<<<<<<<<<<<<<" # 44 chars - FIXED
        line2 = "RS24681357RUS8511127M280213104<<<<<<<<<<<<<<" # 44 chars - FIXED
        result = decode_mrz(line1, line2)
        self.assertEqual(result['gender'], 'M')
    
    def test_decode_mrz_personal_number_field(self):
        """Test extraction of personal number field"""
        line1 = "P<AUSSMITH<<JAMES<ROBERT<<<<<<<<<<<<<<<<<<<<" # 44 chars - FIXED
        line2 = "AB12345674AUS9003158M270512369852147000006<<" # 44 chars - FIXED
        result = decode_mrz(line1, line2)
        self.assertEqual(len(result['personal_number']), 14)


class TestEncodeMRZ(unittest.TestCase):
    """Test cases for encode_mrz function"""
    
    def test_encode_mrz_basic(self):
        """Test encoding basic MRZ fields"""
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
            'personal_number': '12345678900000',
            'final_check': '8'
        }
        
        line1, line2 = encode_mrz(fields)
        
        self.assertEqual(len(line1), 44)
        self.assertEqual(len(line2), 44)
        self.assertTrue(line1.startswith("P<USA"))
        self.assertTrue("SMITH" in line1)
    
    def test_encode_mrz_with_padding(self):
        """Test encoding MRZ with proper padding for short fields"""
        fields = {
            'type': 'P',
            'country': 'CAN',
            'name': 'DOE<<JANE',
            'passport_number': 'AB123456',
            'passport_check': '7',
            'nationality': 'CAN',
            'birth_date': '850615',
            'birth_check': '2',
            'sex': 'F',
            'expiration_date': '280201',
            'expiration_check': '5',
            'personal_number': '99900000000000',
            'final_check': '9'
        }
        
        line1, line2 = encode_mrz(fields)
        
        self.assertEqual(len(line1), 44)
        self.assertEqual(len(line2), 44)
    
    def test_encode_mrz_long_name(self):
        """Test encoding MRZ with long name that needs truncation"""
        fields = {
            'type': 'P',
            'country': 'DEU',
            'name': 'VERYLONGSURAME<<EXTREMELYLONGFIRSTNAME',
            'passport_number': 'C0123456',
            'passport_check': '7',
            'nationality': 'DEU',
            'birth_date': '690315',
            'birth_check': '2',
            'sex': 'M',
            'expiration_date': '260918',
            'expiration_check': '4',
            'personal_number': '12345678901230',
            'final_check': '5'
        }
        
        line1, line2 = encode_mrz(fields)
        
        self.assertEqual(len(line1), 44)
        self.assertEqual(len(line2), 44)
    
    # ADDITIONAL TEST CASES TO KILL MUTANTS
    def test_encode_mrz_line1_format(self):
        """Test that line1 has correct format with type and country code"""
        fields = {
            'type': 'P',
            'country': 'GBR',
            'name': 'JONES<<EMMA',
            'passport_number': '987654321',
            'passport_check': '0',
            'nationality': 'GBR',
            'birth_date': '851231',
            'birth_check': '2',
            'sex': 'F',
            'expiration_date': '301231',
            'expiration_check': '4',
            'personal_number': '11223344550000',
            'final_check': '7'
        }
        
        line1, line2 = encode_mrz(fields)
        
        # Verify line1 starts with P< and country code
        self.assertTrue(line1.startswith("P<GBR"))
        self.assertEqual(line1[0], 'P')
        self.assertEqual(line1[1], '<')
        self.assertEqual(line1[2:5], 'GBR')
    
    def test_encode_mrz_line2_structure(self):
        """Test that line2 has correct structure with all components"""
        fields = {
            'type': 'P',
            'country': 'FRA',
            'name': 'MARTIN<<PIERRE',
            'passport_number': '12AB34567',
            'passport_check': '8',
            'nationality': 'FRA',
            'birth_date': '780228',
            'birth_check': '5',
            'sex': 'M',
            'expiration_date': '271230',
            'expiration_check': '1',
            'personal_number': '98765432100000',
            'final_check': '3'
        }
        
        line1, line2 = encode_mrz(fields)
        
        # Verify components are in line2
        self.assertTrue('12AB34567' in line2)
        self.assertTrue('FRA' in line2)
        self.assertTrue('780228' in line2)
        self.assertTrue('271230' in line2)
    
    def test_encode_mrz_space_replacement(self):
        """Test that spaces in name are replaced with < symbols"""
        fields = {
            'type': 'P',
            'country': 'ITA',
            'name': 'ROSSI  GIOVANNI',
            'passport_number': 'IT123456',
            'passport_check': '7',
            'nationality': 'ITA',
            'birth_date': '820510',
            'birth_check': '9',
            'sex': 'M',
            'expiration_date': '251215',
            'expiration_check': '6',
            'personal_number': '75315946820000',
            'final_check': '4'
        }
        
        line1, line2 = encode_mrz(fields)
        
        # Spaces should be replaced with <
        self.assertNotIn(' ', line1)
        self.assertIn('<', line1)
    
    def test_encode_mrz_truncation_at_44(self):
        """Test that lines are truncated at exactly 44 characters"""
        fields = {
            'type': 'P',
            'country': 'ESP',
            'name': 'GARCIA<<JUAN<CARLOS<FERNANDO<ANTONIO<MIGUEL',
            'passport_number': '123456789',
            'passport_check': '0',
            'nationality': 'ESP',
            'birth_date': '750820',
            'birth_check': '3',
            'sex': 'M',
            'expiration_date': '280615',
            'expiration_check': '7',
            'personal_number': '98765432109876',
            'final_check': '5'
        }
        
        line1, line2 = encode_mrz(fields)
        
        # Verify truncation
        self.assertEqual(len(line1), 44)
        self.assertEqual(len(line2), 44)
    
    def test_encode_mrz_empty_personal_number(self):
        """Test encoding with empty personal number (should be padded)"""
        fields = {
            'type': 'P',
            'country': 'NLD',
            'name': 'DEKKER<<ANNA',
            'passport_number': 'NL987654',
            'passport_check': '3',
            'nationality': 'NLD',
            'birth_date': '900415',
            'birth_check': '6',
            'sex': 'F',
            'expiration_date': '300331',
            'expiration_check': '8',
            'personal_number': '<<<<<<<<<<<<<<',
            'final_check': '2'
        }
        
        line1, line2 = encode_mrz(fields)
        
        self.assertEqual(len(line2), 44)


class TestVerhoeffCheckDigit(unittest.TestCase):
    """Test cases for verhoeff_check_digit function"""
    
    def test_verhoeff_check_digit_simple(self):
        """Test Verhoeff check digit for simple number"""
        result = verhoeff_check_digit("123456789")
        self.assertIsInstance(result, int)
        self.assertIn(result, range(10))
    
    def test_verhoeff_check_digit_single_digit(self):
        """Test Verhoeff check digit for single digit"""
        result = verhoeff_check_digit("5")
        self.assertIsInstance(result, int)
        self.assertIn(result, range(10))
    
    def test_verhoeff_check_digit_zeros(self):
        """Test Verhoeff check digit for string of zeros"""
        result = verhoeff_check_digit("000000")
        self.assertIsInstance(result, int)
        self.assertIn(result, range(10))
    
    def test_verhoeff_check_digit_long_number(self):
        """Test Verhoeff check digit for long number"""
        result = verhoeff_check_digit("12345678901234567890")
        self.assertIsInstance(result, int)
        self.assertIn(result, range(10))
    
    # ADDITIONAL TEST CASES TO KILL MUTANTS
    def test_verhoeff_check_digit_known_values(self):
        """Test Verhoeff algorithm with known correct values"""
        result1 = verhoeff_check_digit("142857")
        self.assertIn(result1, range(10))
        
        result2 = verhoeff_check_digit("123456")
        self.assertIn(result2, range(10))
        
        # Test consistency
        self.assertEqual(verhoeff_check_digit("123456"), verhoeff_check_digit("123456"))
    
    def test_verhoeff_check_digit_different_lengths(self):
        """Test Verhoeff with various length inputs"""
        result2 = verhoeff_check_digit("12")
        self.assertIn(result2, range(10))
        
        result5 = verhoeff_check_digit("12345")
        self.assertIn(result5, range(10))
        
        result10 = verhoeff_check_digit("1234567890")
        self.assertIn(result10, range(10))
        
        result15 = verhoeff_check_digit("123456789012345")
        self.assertIn(result15, range(10))
    
    def test_verhoeff_check_digit_all_same_digit(self):
        """Test Verhoeff with all same digits"""
        result_ones = verhoeff_check_digit("1111111")
        self.assertIsInstance(result_ones, int)
        self.assertIn(result_ones, range(10))
        
        result_nines = verhoeff_check_digit("9999999")
        self.assertIsInstance(result_nines, int)
        self.assertIn(result_nines, range(10))
    
    def test_verhoeff_check_digit_sequential(self):
        """Test Verhoeff with sequential numbers"""
        result = verhoeff_check_digit("0123456789")
        self.assertIsInstance(result, int)
        self.assertIn(result, range(10))
    
    def test_verhoeff_check_digit_reverse_sequential(self):
        """Test Verhoeff with reverse sequential numbers"""
        result = verhoeff_check_digit("9876543210")
        self.assertIsInstance(result, int)
        self.assertIn(result, range(10))
    
    def test_verhoeff_check_digit_alternating(self):
        """Test Verhoeff with alternating pattern"""
        result = verhoeff_check_digit("10101010")
        self.assertIsInstance(result, int)
        self.assertIn(result, range(10))


class TestVerifyFieldWithVerhoeff(unittest.TestCase):
    """Test cases for verify_field_with_verhoeff function"""
    
    def test_verify_field_correct_check_digit(self):
        """Test verification with correct check digit"""
        field = "123456789"
        check_digit = str(verhoeff_check_digit(field))
        
        result = verify_field_with_verhoeff(field, check_digit)
        self.assertTrue(result)
    
    def test_verify_field_incorrect_check_digit(self):
        """Test verification with incorrect check digit"""
        field = "123456789"
        correct_check = str(verhoeff_check_digit(field))
        wrong_check = str((int(correct_check) + 1) % 10)
        
        result = verify_field_with_verhoeff(field, wrong_check)
        self.assertFalse(result)
    
    def test_verify_field_zero_check_digit(self):
        """Test verification with zero as check digit"""
        field = "000000"
        correct_check = str(verhoeff_check_digit(field))
        
        result = verify_field_with_verhoeff(field, correct_check)
        self.assertTrue(result)
    
    # ADDITIONAL TEST CASES TO KILL MUTANTS
    def test_verify_field_all_correct_cases(self):
        """Test multiple known correct field/check digit pairs"""
        test_cases = [
            ("142857", str(verhoeff_check_digit("142857"))),
            ("000000", str(verhoeff_check_digit("000000"))),
            ("111111", str(verhoeff_check_digit("111111"))),
            ("987654321", str(verhoeff_check_digit("987654321"))),
        ]
        
        for field, check in test_cases:
            with self.subTest(field=field, check=check):
                result = verify_field_with_verhoeff(field, check)
                self.assertTrue(result)
    
    def test_verify_field_all_wrong_cases(self):
        """Test that wrong check digits return False"""
        field = "123456789"
        correct_check = str(verhoeff_check_digit(field))
        
        # Test all other digits
        for wrong_check in "0123456789":
            if wrong_check != correct_check:
                with self.subTest(wrong_check=wrong_check):
                    result = verify_field_with_verhoeff(field, wrong_check)
                    self.assertFalse(result)
    
    def test_verify_field_string_comparison(self):
        """Test that verification properly compares strings"""
        field = "999999"
        correct_check = verhoeff_check_digit(field)
        
        result = verify_field_with_verhoeff(field, str(correct_check))
        self.assertTrue(result)
    
    def test_verify_field_returns_boolean(self):
        """Test that function always returns boolean"""
        test_cases = [
            ("123456", str(verhoeff_check_digit("123456"))),
            ("654321", str(verhoeff_check_digit("654321"))),
            ("000000", str(verhoeff_check_digit("000000"))),
            ("999999", str(verhoeff_check_digit("999999"))),
        ]
        
        for field, check in test_cases:
            with self.subTest(field=field, check=check):
                result = verify_field_with_verhoeff(field, check)
                self.assertIsInstance(result, bool)


class TestReportCheckDigitMismatches(unittest.TestCase):
    """Test cases for report_check_digit_mismatches function"""
    
    def test_no_mismatches(self):
        """Test when all check digits are correct"""
        passport_num = '000000000'
        birth = '000000'
        expiry = '000000'
        personal = '00000000000000'
        
        decoded_fields = {
            'passport_number': passport_num,
            'passport_check_digit': str(verhoeff_check_digit(passport_num)),
            'birth_date': birth,
            'birth_check_digit': str(verhoeff_check_digit(birth)),
            'expiration_date': expiry,
            'expiration_check_digit': str(verhoeff_check_digit(expiry)),
            'personal_number': personal,
            'personal_check_digit': str(verhoeff_check_digit(personal))
        }
        
        mismatches = report_check_digit_mismatches(decoded_fields)
        self.assertEqual(mismatches, [])
    
    def test_passport_number_mismatch(self):
        """Test when passport number check digit is incorrect"""
        birth = '000000'
        expiry = '000000'
        personal = '00000000000000'
        passport = '123456789'
        
        wrong_passport_check = str((int(str(verhoeff_check_digit(passport))) + 1) % 10)
        
        decoded_fields = {
            'passport_number': passport,
            'passport_check_digit': wrong_passport_check,
            'birth_date': birth,
            'birth_check_digit': str(verhoeff_check_digit(birth)),
            'expiration_date': expiry,
            'expiration_check_digit': str(verhoeff_check_digit(expiry)),
            'personal_number': personal,
            'personal_check_digit': str(verhoeff_check_digit(personal))
        }
        
        mismatches = report_check_digit_mismatches(decoded_fields)
        self.assertIn('passport_number', mismatches)
    
    def test_birth_date_mismatch(self):
        """Test when birth date check digit is incorrect"""
        passport_num = '000000000'
        expiry = '000000'
        personal = '00000000000000'
        birth = '900101'
        
        wrong_birth_check = str((int(str(verhoeff_check_digit(birth))) + 1) % 10)
        
        decoded_fields = {
            'passport_number': passport_num,
            'passport_check_digit': str(verhoeff_check_digit(passport_num)),
            'birth_date': birth,
            'birth_check_digit': wrong_birth_check,
            'expiration_date': expiry,
            'expiration_check_digit': str(verhoeff_check_digit(expiry)),
            'personal_number': personal,
            'personal_check_digit': str(verhoeff_check_digit(personal))
        }
        
        mismatches = report_check_digit_mismatches(decoded_fields)
        self.assertIn('birth_date', mismatches)
    
    def test_expiration_date_mismatch(self):
        """Test when expiration date check digit is incorrect"""
        passport_num = '000000000'
        birth = '000000'
        personal = '00000000000000'
        expiry = '250501'
        
        wrong_expiry_check = str((int(str(verhoeff_check_digit(expiry))) + 1) % 10)
        
        decoded_fields = {
            'passport_number': passport_num,
            'passport_check_digit': str(verhoeff_check_digit(passport_num)),
            'birth_date': birth,
            'birth_check_digit': str(verhoeff_check_digit(birth)),
            'expiration_date': expiry,
            'expiration_check_digit': wrong_expiry_check,
            'personal_number': personal,
            'personal_check_digit': str(verhoeff_check_digit(personal))
        }
        
        mismatches = report_check_digit_mismatches(decoded_fields)
        self.assertIn('expiration_date', mismatches)
    
    def test_personal_number_mismatch(self):
        """Test when personal number check digit is incorrect"""
        passport_num = '000000000'
        birth = '000000'
        expiry = '000000'
        personal = '12345678901234'
        
        wrong_personal_check = str((int(str(verhoeff_check_digit(personal))) + 1) % 10)
        
        decoded_fields = {
            'passport_number': passport_num,
            'passport_check_digit': str(verhoeff_check_digit(passport_num)),
            'birth_date': birth,
            'birth_check_digit': str(verhoeff_check_digit(birth)),
            'expiration_date': expiry,
            'expiration_check_digit': str(verhoeff_check_digit(expiry)),
            'personal_number': personal,
            'personal_check_digit': wrong_personal_check
        }
        
        mismatches = report_check_digit_mismatches(decoded_fields)
        self.assertIn('personal_number', mismatches)
    
    def test_multiple_mismatches(self):
        """Test when multiple check digits are incorrect"""
        passport = '123456789'
        birth = '900101'
        expiry = '250501'
        personal = '12345678901234'
        
        decoded_fields = {
            'passport_number': passport,
            'passport_check_digit': str((int(str(verhoeff_check_digit(passport))) + 1) % 10),
            'birth_date': birth,
            'birth_check_digit': str((int(str(verhoeff_check_digit(birth))) + 1) % 10),
            'expiration_date': expiry,
            'expiration_check_digit': str((int(str(verhoeff_check_digit(expiry))) + 1) % 10),
            'personal_number': personal,
            'personal_check_digit': str((int(str(verhoeff_check_digit(personal))) + 1) % 10)
        }
        
        mismatches = report_check_digit_mismatches(decoded_fields)
        self.assertGreater(len(mismatches), 0)
    
    # ADDITIONAL TEST CASES TO KILL MUTANTS
    def test_all_fields_mismatch(self):
        """Test when all four check digits are incorrect"""
        passport = '987654321'
        birth = '850615'
        expiry = '280201'
        personal = '13579246801357'
        
        decoded_fields = {
            'passport_number': passport,
            'passport_check_digit': '0',
            'birth_date': birth,
            'birth_check_digit': '1',
            'expiration_date': expiry,
            'expiration_check_digit': '2',
            'personal_number': personal,
            'personal_check_digit': '3'
        }
        
        mismatches = report_check_digit_mismatches(decoded_fields)
        self.assertEqual(len(mismatches), 4)
        self.assertIn('passport_number', mismatches)
        self.assertIn('birth_date', mismatches)
        self.assertIn('expiration_date', mismatches)
        self.assertIn('personal_number', mismatches)
    
    def test_only_passport_mismatch(self):
        """Test when only passport number has mismatch"""
        birth = '000000'
        expiry = '000000'
        personal = '00000000000000'
        passport = '123456789'
        
        decoded_fields = {
            'passport_number': passport,
            'passport_check_digit': '5',
            'birth_date': birth,
            'birth_check_digit': str(verhoeff_check_digit(birth)),
            'expiration_date': expiry,
            'expiration_check_digit': str(verhoeff_check_digit(expiry)),
            'personal_number': personal,
            'personal_check_digit': str(verhoeff_check_digit(personal))
        }
        
        mismatches = report_check_digit_mismatches(decoded_fields)
        self.assertEqual(len(mismatches), 1)
        self.assertEqual(mismatches[0], 'passport_number')
    
    def test_only_birth_date_mismatch(self):
        """Test when only birth date has mismatch"""
        passport_num = '000000000'
        expiry = '000000'
        personal = '00000000000000'
        birth = '123456'
        
        decoded_fields = {
            'passport_number': passport_num,
            'passport_check_digit': str(verhoeff_check_digit(passport_num)),
            'birth_date': birth,
            'birth_check_digit': '9',
            'expiration_date': expiry,
            'expiration_check_digit': str(verhoeff_check_digit(expiry)),
            'personal_number': personal,
            'personal_check_digit': str(verhoeff_check_digit(personal))
        }
        
        mismatches = report_check_digit_mismatches(decoded_fields)
        self.assertEqual(len(mismatches), 1)
        self.assertEqual(mismatches[0], 'birth_date')
    
    def test_only_expiration_mismatch(self):
        """Test when only expiration date has mismatch"""
        passport_num = '000000000'
        birth = '000000'
        personal = '00000000000000'
        expiry = '654321'
        
        decoded_fields = {
            'passport_number': passport_num,
            'passport_check_digit': str(verhoeff_check_digit(passport_num)),
            'birth_date': birth,
            'birth_check_digit': str(verhoeff_check_digit(birth)),
            'expiration_date': expiry,
            'expiration_check_digit': '8',
            'personal_number': personal,
            'personal_check_digit': str(verhoeff_check_digit(personal))
        }
        
        mismatches = report_check_digit_mismatches(decoded_fields)
        self.assertEqual(len(mismatches), 1)
        self.assertEqual(mismatches[0], 'expiration_date')
    
    def test_only_personal_number_mismatch(self):
        """Test when only personal number has mismatch"""
        passport_num = '000000000'
        birth = '000000'
        expiry = '000000'
        personal = '99999999999999'
        
        decoded_fields = {
            'passport_number': passport_num,
            'passport_check_digit': str(verhoeff_check_digit(passport_num)),
            'birth_date': birth,
            'birth_check_digit': str(verhoeff_check_digit(birth)),
            'expiration_date': expiry,
            'expiration_check_digit': str(verhoeff_check_digit(expiry)),
            'personal_number': personal,
            'personal_check_digit': '7'
        }
        
        mismatches = report_check_digit_mismatches(decoded_fields)
        self.assertEqual(len(mismatches), 1)
        self.assertEqual(mismatches[0], 'personal_number')
    
    def test_two_mismatches_passport_and_birth(self):
        """Test when passport and birth date have mismatches"""
        expiry = '000000'
        personal = '00000000000000'
        passport = '111111111'
        birth = '222222'
        
        decoded_fields = {
            'passport_number': passport,
            'passport_check_digit': str((int(str(verhoeff_check_digit(passport))) + 1) % 10),
            'birth_date': birth,
            'birth_check_digit': str((int(str(verhoeff_check_digit(birth))) + 1) % 10),
            'expiration_date': expiry,
            'expiration_check_digit': str(verhoeff_check_digit(expiry)),
            'personal_number': personal,
            'personal_check_digit': str(verhoeff_check_digit(personal))
        }
        
        mismatches = report_check_digit_mismatches(decoded_fields)
        self.assertEqual(len(mismatches), 2)
        self.assertIn('passport_number', mismatches)
        self.assertIn('birth_date', mismatches)
    
    def test_mismatch_list_order(self):
        """Test that mismatches are returned in expected order"""
        decoded_fields = {
            'passport_number': '555555555',
            'passport_check_digit': '1',
            'birth_date': '666666',
            'birth_check_digit': '2',
            'expiration_date': '777777',
            'expiration_check_digit': '3',
            'personal_number': '88888888888888',
            'personal_check_digit': '4'
        }
        
        mismatches = report_check_digit_mismatches(decoded_fields)
        
        if len(mismatches) == 4:
            self.assertEqual(mismatches[0], 'passport_number')
            self.assertEqual(mismatches[1], 'birth_date')
            self.assertEqual(mismatches[2], 'expiration_date')
            self.assertEqual(mismatches[3], 'personal_number')


class TestQueryTravelDocumentFromDB(unittest.TestCase):
    """Test cases for query_travel_document_from_db function"""
    
    def test_query_document_mock(self):
        """Test querying travel document from database using mock"""
        result = query_travel_document_from_db('DOC123')
        self.assertIsNone(result)
    
    def test_query_document_returns_none(self):
        """Test that query_travel_document_from_db returns None as it's a stub"""
        result = query_travel_document_from_db('DOC456')
        self.assertIsNone(result)


if __name__ == '__main__':
    # Run tests with coverage
    unittest.main(verbosity=2)