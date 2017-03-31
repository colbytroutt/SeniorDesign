import numpy as np

def non_max_suppression_fast(boxes, overlapThresh):
    if len(boxes) == 0:
        return []

    if boxes.dtype.kind == "i":
        boxes = boxes.astype("float")

    pick = []

    x1 = boxes[:,0]
    y1 = boxes[:,1]
    x2 = boxes[:,2]
    y2 = boxes[:,3]

    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    indexes = np.argsort(y2)

    while len(indexes) > 0:
        last = len(indexes) - 1
        i = indexes[last]
        pick.append(i)

        xx1 = np.maximum(x1[i], x1[indexes[:last]])
        yy1 = np.maximum(y1[i], y1[indexes[:last]])
        xx2 = np.minimum(x2[i], x2[indexes[:last]])
        yy2 = np.minimum(y2[i], y2[indexes[:last]])

        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)

        overlap = (w * h) / area[indexes[:last]]

        indexes = np.delete(indexes, np.concatenate(([last], np.where(overlap > overlapThresh)[0])))

    return boxes[pick].astype("int")
