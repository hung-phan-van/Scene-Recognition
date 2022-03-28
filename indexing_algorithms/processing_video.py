from utils import read_json, make_statistic, merge_output
import cv2
from PIL import Image
import torch
import datetime 
import time
import os
from video_tools import VideoManager
# from multiprocessing import Queue


class VideoIndexing:
    def __init__(self, model, transformations, logger):
        self.model = model
        self.logger = logger
        self.transformations = transformations
        self.dict_io = read_json(os.environ['IO'])
        self.dict_idx_to_name = read_json(os.environ['IDX_TO_NAME'])
        self.dict_name_to_idx = read_json(os.environ['NAME_TO_IDX'])
        self.dict_wrong_classes_index = read_json(os.environ['WRONG_CLASSES_IDX'])

    def check_stream_url(self, url):
        cap_check = cv2.VideoCapture(url)
        if cap_check.isOpened():
            return True
        return False

    def processing_video(self, url, job_payload, reporter, debug=False, log_step=1000, process_fram_every_n=3):
        if not self.check_stream_url(url):
            self.logger.info("Link None")
            return None
        reader = VideoManager(url, 0)
        reader.run_process_get_image()
        with torch.no_grad():
            self.model.eval()
            fps = reader.fps
            n_video_frames = reader.n_video_frames
            self.logger.info("Total frams: {}".format(n_video_frames))

            self.logger.info('FPS: {}'.format(fps))
            frame_width = reader.width
            frame_height = reader.height
            self.logger.info("size: {}x{}".format(frame_width,frame_height))
            s = time.time()
            scene_detect = job_payload['scene_meta']

            is_break = False
            data = []
            count_reader_frame_number = -1
            for value in scene_detect:
                if is_break:
                    break
                info_scene = {}
                for frame_count in range(value[0], value[1] + 1):
                    ret, frame = reader._queue.get()
                    count_reader_frame_number += 1
                    while frame_count - count_reader_frame_number >= 1:
                        ret, frame = reader._queue.get()
                        count_reader_frame_number += 1

                    if ret == False:
                        is_break = True
                        break
                    if frame_count % process_fram_every_n != 0:
                        continue

                    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(img)
                    x = self.transformations(img).cuda()
                    x.unsqueeze_(0)
                    output = self.model(x)
                    _, idx_top3 = output.data.topk(3)
                    percentage = torch.nn.functional.softmax(output, dim=1)[0]
                    if float(percentage[idx_top3[0][0].cpu().numpy()].cpu().numpy()) >= float(os.environ['MIN_CONFIDENCE']):
                        list_idx_top3_1_frame = idx_top3.cpu().numpy()[0].tolist()
                        for idx in list_idx_top3_1_frame:
                            if str(idx) in self.dict_wrong_classes_index:
                                continue
                            percent = percentage.cpu().numpy()[idx]
                            if idx not in info_scene:
                                info_scene[idx] = {}
                                info_scene[idx]['list_percent'] = [percent]
                                info_scene[idx]['count'] = 1
                            else:
                                info_scene[idx]['list_percent'].append(percent)
                                info_scene[idx]['count'] += 1

                    if frame_count % log_step == 0:
                        self.logger.info('Current time video update percent: {}, percent: {}'.format(str(datetime.timedelta(seconds=frame_count/fps)), round(frame_count/n_video_frames, 2)))
                        if reporter is not None:
                            amount_udt = round(frame_count / n_video_frames, 2)
                            res_rp = reporter.report_progress(amount_udt)
                list_idx, list_cof = make_statistic(info_scene)
                if list_idx is not None:
                    start_scene = str(datetime.timedelta(seconds=value[0]/fps))
                    end_scene = str(datetime.timedelta(seconds=value[1]/fps))
                    result_scene = {}
                    result_scene["itv"] = [start_scene, end_scene]
                    list_type = []
                    for idx in list_idx:
                        list_type.append(int(self.dict_io[str(self.dict_idx_to_name[str(idx)])]))
                    result_scene["s_r"] = {'list_idx': list_idx, 'list_cof': list_cof, 'list_type': list_type}
                    data.append(result_scene)
        reader.release()
        data = merge_output(data)
        self.logger.info("Time processing: {}".format(time.time() - s))
        return data
    
