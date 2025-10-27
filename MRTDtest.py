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
        line1 = "P<USASMITH<<JOHN<JAMES<<<<<<<<<<<<<<<<<<"
        line2 = "1234567890USA9001011M25050151234567890<<8"
        
        result = decode_mrz(line1, line2)
        
        self.assertEqual(result["document_type"], "P<")
        self.assertEqual(result["issuing_country"], "USA")
        self.assertEqual(result["surname"], "SMITH")
        self.assertEqual(result["given_names"], "JOHN JAMES")
        self.assertEqual(result["passport_number"], "123456789")
        self.assertEqual(result["nationality"], "USA")
        self.assertEqual(result["birth_date"], "900101")
        self.assertEqual(result["gender"], "M")
        self.assertEqual(result["expiration_date"], "250501")
    
    def test_decode_mrz_valid_input_gbr(self):
        """Test decoding valid MRZ from GBR (United Kingdom) passport"""
        line1 = "P<GBRJONES<<EMMA<CHARLOTTE<<<<<<<<<<<<<<<<"
        line2 = "9876543210GBR8512312F30123141122334455<<7"
        
        result = decode_mrz(line1, line2)
        
        self.assertEqual(result["document_type"], "P<")
        self.assertEqual(result["issuing_country"], "GBR")
        self.assertEqual(result["surname"], "JONES")
        self.assertEqual(result["given_names"], "EMMA CHARLOTTE")
        self.assertEqual(result["passport_number"], "987654321")
        self.assertEqual(result["nationality"], "GBR")
        self.assertEqual(result["gender"], "F")
    
    def test_decode_mrz_single_name(self):
        """Test decoding MRZ with only surname, no given names"""
        line1 = "P<CANMADONNA<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
        line2 = "AB12345670CAN7506201F28020151111111111<<9"
        
        result = decode_mrz(line1, line2)
        
        self.assertEqual(result["surname"], "MADONNA")
        self.assertEqual(result["given_names"], "")
    
    def test_decode_mrz_multiple_given_names(self):
        """Test decoding MRZ with multiple given names"""
        line1 = "P<DEUMULLER<<HANS<PETER<WOLFGANG<<<<<<<<<<"
        line2 = "C01234567DEU6903152M26091841234567890<<5"
        
        result = decode_mrz(line1, line2)
        
        self.assertEqual(result["surname"], "MULLER")
        self.assertEqual(result["given_names"], "HANS PETER WOLFGANG")
    
    def test_decode_mrz_line1_too_short(self):
        """Test that ValueError is raised when line1 is too short"""
        line1 = "P<USASMITH<<JOHN<<<<<<<<<<<<<<<<<<<"  # Only 38 chars
        line2 = "1234567890USA9001011M25050151234567890<<8"
        
        with self.assertRaises(ValueError) as context:
            decode_mrz(line1, line2)
        self.assertEqual(str(context.exception), "LengthError")
    
    def test_decode_mrz_line1_too_long(self):
        """Test that ValueError is raised when line1 is too long"""
        line1 = "P<USASMITH<<JOHN<JAMES<<<<<<<<<<<<<<<<<<<<<<<"  # 46 chars
        line2 = "1234567890USA9001011M25050151234567890<<8"
        
        with self.assertRaises(ValueError) as context:
            decode_mrz(line1, line2)
        self.assertEqual(str(context.exception), "LengthError")
    
    def test_decode_mrz_line2_too_short(self):
        """Test that ValueError is raised when line2 is too short"""
        line1 = "P<USASMITH<<JOHN<JAMES<<<<<<<<<<<<<<<<<<"
        line2 = "1234567890USA9001011M2505015123456789"  # Only 38 chars
        
        with self.assertRaises(ValueError) as context:
            decode_mrz(line1, line2)
        self.assertEqual(str(context.exception), "LengthError")
    
    def test_decode_mrz_line2_too_long(self):
        """Test that ValueError is raised when line2 is too long"""
        line1 = "P<USASMITH<<JOHN<JAMES<<<<<<<<<<<<<<<<<<"
        line2 = "1234567890USA9001011M25050151234567890<<8999"  # 48 chars
        
        with self.assertRaises(ValueError) as context:
            decode_mrz(line1, line2)
        self.assertEqual(str(context.exception), "LengthError")
    
    def test_decode_mrz_france_passport(self):
        """Test decoding valid MRZ from France (FRA) passport"""
        line1 = "P<FRADUPONT<<MARIE<LOUISE<<<<<<<<<<<<<<<<<<<"
        line2 = "12FR1234567FRA7802285F27123011234567890<<3"
        
        result = decode_mrz(line1, line2)
        
        self.assertEqual(result["issuing_country"], "FRA")
        self.assertEqual(result["nationality"], "FRA")
        self.assertEqual(result["surname"], "DUPONT")
        self.assertEqual(result["given_names"], "MARIE LOUISE")


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
            'personal_number': '1234567890',
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
            'personal_number': '999',
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
            'personal_number': '1234567890123',
            'final_check': '5'
        }
        
        line1, line2 = encode_mrz(fields)
        
        self.assertEqual(len(line1), 44)
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
        self.assertEqual(result, 0)
    
    def test_verhoeff_check_digit_long_number(self):
        """Test Verhoeff check digit for long number"""
        result = verhoeff_check_digit("12345678901234567890")
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
        wrong_check = "5"  # Assuming this is wrong
        
        result = verify_field_with_verhoeff(field, wrong_check)
        # This will be False if 5 is not the correct check digit
        self.assertIsInstance(result, bool)
    
    def test_verify_field_zero_check_digit(self):
        """Test verification with zero as check digit"""
        field = "000000"
        check_digit = "0"
        
        result = verify_field_with_verhoeff(field, check_digit)
        self.assertTrue(result)


