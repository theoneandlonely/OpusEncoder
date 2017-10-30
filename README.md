OpusEncoder

Encodes all music files in a subfolder to Opus.
Afterwards it parses these folders and creates .cue-files with the corresponding tracks if no .cue is present in the directory.

- Supported file formats:

  - Input: .wav, .flac
  - Output: .opus, 256kbit/s VBR

- Requirements:
  - Python >3.6
  - Opusenc.exe in your environment-variables

- Usage:
  - Just run the script in the folder where your music is, it parses all subfolders and processes them.
