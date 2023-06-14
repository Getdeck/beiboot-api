from datetime import timedelta
from unittest import TestCase

from cluster.helpers import convert_to_timedelta


class ConvertToTimedelta(TestCase):
    def test_valid(self):
        self.assertEqual(convert_to_timedelta("1d2h3m4s"), timedelta(days=1, hours=2, minutes=3, seconds=4))
        self.assertEqual(convert_to_timedelta("1d2h3m"), timedelta(days=1, hours=2, minutes=3))
        self.assertEqual(convert_to_timedelta("1d2h4s"), timedelta(days=1, hours=2, seconds=4))
        self.assertEqual(convert_to_timedelta("1d3m4s"), timedelta(days=1, minutes=3, seconds=4))
        self.assertEqual(convert_to_timedelta("2h3m4s"), timedelta(hours=2, minutes=3, seconds=4))
        self.assertEqual(convert_to_timedelta("1d2h"), timedelta(days=1, hours=2))
        self.assertEqual(convert_to_timedelta("1d3m"), timedelta(days=1, minutes=3))
        self.assertEqual(convert_to_timedelta("1d4s"), timedelta(days=1, seconds=4))
        self.assertEqual(convert_to_timedelta("2h3m"), timedelta(hours=2, minutes=3))
        self.assertEqual(convert_to_timedelta("2h4s"), timedelta(hours=2, seconds=4))
        self.assertEqual(convert_to_timedelta("3m4s"), timedelta(minutes=3, seconds=4))
        self.assertEqual(convert_to_timedelta("1d"), timedelta(days=1))
        self.assertEqual(convert_to_timedelta("2h"), timedelta(hours=2))
        self.assertEqual(convert_to_timedelta("3m"), timedelta(minutes=3))
        self.assertEqual(convert_to_timedelta("4s"), timedelta(seconds=4))

    def test_invalid_none(self):
        self.assertRaises(TypeError, convert_to_timedelta, None)

    def test_invalid(self):
        self.assertRaises(ValueError, convert_to_timedelta, "bla")
