train_goodware_gp, train_goodware_aa, train_malware_gp, train_malware_aa = ("train_goodware_gp", "train_goodware_aa",
                                                                            "train_malware_gp", "train_malware_aa")

test_goodware_gp, test_goodware_aa, test_malware_gp, test_malware_aa = ("test_goodware_gp", "test_goodware_aa",
                                                                        "test_malware_gp", "test_malware_aa")

DATASET_CONFIGURATION = {
    "gp": {
        train_goodware_gp: 10000,
        train_goodware_aa: 0,
        train_malware_gp: 10000,
        train_malware_aa: 0,

        test_goodware_gp: 4500,
        test_goodware_aa: 0,
        test_malware_gp: 500,
        test_malware_aa: 0,
    },
    "aa": {
        train_goodware_gp: 0,
        train_goodware_aa: 10000,
        train_malware_gp: 0,
        train_malware_aa: 10000,

        test_goodware_gp: 0,
        test_goodware_aa: 4500,
        test_malware_gp: 0,
        test_malware_aa: 500,
    },
    "even": {
        train_goodware_gp: 5000,
        train_goodware_aa: 5000,
        train_malware_gp: 5000,
        train_malware_aa: 5000,

        test_goodware_gp: 2250,
        test_goodware_aa: 2250,
        test_malware_gp: 250,
        test_malware_aa: 250
    },
    "prop": {
        train_goodware_gp: 8000,
        train_goodware_aa: 2000,
        train_malware_gp: 8000,
        train_malware_aa: 2000,

        test_goodware_gp: 3600,
        test_goodware_aa: 900,
        test_malware_gp: 400,
        test_malware_aa: 100,
    },
    "gpaa": {
        train_goodware_gp: 10000,
        train_goodware_aa: 0,
        train_malware_gp: 0,
        train_malware_aa: 10000,

        test_goodware_gp: 4500,
        test_goodware_aa: 0,
        test_malware_gp: 0,
        test_malware_aa: 500
    },
    "aagp": {
        train_goodware_gp: 0,
        train_goodware_aa: 10000,
        train_malware_gp: 10000,
        train_malware_aa: 0,

        test_goodware_gp: 0,
        test_goodware_aa: 4500,
        test_malware_gp: 500,
        test_malware_aa: 0
    }
}


def get_amounts_to_sample(dataset_configuration):
    configuration = DATASET_CONFIGURATION[dataset_configuration]
    return (configuration[train_goodware_gp], configuration[train_goodware_aa], configuration[train_malware_gp],
            configuration[train_malware_aa], configuration[test_goodware_gp], configuration[test_goodware_aa],
            configuration[test_malware_gp], configuration[test_malware_aa])
