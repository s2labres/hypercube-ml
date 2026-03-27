import unittest
from datetime import date

from hypercube.stas.sampler import STASSampler


class STASSamplerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.population_descriptor_json_path_short = "hypercube/stas/tests/data/population_descriptor.json"
        cls.population_descriptor_json_path_extended = "hypercube/stas/tests/data/population_descriptor_extended.json"
        cls.sample_hash_type = "fake_hash"
        cls.timestamp_type = "timestamp"
        cls.detections_key = "num_detection"
        cls.stas_sampler_extended_population = STASSampler(cls.population_descriptor_json_path_extended,
                                                           cls.sample_hash_type, cls.timestamp_type,
                                                           cls.detections_key, 4)

    def test_sampler_setup(self):
        stas_sampler = STASSampler(self.population_descriptor_json_path_short, self.sample_hash_type,
                                   self.timestamp_type, self.detections_key, vtt=4)

        self.assertEqual(stas_sampler.goodware_to_timestamp_dict,
                         {"g_1": date(2015, 1, 15),
                          "g_2": date(2015, 2, 15),
                          "g_3": date(2015, 3, 15)})

        self.assertEqual(stas_sampler.malware_to_timestamp_dict,
                         {"m_1": date(2015, 1, 15),
                          "m_2": date(2015, 2, 15),
                          "m_4": date(2015, 4, 15)})

    def test_sample_dataset(self):
        pass

    def test__get_all_samples_in_time_interval(self):
        start_date, end_date = date(2015, 1, 1), date(2015, 2, 28)
        available_malware = self.stas_sampler_extended_population._get_all_samples_in_time_interval(
            start_date, end_date, is_malware=True
        )
        available_goodware = self.stas_sampler_extended_population._get_all_samples_in_time_interval(
            start_date, end_date, is_malware=False
        )

        self.assertEqual(set(available_malware), {"m_10", "m_11", "m_12", "m_13", "m_14", "m_15", "m_16", "m_17", "m_18",
                                                  "m_20", "m_21", "m_22", "m_23", "m_24", "m_25", "m_26", "m_27",
                                                  "m_28", "m_29"})
        self.assertEqual(set(available_goodware), {"g_10", "g_11", "g_12", "g_13", "g_14", "g_15", "g_16", "g_17",
                                                   "g_18", "g_19", "g_110", "g_111", "g_112", "g_113", "g_114", "g_115",
                                                   "g_116", "g_117", "g_118", "g_119", "g_120", "g_20", "g_21", "g_22",
                                                   "g_23", "g_24", "g_25", "g_26", "g_27", "g_28", "g_29", "g_210",
                                                   "g_211", "g_212", "g_213", "g_214", "g_215", "g_216", "g_217",
                                                   "g_218", "g_219", "g_220", "g_221", "g_222", "g_223",
                                                   "g_224", "g_225"})


if __name__ == '__main__':
    unittest.main()
