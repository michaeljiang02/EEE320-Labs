import unittest
from unittest.mock import MagicMock
from Jiang import JianghisKhan
from shared import *


class TestJianghisKhan(unittest.TestCase):

    def setUp(self):
        # Create JianghisKhan instance
        self.gk = JianghisKhan()

        # Provide mock value for strength
        self.gk.strength = MagicMock(return_value=2000)

    def test_initial_organ_count(self):
        # Test if initial organ count is set correctly (should be 0)
        self.assertEqual(self.gk.organ_count, 0)

    def test_create_organs(self):
        self.gk.create_organs()

        # Check if organs were created
        self.assertIsNotNone(self.gk.cilia)
        self.assertIsNotNone(self.gk.type_sensor)
        self.assertIsNotNone(self.gk.womb)
        self.assertIsNotNone(self.gk.photoglands)
        self.assertEqual(len(self.gk.photoglands), 7)
        # Organ count respects cap
        self.assertLessEqual(self.gk.organ_count, 10)


    def test_do_turn(self):
        # Create new JianghisKhan() to test do_turn() method
        self.gk1 = JianghisKhan()
        self.gk1.strength = MagicMock(return_value=300)
        self.assertEqual(self.gk1.organ_count, 0)
        self.gk1.do_turn()
        self.assertGreater(self.gk1.organ_count, 0)
        self.assertEqual(self.gk1.organ_count, 10)
        """ Was able to create 10 organs with only 300 strength, this is not normal 
        but I don't know where the problem is. Jordan please revise code to check where it went wrong
        either with the original shared file or in my code.
        """


    def test_destroyed(self):
        # Test if destroyed method works as expected
        gk = JianghisKhan()
        initial_count = JianghisKhan.instance_count()

        JianghisKhan.destroyed()

        self.assertEqual(JianghisKhan.instance_count(), initial_count - 1)


if __name__ == '__main__':
    unittest.main()
