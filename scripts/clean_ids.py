#!/usr/bin/env python3
import sys
import logging
import re

logging.basicConfig(filename = 'pipeline_autid.log', filemode = 'a', format = '%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)


def is_valid_youtube_id(id):
	regex_pattern = '^[A-Za-z0-9_-]{11}$'
	return bool(re.fullmatch(regex_pattern, id))


def main():
	for line in sys.stdin:
    		line = line.strip()
    		if not line:
        		continue
    		if is_valid_youtube_id(line):
        		sys.stdout.write(line + '\n')
    		else:
        		logger.error(f'{line} is not a valid id')

if __name__ =="__main__":
	main()
