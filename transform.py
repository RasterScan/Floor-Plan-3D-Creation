import cv2
import numpy as np
from itertools import *



def recursive_loop_element(thelist, res):
   
    if not thelist:
        return res
    else:
        if isinstance(thelist[0], int):
            res.append(thelist[0])
            return recursive_loop_element(thelist[1:], res)
        elif isinstance(thelist[0], float):
            res.append(thelist[0])
            return recursive_loop_element(thelist[1:], res)
        else:
            res.extend( recursive_loop_element(thelist[0], []))
            return  recursive_loop_element(thelist[1:], res)

def verts_to_poslist(verts):
    
    list_of_elements = recursive_loop_element(verts, [])

    res = []
    i = 0
    while(i < len(list_of_elements)-1):
        res.append([list_of_elements[i],list_of_elements[i+1],list_of_elements[i+2]])
        i+= 3
    return res

def scale_point_to_vector(boxes, scale = 1, height = 0):
    
    res = []
    for box in boxes:
        for pos in box:
            res.extend([(pos[0]/scale, pos[1]/scale, height)])
    return res


def write_verts_on_2d_image(boxes, blank_image):
    

    for box in boxes:
        for wall in box:
            cv2.line(blank_image,(int(wall[0][0]),int(wall[1][1])),(int(wall[2][0]),int(wall[2][1])),(255,0,0),5)

    cv2.imshow('show image',blank_image)
    cv2.waitKey(0)

def create_nx4_verts_and_faces(boxes, height = 1, scale = 1, ground = 0):
    
    wall_counter = 0
    verts = []

    for box in boxes:
        box_verts = []
        for index in range(0, len(box) ):
            temp_verts = []
            curr = box[index][0];

            if(len(box)-1 >= index+1):
                next = box[index+1][0];
            else:
                next = box[0][0]; 

            
            temp_verts.extend([(curr[0]/scale, curr[1]/scale, ground)])
            temp_verts.extend([(curr[0]/scale, curr[1]/scale, height)])
            temp_verts.extend([(next[0]/scale, next[1]/scale, ground)])
            temp_verts.extend([(next[0]/scale, next[1]/scale, height)])

            box_verts.extend([temp_verts])

            wall_counter += 1

        verts.extend([box_verts])

    faces = [(0, 1, 3, 2)]
    return verts, faces, wall_counter

def create_verts(boxes, height, scale):
    
    verts = []

    for box in boxes:
        temp_verts = []
        for pos in box:

            temp_verts.extend([(pos[0][0]/scale, pos[0][1]/scale, 0.0)])
            temp_verts.extend([(pos[0][0]/scale, pos[0][1]/scale, height)])

        verts.extend(temp_verts)

    return verts

def write_boxes_on_2d_image(boxes, blank_image):
    

    for box in boxes:
        for index in range(0, len(box) ):

            curr = box[index][0];

            if(len(box)-1 >= index+1):
                next = box[index+1][0];
            else:
                next = box[0][0]; 

            
            cv2.line(blank_image,(curr[0],curr[1]),(next[0],next[1]),(255,0,0),5)

    cv2.imshow('show image',blank_image)
    cv2.waitKey(0)
