from pathlib import Path
import shlex
import subprocess


def render(src_file):

    command = f"""
        blender -b asset.blend -P render.py --
        --path {src_file}
        --wall_height {3}
        --wall_material {shlex.quote('Sherwin Williams Eider white Walls')}
        """

    subprocess.run(shlex.split(command))

    print("Done.")


if __name__ == "__main__":
    src_file = "D:/RasterScan/Floor-Plan-3D-Creation/images/img3.jpg"
    render(src_file)

