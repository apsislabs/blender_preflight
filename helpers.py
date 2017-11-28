import bpy

def group_is_valid(group):
    if not group.name:
        return False
    if len(group.obj_names) < 1:
        return False

    for obj in group.obj_names:
        if not obj.obj_name:
            return False
        if bpy.data.objects.get(obj.obj_name) is None:
            return False

    return True

def groups_are_valid(groups):
    return (len(groups) > 0) and groups_are_unique(groups)

def groups_are_unique(groups):
    group_names = [group.name for group in groups]
    return len(group_names) == len(set(group_names))
