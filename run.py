from pathlib import Path
import argparse
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=str, help="full path of the image file")
    args = parser.parse_args()

    src_file = args.image
    render(src_file)

