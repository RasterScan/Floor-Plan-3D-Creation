from generate import generate_all_files


def process_on_image(image_path):
    
    fpath, fshape = generate_all_files(image_path, True)
    return fpath


def multiple_simple(image_paths, horizontal=True):

    data_paths = list()
    fshape = None
    
    for image_path in image_paths:

        if fshape is not None:
            
            if horizontal:
                fpath, fshape = generate_all_files(image_path, True, position=(0,fshape[1],0))
            else:
                fpath, fshape = generate_all_files(image_path, True, position=(fshape[0],0,0))

        else:
            fpath, fshape = generate_all_files(image_path, True)

        data_paths.append(fpath)
    return data_paths


def multiple_coord(image_paths):

    data_paths = list()
    fshape = None
    
    for tup in image_paths:
        image_path = tup[0]
        pos = tup[1]

        if pos is not None:
            fpath, fshape = generate_all_files(image_path, True, position=(pos[0],pos[1],pos[2]))
        else:
            if fshape is not None:
                fpath, fshape = generate_all_files(image_path, True, position=(fshape[0],fshape[1],fshape[2]))
            else:
                fpath, fshape = generate_all_files(image_path, True)

        data_paths.append(fpath)
    return data_paths
