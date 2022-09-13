import unittest
from ksp_comm_array_calc import GameData, CelestialBody, CommPart
from ksp_comm_array_calc import valid_percent, valid_comm_parts
from ksp_comm_array_calc import read_game_data, GAME_DATA_FILE_PATH
from ksp_comm_array_calc import pretty_distance, pretty_time, pretty_speed
from ksp_comm_array_calc import calculate_combined_comm_power, calculate_minimum_comm_distance


# TODO Make these tests use hard coded values instead of reading from the json file


class TestArgValidFunctions(unittest.TestCase):
    def test_valid_percent(self):
        self.assertEqual(1.0, valid_percent("100%"))
        self.assertEqual(0.01, valid_percent("1%"))

        self.assertEqual(1.0, valid_percent("100"))
        self.assertEqual(0.01, valid_percent("1"))

        self.assertEqual(0.36, valid_percent("36"))
        self.assertEqual(0.02, valid_percent("2"))

        self.assertEqual(0, valid_percent("0"))
        self.assertEqual(0, valid_percent("00"))

        with self.assertRaises(TypeError):
            valid_percent("300%")
        with self.assertRaises(TypeError):
            valid_percent("300")
        with self.assertRaises(TypeError):
            valid_percent("101%")
        with self.assertRaises(TypeError):
            valid_percent("101")

    def test_valid_comm_parts(self):
        self.assertEqual({"HG5": 10}, valid_comm_parts("10:HG5"))
        self.assertEqual({"HG_5": 1}, valid_comm_parts("1:HG_5"))

        self.assertEqual({"HG_5": 1}, valid_comm_parts("1:HG_5,"))
        self.assertEqual({"HG_5": 1, "CT1": 5}, valid_comm_parts("1:HG_5,5:CT1"))
        self.assertEqual({"HG_5": 1, "CT1": 5}, valid_comm_parts("1:HG_5,5:CT1,"))
        self.assertEqual({"HG_5": 1, "CT1": 5, "DC10": 10, "PL1": 2}, valid_comm_parts("1:HG_5,5:CT1,10:DC10,2:PL1"))

        with self.assertRaises(TypeError):
            valid_comm_parts("0:HG_5")
        with self.assertRaises(TypeError):
            valid_comm_parts("-10:HG_5")
        with self.assertRaises(TypeError):
            valid_comm_parts("-10:HG_5,,")
        with self.assertRaises(TypeError):
            valid_comm_parts("1:HG+5")
        with self.assertRaises(TypeError):
            valid_comm_parts("1:HG_5,5:")
        with self.assertRaises(TypeError):
            valid_comm_parts("1:HG5,2:HG5")
        with self.assertRaises(TypeError):
            valid_comm_parts("1:HG52:HG5")


class TestGameData(unittest.TestCase):
    def test_verify_body(self):
        game_data = read_game_data(GAME_DATA_FILE_PATH)

        self.assertTrue(game_data.verify_body("kerbin"))
        self.assertTrue(game_data.verify_body("Kerbin"))
        self.assertTrue(game_data.verify_body("mun"))
        self.assertTrue(game_data.verify_body("Mun"))

        self.assertFalse(game_data.verify_body("space"))
        self.assertFalse(game_data.verify_body("dunae"))

    def test_comm_parts(self):
        game_data = read_game_data(GAME_DATA_FILE_PATH)

        self.assertTrue(game_data.verify_comm_part("HG5"))
        # self.assertTrue(game_data.verify_comm_part("mun"))

        self.assertFalse(game_data.verify_comm_part("Comm Radio"))
        self.assertFalse(game_data.verify_comm_part("HG-5 High Gain Antenna"))

    def test_get_part_name_from_alias(self):
        pass


class TestCelestialBody(unittest.TestCase):
    def test_calculate_orbital_period(self):
        body = CelestialBody("test", {"radius": 200000, "mass": 975990660000000000000,
                                      "sphere of influence": 0, "parent body": ""})

        self.assertEqual(28800, body.calculate_orbital_period(1254850, 565650))
        self.assertEqual(43200, body.calculate_orbital_period(1254850, 1254850))

    def test_calculate_orbit_radius_with_period(self):
        body = CelestialBody("test", {"radius": 200000, "mass": 975990660000000000000,
                                      "sphere of influence": 0, "parent body": ""})

        self.assertEqual(1254855, body.calculate_orbit_radius_with_period(43200))

    def test_calculate_periapsis_with_apoapsis_and_period(self):
        body = CelestialBody("test", {"radius": 200000, "mass": 975990660000000000000,
                                      "sphere of influence": 0, "parent body": ""})

        self.assertEqual(565669, body.calculate_periapsis_with_apoapsis_and_period(1254855, 28800))

    def test_calculate_delta_v_for_hohmann_transfer(self):
        body_1 = CelestialBody("test", {"radius": 600000, "mass": 52915158000000000000000,
                                        "sphere of influence": 0, "parent body": ""})

        self.assertEqual(153, body_1.calculate_delta_v_for_hohmann_transfer(80000, 300000))

        body_2 = CelestialBody("test", {"radius": 200000, "mass": 975990660000000000000,
                                        "sphere of influence": 0, "parent body": ""})
        self.assertEqual(46, body_2.calculate_delta_v_for_hohmann_transfer(432000, 1000000))


