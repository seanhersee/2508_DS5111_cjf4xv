#!/usr/bin/env python3
"""Validates YouTube video IDs from stdin and logs invalid entries."""
import sys
import logging
import re

logging.basicConfig(
    filename = 'pipeline_autid.log',
    filemode = 'a',
    format = '%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG)

logger = logging.getLogger(__name__)


def is_valid_youtube_id(value):
    '''
    Takes a Youtube video title to confirm that it matches the
    correct formatting.
    '''
    regex_pattern = '^[A-Za-z0-9_-]{11}$'
    return bool(re.fullmatch(regex_pattern, value))


def main():
    '''
    Reads in passed file and passes records through is_valid_youtube_id
    to confirm the titles fit the format specifications.
    If a title does not fit the specifications, it is added to the error log.
    '''
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        if is_valid_youtube_id(line):
            sys.stdout.write(line + '\n')
        else:
            logger.error('%s is not a valid id', line)

if __name__ == "__main__":
    main()
