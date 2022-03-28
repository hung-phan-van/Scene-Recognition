import pytest
from utils import *
from unit_tests import test_cfg
import os 
import logging as logger

logger.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logger.DEBUG)

class TestUtils:
    def test_check_streamable_url(self, link=test_cfg.link_error):
        is_streamable = check_streamable_url(link)
        assert not is_streamable

    def test_read_json(self):
        idx_to_name_json = read_json(test_cfg.idx_to_name_path)
        name_to_idx_json = read_json(test_cfg.name_to_idx_path)
        io_json = read_json(test_cfg.io_path)
        assert len(name_to_idx_json) == len(idx_to_name_json) == len(io_json) == 365

    def test_write_json(self):
        path = test_cfg.output_json_path
        if os.path.exists(path):
            os.system("rm -rf {}".format(path))
        content = test_cfg.content_write_json_sample
        write_json(path, content)
        assert os.path.exists(path)


    def test_parse_hls_url(self):
        final_uri = parse_hls_url(test_cfg.link_error)
        assert final_uri == None

        final_uri = parse_hls_url(test_cfg.link_success)
        assert final_uri != None
        assert check_streamable_url(final_uri)

    
    def test_res_invalid_params(self):
        message = 'abc'
        payload = get_response_invalid_params(message)
        assert payload['code'] == 8
        assert  payload['error']['detail'] == message
        assert  payload['error']['message'] == 'Invalid parameter'

    def test_parse_response(self):
        class Response:
            def __init__(self, content):
                self._content = content

        content = b"{\"code\": \"0\", \"message\": \"abc\"}"
        response = Response(content)
        dict_data = parse_response(response, logger)
        assert dict_data['code'] == '0'
        assert dict_data['message'] == 'abc'
        content = b"{'code':}"
        response = Response(content)
        dict_data = parse_response(response, logger)
        assert len(dict_data.keys()) == 0

