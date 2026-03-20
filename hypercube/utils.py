from android_malware_detectors import detectors


def get_model_class(model_name):
    if model_name.lower() == "deepdrebin":
        return detectors.DeepDrebin
    elif model_name.lower() == "drebinsvm":
        return detectors.DrebinSVM
    elif model_name.lower() == "ramda":
        return detectors.RAMDADetector
    elif model_name.lower() == "hcc":
        return detectors.HCCDrebinDetector
    elif model_name.lower() == "malscan":
        return detectors.MalScanRF
    else:
        raise NotImplementedError(f"Model {model_name} not implemented")
