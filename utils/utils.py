import json
import logging
import m3u8
import cv2
import os
from urllib.request import urlopen


def parse_response(response, logger, str_enc = 'utf-8'):
    decoded_content = response._content.decode(str_enc) 
    try:
        dict_content = json.loads(decoded_content)
    except Exception as e:
        logger.info('Exception when parse response:')
        logger.info(decoded_content)
        return {}
    return dict_content

def read_json(filename):
    with open(filename, 'r') as fp:
        content =  json.load(fp)
    return content

def write_json(filename, content_dict, log=True, indent=True):
    with open(filename, 'w') as fp:
        json.dump(content_dict, fp, indent=indent)

    if log:
        print('Write json file {}'.format(filename))

def make_statistic(info_scene, keep_topk=3):
    if not bool(info_scene) or len(info_scene) < keep_topk:
        return None, None
    ips = info_scene.keys()
    sorted_ips = sorted(ips, key=lambda ip: info_scene[ip]['count'], reverse=True)
    list_idx = []
    list_avg_cof = []
    for idx in range(keep_topk):
        list_idx.append(sorted_ips[idx])
        list_percent = info_scene[sorted_ips[idx]]['list_percent']
        count = info_scene[sorted_ips[idx]]['count']
        list_avg_cof.append(round((sum(list_percent)/count),3))
    max_value = max(list_avg_cof)
    max_index = list_avg_cof.index(max_value)
    if max_index != 0 or info_scene[sorted_ips[0]]['count'] < 6 or max_value <0.5:
        return None, None

    return list_idx, list_avg_cof

def check_stream_url(url):
    cap_check = cv2.VideoCapture(url)
    if cap_check.isOpened():
        return True
    return False
    
def parse_hls_url(hls_url):
    final_uri = None
    if check_stream_url(hls_url):
        final_uri = hls_url
    try:
        playlists = m3u8.load(hls_url).playlists
    except Exception as e:
        print("Exception parse hls_url, link using: {}".format(final_uri))
        return final_uri
    quality = None
    min_quality = 4080
    temp = hls_url.split('/')
    prefix_link = '/'.join(temp[:-1])

    for playlist in playlists:
        res = playlist.stream_info.resolution
        
        current_link = playlist.uri
        if check_stream_url(current_link) and min(res[0], res[1]) < min_quality:
            quality = (res[0], res[1])
            min_quality = min(res[0], res[1]) 
            final_uri = current_link

        current_link = prefix_link + '/' + playlist.uri
        if check_stream_url(current_link) and min(res[0], res[1]) < min_quality:
            quality = (res[0], res[1])
            min_quality = min(res[0], res[1])
            final_uri = current_link
    print("Get link parse hls: {}, min_quality: {}".format(final_uri, quality))
    return final_uri


def check_streamable_url(url):
    cap_check = cv2.VideoCapture(url)
    if not cap_check.isOpened():
        return False
    return True

def get_response_invalid_params(detail):
    payload = {
                'code': 8,
                'error': {
                    'message': 'Invalid parameter',
                    'detail': detail
                }
            }
    return payload

def get_headers_ai_service():
    return {
        'AUTHORIZATION': os.environ.get('AI_SERVICE_TK')
    }

def get_scene_meta(logger, forward_result):
    import requests
    parse_result = json.loads(str(forward_result))
    logger.info(parse_result)
    for item in parse_result:
        if item['type'] == int(os.getenv('PREVIOUS_STAGE')):
            res = requests.get(item['data'])
            if res.status_code == 200:
                return res.json()
            return None
    return None

def merge_output(data):
    new_data = []
    total_merge = 0
    idx = 0
    len_list_data = len(data)
    while(idx < len_list_data):
        start = data[idx]['itv'][0]
        start_idx = idx
        curr_data = None
        while idx < len_list_data - 1 and (data[idx]['itv'][1].split(".")[0] == data[idx+1]['itv'][0].split(".")[0]) and data[idx]['s_r']['list_idx'][0] == data[idx+1]['s_r']['list_idx'][0]:
            end = data[idx+1]['itv'][1]
            idx += 1
            total_merge += 1
        if start_idx != idx:
            curr_data = ({"itv": [start, end],"s_r": data[idx]["s_r"] })
            new_data.append(curr_data)
        else:
            curr_data = ({"itv": [start, data[idx]['itv'][1]],"s_r": data[idx]["s_r"] })
            new_data.append(curr_data)
        idx += 1
    print("Total merge output:", total_merge)
    return new_data
