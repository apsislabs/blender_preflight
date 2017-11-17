import argparse
import bpy
import sys
import os
import re
import time

WORD_REGEX_PATTERN = re.compile("[^A-Za-z]+")

def main():
    # Setup and retrieve arguments
    time_start = time.time()
    
    parser = argparse.ArgumentParser(description='Preflight a blendfile for use in Unity')
    parser.add_argument(
        '-o', '--out',
        default='./preflight',
        help='Output path for the generated FBX.'
    )

    output_path = parser.parse_known_args()[0].out

    # Get all relevant layers
    filepath = os.path.normpath(output_path)
    basename = camelFilename(bpy.context.blend_data.filepath)
    layers = get_layers_with_content()

    output_files = []

    # Iterate and Export
    for idx, layerIdx in enumerate(layers):
        # Deselect all and select objects on layer and their armatures
        bpy.ops.object.select_by_layer(extend=False, layers=layerIdx+1)
        select_armatures_for_current_selection()

        mesh_name = name_for_selection()

        output_name = basename + "-" + mesh_name + ".fbx"
        output_name = os.path.join(filepath, output_name)
        output_dir = os.path.dirname(output_name)
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        print("\n------------------------------------------------------")
        print("Outputting file: " + output_name)
        print("------------------------------------------------------\n")
        
        try:
            export_selection(filepath=output_name)
            output_files.append(output_name)
        except:
            print("Error while attempting to write: " + output_name)

    # Report Performance
    print("\n------------------------------------------------------")
    print("Preflight Export Finished in: %.4f sec" % (time.time() - time_start))
    print("Output Files: \n\t" + "\n\t".join(output_files))

# Iterate through all named layers and
# filter to just those that have a non-default
# name.
def get_layers_with_content(sceneIndex=0):
    ret = []
    # layers = [True, True, False, True, False]
    for idx, layer in enumerate(bpy.data.scenes[sceneIndex].layers):
        if (layer == True):
            ret.append(idx)
    return ret

def name_for_selection():
    for obj in bpy.context.selected_objects:
        if (obj.type == "MESH"):
            return obj.name
    return "null"

def select_armatures_for_current_selection():
    for obj in bpy.context.selected_objects:
        if (obj.type == "MESH"):
            armature = obj.find_armature()
            if armature is not None:
                armature.select = True

def export_selection(filepath):
    bpy.ops.export_scene.fbx(
        filepath=filepath,
        axis_forward='-Z',
        axis_up='Y',
        use_selection=True,
        bake_space_transform=True,
        object_types={'ARMATURE','MESH'},
        use_armature_deform_only=True,
        bake_anim=True,
        use_anim=True
    )

def camel(chars):
  words = WORD_REGEX_PATTERN.split(chars)
  return "".join(w.lower() if i is 0 else w.title() for i, w in enumerate(words))

def camelFilename(path):
    return camel(os.path.splitext(os.path.basename(path))[0])


if __name__ == "__main__":
    main()