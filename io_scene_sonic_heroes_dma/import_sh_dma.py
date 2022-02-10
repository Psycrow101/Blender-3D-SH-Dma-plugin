import bpy
from os import path
from . dma import DMA


def invalid_active_object(self, context):
    self.layout.label(text='You need to select the mesh to import animation')


def invalid_sk_number(self, context):
    self.layout.label(text='Invalid number of Shape Keys')


def create_action(mesh_obj, dma_act, fps):
    current_time = 0.0
    act = bpy.data.actions.new('action')
    for t, dmt in enumerate(dma_act.targets):
        target_name = mesh_obj.data.shape_keys.key_blocks[t + 1].name
        fcu = act.fcurves.new(data_path=('key_blocks["%s"].value' % target_name), index=0)
        current_time = 0.0
        for dmf in dmt.frames:
            fcu.keyframe_points.insert(current_time * fps, dmf.start_val, options={'FAST'})
            current_time += dmf.duration
        fcu.keyframe_points.insert(current_time * fps, dmt.frames[-1].end_val, options={'FAST'})
    return act, current_time * fps


def load(context, filepath, *, fps):
    mesh_obj = context.view_layer.objects.active
    if not mesh_obj or type(mesh_obj.data) != bpy.types.Mesh:
        context.window_manager.popup_menu(invalid_active_object, title='Error', icon='ERROR')
        return {'CANCELLED'}

    dma = DMA.load(filepath)
    if not dma.chunks:
        return {'CANCELLED'}

    animation_data = mesh_obj.data.shape_keys.animation_data
    if not animation_data:
        animation_data = mesh_obj.data.shape_keys.animation_data_create()

    for chunk in dma.chunks:
        if len(mesh_obj.data.shape_keys.key_blocks) != len(chunk.action.targets) + 1:
            context.window_manager.popup_menu(invalid_sk_number, title='Error', icon='ERROR')
            return {'CANCELLED'}

        act, act_duration = create_action(mesh_obj, chunk.action, fps)
        act.name = path.basename(filepath)
        animation_data.action = act

    context.scene.frame_start = 0
    context.scene.frame_end = act_duration

    return {'FINISHED'}
