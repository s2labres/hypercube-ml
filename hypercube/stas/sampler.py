import datetime
import random

from android_malware_detectors.datasets_utils.dates import parse_date, generate_dates_in_interval
from android_malware_detectors.utils import load_json

from hypercube.stas.margin_of_error_sampling import compute_margin_of_error_sampling


class STASSampler:
    def __init__(self, population_descriptor_json_path, sample_hash_type, timestamp_type, detections_key, vtt):
        """
        :param population_descriptor_json_path: path to a JSON file containing a list of samples. Each entry must
                                                    contain a hash value keyed by sample_hash_type, a timestamp
                                                    keyed by timestamp_type, and a number of detections keyed by
                                                    detections_key.
        :param sample_hash_type: the type of hash to be used to identify samples. Each sample entry in the population
                                    descriptor file must contain that sample_hash_type.
                                    For example, if sample_hash_type="sha256", there must be for each sample an
                                    entry [..., {"sha256": "...", ...}, ...].
        :param timestamp_type: the type of timestamp to be used for each sample. Each sample entry in the population
                                    descriptor file must contain that timestamp type.
                                    For example, if timestamp_type="dex_date", there must be for each sample an
                                    entry [..., {"dex_date": 12345, ...}, ...].
        :detections_key: the key to identify the number of detections for each sample in the population.
                            Each sample entry in the population descriptor file must contain that timestamp type.
                            For example, if detection_key="vt_detection", there must be for each sample an
                                    entry [..., {"vt_detection": 0, ...}, ...].
        :param vtt: The minimum number of detections to identify a given sample as malicious. Notice that all samples
                        with number of detections greater than 0 but less than vtt are excluded from the population.
        """
        self.sample_hash_type = sample_hash_type
        self.timestamp_type = timestamp_type
        self.detections_key = detections_key
        self.vtt = vtt

        population_descriptor = load_json(population_descriptor_json_path)
        self.malware_to_timestamp_dict = self._get_all_malware(population_descriptor)
        self.goodware_to_timestamp_dict = self._get_all_goodware(population_descriptor)

    def _get_all_malware(self, population_descriptor):
        malware = {}
        for sample in population_descriptor:
            if self.detections_key in sample and int(sample[self.detections_key] or 0) >= self.vtt:
                malware[sample[self.sample_hash_type]] = parse_date(sample[self.timestamp_type])
        return malware

    def _get_all_goodware(self, population_descriptor):
        goodware = {}
        for sample in population_descriptor:
            if self.detections_key in sample and int(sample[self.detections_key] or 15) == 0:
                goodware[sample[self.sample_hash_type]] = parse_date(sample[self.timestamp_type])
        return goodware

    def sample_dataset(self, start_date: datetime.date, end_date: datetime.date,
                       time_granularity: str, time_granularity_value: int, malware_percentage: float = 0.1) -> list:
        dataset = []

        all_dates_in_interval = generate_dates_in_interval(start_date, end_date, time_granularity,
                                                           time_granularity_value)
        all_dates_in_interval += [end_date]
        for date_index in range(len(all_dates_in_interval - 1)):
            window_start, window_end = all_dates_in_interval[date_index], all_dates_in_interval[date_index + 1]
            malware_available = self._get_all_samples_in_time_interval(window_start, window_end, True)
            goodware_available = self._get_all_samples_in_time_interval(window_start, window_end, False)
            malware_sample_size = compute_margin_of_error_sampling(len(malware_available))
            goodware_sample_size = malware_sample_size * int(1 - malware_percentage) * 10
            malware_sample_size = int(malware_sample_size)

            malware_samples = random.sample(malware_available, malware_sample_size)
            goodware_samples = random.sample(goodware_available, min(goodware_sample_size, len(goodware_available)))
            dataset.extend(malware_samples + goodware_samples)

        return dataset

    def _get_all_samples_in_time_interval(self, start_date, end_date, is_malware):
        samples_in_time_interval = []
        if is_malware:
            sample_collection = self.malware_to_timestamp_dict
        else:
            sample_collection = self.goodware_to_timestamp_dict
        for malware, timestamp in sample_collection.items():
            if start_date <= timestamp < end_date:
                samples_in_time_interval.append(malware)
        return samples_in_time_interval
