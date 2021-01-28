# fbx-converter

This tool was designed to handle artwork from the recently released [suicide-barbie demo](https://github.com/theblacklotus/suicide-barbie).
Unfortunately, these files are old and [Blender](https://www.blender.org/) is unable to load the respective FBX version 6100.
Instead, Blender uses FBX version 7100 by default.

I needed a tool so I could import the old FBX files into Blender.
This tool converts the FBX version 6100 files to FBX version 7100, so they can be imported by Blender.

**Results**

![Screenshot of suicide-barbie artwork in Blender](https://user-images.githubusercontent.com/360330/106110590-3552ea80-614b-11eb-87b8-1b8da3ea93c8.png)


**Alternatives**

At the time, I wasn't aware of the [Autodesk FBX Converter](https://www.autodesk.com/developer-network/platform-technologies/fbx-converter-archives), which might also work.
There are also other tools, but they all depend on the FBX SDK, and they typically [convert to other formarts (like glTF)](https://github.com/cyrillef/FBX-glTF).

However, this tool provides a full Open-Source solution to the problem.
Therefore, with more work, this conversion step could also be part of the Blender importer / exporter.


## Supported features

Many bugs exist, because this tool was only tested with a small set of test files from one source.
However, the following features should work reasonably well:


*All features that are not listed are implicitly unsupported.*

- Textures
- Meshes
- Cameras
- Skeleton / Idle Pose

**Explicitly Unsupported**

- Animations / Takes
- Lights


The generated files have only been tested with Blender 2.91.
It's very possible that the output is malformed; support with other FBX tools might be limited.


## Requirements

- [Python 3.x](https://www.python.org/)
- [Blender `io_scene_fbx` addon source-code](https://github.com/blender/blender-addons/tree/master/io_scene_fbx) (used for FBX parsing)


## Usage

[Download a ZIP](https://github.com/JayFoxRox/fbx-converter/archive/master.zip) or clone this repository:

```
git clone https://github.com/JayFoxRox/fbx-converter.git
```

Modify the source-code in convert.py:

- `BLENDER_FBX_PATH` must point to the Blender `io_scene_fbx` addon folder (example: "/usr/share/blender/2.91/scripts/addons/io_scene_fbx/")
- `TMP_PATH_FBX` must point to a temporary filename for an .fbx file

To upgrade a file, simply run the script:

```
./convert.py ~/suicide-barbie/exgirl1/exgirl1.fbx 
```


## Development

Pull requests of any kind are welcome!

For debugging the output, you can use tools provided by Blender:

```
python3 /usr/share/blender/2.91/scripts/addons/io_scene_fbx/fbx2json.py fbx.fbx 
```


## License

The code is licensed under GPLv2 or any later version.
Other license options can be provided on request.
