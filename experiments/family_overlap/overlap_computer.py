import statistics
from collections import defaultdict

import tqdm

from android_malware_detectors.datasets_utils.androzoo_utils import load_androzoo_info_by_keys
from android_malware_detectors.datasets_utils.dates import get_year
from android_malware_detectors.utils.io_operations import load_json


def compute_all_overlaps(meta_files, families_db_file, is_azoo, date_type):
    families_db = load_json(families_db_file)
    aggregated_overlaps_by_year = defaultdict(list)
    aggregated_sample_size_by_year = defaultdict(int)

    for meta_file in tqdm.tqdm(meta_files):
        dataset_by_year = divide_dataset_by_year(meta_file, is_azoo, date_type)
        overlapping_by_year, sample_size_by_year = compute_overlap(
            dataset_by_year, min(dataset_by_year.keys()), families_db
        )
        for year, overlap in overlapping_by_year.items():
            aggregated_overlaps_by_year[year].append(overlap)
        for year, sample_size in sample_size_by_year.items():
            aggregated_sample_size_by_year[year] += sample_size

    average_overlaps_by_year = {
        year: statistics.mean(aggregated_overlap) for year, aggregated_overlap in aggregated_overlaps_by_year.items()
    }

    if len(meta_files) > 1:
        std = {
            year: statistics.stdev(aggregated_overlap) for year, aggregated_overlap in aggregated_overlaps_by_year.items()
        }
    else:
        std = {
            year: 0 for year, aggregated_overlap in aggregated_overlaps_by_year.items()
        }
    average_sample_size_by_year = {year: aggregated_sample_size / len(meta_files)
                                   for year, aggregated_sample_size in aggregated_sample_size_by_year.items()}
    print("mean", average_overlaps_by_year)
    print("std", std)
    print("average sample size by year", average_sample_size_by_year)

    return average_overlaps_by_year, std


def divide_dataset_by_year(meta_file, is_azoo, date_type):
    if isinstance(meta_file, str):
        if is_azoo:
            meta_file = load_androzoo_info_by_keys(meta_file, keys=["dex_date"])
        else:
            meta_file = load_json(meta_file)
            if isinstance(meta_file, list):
                meta_file = {entry["sha256"].lower(): entry for entry in meta_file}

    dataset_by_year = defaultdict(list)
    for sha, entry in meta_file.items():
        year = get_year(entry[date_type])
        dataset_by_year[year].append(sha.lower())
    return dataset_by_year


def compute_overlap(dataset_by_year, training_year, families_db):
    overlapping_by_year = {}
    sample_size_by_year = {training_year: len(dataset_by_year[training_year])}
    training_families = get_families_at_training_time(dataset_by_year[training_year], families_db)
    for year, sha_list in dataset_by_year.items():
        if year > training_year:
            known_at_training_count, unknown_at_training_count, not_found = compare_against_training_set(
                training_families, sha_list, families_db
            )
            total = known_at_training_count + unknown_at_training_count + not_found
            if total == 0:
                raise ZeroDivisionError("ZERO FOUND in:", training_year, year)
            overlapping_by_year[year] = known_at_training_count / total
            sample_size_by_year[year] = total
    return overlapping_by_year, sample_size_by_year


def compare_against_training_set(training_families, test_samples, families_db):
    known_at_training_count = 0
    unknown_at_training_count = 0

    not_found = 0
    families_this_year = set()
    for sample_hash in test_samples:
        family = families_db.get(sample_hash)
        families_this_year.add(family)
        if family:
            if family.lower() in training_families:
                known_at_training_count += 1
            else:
                unknown_at_training_count += 1
        else:
            not_found += 1

    print(f"not found {not_found} / {len(test_samples)}")
    return known_at_training_count, unknown_at_training_count, not_found


def get_families_at_training_time(samples_hash_list, families_db):
    family_distribution = set()
    not_found = 0
    for sample_hash in samples_hash_list:
        family = families_db.get(sample_hash)
        if family:
            family_distribution.add(family.lower())
        else:
            not_found += 1

    if not_found:
        print(f"not found {not_found} / {len(samples_hash_list)}")

    return family_distribution


