import sys, os, cv2
from time import sleep
import numpy as np, math
from argparse import ArgumentParser
from threading import Thread
try:
    from armv7l.openvino.inference_engine import IENetwork, IECore#IEPlugin
except:
    from openvino.inference_engine import IENetwork, IECore#IEPlugin


class DetectionObject():
    xmin = 0
    ymin = 0
    xmax = 0
    ymax = 0
    class_id = 0
    confidence = 0.0

    def __init__(self, x, y, h, w, class_id, confidence, h_scale, w_scale):
        self.xmin = int((x - w / 2) * w_scale)
        self.ymin = int((y - h / 2) * h_scale)
        self.xmax = int(self.xmin + w * w_scale)
        self.ymax = int(self.ymin + h * h_scale)
        self.class_id = class_id
        self.confidence = confidence

        
class YOLO:
    def __init__(self,show = False):
        self.show = show
        self.trigger = False
        self.stop = False
        self.objects = {}
        
        self.m_input_size = 416

        self.yolo_scale_13 = 13
        self.yolo_scale_26 = 26

        self.classes = 80
        self.coords = 4
        self.num = 3
        self.anchors = [10,14, 23,27, 37,58, 81,82, 135,169, 344,319]

        self.LABELS = ("person", "bicycle", "car", "motorbike", "aeroplane",
                  "bus", "train", "truck", "boat", "traffic light",
                  "fire hydrant", "stop sign", "parking meter", "bench", "bird",
                  "cat", "dog", "horse", "sheep", "cow",
                  "elephant", "bear", "zebra", "giraffe", "backpack",
                  "umbrella", "handbag", "tie", "suitcase", "frisbee",
                  "skis", "snowboard", "sports ball", "kite", "baseball bat",
                  "baseball glove", "skateboard", "surfboard","tennis racket", "bottle",
                  "wine glass", "cup", "fork", "knife", "spoon",
                  "bowl", "banana", "apple", "sandwich", "orange",
                  "broccoli", "carrot", "hot dog", "pizza", "donut",
                  "cake", "chair", "sofa", "pottedplant", "bed",
                  "diningtable", "toilet", "tvmonitor", "laptop", "mouse",
                  "remote", "keyboard", "cell phone", "microwave", "oven",
                  "toaster", "sink", "refrigerator", "book", "clock",
                  "vase", "scissors", "teddy bear", "hair drier", "toothbrush")

        self.e2c = {'cat':'猫','book':'书','bottle':'瓶子','keyboard':'键盘','tvmonitor':'屏幕','dog':'狗'}
        self.label_text_color = (255, 255, 255)
        self.label_background_color = (125, 175, 75)
        self.box_color = (255, 128, 0)
        self.box_thickness = 1
        



    def EntryIndex(self,side, lcoords, lclasses, location, entry):
        n = int(location / (side * side))
        loc = location % (side * side)
        return int(n * side * side * (lcoords + lclasses + 1) + entry * side * side + loc)



    def IntersectionOverUnion(self,box_1, box_2):
        width_of_overlap_area = min(box_1.xmax, box_2.xmax) - max(box_1.xmin, box_2.xmin)
        height_of_overlap_area = min(box_1.ymax, box_2.ymax) - max(box_1.ymin, box_2.ymin)
        area_of_overlap = 0.0
        if (width_of_overlap_area < 0.0 or height_of_overlap_area < 0.0):
            area_of_overlap = 0.0
        else:
            area_of_overlap = width_of_overlap_area * height_of_overlap_area
        box_1_area = (box_1.ymax - box_1.ymin)  * (box_1.xmax - box_1.xmin)
        box_2_area = (box_2.ymax - box_2.ymin)  * (box_2.xmax - box_2.xmin)
        area_of_union = box_1_area + box_2_area - area_of_overlap
        retval = 0.0
        if area_of_union <= 0.0:
            retval = 0.0
        else:
            retval = (area_of_overlap / area_of_union)
        return retval


    def ParseYOLOV3Output(self,blob, resized_im_h, resized_im_w, original_im_h, original_im_w, threshold, objects):

        out_blob_h = blob.shape[2]
        out_blob_w = blob.shape[3]

        side = out_blob_h
        anchor_offset = 0

        if side == self.yolo_scale_13:
            anchor_offset = 2 * 3
        elif side == self.yolo_scale_26:
            anchor_offset = 2 * 0

        side_square = side * side
        output_blob = blob.flatten()

        for i in range(side_square):
            row = int(i / side)
            col = int(i % side)
            for n in range(self.num):
                obj_index = self.EntryIndex(side, self.coords, self.classes, n * side * side + i, self.coords)
                box_index = self.EntryIndex(side, self.coords, self.classes, n * side * side + i, 0)
                scale = output_blob[obj_index]
                if (scale < threshold):
                    continue
                x = (col + output_blob[box_index + 0 * side_square]) / side * resized_im_w
                y = (row + output_blob[box_index + 1 * side_square]) / side * resized_im_h
                height = math.exp(output_blob[box_index + 3 * side_square]) * self.anchors[anchor_offset + 2 * n + 1]
                width = math.exp(output_blob[box_index + 2 * side_square]) * self.anchors[anchor_offset + 2 * n]
                for j in range(self.classes):
                    class_index = self.EntryIndex(side, self.coords, self.classes, n * side_square + i, self.coords + 1 + j)
                    prob = scale * output_blob[class_index]
                    if prob < threshold:
                        continue
                    obj = DetectionObject(x, y, height, width, j, prob, (original_im_h / resized_im_h), (original_im_w / resized_im_w))
                    objects.append(obj)
        return objects


    def finish(self):
        self.stop = True
    
    def recognize(self):
        self.trigger = True
        
    def start(self):
        camera_width = 640
        camera_height = 480
        fps = ""
        framepos = 0
        frame_count = 0
        vidfps = 0
        skip_frame = 0
        elapsedTime = 0
        new_w = int(camera_width * self.m_input_size/camera_width)
        new_h = int(camera_height * self.m_input_size/camera_height)

        
        model_xml = "frozen_tiny_yolo_v3.xml" #<--- MYRIAD
        model_bin = os.path.splitext(model_xml)[0] + ".bin"

        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)



        sleep(1)


        ie = IECore()
        load_net = ie.read_network(model_xml, model_bin)
        load_net.batch_size = 1
        exec_net = ie.load_network(network=load_net, device_name="MYRIAD")
        input_blob = next(iter(load_net.input_info))
        
        
        inputs = {}
        for input_name in load_net.input_info:
            inputs[input_name] = np.zeros(load_net.input_info[input_name].input_data.shape)
        while cap.isOpened():
            ret, image = cap.read()
            if not ret:
                break
            
            if self.trigger:
                self.trigger = False
                self.objects = {}
                resized_image = cv2.resize(image, (new_w, new_h), interpolation = cv2.INTER_CUBIC)
                canvas = np.full((self.m_input_size, self.m_input_size, 3), 128)
                canvas[(self.m_input_size-new_h)//2:(self.m_input_size-new_h)//2 + new_h,(self.m_input_size-new_w)//2:(self.m_input_size-new_w)//2 + new_w,  :] = resized_image
                prepimg = canvas
                prepimg = prepimg[np.newaxis, :, :, :]     # Batch size axis add
                prepimg = prepimg.transpose((0, 3, 1, 2))  # NHWC to NCHW
                inputs[input_blob] = prepimg
                outputs = exec_net.infer(inputs=inputs)

                objects = []

                for output in outputs.values():
                    objects = self.ParseYOLOV3Output(output, new_h, new_w, camera_height, camera_width, 0.4, objects)

                # Filtering overlapping boxes
                objlen = len(objects)
                for i in range(objlen):
                    if (objects[i].confidence == 0.0):
                        continue
                    for j in range(i + 1, objlen):
                        if (self.IntersectionOverUnion(objects[i], objects[j]) >= 0.4):
                            if objects[i].confidence < objects[j].confidence:
                                objects[i], objects[j] = objects[j], objects[i]
                            objects[j].confidence = 0.0
                
                # Drawing boxes
                for obj in objects:
                    if obj.confidence < 0.2:
                        continue
                    label = obj.class_id
                    confidence = obj.confidence
                    #if confidence >= 0.2:
                    name = self.LABELS[label]
                    if name in self.e2c:
                        name = self.e2c[name]
                    if name in self.objects:
                        if confidence > self.objects[name]:
                            self.objects[name] = confidence
                    else:
                        self.objects[name] = confidence
                    if self.show: 
                        label_text = self.LABELS[label] + " (" + "{:.1f}".format(confidence * 100) + "%)"
                        cv2.rectangle(image, (obj.xmin, obj.ymin), (obj.xmax, obj.ymax), self.box_color, self.box_thickness)
                        cv2.putText(image, label_text, (obj.xmin, obj.ymin - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.label_text_color, 1)
            if self.show:
                cv2.putText(image, fps, (camera_width - 170, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (38, 0, 255), 1, cv2.LINE_AA)
                cv2.imshow("Result", image)

            #if cv2.waitKey(1)&0xFF == ord('q'):
            if self.stop:
                break

        cv2.destroyAllWindows()
        cap.release()
        del exec_net



if __name__ == '__main__':
    model = YOLO()
    t = Thread(target = model.start).start()
    while True:
        try:
            c = input()
            if c == 'q':
                model.finish()
                break
            elif c == 's':
                model.recognize()
                sleep(2)
                print(model.objects)
        except:
            break

