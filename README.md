# oppai-chunks
http://rarelyupset.com/oppai/

Calculate the difficulty over time of a beatmap with moving windows.

Requires Python 3 and omkelderman's oppai [json fork](https://github.com/omkelderman/oppai/tree/json-output)

## Usage:

### From the command line
`./oppai_chunks.py beatmap [window [step]]`
`beatmap` is the .osu file you want to analyze.
`window` is the window size to use, in milliseconds.
`step` is the step size to use, in milliseconds.

### As a python module
```
from oppai_chunks import oppai
...
oppai(beatmap, window=30000, step=5000)
```
The arguments are the same as above. Here, the beatmap can be given as a path (`oppai('/path/to/beatmap.osu')`), or as the contents of an opened file (`oppai(file.read())`, `oppai(file.readlines())`)