"""
transcend original sample size {2014: 5697, 2015: 3065, 2016: 3973, 2017: 7200, 2018: 6452}
apigraph original sample size  {2014: 4754, 2015: 5688, 2016: 5282, 2017: 2322, 2018: 3322})

original transcendent {2015: 0.9161500815660685, 2016: 0.7379813742763655, 2017: 0.6156944444444444, 2018: 0.44466831990080596}
original apigraph {2015: 0.8078410689170182, 2016: 0.6399091253313139, 2017: 0.665374677002584, 2018: 0.8795906080674293}

vtt4_transcend = {2015: 0.91, 2016: 0.81, 2017: 0.78, 2018: 0.83}
sample_size = {2014: 5597.0, 2015: 5732.0, 2016: 5317.0, 2017: 2337.0, 2018: 3336.0}
{2014: 5597.0, 2015: 5732.0, 2016: 5317.0, 2017: 2337.0, 2018: 3336.0}
apigraph_vtt_4
{2015: 0.91, 2016: 0.81, 2017: 0.78, 2018: 0.83}

vtt15_transcend_sample_size = {2015: 0.85, 2016: 0.74, 2017: 0.71, 2018: 0.81}
sample_size = {2014: 5697.0, 2015: 3065.0, 2016: 3973.0, 2017: 7135.0, 2018: 6313.0}

vtt4_at_2019
{2015: 0.8945513866231648, 2016: 0.8231059652655425, 2017: 0.7694444444444445, 2018: 0.8203657780533169}

vtt4_emulated
{2015: 0.9049265905383361, 2016: 0.8289453813239366, 2017: 0.7180833333333333, 2018: 0.7916305021698699}

vtt4_transcend
{2015: 0.89, 2016: 0.82, 2017: 0.78, 2018: 0.81}
{2014: 5697.0, 2015: 3065.0, 2016: 3973.0, 2017: 7200.0, 2018: 6452.0}

vtt15_at_2019
{2015: 0.838694942903752, 2016: 0.6919204631261012, 2017: 0.6613363028953229, 2018: 0.8189693801344287}

vtt4 emulated 2
{2015: 0.9123654159869494, 2016: 0.8365466901585703, 2017: 0.6308611111111111, 2018: 0.7139181649101054}

vtt4 emulated 21 5
{2015: 0.9119086460032626, 2016: 0.8061414548200352, 2017: 0.4793611111111112, 2018: 0.534252944823AGGREGATION3105}

vtt15 emulated
{2015: 0.8756280587275693, 2016: 0.7642587465391391, 2017: 0.4888433515482696, 2018: 0.3061814289537062}


transcendent scaled up 2
{2015: 0.9232300163132138, 2016: 0.8350113264535615, 2017: 0.7133055555555556, 2018: 0.7190488194269389}

transcendent scaled up 3
{2015: 0.9283088635127786, 2016: 0.8628072824901418, 2017: 0.753638888888889, 2018: 0.7998381596439512}

transcendent scaled up 5
{2015: 0.9372398042414357, 2016: 0.8755398942864335, 2017: 0.801444909344491, 2018: 0.8259666628869485}

transcendent tesseract good - intriguing bad
{2015: 0.9006851549755301, 2016: 0.8099672791341556, 2017: 0.533, 2018: 0.5806091967166739}


{2015: 0.9040783034257749, 2016: 0.7477976340297005, 2017: 0.5873611111111111, 2018: 0.47194388777555113}



2020-2023 vtt4
{2021: 0.915, 2022: 0.8854166666666666, 2023: 0.7580838323353294}
2020-2023 vtt15
{2021: 0.7098765432098766, 2022: 0.8247011952191234, 2023: 0.43283582089552236}

all androzoo  4-15
{2015: 115828,
             1980: 54515,
             2018: 88498,
             2017: 93883,
             2014: 194178,
             2020: 37810,
             2019: 80778,
             2012: 74385,
             2016: 152339,
             2013: 115824,
             2011: 22621,
             2022: 7538,
             2021: 30555,
             2008: 5758,
             1981: 7225,
             2092: 129,
             2010: 3120,
             1985: 36,
             2023: 2071,
             2005: 1,
             2009: 103,
             2107: 104,
             2002: 37,
             2024: 153,
             2007: 14,
             2006: 16,
             2004: 8,
             2081: 1,
             2044: 3,
             2034: 1,
             2039: 2,
             2078: 2,
             2037: 1,
             2046: 2,
             2032: 4,
             2090: 1,
             2003: 3,
             2076: 2,
             2027: 1,
             2045: 4,
             2056: 2,
             2028: 1,
             2000: 1}
             
{2011: 38388,
             1980: 28600,
             2012: 144860,
             2014: 101133,
             2017: 10712,
             2016: 35275,
             2013: 57174,
             2015: 60633,
             2018: 11844,
             2019: 8937,
             2008: 7264,
             2020: 5853,
             2010: 1414,
             1981: 725,
             2021: 1866,
             2022: 67,
             2009: 76,
             2006: 18,
             1999: 1,
             2107: 22,
             2092: 32,
             2023: 7,
             2005: 5,
             2000: 2,
             2002: 5,
             2028: 1,
             2004: 3,
             2007: 1,
             2003: 1,./.var/app/com.spotify.Client/cache/spotify
             1985: 1}



families vtt4
2014: 233 - 242 - 262 - 251 - 249
2015: 219 - 238 - 234 - 243 - 247
2016: 251 - 273 - 277 - 291 - 279
2017: 198 - 223 - 218 - 213 - 232
2018: 176 - 176 - 199 - 192 - 174

2014 {'adflex', 'adinject', 'adleak', 'adlibrary', 'admediav', 'admogo', 'adpush', 'adrd', 'adrotoob', 'adswo', 'adwo', 'airpush', 'andup', 'anserver', 'anydown', 'apkq', 'apperhand', 'appflood', 'appin', 'appinventor', 'appoffer', 'appquanta', 'appsgeyeser', 'appsgeyser', 'apptrack', 'artemis', 'asmalwad', 'autoins', 'axnr', 'basebridge', 'bgserv', 'bips', 'boogr', 'boqx', 'boxer', 'cauly', 'chuli', 'cimsci', 'clevernet', 'cnzz', 'cogl', 'commplat', 'congur', 'cooee', 'ctinzw', 'ctxnjb', 'cudkzt', 'cussul', 'cxqisx', 'cxsxzo', 'cybihq', 'cyerjz', 'cyfin', 'cynctn', 'daolnw', 'daomcd', 'darop', 'dcsuid', 'ddlight', 'deng', 'desktoppush', 'deviceadmin', 'dgrynq', 'dgtikl', 'dianjin', 'dianle', 'dkzrmj', 'dkzttz', 'dkzuxf', 'dkzuxh', 'dnotua', 'dogwin', 'domob', 'dordrae', 'douwan', 'dowgin', 'droidcoupon', 'droidkungfu', 'droidrooter', 'drosel', 'dtznya', 'dxspgs', 'eaxa', 'eldorado', 'elfan', 'erop', 'fakeapp', 'fakeav', 'fakebank', 'fakeinst', 'fakeinstsms', 'fatakr', 'feebs', 'feiad', 'feiwo', 'fengvi', 'fjcon', 'floatgame', 'folu', 'foncy', 'frupi', 'gabas', 'galf', 'ganlet', 'geinimi', 'genbl', 'generisk', 'genpua', 'gepew', 'gexin', 'gingermaster', 'ginmaster', 'glooken', 'gmuse', 'golddream', 'gpqe', 'gudex', 'gumen', 'gxyvt', 'gyzz', 'hamad', 'hamob', 'hata', 'htmjs', 'ibcq', 'iconosys', 'igexin', 'ironsrc', 'ixegin', 'jfpush', 'jiagu', 'jiead', 'joynow', 'jsmshider', 'jumiad', 'kimia', 'kingroot', 'kirko', 'kmin', 'koler', 'koomer', 'kuguo', 'kungfu', 'kyview', 'kyvu', 'leadbolt', 'leapp', 'legana', 'llri', 'lockscreen', 'lotoor', 'maistealer', 'maltiverza', 'mbloc', 'mecor', 'minimob', 'mmarket', 'mobclick', 'mobeleader', 'mobextra', 'mobwin', 'monca', 'moplus', 'mulad', 'multiverze', 'nandrobox', 'nineap', 'ocikq', 'oneclickfraud', 'opfake', 'ormmaad', 'pandaad', 'panev', 'pircob', 'pjapps', 'plankton', 'pletor', 'podec', 'presenoker', 'qysly', 'ramnit', 'repsandbox', 'revmob', 'secapk', 'secneo', 'shedun', 'shixot', 'simpatchy', 'simplocker', 'skplanet', 'skymobi', 'smsagent', 'smsbot', 'smsfeejar', 'smspay', 'smsreg', 'smsspy', 'smsthief', 'smstracker', 'smszombie', 'spuhmes', 'spyagent', 'spyagentad', 'spyhk', 'startapp', 'stopsms', 'sumzand', 'suspici', 'tachi', 'torjok', 'towroot', 'trackphone', 'trogle', 'umeng', 'umpay', 'unld', 'vigua', 'viser', 'wacatac', 'waps', 'wapsx', 'wedo', 'wintertiger', 'wiyun', 'wkload', 'wondertek', 'wpay', 'youku', 'youmi', 'ysapk', 'yzhc', 'zsone', 'zypush'}
2015 {'asmalwad', 'podec', 'femto', 'spyloan', 'kirko', 'gvuc', 'adpush', 'waps', 'minimob', 'pandaad', 'gxamh', 'jiagu', 'dqlyit', 'andup', None, 'baiduprotect', 'skymobi', 'gxamv', 'seldor', 'appquanta', 'moplus', 'smsbot', 'egame', 'generickdz', 'generisk', 'wondertek', 'fivf', 'secneo', 'fengvi', 'feiwo', 'bips', 'fosi', 'libkallsyms', 'inmobi', 'fusob', 'secapk', 'anydown', 'cve', 'jedan', 'aliyuncs', 'dianle', 'spyagent', 'koomer', 'youku', 'kyvu', 'obtes', 'anserver', 'smsthief', 'fhiq', 'gxwcy', 'triada', 'boogr', 'hiddenads', 'secapkpacker', 'taskkiller', 'fakebank', 'goldentouch', 'darop', 'kalfere', 'agentc', 'utchi', 'vigua', 'dowgin', 'inazigram', 'dnotua', 'wintertiger', 'adflex', 'trjdown', 'scamapp', 'pircob', 'mobiad', 'apperhand', 'madad', 'ixegin', 'chatleaker', 'uapush', 'igexin', 'youmi', 'nineap', 'detections', 'cyfin', 'apptrack', 'dinehu', 'gxxno', 'leadbolt', 'gxxiq', 'cauly', 'fictus', 'deng', 'xinyinhe', 'gvuv', 'cussul', 'goqo', 'dilidi', 'domob', 'gxaoj', 'kyview', 'adend', 'admogo', 'gisto', 'plankton', 'frupi', 'ocikq', 'onespy', 'hiddenapps', 'loopb', 'dataeye', 'angupsh', 'droidrooter', 'drosel', 'ppoer', 'eicar', 'stagefright', 'smsspy', 'repsandbox', 'mobtes', 'autoinst', 'smsagent', 'gxwau', 'adswo', 'shedun', 'smspay', 'autoins', 'gdipp', 'adwo', 'folu', 'dxspgs', 'droidkungfu', 'nandrobox', 'commplat', 'gingermaster', 'dzxghk', 'ewind', 'gxajg', 'wpay', 'qysly', 'spymob', 'vnapstore', 'txing', 'glodeagl', 'paccy', 'openconnection', 'cooee', 'dzhtny', 'ginmaster', 'wateh', 'yeahmobi', 'ouwic', 'gxxox', 'huhuad', 'gxysm', 'adlibrary', 'ultima', 'wapsx', 'smsreg', 'jfpush', 'drhaub', 'lockscreen', 'eldorado', 'fiiy', 'wiyun', 'stealthcell', 'hiddenapp', 'iapay', 'revmob', 'dtznya', 'dianjin', 'gxanj', 'agentd', 'genpua', 'gepew', 'dogwin', 'xinhua', 'presenoker', 'folc', 'gxana', 'gxamn', 'dqzrfl', 'gxand', 'lotoor', 'airpush', 'gxyuw', 'torec', 'appsgeyser', 'maltiverza', 'gexin', 'gxagg', 'viser', 'tachi', 'adcolony', 'dzmszd', 'mobwin', 'fakesys', 'gxytu', 'artemis', 'umeng', 'silverpush', 'mobisec', 'fakeapp', 'gxxgy', 'dzwpov', 'kuguo', 'dkzuxh', 'gxanz', 'genbl', 'tifamily', 'gxxce', 'gvuk', 'mogosec', 'cimsci', 'gxafs', 'ads', 'kungfu', 'mgyun', 'startapp', 'highconfidence', 'smsthife', 'dasu', 'gxyts'}
2016 {'asmalwad', 'xingdes', 'bbl', 'adpush', 'waps', 'packaginguntrustworthyjiagu', 'pandaad', 'mmbilling', 'mulad', 'jiagu', 'andup', 'malct', None, 'skymobi', 'baiduprotect', 'gxxup', 'mobilepay', 'appquanta', 'smforw', 'egame', 'ggspo', 'generickdz', 'generisk', 'secneo', 'wondertek', 'ramnit', 'feiwo', 'fosi', 'gxlyr', 'joye', 'blouns', 'sexpay', 'general', 'cwfoot', 'smsregcw', 'gwsna', 'hypay', 'inmobi', 'amaa', 'anydown', 'cve', 'aliyuncs', 'qwgi', 'gxamw', 'dianle', 'spyagent', 'koomer', 'adviator', 'kyvu', 'eeqhcl', 'smsthief', 'yubli', 'triada', 'boogr', 'adfeiwo', 'gxbxa', 'hiddenads', 'axbjg', 'vigua', 'paak', 'dowgin', 'congur', 'ucmore', 'dnotua', 'gxamx', 'goodad', 'adflex', 'snailcut', 'scamapp', 'trjdown', 'sandrorat', 'apperhand', 'spyforw', 'sockbot', 'aevx', 'igexin', 'gxarn', 'inor', 'folv', 'youmi', 'nineap', 'detections', 'apptrack', 'dinehu', 'oimobi', 'leadbolt', 'xcpu', 'dspurj', 'tapcore', 'ysapk', 'fictus', 'softcnapp', 'hqwar', 'deng', 'cata', 'smsregzi', 'svpeng', 'cussul', 'smshider', 'ksapp', 'reflod', 'domob', 'anzhu', 'kyview', 'gidleak', 'levida', 'admediav', 'adend', 'admogo', 'aaaaaaadzt', 'plankton', 'pornvideo', 'frupi', 'hiddenapps', 'morepaks', 'gxwaz', 'ocikq', 'dataeye', 'hiddad', 'spyoo', 'drpxhi', 'offad', 'tencentprotect', 'drosel', 'droidrooter', 'roguesppush', 'repmetagen', 'repsandbox', 'smsspy', 'autoinst', 'edurqu', 'shedunxd', 'adleak', 'vpsdrop', 'smsagent', 'tencent', 'cocopush', 'adswo', 'shedun', 'smspay', 'autoins', 'poogle', 'fakeind', 'gqoa', 'webshell', 'cnzz', 'nanban', 'adwo', 'folu', 'avagent', 'batmobi', 'fhug', 'gingermaster', 'umpay', 'appcare', 'ewind', 'qihoo', 'adshell', 'gxapy', 'qysly', 'glodeagl', 'xgen', 'exploid', 'gxxqa', 'mobby', 'gqhe', 'openconnection', 'styricka', 'cooee', 'judy', 'ffsa', 'revo', 'floatgame', 'dzhtny', 'ginmaster', 'ijiami', 'axent', 'adlibrary', 'becou', 'slocker', 'wapsx', 'smsreg', 'axba', 'fran', 'gxwek', 'lirose', 'xavier', 'gxxul', 'eldorado', 'wiyun', 'fakapp', 'mobclick', 'viking', 'hiddenapp', 'revmob', 'vnetone', 'dianjin', 'rmle', 'genpua', 'folc', 'presenoker', 'xinhua', 'sprovider', 'sysservice', 'addropper', 'dqzrfl', 'generica', 'malctpvu', 'ztorg', 'airpush', 'lotoor', 'pyor', 'gxxuk', 'usafe', 'appsgeyser', 'datacollector', 'kapuser', 'gexin', 'showvideo', 'viser', 'tachi', 'dsploit', 'gxaou', 'artemis', 'boxer', 'mobisec', 'fakeapp', 'kingroot', 'kuguo', 'dkzuxh', 'genbl', 'spysms', 'remotecode', 'silentinstaller', 'rooter', 'jnuk', 'cimsci', 'senrec', 'netbox', 'ogel', 'startapp', 'gxarc', 'fakeinst', 'gqoc', 'drolock', 'highconfidence', 'subox', 'dasu', 'yiwan', 'onexuan', 'hiddenap'}
2017 {'asmalwad', 'cootek', 'xingdes', 'spyloan', 'packaginguntrustworthyjiagu', 'waps', 'piom', 'jiagu', 'vuad', 'nimda', 'vmvol', 'hdmonitor', None, 'baiduprotect', 'skymobi', 'mobilepay', 'smforw', 'coinminer', 'smscom', 'egame', 'wondertek', 'generisk', 'secneo', 'generickdz', 'ramnit', 'ypkt', 'feiwo', 'virut', 'blouns', 'aceheur', 'ffxu', 'general', 'hypay', 'inmobi', 'amaa', 'secapk', 'anydown', 'aliyuncs', 'fgab', 'cve', 'spyagent', 'andut', 'youku', 'kyvu', 'fovt', 'uwasson', 'eidnad', 'fhiq', 'toofan', 'fakeapk', 'djoy', 'boogr', 'hiddenads', 'batmob', 'yuchanglou', 'neucore', 'congur', 'inazigram', 'dowgin', 'rootgle', 'dnotua', 'intesad', 'fanu', 'adflex', 'aevx', 'gbqei', 'apperhand', 'yvcy', 'estanm', 'igexin', 'youmi', 'autopay', 'apptrack', 'cyfin', 'dinehu', 'appad', 'leadbolt', 'jiubang', 'tapcore', 'fanj', 'nagaprotect', 'simpo', 'hifrm', 'reflod', 'kyview', 'admediav', 'admogo', 'marsdaemon', 'buzztouch', 'plankton', 'pornvideo', 'frupi', 'ocikq', 'trojandrop', 'hiddad', 'dataeye', 'blacklister', 'gcekhp', 'tencentprotect', 'mlasdl', 'droidrooter', 'drosel', 'multios', 'repmetagen', 'smsspy', 'autoinst', 'vpsdrop', 'fdxmo', 'xiny', 'rexp', 'shedun', 'smspay', 'autoins', 'ggsuy', 'adwo', 'nanban', 'ewind', 'gomunc', 'androeed', 'qihoo', 'susgen', 'notifyer', 'dcer', 'glodeagl', 'oivim', 'esjfmq', 'mobby', 'styricka', 'judy', 'cooee', 'fgey', 'ginmaster', 'callpay', 'adlibrary', 'gxzcyt', 'smsreg', 'xavier', 'amac', 'lockscreen', 'eldorado', 'fakapp', 'hiddenapp', 'swfexp', 'revmob', 'dianjin', 'rmle', 'genpua', 'sprovider', 'presenoker', 'xinhua', 'ggepo', 'ztorg', 'airpush', 'cynos', 'opda', 'rogueurl', 'soltern', 'maltiverza', 'datacollector', 'gexin', 'yiyuantao', 'packedtencent', 'viser', 'adir', 'tachi', 'facestealer', 'mobwin', 'artemis', 'ransomkd', 'ginamster', 'gatf', 'fakeapp', 'kingroot', 'rlgk', 'fheb', 'salmonads', 'dkzuxh', 'kuguo', 'refresh', 'silentinstaller', 'mazarbot', 'oaux', 'cimsci', 'ujxrw', 'hiddendown', 'joinad', 'patacore', 'rootnik', 'multipacked', 'oveead', 'startapp', 'remco', 'fakeinst', 'subox', 'vypk', 'highconfidence', 'robtes', 'uunwn'}
2018 {'asmalwad', 'cootek', 'scrinject', 'secureteen', 'fizime', 'adpush', 'packaginguntrustworthyjiagu', 'piom', 'lezok', 'pandaad', 'waps', 'ieaj', 'mankess', 'jiagu', 'finspy', None, 'skymobi', 'baiduprotect', 'mobilepay', 'smforw', 'coinminer', 'fakewallet', 'moplus', 'egame', 'generickdz', 'generisk', 'secneo', 'wondertek', 'ramnit', 'fyben', 'fopx', 'virut', 'feiwo', 'aceheur', 'apofer', 'general', 'chuli', 'wekf', 'hypay', 'gwsko', 'inmobi', 'amaa', 'apkprotector', 'anydown', 'hiddapp', 'kyvu', 'uuzg', 'uwasson', 'bankbot', 'boogr', 'hiddenads', 'resharer', 'kalfere', 'asoj', 'inazigram', 'browserad', 'dnotua', 'gameguardian', 'loicdos', 'aevx', 'scamapp', 'apperhand', 'yuanpay', 'fifo', 'myfolder', 'pengu', 'detections', 'apptrack', 'gamecheater', 'spynote', 'leadbolt', 'foto', 'tapcore', 'ghoe', 'beita', 'hqwar', 'hifrm', 'gdirq', 'kyview', 'gditv', 'marsdaemon', 'pornvideo', 'plankton', 'ocikq', 'admob', 'trojandrop', 'dataeye', 'blacklister', 'beitaad', 'tencentprotect', 'droidrooter', 'smsspy', 'autoinst', 'vpsdrop', 'smsagent', 'gfqio', 'shedun', 'adswo', 'smspay', 'autoins', 'swfdec', 'azmo', 'ffoa', 'necro', 'jnip', 'ewind', 'johnnie', 'egamepay', 'qihoo', 'carbonsteal', 'notifyer', 'qysly', 'xgen', 'fhuqkp', 'oivim', 'untrustedcert', 'fnie', 'fakedep', 'styricka', 'qrhu', 'fopz', 'cloxer', 'ginmaster', 'fihm', 'pbuu', 'ulyya', 'adlibrary', 'mdnsoft', 'wapsx', 'smsreg', 'scythescf', 'qlist', 'paaf', 'igthb', 'stealthcell', 'wiyun', 'eldorado', 'revmob', 'dianjin', 'genpua', 'presenoker', 'pinap', 'smskey', 'fakengry', 'fendol', 'cynos', 'airpush', 'vktihs', 'cryxos', 'strarpay', 'soltern', 'maltiverza', 'datacollector', 'ghigs', 'gexin', 'packedtencent', 'utencad', 'tachi', 'artemis', 'ginamster', 'fakeapp', 'metasploit', 'dkzuxh', 'kuguo', 'silentinstaller', 'showpak', 'cimsci', 'patacore', 'coinstealer', 'remco', 'iucm', 'highconfidence', 'irsmonitor', 'sexpay', 'fimv', 'robtes'}


families vtt15

2014: 241 - 243 - 253 - 227 - 244
2015: 268 - 266 - 265 - 279 - 276
2016: 304 - 307 - 308 - 327 - 314
2017: 321 - 317 - 311 - 314 - 323
2018: 250 - 244 - 255 - 247 - 240

2014: {'adend', 'adflex', 'adinject', 'adlibrary', 'admichao', 'admogo', 'adpush', 'adrd', 'adswo', 'adwo', 'airpush', 'alycunis', 'andup', 'anserver', 'anzhi', 'apofer', 'appad', 'appoffer', 'appquanta', 'aptoide', 'artemis', 'asmalwad', 'asroot', 'aulrin', 'avxc', 'balafeel', 'bankstl', 'basebridge', 'battpatch', 'bips', 'bodkel', 'boogr', 'boqx', 'boxer', 'buzztouch', 'cajino', 'callflakes', 'cimsci', 'clevernet', 'climap', 'cnzz', 'commplat', 'congur', 'cooee', 'cudkzt', 'cve', 'cybihq', 'cyfin', 'cynos', 'dabom', 'darop', 'deng', 'detections', 'dgyvuj', 'dianjin', 'dianle', 'dianru', 'dkztzo', 'dkzuxf', 'dnotua', 'dogwin', 'domob', 'dordrae', 'dowgin', 'droidkungfu', 'droidrooter', 'drokole', 'drosel', 'dsploit', 'egyjik', 'eldorado', 'elfan', 'erop', 'exploid', 'fakeapp', 'fakeav', 'fakebank', 'fakeinst', 'fatakr', 'feejar', 'feiad', 'feiwo', 'fengvi', 'fiiy', 'folu', 'frupi', 'ganlet', 'gasms', 'geinimi', 'gena', 'generisk', 'genpua', 'gepat', 'gepew', 'gexin', 'gidix', 'gingermaster', 'gleu', 'glodream', 'glooken', 'gmobi', 'golddream', 'gomunc', 'goyear', 'gpqo', 'gpuu', 'gqoc', 'grag', 'gumen', 'gvuo', 'gxabc', 'gxagv', 'gxahg', 'gxaiu', 'gxamn', 'gxaxb', 'gxxum', 'gxxuo', 'hamad', 'hiddenads', 'highconfidence', 'hyspu', 'igexin', 'ihouse', 'jfpush', 'jiagu', 'joye', 'jsmshider', 'jufu', 'jumiad', 'kasandra', 'kingroot', 'kmin', 'koomer', 'kuguo', 'kungfu', 'kyview', 'kyvu', 'ldpinch', 'leadbolt', 'leapp', 'libkallsyms', 'lockscreen', 'lotoor', 'lozfoon', 'malapp', 'maltiverza', 'marte', 'mecor', 'minimob', 'misosms', 'mobclick', 'mobeleader', 'mobinauten', 'mobtes', 'mofin', 'moplus', 'mseg', 'mulad', 'najin', 'nandrobox', 'nickispy', 'nineap', 'obtes', 'oneclickfraud', 'opfake', 'pandaad', 'perkele', 'piom', 'pircob', 'pjapps', 'plangton', 'plankton', 'pletor', 'podec', 'presenoker', 'qumi', 'qysly', 'raden', 'ramnit', 'reflod', 'revmob', 'rgsess', 'robtes', 'rooter', 'rootnik', 'saho', 'secapk', 'shedun', 'shixot', 'simpatchy', 'simplocker', 'skymobi', 'smforw', 'smpho', 'smsagent', 'smsblocker', 'smsbot', 'smsforward', 'smshider', 'smskey', 'smspay', 'smsreg', 'smsreplicator', 'smsspy', 'sprovider', 'spuhmes', 'spyagent', 'spymob', 'stopsms', 'suad', 'svpeng', 'tebak', 'telman', 'tocrenu', 'torec', 'torjok', 'trackop', 'ulpm', 'umpay', 'utchi', 'uten', 'viser', 'waps', 'wapsx', 'wateh', 'webapp', 'wedo', 'wintertiger', 'wkload', 'wondertek', 'wonka', 'wronginf', 'wssender', 'xiny', 'xinyinhe', 'yichuad', 'youmi', 'yuyou', 'yzhc', 'zhui'}
2015: {'admogo', 'appquanta', 'fakeapp', 'roop', 'plangton', 'gxamm', 'rootnik', 'tawatcher', 'darop', 'gvul', 'gxame', None, 'cimsci', 'gxyuj', 'gxxli', 'zhui', 'mobtes', 'mobisec', 'gvuk', 'ogel', 'gbqby', 'fakedown', 'torec', 'adwo', 'gxyul', 'gmobi', 'gxams', 'masnu', 'hiddenapp', 'bgserv', 'qysly', 'xinyinhe', 'gepew', 'smforw', 'usist', 'gxxok', 'cheica', 'ebcrrk', 'dadmo', 'ocikq', 'dowgin', 'yeahmobi', 'gxamv', 'clevernet', 'gone60', 'gxang', 'droidkungfu', 'wintertiger', 'boqx', 'adwe', 'goji', 'gepat', 'eldorado', 'smskey', 'gxxoj', 'feiwo', 'kingroot', 'gxysm', 'vnapstore', 'cynos', 'fakebank', 'gxana', 'plankton', 'cbta', 'ekfrpa', 'gxxoa', 'dordrae', 'admediav', 'gxaov', 'mobwin', 'gorpo', 'gxxox', 'soobek', 'fakeinst', 'basebridge', 'spyoo', 'lockdroid', 'fusob', 'ramnit', 'asmalwad', 'wapsx', 'kyvu', 'gxwyh', 'gvvy', 'adflex', 'symkob', 'folu', 'pandaad', 'gxxhy', 'jsmshider', 'gxxse', 'gxwys', 'angq', 'xinhua', 'shedun', 'fryp', 'igexin', 'detections', 'mgyun', 'leadbolt', 'cyfin', 'gxani', 'airpush', 'scamapp', 'fituw', 'revmob', 'vpsdrop', 'appsgeyser', 'cve', 'anserver', 'mindms', 'gxafo', 'ginmaster', 'kalfere', 'general', 'gxagf', 'gvum', 'apptrack', 'wateh', 'bips', 'smsreg', 'adznvwopzcu', 'gxafv', 'simpatchy', 'gxytz', 'ibcj', 'obtes', 'smsspy', 'gxxot', 'fictus', 'droidrooter', 'mobinauten', 'smspay', 'remotecode', 'etooe', 'dasu', 'gxxom', 'commplat', 'gxafs', 'gxytt', 'aupitou', 'artemis', 'revo', 'gxamp', 'gxwyu', 'gxytu', 'viser', 'moplus', 'gxwcy', 'kazy', 'minimob', 'autoins', 'podec', 'adlibrary', 'gvqu', 'jiagu', 'gappusin', 'deng', 'gvue', 'koomer', 'glodeagl', 'adend', 'congur', 'opfake', 'gxxop', 'ffol', 'jedan', 'gxwwe', 'gxytq', 'gxahx', 'joynow', 'gxwbo', 'lotoor', 'hamob', 'secapkpacker', 'gvuu', 'triada', 'adviator', 'generickdz', 'smsbot', 'razy', 'kyview', 'geinimi', 'secneo', 'zitmo', 'highconfidence', 'gexwb', 'fogod', 'seldor', 'natpa', 'ewind', 'trjdropper', 'bauts', 'costil', 'presenoker', 'smsagent', 'gxamh', 'generisk', 'fosi', 'genericrxuk', 'gvus', 'secapk', 'dnotua', 'youku', 'shupup', 'kungfu', 'gqau', 'paccy', 'boomp', 'gingermaster', 'gxxui', 'andup', 'mobiad', 'anydown', 'gudex', 'gvup', 'badpac', 'kirko', 'youmi', 'dsploit', 'enoket', 'waps', 'egame', 'smaps', 'genpua', 'gron', 'floodad', 'fakenotify', 'rooter', 'gxxob', 'gxamg', 'levida', 'wiyun', 'gxagi', 'styricka', 'umpay', 'ztorg', 'baiduprotect', 'gxxoc', 'gxyor', 'boogr', 'semes', 'skymobi', 'kasandra', 'gxytn', 'jfpush', 'gxyuy', 'gxypr', 'drosel', 'sprovider', 'gxyui', 'adcolony', 'hiddenads', 'trjdown', 'gvud', 'dogwin', 'spyagent', 'walkinwat', 'gxzym', 'gxacd', 'mobclick', 'dilidi', 'kuguo', 'ppoer', 'gxagx', 'damon', 'frupi', 'wondertek'}
2016: {'admogo', 'gugi', 'fhub', 'gxxqy', 'appquanta', 'sriy', 'fakeapp', 'gqod', 'rootnik', 'gxarh', 'nandrobox', 'netbox', 'ggtwa', 'oveead', 'clinator', None, 'cimsci', 'sagnt', 'eeeggz', 'gqle', 'lootor', 'aliyuncs', 'gxarm', 'general', 'gqiw', 'mobtes', 'mobisec', 'smsthief', 'floatgame', 'gxalh', 'adwo', 'adfeiwo', 'hiddenapp', 'qysly', 'frelect', 'oimobi', 'genericrxlj', 'gomunc', 'expkit', 'lezok', 'inmobi', 'axvp', 'mobi', 'mobby', 'gepew', 'smforw', 'silentinstaller', 'gqoc', 'gdhte', 'kapuser', 'ocikq', 'dowgin', 'yeahmobi', 'clevernet', 'silverpush', 'hiddenap', 'shuame', 'droidkungfu', 'eldorado', 'gxard', 'smskey', 'gxysm', 'feiwo', 'cynos', 'vnapstore', 'gxxug', 'subspod', 'gqoy', 'plankton', 'kingroot', 'dinehu', 'snailcut', 'admediav', 'gmaufi', 'gorpo', 'hypay', 'fakeinst', 'cepsbot', 'spyoo', 'xingdes', 'ramnit', 'fiui', 'wapsx', 'asmalwad', 'gxwan', 'kyvu', 'folu', 'adflex', 'gxxse', 'xavier', 'pandaad', 'aevx', 'mogosec', 'gwssn', 'onespy', 'xinhua', 'gibdy', 'shedun', 'dataeye', 'gxapy', 'igexin', 'detections', 'gqhe', 'nativead', 'leadbolt', 'gxxsa', 'ffsa', 'cyfin', 'suaban', 'gxxue', 'avvdj', 'airpush', 'anzhu', 'gxath', 'uapush', 'uten', 'ghhig', 'revmob', 'vpsdrop', 'apkprotector', 'ghhfy', 'piom', 'reflod', 'sandrorat', 'kalfere', 'ginmaster', 'dmbe', 'fhug', 'apptrack', 'adloader', 'bips', 'smsreg', 'hiddad', 'gxatg', 'pdcu', 'kilb', 'tencentprotect', 'hfbao', 'clarda', 'gxxuk', 'morepacks', 'blouns', 'obtes', 'smsspy', 'fictus', 'gxaqy', 'droidrooter', 'fhom', 'smspay', 'asacub', 'dkpush', 'dasu', 'egamefee', 'etooe', 'hxqg', 'apay', 'mulad', 'gexin', 'folc', 'adulty', 'artemis', 'revo', 'testfile', 'sivu', 'viser', 'moplus', 'fhui', 'pornvideo', 'minimob', 'autoins', 'fran', 'yekrand', 'najin', 'adlibrary', 'jiagu', 'koomer', 'adend', 'congur', 'phonespy', 'glodeagl', 'dgqgku', 'batmobi', 'yubli', 'opfake', 'dgsiwf', 'gxxuj', 'svpeng', 'androidlotoor', 'judy', 'milkydoor', 'lotusid', 'cwfoot', 'loodos', 'cbtrwa', 'lotoor', 'secapkpacker', 'gxask', 'mobextra', 'urvqo', 'triada', 'gxalg', 'generickdz', 'gqke', 'adviator', 'razy', 'adiwky', 'kyview', 'repsandbox', 'xolco', 'secneo', 'haynu', 'eicar', 'zitmo', 'gxwek', 'gxapc', 'marte', 'callpay', 'axent', 'gxxqe', 'mobistealth', 'enoket', 'linksmshider', 'presenoker', 'smsagent', 'hmad', 'generisk', 'gxxup', 'gxwep', 'fosi', 'secapk', 'dnotua', 'mobilepay', 'gluper', 'gbqdy', 'gingermaster', 'softcnapp', 'gxxqa', 'roversa', 'nagaprotect', 'boxer', 'gxxuo', 'badpac', 'gidleak', 'youmi', 'hqwar', 'egame', 'waps', 'inor', 'genpua', 'nanban', 'stealthcell', 'dsploit', 'fiiy', 'ninebox', 'avagent', 'groi', 'fakesys', 'gxatl', 'rooter', 'abxd', 'virut', 'grut', 'levida', 'iadpush', 'wiyun', 'pircob', 'gdidr', 'styricka', 'boogr', 'ztorg', 'gxxny', 'baiduprotect', 'gxbxi', 'shixot', 'sypay', 'skymobi', 'kasandra', 'smsstealer', 'drosel', 'sprovider', 'delayload', 'buic', 'hiddenads', 'paat', 'srhu', 'gxwev', 'subox', 'dogwin', 'ewcnuh', 'gxarc', 'spyagent', 'yiwan', 'mobclick', 'gxxne', 'gxzeg', 'autoinst', 'sodsack', 'chuli', 'kuguo', 'ayyg', 'irsmonitor', 'loki', 'frupi', 'wondertek'}
2017: {'reptilicus', 'fakeapp', 'rootnik', 'appad', 'meterpreter', 'hiddenapp', 'favz', 'xinyinhe', 'smforw', 'gdiew', 'dowgin', 'silverpush', 'fakapp', 'sunmobi', 'ciban', 'mobwin', 'contactscollector', 'vmvol', 'xavier', 'pandaad', 'anlost', 'mogosec', 'mobtool', 'shedun', 'agentb', 'fimv', 'walex', 'lovetheater', 'yqobn', 'ghhuc', 'uten', 'fobus', 'piom', 'jjadj', 'hiddad', 'wapron', 'tucys', 'fjyc', 'matrixspy', 'smsspy', 'droidrooter', 'marsdaemon', 'hdmonitor', 'gexin', 'liballsyms', 'autosus', 'viser', 'ransomkd', 'koomer', 'nawiaiad', 'tapcore', 'judy', 'fisw', 'triada', 'generickdz', 'frou', 'sdwaj', 'kyview', 'wrqe', 'secneo', 'zitmo', 'genieo', 'ffxu', 'fanu', 'lockerpin', 'fosi', 'mobilepay', 'estanm', 'spynote', 'sobot', 'fakesys', 'gatf', 'hiddapp', 'fyec', 'faht', 'kasandra', 'anubisspy', 'fgey', 'sprovider', 'frir', 'soltern', 'ginamster', 'robtes', 'gbqeb', 'callad', 'frupi', 'adwoad', 'admogo', 'drolock', 'enlgat', 'aliyuncs', 'fzamhc', 'mobikok', 'silentinstaller', 'ocikq', 'domob', 'shuame', 'smskey', 'eldorado', 'feiwo', 'hypay', 'patacore', 'asmalwad', 'wapsx', 'xiny', 'aevx', 'ubsod', 'ghhpi', 'ffsa', 'jayqa', 'tencentprotect', 'smspay', 'commplat', 'fhiq', 'artemis', 'notifyer', 'revo', 'ekrkll', 'aks', 'autoins', 'adlibrary', 'epatroa', 'eiwiwp', 'firu', 'iatoy', 'gatc', 'smsbot', 'sacti', 'qqspy', 'spampo', 'lmaj', 'aztq', 'ethwuo', 'generisk', 'gewsl', 'dnotua', 'djoy', 'paccy', 'spyagnt', 'joinad', 'youmi', 'egame', 'nanban', 'xafekopy', 'rooter', 'ownspy', 'evsxq', 'wiyun', 'styricka', 'boogr', 'ztorg', 'apofer', 'redirector', 'subox', 'spyagent', 'wondertek', 'joye', 'grammstealer', None, 'wpay', 'adwo', 'dianjin', 'gomunc', 'kyjoy', 'roversa', 'lezok', 'frid', 'elrgkt', 'fiqy', 'clevernet', 'gdizl', 'repmetagen', 'ibay', 'oaux', 'gdiws', 'remco', 'plankton', 'panev', 'qhost', 'fakeinst', 'spyoo', 'ramnit', 'rmle', 'autopay', 'cooee', 'dataeye', 'simpo', 'leadbolt', 'batmob', 'gace', 'cve', 'ginmaster', 'kalfere', 'general', 'iijm', 'apptrack', 'adswo', 'smsreg', 'renamer', 'gdiat', 'amaa', 'ffro', 'mazarbot', 'toofan', 'pornvideo', 'dcer', 'amae', 'gdixu', 'lockscreen', 'glodeagl', 'svpeng', 'lotusid', 'lotoor', 'regon', 'gewtw', 'ewind', 'metasploit', 'presenoker', 'nloader', 'nagaprotect', 'packaginguntrustworthyjiagu', 'fiiy', 'virut', 'fovt', 'tekwon', 'yvcy', 'adpush', 'mobilespy', 'azta', 'stealmoneygame', 'ggepg', 'carbonsteal', 'inazigram', 'smszombie', 'luckypatcher', 'sriy', 'fjov', 'rubank', 'nandrobox', 'zniu', 'nwhit', 'uunwn', 'cimsci', 'cghu', 'spyloan', 'qysly', 'mobby', 'goldeneagle', 'inmobi', 'tachi', 'androidoscad', 'blueguard', 'kingroot', 'cynos', 'ihang', 'gdiel', 'wajar', 'kyvu', 'rogueurl', 'folu', 'adflex', 'nimda', 'coinminer', 'oyoj', 'ffri', 'cyfin', 'airpush', 'rootgle', 'amqms', 'revmob', 'vpsdrop', 'reflod', 'qlist', 'madad', 'ibcj', 'blouns', 'amac', 'trackmyphone', 'etooe', 'oivim', 'moplus', 'ficj', 'runouce', 'cgyh', 'smthief', 'nofuk', 'jiagu', 'congur', 'esjfmq', 'xgen', 'mankess', 'highconfidence', 'strarpay', 'ldpinch', 'buzztouch', 'secapk', 'fadeb', 'anydown', 'stealthcell', 'ggsuu', 'kirko', 'hqwar', 'yuchanglou', 'waps', 'ratker', 'cayr', 'pircob', 'baiduprotect', 'fanj', 'mlasdl', 'adlock', 'skymobi', 'recmads', 'drosel', 'hiddenads', 'bdhl', 'virtualapp', 'trojandrop', 'autoinst', 'grabos', 'smsagent'}
2018: {'ffoa', 'carbonsteal', 'eris', 'dqshell', 'ulklb', 'admogo', 'fendol', 'inazigram', 'drolock', 'appf', 'fifo', 'fakeapp', 'cryxos', 'joye', 'rootnik', 'fjci', 'slugin', 'eyic', 'meterpreter', 'bajaspy', 'fiyt', 'cgho', None, 'gfpru', 'cimsci', 'nuqel', 'amam', 'ghigs', 'bankbot', 'gqiw', 'showpak', 'ogel', 'rkor', 'wpay', 'necro', 'adwo', 'muate', 'ghiis', 'dianjin', 'fakeplayer', 'qysly', 'goldeneagle', 'lezok', 'xinyinhe', 'fapwdr', 'inmobi', 'silentinstaller', 'smforw', 'ghiia', 'kapuser', 'fnoi', 'ocikq', 'axumvm', 'clevernet', 'shuame', 'fjgi', 'repmetagen', 'foto', 'tachi', 'eldorado', 'remco', 'antoru', 'cynos', 'feiwo', 'phantomlance', 'evir', 'ghiao', 'mobwin', 'amba', 'hypay', 'wajar', 'patacore', 'ramnit', 'wapsx', 'kyvu', 'asmalwad', 'autopay', 'xiny', 'adflex', 'nimda', 'aevx', 'anlost', 'pandaad', 'shedun', 'dataeye', 'coinminer', 'igexin', 'fhuw', 'leadbolt', 'cyfin', 'airpush', 'agnsmit', 'fituw', 'frru', 'paah', 'uten', 'sunnet', 'ghiak', 'uuzg', 'revmob', 'vpsdrop', 'apkprotector', 'paaf', 'piom', 'ginmaster', 'sandrorat', 'kalfere', 'qlist', 'lekp', 'apptrack', 'adswo', 'smsreg', 'wapron', 'tiggre', 'hiddad', 'tencentprotect', 'fafe', 'revtcp', 'fokz', 'smsspy', 'fictus', 'droidrooter', 'spymob', 'smspay', 'asacub', 'remotecode', 'commplat', 'gexin', 'amaa', 'oivim', 'artemis', 'notifyer', 'gfqyf', 'andut', 'wcojn', 'eyecar', 'pornvideo', 'fozd', 'autoins', 'dcer', 'adlibrary', 'epatroa', 'jiagu', 'lockscreen', 'congur', 'glodeagl', 'opfake', 'xgen', 'fite', 'ffmvhd', 'wuwua', 'ihde', 'iculh', 'meftadon', 'fizime', 'blacklister', 'mankess', 'pengu', 'generickdz', 'triada', 'illredir', 'sacti', 'kyview', 'xolco', 'fksxad', 'secneo', 'eicar', 'brontok', 'fakedep', 'highconfidence', 'vidar', 'ewind', 'gamclk', 'gqlaf', 'metasploit', 'mobistealth', 'strarpay', 'hosx', 'presenoker', 'ghihb', 'fakengry', 'genericgba', 'generisk', 'iconhider', 'droidsheep', 'gapac', 'dnotua', 'mobilepay', 'appoffer', 'fand', 'xhelper', 'fadeb', 'estanm', 'boxer', 'joinad', 'packaginguntrustworthyjiagu', 'spynote', 'hqwar', 'youmi', 'egame', 'waps', 'sobot', 'raddex', 'soundy', 'gameguardian', 'generik', 'rooter', 'zliit', 'fakewallet', 'simbad', 'virut', 'hiddapp', 'wiyun', 'umpay', 'styricka', 'boogr', 'baiduprotect', 'basepay', 'apofer', 'mlasdl', 'gemqtwpovto', 'resharer', 'utchi', 'adlock', 'skymobi', 'kasandra', 'masspr', 'exkgyj', 'recmads', 'packmal', 'drosel', 'adpush', 'johnnie', 'hiddenads', 'virtualapp', 'soltern', 'trojandrop', 'subox', 'ginamster', 'spyagent', 'gamecheater', 'chuli', 'cgeq', 'btapk', 'robtes', 'ijrw', 'irsmonitor', 'gaming', 'smsagent', 'wondertek'}

"""
