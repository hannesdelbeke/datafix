# class collect_meshes_blender():
#     def run(self):
#         """Collect meshes from Blender"""
#         meshes = []
#         for obj in bpy.context.selected_objects:
#             if obj.type == 'MESH':
#                 meshes.append(obj)
#         return meshes
#
#
# class validate_meshes_vertcount():
#     def run(self):
#         """Validate meshes have the correct number of vertices"""
#         for mesh in meshes:
#             if len(mesh.data.vertices) < 3:
#                 return False
#         return True


# class validate_meshes_vertcount_dependant():
#     def run(self):
#         """Validate meshes have the correct number of vertices"""
#         for mesh in meshes:
#             if len(mesh.data.vertices) < 3:
#                 return False
#         return True
