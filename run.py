import bpy
import numpy as np
import json
import sys
import math


def read_from_file(file_path):
    with open(file_path + '.txt', 'r') as f:
        data = json.loads(f.read())
    return data


def init_object(name):
    mymesh = bpy.data.meshes.new(name)
    myobject = bpy.data.objects.new(name, mymesh)
    bpy.context.collection.objects.link(myobject)
    return myobject, mymesh


def average(lst):
    return sum(lst) / len(lst)


def get_mesh_center(verts):
    x = []
    y = []
    z = []

    for vert in verts:
        x.append(vert[0])
        y.append(vert[1])
        z.append(vert[2])

    return [average(x), average(y), average(z)]


def subtract_center_verts(verts1, verts2):
    for i in range(0, len(verts2)):
        verts2[i][0] -= verts1[0]
        verts2[i][1] -= verts1[1]
        verts2[i][2] -= verts1[2]
    return verts2


def create_custom_mesh(objname, verts, faces, pos=None, rot=None, mat=None, cen=None):
    myobject, mymesh = init_object(objname)

    center = get_mesh_center(verts)

    proper_verts = subtract_center_verts(center, verts)

    mymesh.from_pydata(proper_verts, [], faces)

    mymesh.update(calc_edges=True)

    parent_center = [0, 0, 0]
    if cen is not None:
        parent_center = [int(cen[0] / 2), int(cen[1] / 2), int(cen[2])]

    myobject.location.x = center[0] - parent_center[0]
    myobject.location.y = center[1] - parent_center[1]
    myobject.location.z = center[2] - parent_center[2]

    if pos is not None:
        myobject.location.x += pos[0]
        myobject.location.y += pos[1]
        myobject.location.z += pos[2]

    if rot is not None:
        myobject.rotation_euler = rot

    if mat is None:
        myobject.data.materials.append(create_mat([10, 10, 128, 0.2]))  # add the material to the object

    # else:
    # myobject.data.materials.append(mat)
    return myobject


def create_mat(rgb_color):
    mat = bpy.data.materials.new(name="MaterialName")
    mat.diffuse_color = rgb_color
    return mat


def create_floor_plan():
    parent, parent_mesh = init_object("Floorplan" + str(0))

    path_to_wall_faces_file = "E:/RasterScan/Floor-Plan-3D-Creation/temp/" + "wall_faces"
    path_to_wall_verts_file = "E:/RasterScan/Floor-Plan-3D-Creation/temp/" + "wall_verts"

    path_to_floor_faces_file = "E:/RasterScan/Floor-Plan-3D-Creation/temp/" + "floor_faces"
    path_to_floor_verts_file = "E:/RasterScan/Floor-Plan-3D-Creation/temp/" + "floor_verts"

    path_to_rooms_faces_file = "E:/RasterScan/Floor-Plan-3D-Creation/temp/" + "rooms_faces"
    path_to_rooms_verts_file = "E:/RasterScan/Floor-Plan-3D-Creation/temp/" + "rooms_verts"

    path_to_transform_file = "E:/RasterScan/Floor-Plan-3D-Creation/temp/" + "transform"

    transform = read_from_file(path_to_transform_file)

    rot = transform["rotation"]
    pos = transform["position"]

    cen = transform["shape"]

    parent.rotation_euler = (0, math.pi, 0)

    bpy.context.scene.cursor.location = (0, 0, 0)

    verts = read_from_file(path_to_wall_verts_file)
    faces = read_from_file(path_to_wall_faces_file)

    boxcount = 0
    wallcount = 0

    wall_parent, wall_parent_mesh = init_object("Walls")

    for box in verts:
        boxname = "Box" + str(boxcount)
        for wall in box:
            wallname = "Wall" + str(wallcount)

            obj = create_custom_mesh(boxname + wallname, wall, faces, pos=pos, rot=rot, cen=cen)
            obj.parent = wall_parent

            wallcount += 1
        boxcount += 1

    wall_parent.parent = parent

    verts = read_from_file(path_to_floor_verts_file)
    faces = read_from_file(path_to_floor_faces_file)

    cornername = "Floor"
    obj = create_custom_mesh(cornername, verts, [faces], pos=pos, mat=create_mat((90, 90, 90, 1)), cen=cen)
    obj.parent = parent

    verts = read_from_file(path_to_rooms_verts_file)
    faces = read_from_file(path_to_rooms_faces_file)

    room_parent, room_parent_mesh = init_object("Rooms")

    for i in range(0, len(verts)):
        roomname = "Room" + str(i)
        obj = create_custom_mesh(roomname, verts[i], faces[i], pos=pos, rot=rot, cen=cen)
        obj.parent = room_parent

    room_parent.parent = parent


def main(argv):
    objs = bpy.data.objects
    objs.remove(objs["Cube"], do_unlink=True)

    create_floor_plan()

    bpy.ops.wm.save_as_mainfile(filepath="E:/3D_Mesh.blend")

    exit(0)


if __name__ == "__main__":
    main(sys.argv)


