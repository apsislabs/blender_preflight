# Blender Preflight

The goal of this project is to script the export of `.blend` files to `.fbx` assets for simpler use in Unity (or other game engines). By taking advantage of the scriptable nature of Blender, we can iterate through a well-structured `.blend` file and automate the tedious process of exporting with the correct settings.

## Usage

```
$ blender {path_to_blendfile} -b --python blender_preflight.py
```

By default, this will output all `.fbx` files to `./preflight`, relative to your current directory. Exported files are named according to the convention: `{blendfileName}-{meshName}.fbx`, where both `blendfileName` and `meshName` are camelcase. Animations are exported according to `{blendfileName}-{armatureName}@animations.fbx`.

## Assumptions

1. Each layer in a `.blend` file will be exported as a single `.fbx`.
2. Each resulting `.fbx` will contain all associated armatures, but no animations.
3. Each armature will also be exported with all associated animations, but no meshes.

## Logic

The script processes each `.blend` file in the following steps:

1. Find each layer that has at least 1 mesh.
2. Select all objects on each relevant layer, along with their parent armatures (regardless of layer).
3. Export to FBX using only `ARMATURE` and `MESH`, without animations, and only the selected objects.
4. Iterate through each armature and export with animations.

## TODO

1. Code cleanup. The script is quite rough as is.
2. Better documentation.
3. Parent script for executing on an entire directory.