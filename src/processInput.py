# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
from __future__ import print_function

import sys
import os
import pickle
import re

import parse
import format
import stateFiles
from formattedText import FormattedText
from usageStrings import USAGE_STR
from screenFlags import ScreenFlags


def getLineObjs():
    inputLines = sys.stdin.readlines()
    return getLineObjsFromLines(inputLines)


def getLineObjsFromLines(inputLines, validateFileExists=True):
    lineObjs = {}
    for index, line in enumerate(inputLines):
        line = line.replace('\t', '    ')
        # remove the new line as we place the cursor ourselves for each
        # line. this avoids curses errors when we newline past the end of the
        # screen
        line = line.replace('\n', '')
        formattedLine = FormattedText(line)
        result = parse.matchLine(str(formattedLine),
                                 validateFileExists=validateFileExists)

        if not result:
            line = format.SimpleLine(formattedLine, index)
        else:
            line = format.LineMatch(formattedLine, result,
                                    index, validateFileExists=validateFileExists)

        lineObjs[index] = line

    return lineObjs


def doProgram():
    filePath = stateFiles.getPickleFilePath()
    lineObjs = getLineObjs()
    # pickle it so the next program can parse it
    pickle.dump(lineObjs, open(filePath, 'wb'))


def usage():
    print(USAGE_STR)


if __name__ == '__main__':
    flags = ScreenFlags.initFromArgs(sys.argv[1:])
    if (flags.getIsCleanMode()):
        print('Cleaning out state files...')
        for filePath in stateFiles.getAllStateFiles():
            if os.path.isfile(filePath):
                os.remove(filePath)
        print('Done! Removed %d files ' % len(stateFiles.getAllStateFiles()))
        sys.exit(0)

    if sys.stdin.isatty():
        if os.path.isfile(stateFiles.getPickleFilePath()):
            print('Using old result...')
        else:
            usage()
        # let the next stage parse the old version
        sys.exit(0)
    else:
        # delete the old selection
        selectionPath = stateFiles.getSelectionFilePath()
        if os.path.isfile(selectionPath):
            os.remove(selectionPath)

        doProgram()
        sys.exit(0)
