[![en](https://img.shields.io/badge/lang-en-red.svg)](README.md)
[![kr](https://img.shields.io/badge/lang-kr-green.svg)](README.kr.md)

> This document was translated from Korean to English with the help of ChatGPT.<br>
> If you find any mistranslations or unclear expressions, please feel free to open an issue.

---

# UWDTool
A tool for extracting, packing, or inspecting the contents of data files used in Unity WebGL games, including assets and other related resources.

## What Is UnityWebData
A UnityWebData file is a file that is loaded and used in conjunction with a WebAssembly file in a WebGL game, primarily a file that combines all of the asset, resource, and metadata files.

## Installation and Usage
### Installation
```
pip install uwdtool
```

### CLI
```
uwdtool [-h] [-p | -u | -isp] [-i ARG_INPUT] [-o ARG_OUTPUT] [-c {brotli,gzip,none}]
```

* `-h`, `--help`: Displays help and information about the program.

* `-p`, `--pack`: Packs the files in the specified input directory into a UnityWebData file and saves it to the output path.  
  The input should be the path to the folder containing the files to pack.
* `-u`, `--unpack`: Unpacks the specified UnityWebData file and saves the extracted files to the output directory.  
  The input should be the path to the file to unpack, and the output should be the target folder for the extracted files.
* `-isp`, `--inspect`: Displays information about the contents of a UnityWebData file, including file names and sizes.  
  Only the input file is required; the output path is not needed.

* `-c`: Specifies the compression format.  
  Available options are `brotli`, `gzip`, or `none`.  
  If omitted, the format is automatically detected.

## What is a UnityWebData File?

A UnityWebData file is a bundled resource file used in Unity WebGL games, loaded alongside the WASM file. It typically contains assets, resources, and metadata packed into a single file.

In Unity versions 5.0 through 2019, these files used the `.unityweb` extension. Starting with later versions, the extension changed to `.data`. Unity supports compression formats like gzip and Brotli during the build process. Since 2019, the file extension itself (e.g., `.data.gz` or `.data.br`) indicates the compression format, making it easy to determine how to decompress it. However, in earlier versions, the `.unityweb` extension was used regardless of compression type, so the engine had to rely on markers inside the file to determine whether and how the data was compressed.

Importantly, once decompressed, the internal structure of a UnityWebData file is consistent regardless of its compression status.

## UnityWebData Structure
![unitywebdata_format.png](img/unitywebdata_format.png)

### Header
| Name          | Size (bytes) | Type    | Description                                                                 |
|---------------|--------------|---------|-----------------------------------------------------------------------------|
| Signature     | 16           | string  | Fixed string: `"UnityWebData1.0\0"`                                        |
| File Table Offset | 4        | uint32  | Offset to the start of the file data section (same as the first file's offset) |

### File Info Header  
The following structure is repeated for each file, up until the file data section begins:

| Name           | Size (bytes) | Type    | Description                          |
|----------------|--------------|---------|--------------------------------------|
| File Offset    | 4            | uint32  | Offset to the start of the file      |
| File Size      | 4            | uint32  | Size of the file in bytes            |
| Filename Length| 4            | uint32  | Length of the file name (n)          |
| Filename       | n            | string  | Name of the file                     |

### File Data Section  
After the headers, all the actual file contents are stored sequentially.  
To read a specific file, locate its offset and size from the header, then read the corresponding byte range from the data section.

## Binary Template for 010 Editor  
![uwd010template.png](img/uwd010template.png)  
<https://gist.github.com/akio7624/908497ef15a84a436fae9ab5439aa01f>

This is a custom binary template for UnityWebData files, designed for use with 010 Editor's binary template system. It provides a visual representation of the internal structure, making it easier to analyze and understand the contents of a UnityWebData file.

If the data file is compressed, you must decompress it before analysis.

## Other  
The Python module that includes the feature to compress with Brotli, including comments, was built using the code from [this link](https://github.com/Unity-Technologies/brotli/tree/5a6d5d9c7f3f813280900cabcaabcbd0d51d5bbc).