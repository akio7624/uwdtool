* [한국어](README-kr.md)
* English

The tool for packing or unpacking UnityWebData files.
You can also simply check the file information that it contains.

## What Is UnityWebData
A UnityWebData file is a file that is loaded and used in conjunction with a WebAssembly file in a WebGL game, primarily a file that combines all of the asset, resource, and metadata files.

## The Struct Of UnityWebData
This section describes the structure of binary files based on UnityWebData1.0
The int value must be read in Little Endian.

### File Header
| Name | Length(byte) | Type | Description |
| :------------: | :------------: | :------------: | :------------: |
| File Signature | 16 | String | "UnityWebData1.0\0" |
| File Body Offset | 4 | int | The starting location for the entire listed file, the same as the location of the first file |

### File Information Header
The bundles below will then be repeated for each file until the file body starts.

| Name | Length(byte) | Type | Description |
| :------------: | :------------: | :------------: | :------------: |
| File Offset | 4 | int | Start offset of the file |
| File Length | 4 | int | Size of file |
| File Name Length | 4 | int | Length of file name |
| File Name | n | String | File name |

### File Body
Each file is listed immediately after the header.
If you want to read a file, you can take its offset in the header and read it from that location to the size of the file in the header.

## File Struct Image
![img_format](https://raw.githubusercontent.com/yuria0309/UWDTool/master/uwdtool/img/unitywebdata_format.png)

## Usage
```
python UWDTool.py <Control Option> [-i input_path] [-o output_path]
```

### Control Option
* -p --pack: Make the files in the input path into a UnityWebData file and save them to the output path.
The input path is the path of the folder containing the files to be packed.
* -u --unpack: Unpack the UnityWebData file in the input path and save it to the output path.
The input path is the path of the file to be unpacked, and the output path is the path of the folder where the files will be stored.
* -isp --inspect: Print information about the files that the UnityWebData file in the input path contains.
It shows the name and size of the file. No output path is required in this case.
* -h --help: Print help message and information from the program.