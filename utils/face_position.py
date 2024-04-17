import enum
from io import BytesIO

import numpy as np
from facenet_pytorch import MTCNN
from PIL import Image


class ProfilePhoto(enum.Enum):
    LEFT_PROFILE = enum.auto()
    RIGHT_PROFILE = enum.auto()
    FULL_FACE_PROFILE = enum.auto()
    NO_FACES_DETECTED = enum.auto()


mtcnn = MTCNN(
    image_size=160,
    margin=0,
    min_face_size=20,
    thresholds=[0.6, 0.7, 0.7],  # MTCNN thresholds
    factor=0.709,
    post_process=True,
    device="cpu",
)


def np_angle(a, b, c):
    ba = np.array(a) - np.array(b)
    bc = np.array(c) - np.array(b)

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)

    return np.degrees(angle)


def pred_face_pose(image_obj: BytesIO):
    im = Image.open(image_obj)

    if im.mode != "RGB":
        im = im.convert("RGB")

    bbox_, prob_, landmarks_ = mtcnn.detect(im, landmarks=True)

    angle_R_List = []
    angle_L_List = []
    pred_label_list = []

    if bbox_ is None or landmarks_ is None or prob_ is None:
        print("No faces detected in the image.")
        return ProfilePhoto.NO_FACES_DETECTED

    for bbox, landmarks, prob in zip(bbox_, landmarks_, prob_):
        if bbox is not None and prob > 0.9:
            angR = np_angle(landmarks[0], landmarks[1], landmarks[2])
            angL = np_angle(landmarks[1], landmarks[0], landmarks[2])

            angle_R_List.append(angR)
            angle_L_List.append(angL)

            if (int(angR) in range(35, 57)) and (int(angL) in range(35, 58)):
                pred_label = ProfilePhoto.FULL_FACE_PROFILE
            elif angR < angL:
                pred_label = ProfilePhoto.LEFT_PROFILE
            else:
                pred_label = ProfilePhoto.RIGHT_PROFILE

            pred_label_list.append(pred_label)
        else:
            print(
                "The detected face is below the detection threshold or no bounding box available."
            )

    return pred_label_list[-1] if pred_label_list else ProfilePhoto.NO_FACES_DETECTED
