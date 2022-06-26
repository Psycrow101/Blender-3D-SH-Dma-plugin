import bpy
from bpy.props import (
        StringProperty,
        FloatProperty,
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        )
from . dma import unpack_rw_lib_id, pack_rw_lib_id

bl_info = {
    "name": "Sonic Heroes Delta Morph Animation",
    "author": "Psycrow",
    "version": (0, 0, 3),
    "blender": (2, 81, 0),
    "location": "File > Import-Export",
    "description": "Import / Export Sonic Heroes Delta Morph Animation (.dma)",
    "warning": "",
    "wiki_url": "",
    "support": 'COMMUNITY',
    "category": "Import-Export"
}

if "bpy" in locals():
    import importlib
    if "import_sh_dma" in locals():
        importlib.reload(import_sh_dma)
    if "export_sh_dma" in locals():
        importlib.reload(export_sh_dma)


class ImportSonicHeroesDma(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.sonic_heroes_dma"
    bl_label = "Import Sonic Heroes Delta Morph Animation"
    bl_options = {'PRESET', 'UNDO'}

    filter_glob: StringProperty(default="*.dma", options={'HIDDEN'})
    filename_ext = ".dma"

    fps: FloatProperty(
        name="FPS",
        description="Value by which the keyframe time is multiplied",
        default=30.0,
    )

    def execute(self, context):
        from . import import_sh_dma

        keywords = self.as_keywords(ignore=("filter_glob",
                                            ))

        return import_sh_dma.load(context, **keywords)


class ExportSonicHeroesDma(bpy.types.Operator, ExportHelper):
    bl_idname = "export_scene.sonic_heroes_dma"
    bl_label = "Export Sonic Heroes Delta Morph Animation"
    bl_options = {'PRESET'}

    filter_glob: StringProperty(default="*.dma", options={'HIDDEN'})
    filename_ext = ".dma"

    export_version: bpy.props.StringProperty(
        maxlen=7,
        default="3.5.0.0",
        name="Version Export"
    )

    fps: FloatProperty(
        name="FPS",
        description="Value by which the keyframe time is divided",
        default=30.0,
    )

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.alignment = 'CENTER'

        col.alert = not self.verify_rw_version()
        icon = "ERROR" if col.alert else "NONE"
        col.prop(self, "export_version", icon=icon)

        col = layout.column()
        col.alignment = 'CENTER'
        col.prop(self, "fps")

    def execute(self, context):
        from . import export_sh_dma

        if not self.verify_rw_version():
            self.report({"ERROR_INVALID_INPUT"}, "Invalid RW Version")
            return {'CANCELLED'}

        return export_sh_dma.save(context, self.filepath, self.get_selected_rw_version(), self.fps)

    def invoke(self, context, event):
        mesh_obj = context.view_layer.objects.active
        if mesh_obj and type(mesh_obj.data) == bpy.types.Mesh:
            shape_keys = mesh_obj.data.shape_keys
            if shape_keys:
                animation_data = shape_keys.animation_data
                if animation_data and animation_data.action and 'dragonff_rw_version' in animation_data.action:
                    rw_version = animation_data.action['dragonff_rw_version']
                    self.export_version = '%x.%x.%x.%x' % unpack_rw_lib_id(rw_version)

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def verify_rw_version(self):
        if len(self.export_version) != 7:
            return False

        for i, c in enumerate(self.export_version):
            if i % 2 == 0 and not c.isdigit():
                return False
            if i % 2 == 1 and not c == '.':
                return False

        return True

    def get_selected_rw_version(self):
        ver = self.export_version
        return pack_rw_lib_id(*map(lambda c: int('0x%c' % c, 0), (ver[0], ver[2], ver[4], ver[6])))


def menu_func_import(self, context):
    self.layout.operator(ImportSonicHeroesDma.bl_idname,
                         text="Sonic Heroes Delta Morph Animation (.dma)")


def menu_func_export(self, context):
    self.layout.operator(ExportSonicHeroesDma.bl_idname,
                         text="Sonic Heroes Delta Morph Animation (.dma)")


classes = (
    ImportSonicHeroesDma,
    ExportSonicHeroesDma,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
