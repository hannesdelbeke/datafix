import bpy


def export(object):
    """Export object"""
    bpy.ops.object.select_all(action='DESELECT')
    object.select_set(True)
    bpy.ops.export_scene.obj(filepath=object.name + '.obj', use_selection=True)
    return True
