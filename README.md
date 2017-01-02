# oppai-chunks
http://rarelyupset.com/oppai/

Calculate the difficulty over time of a beatmap with moving windows.

Runs on Python 3 and uses [oppai](https://github.com/Francesco149/oppai)

## Usage:

### From the command line
`./oppai_chunks.py beatmap [window [step]]`

`beatmap` is the .osu file you want to analyze.
`window` is the window size to use, in milliseconds.

`step` is the step size to use, in milliseconds.

For example, `./oppai_chunks.py "haitai.osu" 12000 2000` will calculate the difficulty from 0:00 to 0:12, then 0:02 to 0:14, and so on.

### As a python module
```
from oppai_chunks import oppai
...
oppai(beatmap, window=30000, step=5000)
```
The arguments are the same as above. Here, the beatmap can be given as a path (`oppai('/path/to/beatmap.osu')`), or as the contents of an opened file (`oppai(file.read())`, `oppai(file.readlines())`). The output is a list of `(time, overall stars, aim stars, speed stars)` tuples.
