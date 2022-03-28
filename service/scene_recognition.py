import os
import time
from utils import *
import shortuuid
import math
from s3_utils import client, upload_file


class SceneRecognition:
    def __init__(self, indexing_obj, logging):
        self.logger = logging
        self.s3_bucket = os.environ.get('OUTPUT_BUCKET')
        self.indexing_obj = indexing_obj

    def report_job_fail(self, reporter, max_retry, task_pipeline_job_id):
        respone = None
        for retry_time in range(max_retry):
            is_request, respone = reporter.fail_job()
            if is_request:
                self.logger.info('End process of video {}'.format(task_pipeline_job_id))
                break
            self.logger.info('Fail in report job fail: {}, retry {} time'.format(respone.text, str(retry_time + 1)))
            time.sleep(1)
        return respone


    def processing(self, stream_url, job_payload, reporter):
        bf_pc_dt = self.before_process(job_payload)
        list_track = None
        try:
            list_track = self.indexing_obj.processing_video(stream_url, job_payload, reporter)
        except Exception as e:
            self.logger.info(e)
            self.logger.info("Fail in processing video")
            self.report_job_fail(reporter, job_payload['max_retry'], job_payload['task_pipeline_job_id'])
            return False
        self.have_success(list_track, job_payload, bf_pc_dt, reporter)
        self.logger.info("Completed indexing with task_pipeline_job_id: {}".format(job_payload['task_pipeline_job_id']))
        return True

    def before_process(self, job_payload):
        local_ji = '{}__{}'.format(job_payload.get('task_pipeline_job_id'), shortuuid.uuid())

        movie_name = job_payload['content_id']

        dir_json = os.path.join(os.environ['OUTPUT_JSON'], movie_name)
        if not os.path.exists(os.environ['OUTPUT_JSON']):
            os.makedirs(os.environ['OUTPUT_JSON'])
        if not os.path.exists(dir_json):
            os.makedirs(dir_json)
        start_time = time.time()
        result = {
            'local_ji': local_ji,
            'start_time': start_time, 
            'dir_json': dir_json
        }
        return result


    def have_success(self, list_track, job_payload, bf_process_dt, reporter):
        output_json = os.path.join(bf_process_dt['dir_json'], '{}.json'.format(bf_process_dt['local_ji']))
        write_json(output_json, list_track, True, None)
        up_res = upload_file(client, self.s3_bucket, output_json, output_json, True)
        url_data = None
        if up_res:
            self.logger.info("Uploaded file {} to s3 bucket {}".format(output_json, 
                                self.s3_bucket))
            url_data = "{}/{}/{}".format(os.environ['ENDPOINT_URL'], self.s3_bucket, output_json)
        else:
            self.logger.info('Could not upload file {} to s3 bucket {}'.format(output_json,
                                self.s3_bucket))
        payload = {'data': url_data, 'type': int(os.environ.get('JOB_TYPE')), 'duration': math.ceil(time.time() - float(os.environ['START_TIME']))}
        self.logger.info(payload)
        res_ss = False
        for retry_time in range(job_payload['max_retry']):
            res_ss, res_rp = reporter.done_job(payload)
            if res_ss:
                res = parse_response(res_rp, self.logger)
                self.logger.info(json.dumps(res, indent=True))
                self.logger.info('End indexing process of video {}'.format(job_payload.get('task_pipeline_job_id')))
                break
            self.logger.info('Fail in report done job, retry {} time'.format(str(retry_time + 1)))
            time.sleep(1)
        assert res_ss