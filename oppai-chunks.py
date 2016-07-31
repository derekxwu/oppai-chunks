#!/usr/bin/python3
"""oppai-chunks

 Moving-window difficulty calculation for osu beatmaps.
 Intended for mappers to check difficulty spikes/dips.

 Run in CLI as ./oppai-chunks.py <path_to_beatmap>
 Import oppai() and run oppai('path_to_beatmap')
"""
import codecs
import json
import subprocess
import sys
import tempfile


def print_usage():
    """Instructions on using the script
    """
    print(
        "oppai-chunks.py\n"
        "Usage: ./oppai-chunks.py <beatmap>\n"
        "<beatmap> is a .osu file for a specific difficulty.\n"
        "You can unzip a .osz file to extract the .osu files.\n"
    )


def oppai(bmname):
    """Open beatmap and process

    Runs oppai on chunks (30sec) of the beatmap at regular intervals (5sec).

    Arguments:
        bmname {str} -- Path to beatmap

    Returns:
        list -- A list of tuples for each chunk formatted as follows:
        (chunk start time (ms), overall stars, aim stars, speed stars)
    """

    # Very efficient parsing
    # I think it's awful please contribute anything better
    # For a challenge, keep pylint happy while you do it
    try:
        with codecs.open(bmname, 'r', 'utf-8') as file:
            bmap = file.readlines()
    except IOError:
        print("Error opening file: {}".format(bmname))
        sys.exit()

    # Split into hitcircles and not hitcircles
    metadata = bmap[:bmap.index('[HitObjects]\r\n')]
    bmap = bmap[bmap.index('[HitObjects]\r\n') + 1:]

    bm_info = {}

    # This is the awful part
    bm_info['Title'] = [x for x in metadata if x.startswith('Title:')]
    bm_info['Artist'] = [x for x in metadata if x.startswith('Artist:')]
    bm_info['Mapper'] = [x for x in metadata if x.startswith('Creator:')]
    bm_info['Diff name'] = [x for x in metadata if x.startswith('Version:')]
    bm_info['HP'] = [x for x in metadata if x.startswith('HPDrainRate:')]
    bm_info['CS'] = [x for x in metadata if x.startswith('CircleSize:')]
    bm_info['OD'] = [x for x in metadata if x.startswith('OverallDifficulty:')]
    bm_info['AR'] = [x for x in metadata if x.startswith('ApproachRate:')]
    bm_info['SV'] = [x for x in metadata if x.startswith('SliderMultiplier:')]
    bm_info['TR'] = [x for x in metadata if x.startswith('SliderTickRate:')]

    if [] in bm_info.values():
        for field in [x for x in bm_info if bm_info[x] == []]:
            print("Error: Missing beatmap info: {}".format(field))
            print("\tTry resaving the beatmap from the osu editor.")
        sys.exit(1)

    # Recover from using a list comprehension for everything
    for key in bm_info:
        bm_info[key] = bm_info[key][0]

    # The one line with a guaranteed position
    bm_info['format_ver'] = metadata[0]

    # Compose the necessary heading parts to keep oppai happy
    # and enable difficulty calculation
    bm_head = ''.join((bm_info['format_ver'],
                       '[General]\r\n',
                       '[Metadata]\r\n',
                       bm_info['Title'],
                       bm_info['Artist'],
                       bm_info['Mapper'],
                       bm_info['Diff name'],
                       '[Difficulty]\r\n',
                       bm_info['HP'],
                       bm_info['CS'],
                       bm_info['OD'],
                       bm_info['AR'],
                       bm_info['SV'],
                       bm_info['TR'],
                       '[TimingPoints]\r\n',
                       '[HitObjects]\r\n'))

    results = []  # Array of (time, stars, aim stars, speed stars) tuples
    seek = 0  # Time in ms
    with tempfile.TemporaryDirectory() as tmpdir:
        while bmap:
            # 30 second window size
            # TODO: Make this configurable
            out = ''.join(
                [x for x in bmap if int(x.split(',')[2]) < seek + 30000])

            with open(tmpdir + '/tmp.osu', 'w') as tmp:
                tmp.write(bm_head + out)

            # Use omkelderman's json-output fork of oppai
            # https://github.com/omkelderman/oppai/tree/json-output
            # TODO: Of course, make the oppai path configurable
            oppai_out = subprocess.check_output(
                ["oppai", tmpdir + '/tmp.osu'])
            oppai_out = json.loads(oppai_out.decode())

            results.append((seek,
                            float(oppai_out['stars']),
                            float(oppai_out['aim_stars']),
                            float(oppai_out['speed_stars'])))

            # Move in 5-second steps
            # TODO: Make this configurable too
            seek = seek + 5000
            bmap = [x for x in bmap if int(x.split(',')[2]) > seek]

    return results


def main():
    """oppai-chunks from CLI

    Prints table of time|stars|aim|speed when run
    ./oppai-chunks.py beatmap.osu
    """
    if len(sys.argv) != 2 or not sys.argv[1].endswith('.osu'):
        print_usage()
        sys.exit()

    print("Analyzing \"{}\"...".format(sys.argv[1]))

    results = oppai(sys.argv[1])

    print("Time\tOverall\tAim\tSpeed")
    for chunk in results:
        print("{}\t{}\t{}\t{}".format(*chunk))

if __name__ == '__main__':
    main()
