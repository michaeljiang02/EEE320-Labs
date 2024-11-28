import unittest
from unittest.mock import MagicMock
from Jiang import GenghisKhan
from shared import *


class TestGenghisKhan(unittest.TestCase):

    def setUp(self):
        # Create GenghisKhan instance
        self.gk = GenghisKhan()

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
        # Create new GenghisKhan() to test do_turn() method
        self.gk1 = GenghisKhan()
        self.gk1.strength = MagicMock(return_value=2000)
        self.assertEqual(self.gk1.organ_count, 0)
        self.gk1.do_turn()
        self.assertGreater(self.gk1.organ_count, 0)
        self.assertLessEqual(self.gk1.organ_count, 10)


    def test_destroyed(self):
        # Test if destroyed method works as expected
        gk = GenghisKhan()
        initial_count = GenghisKhan.instance_count()

        GenghisKhan.destroyed()

        self.assertEqual(GenghisKhan.instance_count(), initial_count - 1)


if __name__ == '__main__':
    unittest.main()
