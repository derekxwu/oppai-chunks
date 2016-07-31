"""oppai-chunks
"""
import codecs
import os
import subprocess
import sys
import tempfile

if os.name == 'nt':
    LINE_ENDING = '\r\n'
else:
    LINE_ENDING = '\n'


def print_usage():
    """Instructions on using the script
    """
    print("Hello")


def oppai(bmname):
    """Open beatmap and process

    Opens beatmap passed as argument and runs chunks through oppai.
    Current implementation is printing to named pipe and running oppai
    several times.

    Arguments:
        bmname {str} -- Path to beatmap
    """
    try:
        with codecs.open(bmname, 'r', 'utf-8') as file:
            bmap = file.readlines()
    except EnvironmentError:
        print("Error opening file: {}".format(bmname))
        sys.exit()

    # Very efficient parsing
    metadata = bmap[:bmap.index('[HitObjects]' + LINE_ENDING)]
    bmap = bmap[bmap.index('[HitObjects]' + LINE_ENDING) + 1:]

    bm_info = {}

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
        for prop in [x for x in bm_info if bm_info[x] == []]:
            print("Error: Missing beatmap info: {}".format(prop))
        sys.exit()
    for key in bm_info:
        bm_info[key] = bm_info[key][0]

    bm_info['format_ver'] = metadata[0]

    bm_head = ''.join((bm_info['format_ver'],
                       '[General]' + LINE_ENDING,
                       '[Metadata]' + LINE_ENDING,
                       bm_info['Title'],
                       bm_info['Artist'],
                       bm_info['Mapper'],
                       bm_info['Diff name'],
                       '[Difficulty]' + LINE_ENDING,
                       bm_info['HP'],
                       bm_info['CS'],
                       bm_info['OD'],
                       bm_info['AR'],
                       bm_info['SV'],
                       bm_info['TR'],
                       '[TimingPoints]' + LINE_ENDING,
                       '[HitObjects]' + LINE_ENDING))

    results = []
    seek = 0
    with tempfile.TemporaryDirectory() as tmpdir:
        while bmap:
            out = ''.join(
                [x for x in bmap if int(x.split(',')[2]) < seek + 30000])

            with open(tmpdir + '/tmp', 'w') as tmp:
                tmp.write(bm_head + out)

            oppai_out = subprocess.check_output(
                ["oppai/oppai.exe", tmpdir + '/tmp'])

            print(oppai_out.decode())
            results.append(('a', 'b', 'c', 'd'))

            seek = seek + 5000
            bmap = [x for x in bmap if int(x.split(',')[2]) > seek]

    return results


def main():
    """oppai-chunks from CLI

    Print results when run, e.g. ./oppai-chunks.py beatmap.osu
    """
    if len(sys.argv) != 2:
        print_usage()
        sys.exit()

    print("\nAnalyzing \"{}\"...".format(sys.argv[1]))

    results = oppai(sys.argv[1])

    print("Time\tOverall\tAim\tSpeed")
    bigprint = ""
    for chunk in results:
        bigprint += "{}\t{}\t{}\t{}\n".format(*chunk)
    print(bigprint)

if __name__ == '__main__':
    main()
