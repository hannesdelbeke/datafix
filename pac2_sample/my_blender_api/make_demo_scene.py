import bpy


def create_env():
    # Clear existing mesh objects
    #bpy.ops.wm.open_mainfile(filepath=bpy.data.filepath, display_warning=False)

    # Create the grass (large green flat cube)
    bpy.ops.mesh.primitive_plane_add(size=10, enter_editmode=False, align='WORLD', location=(0, 0, 0))
    grass = bpy.context.active_object
    grass.name = "Grass"
    grass.data.materials.append(bpy.data.materials.new(name="Green"))
    grass.active_material.diffuse_color = (0.6, 1, 0.1, 1)  # Set material color to green

    # Create the tree (long brown trunk with a green cube on top)
    bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 1))
    trunk = bpy.context.active_object
    trunk.scale = (0.3, 0.3, 2)  # Adjust the scale for the trunk
    trunk.name = "Tree_Trunk"
    trunk.data.materials.append(bpy.data.materials.new(name="Brown"))
    trunk.active_material.diffuse_color = (0.4, 0.2, 0, 2)  # Set material color to brown

    bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 2))
    leaves = bpy.context.active_object
    leaves.scale = (1, 1, 1)  # Adjust the scale for the leaves
    leaves.name = "Tree_Leaves"
    leaves.data.materials.append(bpy.data.materials.new(name="Green"))
    leaves.active_material.diffuse_color = (0, 0.6, 0, 1)  # Set material color to green

    # Select and join the tree parts into a single object
    trunk.select_set(True)
    leaves.select_set(True)
    bpy.context.view_layer.objects.active = trunk
    bpy.ops.object.join()

    # Set the origin of the tree to the bottom of the trunk
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')

    # Set the tree's location
    trunk.location = (4, 0, 1.5)


def create_char():
    # Create the character mesh (a cube in this example)
    bpy.ops.mesh.primitive_cube_add(size=1, align='WORLD', location=(0, 0, 0))
    character = bpy.context.active_object
    character.name = "Character"

    # Create the armature
    bpy.ops.object.armature_add(align='WORLD', location=(0, 0, 0))
    armature = bpy.context.active_object
    armature.name = "Armature"

    # Enter Edit Mode for the armature to add bones
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')

    # Create the root bone (spine)
    root_bone = armature.data.edit_bones.new("Root")
    root_bone.head = (0, 0, 0)
    root_bone.tail = (0, 0, 1)

    # Create additional bones (e.g., limbs, head, etc.) and connect them as needed
    # Example: Creating a leg bone
    leg_bone = armature.data.edit_bones.new("Leg")
    leg_bone.head = (0, 0, 1)
    leg_bone.tail = (0, 0, 2)
    leg_bone.parent = root_bone  # Connect the leg bone to the root bone

    # Example: Creating an arm bone
    arm_bone = armature.data.edit_bones.new("Arm")
    arm_bone.head = (0, 0, 1)
    arm_bone.tail = (0, 0, 2)
    arm_bone.parent = root_bone  # Connect the arm bone to the root bone

    # Exit Edit Mode for the armature
    bpy.ops.object.mode_set(mode='OBJECT')

    # Parent the character mesh to the armature (with automatic weights)
    character.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')

    # Set the armature as the character's armature
    character.modifiers.new("Armature", 'ARMATURE').object = armature

    # Adjust the character's scale and position as needed
    character.scale = (1, 1, 2)  # Example: Scaling the character in the Z-axis to make it taller
    character.location = (0, 0, 0)  # Example: Repositioning the character


def setup_render():
    # Create a camera and set its position
    bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(6, -6, 6))
    camera = bpy.context.active_object
    bpy.context.scene.camera = camera
    camera.rotation_euler = (1.0, 0.0, 0.8)  # Adjust camera rotation

    # Create a light source
    bpy.ops.object.light_add(type='SUN', radius=1, align='WORLD', location=(6, -6, 8))

    # Set the render resolution
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080

    # Set the render engine to Cycles
    bpy.context.scene.render.engine = 'CYCLES'

    # Set the number of render samples
    bpy.context.scene.cycles.samples = 100

    # Set the output format and path
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.filepath = "/path/to/render_output.png"

    # Render the scene
    # bpy.ops.render.render(write_still=True)