class TestHelperFunctions(unittest.TestCase):
    def test_pretty_distance(self):
        self.assertEqual("10 m", pretty_distance(10))
        self.assertEqual("542 m", pretty_distance(542))
        self.assertEqual("999 m", pretty_distance(999))

        self.assertEqual("1 km", pretty_distance(1000))
        self.assertEqual("3.333 km", pretty_distance(3333))
        self.assertEqual("10 km", pretty_distance(10000))
        self.assertEqual("75.671 km", pretty_distance(75671))
        self.assertEqual("999.999 km", pretty_distance(999999))

        self.assertEqual("1 Mm", pretty_distance(1000000))
        self.assertEqual("3.333333 Mm", pretty_distance(3333333))
        self.assertEqual("10 Mm", pretty_distance(10000000))
        self.assertEqual("75.671382 Mm", pretty_distance(75671382))
        self.assertEqual("999.999999 Mm", pretty_distance(999999999))

        self.assertEqual("1 Gm", pretty_distance(1000000000))
        self.assertEqual("3.333333333 Gm", pretty_distance(3333333333))
        self.assertEqual("10 Gm", pretty_distance(10000000000))
        self.assertEqual("75.671382123 Gm", pretty_distance(75671382123))
        self.assertEqual("999.999999999 Gm", pretty_distance(999999999999))

        self.assertEqual("1 Tm", pretty_distance(1000000000000))
        self.assertEqual("3.333333333333 Tm", pretty_distance(3333333333333))
        self.assertEqual("10 Tm", pretty_distance(10000000000000))
        self.assertEqual("75.671382123487 Tm", pretty_distance(75671382123487))
        self.assertEqual("999.999999999999 Tm", pretty_distance(999999999999999))

    def test_pretty_time(self):
        self.assertEqual("0 secs", pretty_time(0))
        self.assertEqual("1 sec", pretty_time(1))
        self.assertEqual("10 secs", pretty_time(10))
        self.assertEqual("59 secs", pretty_time(59))

        self.assertEqual("1 min 0 secs", pretty_time(60))
        self.assertEqual("42 mins 2 secs", pretty_time(2522))
        self.assertEqual("30 mins 0 secs", pretty_time(1800))
        self.assertEqual("30 mins 1 sec", pretty_time(1801))
        self.assertEqual("59 mins 59 secs", pretty_time(3599))

        self.assertEqual("1 hr 0 mins 0 secs", pretty_time(3600))
        self.assertEqual("256 hrs 34 mins 3 secs", pretty_time(923643))
        self.assertEqual("24 hrs 0 mins 0 secs", pretty_time(86400))
        self.assertEqual("9517 hrs 20 mins 17 secs", pretty_time(34262417))

    def test_pretty_speed(self):
        self.assertEqual("100 m/s", pretty_speed(100))
        self.assertEqual("1 m/s", pretty_speed(1))
        self.assertEqual("254 m/s", pretty_speed(254))
        self.assertEqual("999 m/s", pretty_speed(999))
        self.assertEqual("1,000 m/s", pretty_speed(1000))
        self.assertEqual("1,526 m/s", pretty_speed(1526))
        self.assertEqual("1,273,893 m/s", pretty_speed(1273893))


class TestCommunicationCalculators(unittest.TestCase):
    def test_calculate_combined_comm_power(self):
        test_part_1 = {"alias": None, "power": 5000000, "combinable": None,
                       "combinability exponent": 0.75, "relay": None}
        test_part_2 = {"alias": None, "power": 100_000_000_000, "combinable": None,
                       "combinability exponent": 0.75, "relay": None}
        test_part_3 = {"alias": None, "power": 500_000, "combinable": None,
                       "combinability exponent": 1, "relay": None}

        self.assertEqual(5000000, calculate_combined_comm_power([CommPart("Test Part", test_part_1, 1)]))
        self.assertEqual(8408964, calculate_combined_comm_power([CommPart("Test Part", test_part_1, 2)]))

        self.assertEqual(100000375000, calculate_combined_comm_power([CommPart("Test Part 1", test_part_2, 1),
                                                                      CommPart("Test Part 2", test_part_3, 1)]))

    def test_calculate_minimum_comm_distance(self):
        self.assertEqual(454009, calculate_minimum_comm_distance(5000000, 500000, 0.8))

        self.assertEqual(588777, calculate_minimum_comm_distance(8408964, 500000, 0.8))


class FullArgumentPassingFailureTests(unittest.TestCase):
    def test_valid_percent(self):
        pass

