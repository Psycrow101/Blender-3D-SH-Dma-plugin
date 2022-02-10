import bpy
from . dma import DMA, DMAChunk, DMAction, DMATarget, DMAFrame, DMA_CHUNK_ID, DMA_CHUNK_VERSION, DMA_ANIM_VERSION


def invalid_active_object(self, context):
    self.layout.label(text='You need to select the mesh to export animation')


def missing_action(self, context):
    self.layout.label(text='No action for active mesh data. Nothing to export')


def missing_key_blocks(self, context):
    self.layout.label(text='No key blocks for active mesh data. Nothing to export')


def create_dma_action(act, targets, fps):
    for target_index, kf in enumerate(act.fcurves):
        keyframes = sorted([kp.co for kp in kf.keyframe_points])
        keyframes_num = len(keyframes)

        for i, (time, val) in enumerate(keyframes[:-1]):
            next_frame = i + 1
            next_time, next_val = keyframes[next_frame]
            duration = (next_time - time) / fps

            dmf = DMAFrame(val, next_val, duration, 1.0 / duration, next_frame)
            targets[target_index].frames.append(dmf)

    return DMAction(DMA_ANIM_VERSION, 0, targets)


def save(context, filepath, fps):
    mesh_obj = context.view_layer.objects.active
    if not mesh_obj or type(mesh_obj.data) != bpy.types.Mesh:
        context.window_manager.popup_menu(invalid_active_object, title='Error', icon='ERROR')
        return {'CANCELLED'}

    act = None
    animation_data = mesh_obj.data.shape_keys.animation_data
    if animation_data:
        act = animation_data.action

    if not act:
        context.window_manager.popup_menu(missing_action, title='Error', icon='ERROR')
        return {'CANCELLED'}

    targets = None
    shape_keys = mesh_obj.data.shape_keys
    if shape_keys:
        targets = [DMATarget([]) for kb in mesh_obj.data.shape_keys.key_blocks if kb.name != 'Basis']

    if not targets:
        context.window_manager.popup_menu(missing_key_blocks, title='Error', icon='ERROR')
        return {'CANCELLED'}

    dma_act = create_dma_action(act, targets, fps)
    dma = DMA([DMAChunk(DMA_CHUNK_ID, DMA_CHUNK_VERSION, dma_act)])
    dma.save(filepath)

    return {'FINISHED'}
