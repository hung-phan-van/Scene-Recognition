from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import logging
from datetime import datetime



class JobStatusDB():
    def __init__(self, db_url, job_type, db_name, logging):
        self.db_url = db_url
        self.client = self._create_client()
        self.job_status_tb = getattr(self.client, db_name).jobs
        self.worker_status_tb = getattr(self.client, db_name).status
        self.logger = logging
        self.job_type = job_type
        self.logger.info("Client and dbname: {} {}".format(self.client,db_name))
        self.logger.info("Worker status tb: {}".format(self.worker_status_tb))
        self.worker_id = self.worker_status_tb.find().limit(1)[0]["_id"]
        self.logger.info("worker_id: {}".format(self.worker_id))

    def _create_client(self):
        client = MongoClient(
                host=os.getenv('MONGODB_HOST') or '172.16.5.49',
                port=int(os.getenv('MONGODB_PORT')) or 27017,
                username=os.getenv('MONGO_USER') or 'root',
                password=os.getenv('MONGO_PASS') or '1',
                authSource=os.getenv('MONGO_DB') or 'admin',
                authMechanism='SCRAM-SHA-256'
            )
        return client
    
    
    def create_job(self, payload):
        job = {
            'status': 1,
            'percent': 0,
            'job_type': self.job_type,
            'id': payload.get('job_id'),
            'updated_at': datetime.now(),
            'created_at':datetime.now(),
            'stage_id': payload.get('stage_id')
            
        }
        result = self.job_status_tb.insert_one(job)
        self.logger.info('Created job with id: {}'.format(result.inserted_id))
        self.update_job_counter(1)
        self.update_document(self.worker_status_tb, '$set', {'status': 1}, self.worker_id)
        return result.inserted_id
    
    
    def update_status(self, job_id, job_status):
        query = {
            '_id': ObjectId(job_id)
        }
        new_status = {
            '$set': job_status
        }
        update_res = self.job_status_tb.update_one(query, new_status)
        
        if update_res.matched_count > 0:
            return True

        self.logger.info('Job {} is not found on DB'.format(job_id))
        return False

    
    def update_job_counter(self, amount):
        query = {
            '_id': ObjectId(self.worker_id)
        }
        update = {
            '$inc': {
                'total_jobs': amount
            }
        }
        update_res = self.worker_status_tb.update_one(query, update)
        if update_res.matched_count > 0:
            return True

        self.logger.info('Worker {} is not found on DB'.format(self.worker_id))
        return False

    
    def update_document(self, table, operator, new_val, doc_id):
        query = {
            '_id': ObjectId(doc_id)
        }
        update = {
            operator: new_val
        }
        update_res = table.update_one(query, update)
        if update_res.matched_count > 0:
            return True

        self.logger.info('Id {} is not found on table {}'.format(doc_id, 
                            table.__str__()))
        return False

    
    def done_job(self, job_id):
        self.update_status(job_id, {
            'status': 2,
            'percent': 1.0,
            'updated_at': datetime.now()
        })
        self.update_job_counter(-1)

    
    def update_idle_for_worker(self):
        query = {
            '_id': ObjectId(self.worker_id)
        }
        res = self.worker_status_tb.find_one(query)
        if res:
            if res.get('total_jobs') == 0:
                self.update_document(self.worker_status_tb, '$set', {'status': 2}, self.worker_id)
                self.logger.info('Worker is idle now')
            else:
                self.logger.info('Now jobs on worker: {}'.format(res.get('total_jobs')))
        else:
            self.logger.info('Worker id {} is not found'.format(self.worker_id))

