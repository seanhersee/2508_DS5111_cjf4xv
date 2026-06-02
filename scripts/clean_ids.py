#!/usr/bin/env python3
import sys
import logging
import re

logging.basicConfig(filename = 'pipeline_autid.log', filemode = 'a', format = '%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

data = sys.stdin
regex_pattern = '^[A-Za-z0-9_-]{11}$'

for line in data:
    line = line.strip()
    if not line:
        continue
    if re.fullmatch( regex_pattern, line):
        sys.stdout.write(line + '\n')
    else:
        logger.error(f'{line} is not a valid id')