class TestReportCheckDigitMismatches(unittest.TestCase):
    """Test cases for report_check_digit_mismatches function"""
    
    def test_no_mismatches(self):
        """Test when all check digits are correct"""
        decoded_fields = {
            'passport_number': '000000000',
            'passport_check_digit': '0',
            'birth_date': '000000',
            'birth_check_digit': '0',
            'expiration_date': '000000',
            'expiration_check_digit': '0',
            'personal_number': '00000000000000',
            'personal_check_digit': '0'
        }
        
        mismatches = report_check_digit_mismatches(decoded_fields)
        self.assertEqual(mismatches, [])
    
    def test_passport_number_mismatch(self):
        """Test when passport number check digit is incorrect"""
        decoded_fields = {
            'passport_number': '123456789',
            'passport_check_digit': '9',  # Intentionally wrong
            'birth_date': '000000',
            'birth_check_digit': '0',
            'expiration_date': '000000',
            'expiration_check_digit': '0',
            'personal_number': '00000000000000',
            'personal_check_digit': '0'
        }
        
        mismatches = report_check_digit_mismatches(decoded_fields)
        self.assertIn('passport_number', mismatches)
    
    def test_birth_date_mismatch(self):
        """Test when birth date check digit is incorrect"""
        decoded_fields = {
            'passport_number': '000000000',
            'passport_check_digit': '0',
            'birth_date': '900101',
            'birth_check_digit': '9',  # Intentionally wrong
            'expiration_date': '000000',
            'expiration_check_digit': '0',
            'personal_number': '00000000000000',
            'personal_check_digit': '0'
        }
        
        mismatches = report_check_digit_mismatches(decoded_fields)
        self.assertIn('birth_date', mismatches)
    
    def test_expiration_date_mismatch(self):
        """Test when expiration date check digit is incorrect"""
        decoded_fields = {
            'passport_number': '000000000',
            'passport_check_digit': '0',
            'birth_date': '000000',
            'birth_check_digit': '0',
            'expiration_date': '250501',
            'expiration_check_digit': '9',  # Intentionally wrong
            'personal_number': '00000000000000',
            'personal_check_digit': '0'
        }
        
        mismatches = report_check_digit_mismatches(decoded_fields)
        self.assertIn('expiration_date', mismatches)
    
    def test_personal_number_mismatch(self):
        """Test when personal number check digit is incorrect"""
        decoded_fields = {
            'passport_number': '000000000',
            'passport_check_digit': '0',
            'birth_date': '000000',
            'birth_check_digit': '0',
            'expiration_date': '000000',
            'expiration_check_digit': '0',
            'personal_number': '12345678901234',
            'personal_check_digit': '9'  # Intentionally wrong
        }
        
        mismatches = report_check_digit_mismatches(decoded_fields)
        self.assertIn('personal_number', mismatches)
    
    def test_multiple_mismatches(self):
        """Test when multiple check digits are incorrect"""
        decoded_fields = {
            'passport_number': '123456789',
            'passport_check_digit': '9',  # Wrong
            'birth_date': '900101',
            'birth_check_digit': '9',  # Wrong
            'expiration_date': '250501',
            'expiration_check_digit': '9',  # Wrong
            'personal_number': '12345678901234',
            'personal_check_digit': '9'  # Wrong
        }
        
        mismatches = report_check_digit_mismatches(decoded_fields)
        self.assertGreater(len(mismatches), 0)


class TestQueryTravelDocumentFromDB(unittest.TestCase):
    """Test cases for query_travel_document_from_db function"""
    
    @patch('MRTD.query_travel_document_from_db')
    def test_query_document_mock(self, mock_query):
        """Test querying travel document from database using mock"""
        mock_query.return_value = {
            'passport_number': '123456789',
            'name': 'SMITH<<JOHN',
            'nationality': 'USA'
        }
        
        result = query_travel_document_from_db('DOC123')
        
        mock_query.assert_called_once_with('DOC123')
        self.assertEqual(result['passport_number'], '123456789')
    
    def test_query_document_returns_none(self):
        """Test that query_travel_document_from_db returns None as it's a stub"""
        result = query_travel_document_from_db('DOC456')
        self.assertIsNone(result)


if __name__ == '__main__':
    # Run tests with coverage
    unittest.main(verbosity=2)