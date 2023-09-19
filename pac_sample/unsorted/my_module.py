def mesh_collection():
    """Collect meshes from Blender"""

    import bpy  # todo move

    meshes = []
    for obj in bpy.context.selected_objects:
        if obj.type == 'MESH':
            meshes.append(obj)
    return meshes
