from road_work import hexstr_matches, pairs_list, within_interval, get_inj_id, convert_attack_to_csv
import unittest
import json


class TestHexStrMatches(unittest.TestCase):
    def test_hex(self):
        self.assertTrue(hexstr_matches(data="3F7", inj="3F7"))
        self.assertFalse(hexstr_matches(data="3F7", inj="3F8"))
    def test_inj_none(self):
        self.assertTrue(hexstr_matches(data="A", inj=None))
    def test_diff_len(self):
        self.assertFalse(hexstr_matches(data="A", inj="AA"))
        self.assertFalse(hexstr_matches(data="AA", inj="A"))
    def test_wildcard(self):
        self.assertTrue(hexstr_matches(data="111DF2", inj="11XXF2"))
        self.assertTrue(hexstr_matches(data="ABCD", inj="XXXX"))
        self.assertFalse(hexstr_matches(data="ABC", inj="XXXX"))


class TestPairsList(unittest.TestCase):
    def test_even(self):
        self.assertEqual(["12", "34", "56"], pairs_list("123456"))
    def test_odd(self):
        self.assertEqual(["12", "34"], pairs_list("12345"))


class TestWithinInterval(unittest.TestCase):
    def test_none(self):
        self.assertTrue(within_interval(2, None))
    def test_int(self):
        self.assertTrue(within_interval(2, (1, 3)))
        self.assertTrue(within_interval(2, (2, 3)))
        self.assertTrue(within_interval(2, (1, 2)))
    def test_float(self):
        orig_start = 9.191851  # start of interval from json file
        orig_end = 30.050109  # end of interval from json file
        offset = 1030000000.000000  # offset is timestamp of first line in log file
        # line 21992 of correlated_signal_attack_1.log should be in interval
        self.assertTrue(within_interval(1030000009.191851,
                                        (orig_start + offset, orig_end + offset)))
    def test_float_from_str(self):
        orig_start = 9.191851  # start of interval from json file
        orig_end = 30.050109  # end of interval from json file
        capture = "(1030000000.000000) can0 354#200A000000027480".strip().split()
        offset = float(capture[0][1:-1])  # offset is timestamp of first line in log file
        # line 21992 of correlated_signal_attack_1.log should be in interval
        self.assertTrue(within_interval(1030000009.191851,
                                        (orig_start + offset, orig_end + offset)))


class TestGetInjId(unittest.TestCase):
    def test_none(self):
        self.assertIsNone(get_inj_id(None))
    def test_hex_len_3(self):
        self.assertEqual("ABC", get_inj_id("0xABC"))
    def test_hex_len_2(self):
        self.assertEqual("0F4", get_inj_id("0xF4"))
    def test_capital(self):
        self.assertEqual("A2C", get_inj_id("0xa2c"))


class TestConvertAttackToCsv(unittest.TestCase):
    # these tests make sure miscellaneous things in the
    # convert_attack_to_csv function work as intended.
    # copy/pasting the code isn't ideal, but it's fine
    def test_offset(self):
        line = "(1030000000.000000) can0 354#200A000000027480"  # first line in correlated_signal_attack_1.log
        capture = line.strip().split()
        offset = int(float(capture[0][1:-1]))
        self.assertEqual(1030000000, offset)
    def test_cap_time(self):
        line = "(1030000000.093102) can0 125#900040DF3FFF9160"  # line 225 in correlated_signal_attack_1.log
        capture = line.strip().split()
        cap_time = float(capture[0][1:-1])  # timestamp of capture
        self.assertEqual(1030000000.093102, cap_time)


# def attack_to_csv_test():
#     # open outfile and look for:
#         # - correct times with 6 decimal places
#         # - correct ids and bytes
#         # - attacks are labelled
#     features = ["Time", "Id", "Byte1", "Byte2", "Byte3", "Byte4",
#             "Byte5", "Byte6", "Byte7", "Byte8", "Label"]
#     with open("road-dataset/attacks/capture_metadata.json", "r") as f:
#         metadata = json.load(f)
#         convert_attack_to_csv("road-dataset/attacks/correlated_signal_attack_1.log",
#                               "LCCDE-code-cleaning/attacks/correlated_signal_attack_1.csv",
#                               features,
#                               metadata["correlated_signal_attack_1"],
#                               "correlated_signal_attack_1")
#
#
# attack_to_csv_test()


if __name__ == '__main__':
    unittest.main()
