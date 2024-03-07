import cv2
import numpy as np

from detect import *
from transform import *
from utils import *

base_path = "data/"
path = "data/"

if not os.path.exists(path):
    os.makedirs(path)


def generate_all_files(imgpath, info, position=None, rotation=None):
    
    # global path
    #
    print(" ----- Generate ", imgpath, " at pos ", position ," rot ",rotation," -----")
    #
    #
    # path = create_new_floorplan_path(base_path)

    shape = generate_floor_file(imgpath, info)
    new_shape = generate_walls_file(imgpath, info)
    shape = validate_shape(shape, new_shape)
    new_shape = generate_rooms_file(imgpath, info)
    shape = validate_shape(shape, new_shape)

    transform = generate_transform_file(imgpath, info, position, rotation, shape)

    return path, shape


def validate_shape(old_shape, new_shape):
    
    shape = [0,0,0]
    shape[0] = max(old_shape[0], new_shape[0])
    shape[1] = max(old_shape[1], new_shape[1])
    shape[2] = max(old_shape[2], new_shape[2])
    return shape

def get_shape(verts, scale):
    
    if len(verts) == 0:
        return [0,0,0]

    posList = verts_to_poslist(verts)
    high = [0,0,0]
    low = posList[0]

    for pos in posList:
        if pos[0] > high[0]:
            high[0] = pos[0]
        if pos[1] > high[1]:
            high[1] = pos[1]
        if pos[2] > high[2]:
            high[2] = pos[2]
        if pos[0] < low[0]:
            low[0] = pos[0]
        if pos[1] < low[1]:
            low[1] = pos[1]
        if pos[2] < low[2]:
            low[2] = pos[2]

    return [high[0] - low[0],high[1] - low[1],high[2] - low[2]]

def generate_transform_file(imgpath, info, position, rotation, shape):
    
    transform = {}
    if position is None:
        transform["position"] = (0,0,0)
    else:
        transform["position"] = position

    if rotation is None:
        transform["rotation"] = (0,0,0)
    else:
        transform["rotation"] = rotation

    if shape is None:
        transform["shape"] = (0,0,0)
    else:
        transform["shape"] = shape

    save_to_file(path+"transform", transform)

    return transform

def generate_rooms_file(img_path, info):
    
    img = cv2.imread(img_path)

    
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    verts = []
    faces = []

    height = 0.999

    scale = 100

    gray = wall_filter(gray)

    gray = ~gray

    rooms, colored_rooms = find_rooms(gray.copy())

    gray_rooms =  cv2.cvtColor(colored_rooms,cv2.COLOR_BGR2GRAY)

    boxes, gray_rooms = detectPreciseBoxes(gray_rooms, gray_rooms)

    room_count = 0
    for box in boxes:
        verts.extend([scale_point_to_vector(box, scale, height)])
        room_count+= 1

    for room in verts:
        count = 0
        temp = ()
        for pos in room:
            temp = temp + (count,)
            count += 1
        faces.append([(temp)])

    if(info):
        print("Number of rooms detected : ", room_count)

    save_to_file(path+"rooms_verts", verts)
    save_to_file(path+"rooms_faces", faces)

    return get_shape(verts, scale)

def generate_small_windows_file(img_path, info):
    
    img = cv2.imread(img_path)

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    verts = []
    faces = []

    height = 1

    scale = 100

    gray = wall_filter(gray)

    gray = ~gray

    rooms, colored_rooms = find_details(gray.copy())

    gray_rooms =  cv2.cvtColor(colored_rooms,cv2.COLOR_BGR2GRAY)

    boxes, gray_rooms = detectPreciseBoxes(gray_rooms, gray_rooms)

    windows = []

    for box in boxes:
        if(len(box) >= 4):
            x = box[0][0][0]
            x1 = box[2][0][0]
            y = box[0][0][1]
            y1 = box[2][0][1]

            if (abs(x-x1) > abs(y-y1)):
                windows.append([[[x,round((y+y1)/2)]],[[x1,round((y+y1)/2)]]])
            else:
                windows.append([[[round((x+x1)/2),y]],[[round((x+x1)/2),y1]]])

    
    v, faces, window_amount1 = create_nx4_verts_and_faces(windows, height=0.25, scale=scale) # create low piece
    v2, faces, window_amount2 = create_nx4_verts_and_faces(windows, height=1, scale=scale, ground= 0.75) # create heigher piece

    verts = v
    verts.extend(v2)
    window_amount = window_amount1 + window_amount2

    if(info):
        print("Windows created : ", window_amount)


    save_to_file(path+"windows_verts", verts)
    save_to_file(path+"windows_faces", faces)

    return get_shape(verts, scale)

def generate_doors_file(img_path, info):
    
    img = cv2.imread(img_path)

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    verts = []
    faces = []

    height = 1

    scale = 100

    gray = wall_filter(gray)

    gray = ~gray

    rooms, colored_rooms = find_details(gray.copy())

    gray_rooms =  cv2.cvtColor(colored_rooms,cv2.COLOR_BGR2GRAY)

    boxes, gray_rooms = detectPreciseBoxes(gray_rooms, gray_rooms)

    doors = []

    for box in boxes:
        if shape_of_door(point):
            for x,y,x1,y1 in box:
                doors.append([round((x+x1)/2),round((y+y1)/2)])

    
    verts, faces, door_amount = create_nx4_verts_and_faces(doors, height, scale)

    if(info):
        print("Doors created : ", door_amount)

    save_to_file(path+"doors_verts", verts)
    save_to_file(path+"doors_faces", faces)

    return get_shape(verts, scale)

def generate_floor_file(img_path, info):
    
    img = cv2.imread(img_path)

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    contour, img = detectOuterContours(gray)

    verts = []
    faces = []

    height = 1

    scale = 100

    verts = scale_point_to_vector(contour, scale, height)

    count = 0
    for box in verts:
        faces.extend([(count)])
        count += 1


    if(info):
        print("Approximated apartment size : ", cv2.contourArea(contour))

    save_to_file(path+"floor_verts", verts)
    save_to_file(path+"floor_faces", faces)

    return get_shape(verts, scale)

def generate_walls_file(img_path, info):
    
    img = cv2.imread(img_path)

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    wall_img = wall_filter(gray)

    boxes, img = detectPreciseBoxes(wall_img)

    verts = []
    faces = []

    wall_height = 1

    scale = 100

    verts, faces, wall_amount = create_nx4_verts_and_faces(boxes, wall_height, scale)

    if(info):
        print("Walls created : ", wall_amount)

    save_to_file(path+"wall_verts", verts)
    save_to_file(path+"wall_faces", faces)

    return get_shape(verts, scale)
