# Options - Flipnote ID

To list usage information and options, run
```sh
python3 flipnote_id.py -h
```

When the specified input path is a file, any options given are ignored, as they mostly only apply to the directory searches. Verbose output will be given and the resulting information will be printed to the terminal.

Below is a list of all options available when the input path is a directory.

Option | Function
--------|--------
`-c` | Print to the console instead of exporting to HTML files
`-ik` | Ignore KWZ files when searching through directories
`-ip` | Ignore PPM files when searching through directories
`-nr` | This program defaults to recursively searching through any found subdirectories. Pass this option to prevent recursive searching.
`-ns` | Do not copy Sudofont to the export directory. This option is not necessary if sudofont.ttf is not in the flipnote-id directory.
`-nt` | Do not extract thumbnails from Flipnotes. Useful for keeping output sizes down and for speeding up the processing.
`-o="[OUT_PATH]"` | Specify the directory to send an HTML export to. Default is the specified input path.
`-t=[TEMPLATE]` | Specify a template to be used when exporting to HTML. Default is "plain"
`-v` | Give verbose output.

