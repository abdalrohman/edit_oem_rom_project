#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# File Name    :   img2sdat.py
# Created Time :   2022/11/10 19:09:36
"""
  Edit_OEM_ROM_Project
  Copyright (C) <2022>  <Abdalrohman Alnasier>

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


from __future__ import print_function

import argparse
import os
import sys
import tempfile

import sparse_img
import common
import blockimgdiff
from images import EmptyImage


def main(input_image, prefix, cache_size, out_dir, version):
  """Convert image to new.dat format."""

  if sys.hexversion < 0x02070000:
    print('Python 2.7 or newer is required.', file=sys.stderr)
    sys.exit(1)

  if not os.path.isdir(out_dir):
    os.makedirs(out_dir)

  path = os.path.join(out_dir, prefix)

  if os.path.exists(out_dir):
    image = sparse_img.SparseImage(input_image, tempfile.mkstemp()[1], '0')

    common.OPTIONS.cache_size = cache_size
    src = EmptyImage()
    block_image_diff = blockimgdiff.BlockImageDiff(image, src, version)
    block_image_diff.Compute(path)


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('image', help='input system image')
  parser.add_argument('cachsize', help='chach size')
  parser.add_argument(
    '-o', '--outdir', help='output directory (current directory by default)')
  parser.add_argument(
    '-v', '--version', help='transfer list version number (3,4 default=4)')
  parser.add_argument(
    '-p', '--prefix', help='name of image (prefix.new.dat)')

  args = parser.parse_args()

  image = args.image

  if args.prefix:
    prefix = args.prefix
  else:
    prefix = 'system'

  cache_size = int(args.cachsize)

  if args.outdir:
    out_dir = args.outdir
  else:
    out_dir = '.'

  if args.version:
    version = int(args.version)
  else:
    version = 4

  main(image, prefix, cache_size, out_dir, version)
