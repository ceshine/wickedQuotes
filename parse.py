import re
import sys
import json
from functools import partial
from xml.dom.minidom import parse

import xmltodict
from langdetect import detect

import unwiki


def writeQuotes(content, langArg, cutoffArg):
    quoteList = []
    write = False
    i = 0

    while i < len(content):
        line = content[i]

        if line.startswith('==') and line[2] != "=":
            write = False
        if write and line.startswith('* ') and len(line) < (cutoffArg + 3):
            # would optimize, but since the program only needs to be run once, not really a priority
            cleaned_line = unwiki.loads(line, compress_spaces=True) + '\n'
            cleaned_line = multireplace(
                cleaned_line,
                {
                    "\\u2018": "'", "\\u2019": "'", "\\u2026": "...",
                    "\\u2013": "-", "\\u2014": "-", "\\u201c": '"',
                    "\\u201d": '"', "\\'": "'", "'''": "", "\n": ""
                })
            cleaned_line = re.sub(
                r"<.*>|'('+)|\\\\x..|\\u....", "", cleaned_line)
            cleaned_line = cleaned_line[2:]

            if (detect(cleaned_line) == langArg and "://" not in cleaned_line):
                quoteList.append(cleaned_line)

        if line == '==Quotes==' or line == '== Quotes ==':
            write = True
        i += 1

    return quoteList


def handle(_, value, quotesObject, langArg, cutoffArg):
    try:
        quoteList = writeQuotes(
            str(value['revision']['text']).split('\\n'),
            langArg, cutoffArg
        )
        if len(quoteList) > 0:
            quotesObject[str(value['title'])] = quoteList
    except Exception as e:
        pass
    return True


def multireplace(string, replacements):
    substrs = sorted(replacements, key=len, reverse=True)
    regexp = re.compile('|'.join(map(re.escape, substrs)))
    return regexp.sub(lambda match: replacements[match.group(0)], string)


def main():
    quotesObject = {}

    if (len(sys.argv) == 1):
        print("You must specify an input file.")
        sys.exit()
    if (len(sys.argv) == 2):
        cutoffArg = 50
        langArg = "en"
    if (len(sys.argv) == 3):
        cutoffArg = int(sys.argv[2])
        langArg = "en"
    if (len(sys.argv) > 3):
        cutoffArg = int(sys.argv[2])
        langArg = str(sys.argv[3])

    xmltodict.parse(
        open(str(sys.argv[1]), "rb"),
        item_depth=2,
        item_callback=partial(
            handle,
            quotesObject=quotesObject,
            langArg=langArg,
            cutoffArg=cutoffArg
        )
    )

    with open('quotes-' + str(cutoffArg) + '-' + str(langArg) + '.json', 'w') as outfile:
        json.dump(
            quotesObject, outfile, sort_keys=True,
            indent=4, ensure_ascii=False
        )


if __name__ == "__main__":
    main()
