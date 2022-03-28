import torchvision.models as models
import torch
import os
import cv2
from PIL import Image
import torchvision.transforms.functional as TF
from torchvision import transforms
import time
import json
import datetime
model = models.resnet50(pretrained=False, num_classes=365)
os.environ["CUDA_VISIBLE_DEVICES"]="1"


pretrained_dict=torch.load('/home/ailab/users/hung/classify_imagenet/FixRes/weights/checkpoint.pth',map_location='cpu')['model']
model_dict = model.state_dict()
count=0
count2=0
for k in model_dict.keys():
    count=count+1.0
    if(('module.'+k) in pretrained_dict.keys()):
        # if k == 'fc.weight' or k == 'fc.bias':
            # continue
        count2=count2+1.0
        model_dict[k]=pretrained_dict.get(('module.'+k))
model.load_state_dict(model_dict)

print("load "+str(count2*100/count)+" %")

f = open('IO.json',) 
dict_io = json.load(f) 

f = open('IO.json',) 
dict_io = json.load(f) 

f = open('idx_to_name.json',) 
dict_idx_to_name = json.load(f) 

f = open('name_to_idx.json',) 
dict_name_to_idx = json.load(f)

def make_decisions(dict_info, num_frame_make_descisions):
    count_top1_idx = -1
    idx_top1 = -1
    for idx in list(dict_info):
        if dict_info[idx]['count'] > count_top1_idx:
            count_top1_idx = dict_info[idx]['count']
            idx_top1 = idx
    if count_top1_idx <= num_frame_make_descisions//2:
        return False, None
    return True, [dict_info[idx_top1]['top5_idx'],dict_info[idx_top1]['top5_percent']]

def get_logger_for_run(log_container,logger_id=3):
    run_id = datetime.now().strftime(r'%m%d_%H%M%S')
    log_dir = os.path.join(log_container, run_id)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    setup_logging(log_dir)
    logger = logging.getLogger(logger_id)
    return logger, log_dir




mean, std = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]

transformations = transforms.Compose(
                [transforms.Resize(256),  
                 transforms.ToTensor(),
                 transforms.Normalize(mean, std)])

with torch.no_grad():
    model.cuda()
    model.eval()
    list_name = ['niu_duyen', 'dom_dom', 'di_ve_nha','TottenhnnvsBrentforrd', 'main','sieu_tri_tue']
    # list_name = ['niu_duyen']
        # name_video = 'main'
    for name_video in list_name:
        path = './videos/' + name_video +'.mp4'
        print(path)
        # name_video = 'main'
        cap = cv2.VideoCapture(path) 
        if (cap.isOpened()== False):  
            print("Error opening video  file")
        fps = cap.get(cv2.CAP_PROP_FPS)


        print('FPS', fps)
        result =None
        frame_width = int(cap.get(3)) 
        frame_height = int(cap.get(4))
        size = (frame_width, frame_height) 
        result = cv2.VideoWriter('output/' + name_video + '_save.avi',  
                            cv2.VideoWriter_fourcc(*'MJPG'), 
                            fps, size)
        print(size)

        count =0
        list_fps = []
        NUM_FRAME_STATISTICS = 11
        list_time_statistics = []
        dict_info_statistics = {}
        list_frame = []
        while(cap.isOpened()):
            s = time.time()
            ret, frame = cap.read()
            count += 1
            if ret == False:
                break
            # if count % 3 == 0:
            #     continue
            text = ''
            img1 = frame
            img = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            x = transformations(img).cuda()
            x.unsqueeze_(0)
            output = model(x)
            # _, predicted = torch.max(output.data, 1)
            values_top5, idx_top5 = output.data.topk(5)
            percentage = torch.nn.functional.softmax(output, dim=1)[0] * 100
            # print('idx: ',idx_top5.cpu().numpy()[0])
            
            # print('pct: ',percentage.cpu().numpy())
            processing =False
            if int(percentage[idx_top5[0][0].cpu().numpy()].cpu().numpy()) > 20:
                processing = True

                list_idx_top5_1_frame = idx_top5.cpu().numpy()[0]
                list_percent_top5_1_frame = []
                for idx in list_idx_top5_1_frame:
                    percent =percentage.cpu().numpy()[idx]
                    list_percent_top5_1_frame.append(percent)

                    # text += dict_idx_to_name[str(idx)] + ': ' + str(int(percent)) + '\n'
                idx_top1 = list_idx_top5_1_frame[0]
                if  idx_top1 not in dict_info_statistics:
                    dict_info_statistics[idx_top1] = {}
                    dict_info_statistics[idx_top1]['count'] = 1
                    dict_info_statistics[idx_top1]['top5_idx'] = list_idx_top5_1_frame
                    dict_info_statistics[idx_top1]['top5_percent'] = list_percent_top5_1_frame
                else:
                    # dict_info_statistics[idx] += 1
                    dict_info_statistics[idx_top1]['count'] += 1
                    if dict_info_statistics[idx_top1]['top5_idx'][0] < list_idx_top5_1_frame[0]:
                        dict_info_statistics[idx_top1]['top5_idx'] = list_idx_top5_1_frame
                        dict_info_statistics[idx_top1]['top5_percent'] = list_percent_top5_1_frame

                time_hh_mm_ss_current_frame = str(datetime.timedelta(seconds=count/fps))
                list_time_statistics.append(time_hh_mm_ss_current_frame)
                list_frame.append(frame)


            if len(list_time_statistics) == NUM_FRAME_STATISTICS:
                is_scene, top5_idx_and_percent = make_decisions(dict_info_statistics, NUM_FRAME_STATISTICS)
                if is_scene:
                    type = "Indoor"
                    idx_top1 = top5_idx_and_percent[0][0]
                    io = dict_io[dict_idx_to_name[str(idx_top1)]]
                    if io == '2':
                        type = 'Outdoor'
                    for img_write in list_frame:
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        img_write = cv2.putText(img_write, type, (50, 50-27 ),font, 1,  (0,255,127),  2,  cv2.LINE_4)
                        y0, dy = 50, 27
                        for i in range(5):
                            y = y0 + i*dy
                            idx = top5_idx_and_percent[0][i]
                            percent = top5_idx_and_percent[1][i]
                            text = dict_idx_to_name[str(idx)] + ': ' + str(int(percent)) 
                            img_write = cv2.putText(img_write, text, (50, y),font, 0.7,  (0, 255, 255),  1,  cv2.LINE_4)
                        
                        img_write = cv2.putText(img_write,"Time video: " + str(list_time_statistics[i]), (50, 50+27*5),font, 0.7,  (0, 255, 255),  1,  cv2.LINE_4)
                        result.write(img_write)
                        
                else:
                    for img_write in list_frame:
                        result.write(img_write)
                list_frame = []
                list_time_statistics = []
                dict_info_statistics = {}

            if processing == False:
                for img_write in list_frame:
                    result.write(img_write)
                list_frame = []
                list_time_statistics = []
                dict_info_statistics = {}
                result.write(frame)

        cap.release()
        result.release() 
        cv2.destroyAllWindows()  

