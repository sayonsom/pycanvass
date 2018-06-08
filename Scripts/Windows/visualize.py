#!/usr/bin/python

import sys;
import re;
import os

infile = open(sys.argv[1], 'r')
outfile = open(sys.argv[2], 'w')

lines = infile.readlines()

# .dot files begin with the 'graph' keyword.
outfile.write("digraph {\n")
outfile.write("node [shape=box]\n")
# These are state variables.  There is no error checking, so we rely on
# well formatted *.GLM files.
s = 0
state = 'start'
edge_color = 'black'
edge_style = 'solid'
lengthVal = 'None'
lineLengthIncrement = 0

# Loop through each line in the input file...
while s < len(lines):
    # Discard Comments
    if re.match("//", lines[s]) == None:
        if re.search("from", lines[s]) != None:
            ts = lines[s].split()
            # Graphvis format can't handle '-' characters, so they are converted to '_'
            ns = ts[1].rstrip(';').replace('-', '_').replace(':', '_')
            outfile.write(ns)
            state = 'after_from'
        elif state == 'after_from' and re.search("to ", lines[s]) != None:
            ts = lines[s].split()
            ns = ts[1].rstrip(';').replace('-', '_').replace(':', '_')
            if edge_color == 'red':
                outfile.write(
                    ' -> ' + ns + '[style=' + edge_style + ' color=' + edge_color + ' label="' + lengthVal + '"]\n')
                outfile.write("node [shape=box]\n")
            else:
                outfile.write(
                    ' -> ' + ns + '[style=' + edge_style + ' color=' + edge_color + ' label="' + lengthVal + '"]\n')
            lengthVal = 'None'
            # After an edge is added to the graph, reset the states back to default
            state = 'start'
            edge_color = 'black'
            edge_style = 'solid'
        elif (re.search("object underground_line", lines[s]) != None) or (
            re.search("object overhead_line", lines[s]) != None):
            while '}' not in lines[s + lineLengthIncrement]:
                if re.search("length ", lines[s + lineLengthIncrement]) != None:
                    les = lines[s + lineLengthIncrement].split()
                    if len(les) > 2:
                        tsVal = les[1] + ' ' + les[2].strip(';')
                        lengthVal = tsVal
                    elif len(les) <= 2:
                        tsVal = les[1].strip(';')
                        lengthVal = tsVal
                    break
                else:
                    lineLengthIncrement = lineLengthIncrement + 1
                if '}' in lines[s + lineLengthIncrement]:
                    lineLengthIncrement = 0
                    lengthVal = 'None'
                    break
            if re.search("object underground_line", lines[s]) != None:
                lengthVal = "UG_line\\n" + lengthVal
            elif re.search("object overhead_line", lines[s]) != None:
                lengthVal = "OH_line\\n" + lengthVal
        elif re.search("object transformer", lines[s]) != None:
            edge_color = 'red'
            lengthVal = "transformer\\n" + lengthVal
            outfile.write("node [shape=oval]\n")
        elif re.search("object triplex_line", lines[s]) != None:
            edge_color = 'green'
            lengthVal = "triplex_line\\n" + lengthVal
        elif re.search("object fuse", lines[s]) != None:
            edge_color = 'blue'
            lengthVal = "Fuse\\n" + lengthVal
        elif re.search("phases ", lines[s]) != None:
            ts = lines[s].split()
            if len(ts[1].rstrip(';')) > 3:
                edge_style = 'bold'
            elif len(ts[1].rstrip(';')) > 2:
                edge_style = 'dashed'

    s += 1

outfile.write("}\n")
infile.close()
outfile.close()
os.system("dot -Tsvg -O " + sys.argv[2])