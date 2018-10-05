# Blender Preflight

The goal of this project is to script the export of `.blend` files to `.fbx` assets for simpler use in Unity (or other game engines). By taking advantage of the scriptable nature of Blender, we can iterate through a well-structured `.blend` file and automate the tedious process of exporting with the correct settings.

## CLI Usage

Preflight can also be done from the command line. While the operation itself is available with the `bpy.ops.preflight.export_groups()` method, it is easier to simply pass a python script to blender along with a `.blend` file. Usage for the bundled script is:

```
$ blender test/Preflight\ Test.blend -b --python cli/preflight_blendfile.py
```

This script also accepts two arguments:

```
--fbx-output {output_directory}
--export-animations
```

These arguments will temporarily override the settings inside the `.blend` file for all export groups, but will not change the data stored in the `.blend` file permanently.

---

# Built by Apsis

[![apsis](https://s3-us-west-2.amazonaws.com/apsiscdn/apsis.png)](https://www.apsis.io)

`fbx_preflight` was built by Apsis Labs. We love sharing what we build! Check out our [other libraries on Github](https://github.com/apsislabs), and if you like our work you can [hire us](https://www.apsis.io/work-with-us/) to build your vision.
