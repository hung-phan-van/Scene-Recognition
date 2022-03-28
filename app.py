from requests.api import get
import torch
import os
from dotenv import load_dotenv
load_dotenv("env/.env")
from utils import *
import logging as logger
import indexing_algorithms as idx_alg_md
from service import SceneRecognition, JobReporter
import multiprocessing as mp
import argparse
import time

def get_env():
    job_payload = {}
    job_payload['hls_url'] = os.environ['HLS_URL']
    job_payload['content_id'] = os.environ['CONTENT_ID']
    job_payload['season_id'] = os.environ['SEASON_ID']
    job_payload['drm'] = os.environ.get('DRM', None)
    job_payload['task_pipeline_job_id'] = os.environ['TASK_PIPELINE_JOB_ID']
    job_payload['max_retry'] = int(os.environ.get('MAX_RETRY', '5'))
    return job_payload


def create_app():
    if os.environ['IS_LOG_FILE'] == 'True':
        if not os.path.exists(os.environ['OUTPUT_LOG']):
            os.makedirs(os.environ['OUTPUT_LOG'])
        logger.basicConfig(filename=os.environ['LOG_FILE'],
                            filemode='a',
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logger.DEBUG)
    else:
        logger.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logger.DEBUG)
    logger.info("Start processing app.py")

    __ALL_MODEL__ = ['resnet50', 'deit_small_patch16_224']
    if os.environ['MODEL_NAME'] == 'resnet50':
        from models import resnet50
        model = resnet50.load_model(model_name=os.environ['MODEL_NAME'])
        transformations = resnet50.build_transform()
    else:
        from models import deit
        model = deit.load_model(model_name=os.environ['MODEL_NAME'])
        transformations = deit.build_transform()
       
    indexing_obj = idx_alg_md.VideoIndexing(model, transformations, logger)
    scene_recog = SceneRecognition(indexing_obj, logger)
    job_payload = get_env()
    reporter = JobReporter(os.environ['PL_API_URL'], os.environ['PINELINE_RP_EP'], 
                            job_payload['task_pipeline_job_id'], logger)
    try:
        scene_meta = get_scene_meta(logger, os.getenv('FORWARD_RESULT'))
        if scene_meta is None:
            raise Exception('scene_meta field is not found')
        job_payload['scene_meta'] = scene_meta
        stream_url = parse_hls_url(job_payload['hls_url'])
        if stream_url is None:
            raise Exception('Can not parse link from hls_url')
        scene_recog.processing(stream_url, job_payload, reporter)
    except Exception as e:
        logger.info(e)
        respone = scene_recog.report_job_fail(reporter, job_payload['max_retry'], job_payload['task_pipeline_job_id'])
        return respone

if __name__ == '__main__':
    os.environ['START_TIME'] = str(time.time())
    mp.set_start_method('spawn')
    app = create_app()
