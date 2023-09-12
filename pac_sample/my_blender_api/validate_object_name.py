try:
    import bpy
except:
    pass


def main(object, name):
    """check if object name matches a string"""
    return object.name == name
