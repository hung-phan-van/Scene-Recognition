import os
import requests
import json
from utils import parse_response

class JobReporter:
    def __init__(self, base_url, endpoint, job_id, logger):
        self.base_url = base_url
        self.endpoint = endpoint
        self.logger = logger
        self.main_url = '{}/{}/{}'.format(base_url, endpoint, job_id)
        self.job_id = job_id
        self.logger.info("Start report job: {}/{}".format(self.main_url, self.job_id))
        self.factor = 100
        self.progress = 0
        self.max_progress = 100
        self.success_code = 200
        self.headers = {
            'Authorization': os.environ['PILELINE_TOKEN']
        }
        self.status = {
            'IN_PROGRESS': 1,
            'SUCCESS': 2,
            'FAIL': 3
        }
    
    def report_progress(self, amount):
        # amount is float in 0 -> 1
        int_amount = int(amount * self.factor)
        self.progress = int_amount
        payload = {
            "status": self.status['IN_PROGRESS'],
            "process": int_amount
        }
        res_report = requests.put(self.main_url, json=payload, headers=self.headers)
        try:
            assert res_report.status_code == self.success_code
        except Exception as e:
            self.logger.info("Report job progress fail, job_id: {}, ex: {}".format(self.job_id, 
                                parse_response(res_report, self.logger)))
            return False
        return True


    def done_job(self, result):
        
        self.progress = self.max_progress

        payload = {
            'status': self.status['SUCCESS'],
            'process': self.progress,
            'result': result
        }
        res_report = requests.put(self.main_url, json=payload, headers=self.headers)
        try:
            assert res_report.status_code == self.success_code
        except Exception as e:
            self.logger.info("Fail in finishing job_id {}, ex: {}, result: {}".format(self.job_id, 
                                parse_response(res_report, self.logger), 
                                result))
            return False, res_report

        # task_pl_job_id_next = os.environ.get('TASK_PIPELINE_JOB_ID_NEXT', None)
        next_job_id = os.environ.get('TASK_PIPELINE_JOB_ID_NEXT', None)
        if next_job_id:
            parse_result = json.loads(str(os.getenv('FORWARD_RESULT')))
            parse_result.append(result)
            next_job_url = '{}/{}/{}'.format(self.base_url, self.endpoint, next_job_id)
            r_get_info = requests.get(next_job_url,  headers=self.headers)
            try:
                assert r_get_info.status_code == self.success_code
            except Exception as e:
                self.logger.info("Fail in get TASK_PIPELINE_JOB_ID_NEXT {}, ex: {}, result: {}".format(next_job_id, 
                                    parse_response(res_report, self.logger), 
                                    result))
                return False, res_report
            forward_result = {}
            forward_result['forward_env'] = r_get_info.json()['result']['forward_env']
            forward_result['forward_env']['FORWARD_RESULT'] = json.dumps(parse_result)
            self.logger.info("forward_result: {}".format(forward_result))
            res_report = requests.put(next_job_url, json=forward_result, headers=self.headers)
            try:
                assert res_report.status_code == self.success_code
            except Exception as e:
                self.logger.info("Fail in forwarding TASK_PIPELINE_JOB_ID_NEXT {}, ex: {}, result: {}".format(next_job_id, 
                                    parse_response(res_report, self.logger), 
                                    forward_result))
                return False, res_report

        return True, res_report
    

    def fail_job(self):
        payload = {
            'status' : self.status['FAIL']
        }
        res_report = requests.put(self.main_url, json=payload, headers=self.headers)
        try:
            assert res_report.status_code == self.success_code
        except Exception as e:
            self.logger.info("Fail in fowarding job_id {}, ex: {}, result: {}".format(self.job_id, 
                            parse_response(res_report, self.logger), 
                            payload))
            return False, res_report
        return True, res_report
