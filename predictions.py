import cv2
from ultralytics import YOLO

yolo = YOLO('best.pt')

def detection(frame):
    pred = yolo.predict(frame)
    objs = list(pred[0].boxes.xyxy)
    conf = list(pred[0].boxes.conf)
    co_ords = []

    for i, j in zip(objs, conf):
        if float(j) > 0.5:  # confidence threshold
            co_ords.append([(int(i[0]), int(i[1])), (int(i[2]), int(i[3])), float(j)])
    return co_ords

def cal_area(co_ordinates):
    height = co_ordinates[1][0] - co_ordinates[0][0]
    width = co_ordinates[1][1] - co_ordinates[0][1]
    area = (height / 10) * (width / 10)
    return int(area)

def draw_bounding_boxes(co_ords, img_new):
    for i in co_ords:
        area = cal_area(i)
        text = f'Pothole approx area: {area} sq.cm'
        cv2.rectangle(img_new, i[0], i[1], (0, 255, 0), 2)
        cv2.putText(img_new, text, (i[0][0], i[0][1] - 5),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)
    return img_new
