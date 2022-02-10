import bpy
from bpy.props import (
        StringProperty,
        FloatProperty,
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        )

bl_info = {
    "name": "Sonic Heroes Delta Morph Animation",
    "author": "Psycrow",
    "version": (0, 0, 1),
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

    fps: FloatProperty(
        name="FPS",
        description="Value by which the keyframe time is divided",
        default=30.0,
    )

    def execute(self, context):
        from . import export_sh_dma

        keywords = self.as_keywords(ignore=("filter_glob",
                                            ))

        return export_sh_dma.save(context, keywords['filepath'], keywords['fps'])


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
