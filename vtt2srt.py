from glob import glob
import argparse
import os


def isEmptyLine(str):
    return len(line.strip()) == 0


parser = argparse.ArgumentParser(description='Convertir .vtt a .srt')
parser.add_argument('dest', nargs='+', help='path to vtt files (accepts wildcards)')
args = parser.parse_args()

files = glob(args.dest[0])
for f in files:
    src = open(f, 'r')
    dest = open(os.path.splitext(f)[0] + ".srt", 'w')

    # find first subtitle line
    while True:
        line = src.readline()
        if not line: raise Exception("Invalid file")
        if line[0].isnumeric(): break
    
    # write srt
    count = 1
    while line:
        dest.write(str(count) + "\n")
        dest.write(line)
        line = src.readline()
        
        # write until empty line
        while line and not isEmptyLine(line):
            dest.write(line)
            line = src.readline()
        
        dest.write("\n")
        count += 1
        line = src.readline()
    
    src.close()
    dest.close()