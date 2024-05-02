import unittest
import os

from main.python import sparktask01
from dotenv import load_dotenv

class TestFunctions(unittest.TestCase):
    def setUp(self):
        # real location for test
        self.testlocation = {
            'county':"HU",
            'city' : "Budapest",
            'address' :"1054 Kossuth tér 1-3",
            'latitude' : 47.50671,
            'longitude' : 19.04552
        }
        load_dotenv()

        #OPENCAGE_API_KEY comes from .env file, or OS environmment variable in unit tests. In the main program, it is set in spark-context.
        sparktask01.OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")

    # get_latitude tests
    def test_latitude_valid_int(self):
        value = 40
        result = sparktask01.get_latitude(value, "","","")
        self.assertEqual(result,value)

    def test_latitude_valid_float(self):
        value = -4.6
        result = sparktask01.get_latitude(value, "","","")
        self.assertEqual(result,value)

    def test_latitude_valid_string(self):
        value = "-4.6"
        result = sparktask01.get_latitude(value, "","","")
        self.assertEqual(result,value)

    def test_latitude_invalid_null(self):
        value = None
        result = sparktask01.get_latitude(value, "","","")
        self.assertIsInstance(result, str)
        self.assertEqual(float(result),0.0)

    def test_latitude_invalid_string(self):
        value = "NA"
        result = sparktask01.get_latitude(value, "","","")
        self.assertIsInstance(result, str)
        self.assertEqual(float(result),0.0)

    def test_latitude_null_valid_address(self):
        value = None
        result = sparktask01.get_latitude(value, self.testlocation['county'],self.testlocation['city'],self.testlocation['address'])
        self.assertIsInstance(result, str)
        self.assertAlmostEqual(float(result),self.testlocation['latitude'],2) #2-digit precision is enough

    def test_latitude_string_valid_address(self):
        value = "NA"
        result = sparktask01.get_latitude(value, self.testlocation['county'],self.testlocation['city'],self.testlocation['address'])
        self.assertIsInstance(result, str)
        self.assertAlmostEqual(float(result),self.testlocation['latitude'],2) #2-digit precision is enough

    # get_longitude tests
    def test_longitude_valid_int(self):
        value = 40
        result = sparktask01.get_longitude(value, "","","")
        self.assertEqual(result,value)

    def test_longitude_valid_float(self):
        value = -4.6
        result = sparktask01.get_longitude(value, "","","")
        self.assertEqual(result,value)

    def test_longitude_valid_string(self):
        value = "-4.6"
        result = sparktask01.get_longitude(value, "","","")
        self.assertEqual(result,value)

    def test_longitude_invalid_null(self):
        value = None
        result = sparktask01.get_longitude(value, "","","")
        self.assertIsInstance(result, str)
        self.assertEqual(float(result),0.0)

    def test_longitude_invalid_string(self):
        value = "NA"
        result = sparktask01.get_longitude(value, "","","")
        self.assertIsInstance(result, str)
        self.assertEqual(float(result),0.0)

    def test_longitude_null_valid_address(self):
        value = None
        result = sparktask01.get_longitude(value, self.testlocation['county'],self.testlocation['city'],self.testlocation['address'])
        self.assertIsInstance(result, str)
        self.assertAlmostEqual(float(result),self.testlocation['longitude'],2) #2-digit precision is enough

    def test_longitude_string_valid_address(self):
        value = "NA"
        result = sparktask01.get_longitude(value, self.testlocation['county'],self.testlocation['city'],self.testlocation['address'])
        self.assertIsInstance(result, str)
        self.assertAlmostEqual(float(result),self.testlocation['longitude'],2) #2-digit precision is enough

    # geohash_encode test
    def test_geohash_encode_length(self):
        result = sparktask01.geohash_encode(self.testlocation['latitude'], self.testlocation['longitude'])
        self.assertIsInstance(result, str)
        self.assertEqual(len(result),4)


if __name__ == '__main__':
    unittest.main()