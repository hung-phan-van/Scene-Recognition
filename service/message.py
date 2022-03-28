fail_message = {
    '0': 'payload validation exception',
    '1': 'running indexing thread',
    '2': 'Reporting fail job IS NOT success',
    '3': 'This job does not have job_id',
    '4': 'This job does not have hls_url',
    '5': 'Can not get links from this hls_url',
    '6': 'Can not stream from this link',
    '7': 'Local DB: fail on update fail job'
}

fail_pt = {
    '0': 'Exception when validate payload: {}',
    '1': 'Fail when update fail job: {}',
    '3': 'Could not generate signed url for {}',
    '4': 'Could not upload file {} to s3 bucket {}',
    '5': 'Fail in sending job results: {}'
}

success_message = {
    '0': 'Worker is alive now',
    '1': 'Receive job successfully'
}

success_pt = {
    '0': 'Uploaded file {} to s3 bucket {}',
    '1': 'End indexing process of video {}'
}


report_message = {
    '0': 'Update job on AI Service with payload:',
    '1': 'Response when updating job:',
    "START_REPORT_JOB": "Start report to {}, job_id {}"
}


exceptions = {
    'REPORT_JOB_PROGRESS': 'Report job progress fail, job_id: {}, ex: {}',
    'DONE_JOB': 'Fail in finishing job_id {}, ex: {}, result: {}',
    'FAIL_JOB': 'Fail in failing job_id {}, ex: {}, result: {}'
}
