import os
import sys
import bpy
from pathlib import Path
from mathutils import Euler, Vector


class RasterScanGenerator:

    def __init__(self) -> None:

        self.active_object = None
        self.image = None
        self.scale_factor = None
        self.args = {}

        self.parse_args()

        self.file_path: Path = Path(self.args['path'])

        self.image_name = self.file_path.name
        self.image_title = os.path.splitext(self.image_name)[0]

    def parse_args(self):
        args: list = sys.argv
        
        args: list[str] = args[args.index('--') + 1:]
        
        for idx, item in enumerate(args):
            if '--' in item:
                arg_name = item.replace('--', '')
                self.args[arg_name] = args[idx + 1]

        print(self.args)

    @staticmethod
    def select_and_make_active(ob: bpy.types.Object):

        for object in bpy.data.objects:
            object.select_set(False)

        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob

    @staticmethod
    def get_mesh(mesh_name) -> bpy.types.Mesh | None:
        return bpy.data.meshes.get(mesh_name)

    @staticmethod
    def get_image(image_name: str) -> bpy.types.Image | None:
        return bpy.data.images.get(image_name)

    @staticmethod
    def create_collection(collection_name, parent=None) -> bpy.types.Collection:

        if collection_name in bpy.data.collections:
            return

        collection = bpy.data.collections.new(collection_name)

        if parent:
            bpy.data.collections[parent].children.link(collection)
            return collection
        else:
            bpy.context.scene.collection.children.link(collection)
            return collection

    @staticmethod
    def add_to_collection(ob: bpy.types.Object, collection: str) -> None:
        bpy.data.collections[collection].objects.link(ob)

    def create_object(self, name, mesh, collection='Planes'):

        ob = bpy.data.objects.new(name, mesh)

        self.add_to_collection(ob, collection)

        return ob

    def create_material(self, rgb):
        mat = bpy.data.materials.new(name="MaterialName")
        mat.diffuse_color = rgb
        return mat

    def set_variables(self):

        global_var = bpy.data.objects["GLOBALVAR"]
        modifier = global_var.modifiers['GeometryNodes']
        modifier["Input_2"] = float(self.args['wall_height'])

        global_var.data.update()

    def set_image(self):

        bpy.ops.object.load_reference_image(
            filepath=self.file_path.as_posix(),
            view_align=False)

        reference_image: bpy.types.Object = bpy.context.active_object

        reference_image.empty_display_size = 1

        self.image = reference_image.data

    def image_to_gpencil(self):

        bpy.ops.gpencil.trace_image(
            target='NEW',
            thickness=1,
            resolution=20,
            scale=1,
            # sample= 0.1,
            threshold=0.5,
            turnpolicy='BLACK',
            mode='SINGLE',
            use_current_frame=True)

        self.active_object = bpy.data.objects['GPencil']

    def get_image_space(self):

        image = self.image

        image_x, image_y = image.size

        if image_x == image_y:
            ratio = 1 / image_x
            normalizer = Vector((ratio, ratio))
            center_vector = Vector((0.5, 0.5)) * Vector((1, image_y / image_x))

        elif image_x > image_y:
            ratio = 1 / image_x
            normalizer = Vector((ratio, ratio))
            center_vector = Vector((0.5, 0.5)) * Vector((1, image_y / image_x))

        else:
            ratio = 1 / image_y
            normalizer = Vector((ratio, ratio))
            center_vector = Vector((0.5, 0.5)) * Vector((image_x / image_y, 1))

        return ratio, normalizer, center_vector, image_y

    @staticmethod
    def context_override():

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        area_override = area
                        region_override = region
                        return area_override, region_override
        else:
            return None, None

    def strokes_to_object(self):

        self.select_and_make_active(self.active_object)

        area_override, region_override = self.context_override()

        with bpy.context.temp_override(area=area_override, region=region_override):
            bpy.ops.gpencil.editmode_toggle()
            bpy.ops.gpencil.select_all(action='SELECT')
            bpy.ops.gpencil.stroke_simplify(factor=0.005)
            bpy.ops.gpencil.editmode_toggle()
            bpy.ops.gpencil.convert(type='POLY', timing_mode='LINEAR', use_timing_data=False)

        bpy.ops.object.select_all(action='DESELECT')

        self.active_object = ob = bpy.data.objects['Trace']

        self.select_and_make_active(ob)

        bpy.ops.transform.resize(
            value=(0.978478, 0.978478, 0.978478),
            orient_type='GLOBAL',
            orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            orient_matrix_type='GLOBAL',
        )

        scale_factor = self.scale_factor if self.scale_factor else 20

        bpy.ops.transform.resize(
            value=(scale_factor, scale_factor, scale_factor),
            orient_type='GLOBAL',
            orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            orient_matrix_type='GLOBAL',
        )

        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    def add_nodes(self):

        ob = bpy.data.objects['Trace']
        name = 'base'

        modifier = ob.modifiers.new(name, 'NODES')

        walls_node_group = bpy.data.node_groups["wall2"]
        modifier.node_group = walls_node_group

        modifier["Input_6"] = bpy.data.materials[self.args['wall_material']]

    def export(self):

        bpy.ops.object.select_all(action='DESELECT')

        model_export: bpy.types.Object = bpy.data.objects.get('Trace')
        model_export.select_set(True)

        glb_path: Path = self.file_path.parent / f'{self.image_title}.glb'
        bpy.ops.export_scene.gltf(filepath=glb_path.as_posix(), use_selection=True, export_apply=True)

        fbx_path: Path = self.file_path.parent / f'{self.image_title}.fbx'
        bpy.ops.export_scene.fbx(filepath=fbx_path.as_posix(), use_selection=True, use_mesh_modifiers = True)

        obj_path: Path = self.file_path.parent / f'{self.image_title}.obj'
        bpy.ops.export_scene.obj(filepath=obj_path.as_posix(), use_selection=True, use_mesh_modifiers = True)

        stl_path: Path = self.file_path.parent / f'{self.image_title}.stl'
        bpy.ops.export_mesh.stl(filepath=stl_path.as_posix(), use_selection=True, use_mesh_modifiers = True)

    def render(self):
        print('[ Rendering in Blender]')

        print("1. Set variables")
        self.set_variables()

        print("2. Set input image")
        self.set_image()

        print("3. Convert image to gpencil")
        self.image_to_gpencil()

        print("4. Stroke to object")
        self.strokes_to_object()

        print("5. Add nodes")
        self.add_nodes()

        print("6. Export Files")
        self.export()


runner = RasterScanGenerator()
runner.render()
