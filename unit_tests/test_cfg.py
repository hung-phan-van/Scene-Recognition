from utils import check_stream_url


link_error = "http://s3.vieon.vn/ott-vod_dev-2020/12/17/tearsofsteel-eacd39b020f3ec9b011ff1056f692f49error/playlist.m3u8"

link_success = "http://s3.vieon.vn/ott-vod_dev-2020/12/17/tearsofsteel-eacd39b020f3ec9b011ff1056f692f49/playlist.m3u8"

##### backup if current link not working #######################
if not check_stream_url(link_success):
    link_success = "http://s3.vieon.vn/ott-vod_dev-2020/12/17/tearsofsteel-eacd39b020f3ec9b011ff1056f692f49/playlist.m3u8"
if not check_stream_url(link_success):
    link_success = 'http://devstreaming-cdn.apple.com/videos/streaming/examples/img_bipbop_adv_example_fmp4/master.m3u8'


idx_to_name_path = "./json_files/idx_to_name.json"

name_to_idx_path = "./json_files/name_to_idx.json"

io_path = "./json_files/IO.json"

content_write_json_sample = {"data": [{"itv": ["0:00:00", "0:00:09.160000"], "s_r": {"list_idx": [186, 306, 187], "list_cof": [0.49, 0.184, 0.059], "list_type": [2, 2, 2]}}, {"itv": ["0:00:09.160000", "0:00:14.600000"], "s_r": {"list_idx": [282, 264, 133], "list_cof": [0.436, 0.207, 0.071], "list_type": [1, 1, 1]}}]}

output_json_path = "./unit_tests/data/test.json"

info_scene = {  50: {'count':10,'list_percent':[0.34, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95, 0.9, 0.8, 0.7]},
                80: {'count':3,'list_percent':[0.34, 0.45, 0.55]},
                60: {'count':8,'list_percent':[0.34, 0.45, 0.55, 0.65, 0.75, 0.85, 0.8, 0.6]},
                70: {'count':12,'list_percent':[0.34, 0.45, 0.55, 0.65, 0.75, 0.85, 0.8, 0.5, 0.6, 0.9, 0.55, 0.7]},
                90: {'count':4,'list_percent':[0.34, 0.45, 0.55, 0.6]},
                95: {'count':6,'list_percent':[0.34, 0.45, 0.55, 0.6, 0.7, 0.8]}
            }

