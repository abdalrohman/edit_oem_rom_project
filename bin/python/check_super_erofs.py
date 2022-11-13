#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# File Name    :   file_type.py
# Created Time :   2022/11/11 06:01:39
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

import mmap
from sys import argv

from construct import Array, Int8ul, Int16ul, Int32ul, Int64ul, Struct

struct_erofs = Struct(
  "magic" / Int32ul,
  "checksum" / Int32ul,
  "features" / Int32ul,
  "blkszbits" / Int8ul,
  "reserved" / Int8ul,
  "root_nid" / Int16ul,
  "inos" / Int64ul,
  "build_time" / Int64ul,
  "build_time_nsec" / Int32ul,
  "blocks" / Int32ul,
  "meta_blkaddr" / Int32ul,
  "xattr_blkaddr" / Int32ul,
  "uuid" / Array(16, Int8ul),
  "volume_name" / Array(16, Int8ul),
  "reserved2" / Array(48, Int8ul)
)
assert struct_erofs.sizeof() == 128, struct_erofs.sizeof()


def check_erofs(input_img: str):
  """Check if erofs filesystem"""
  file_handle = open(input_img, 'rb')
  mmmap = mmap.mmap(file_handle.fileno(), 0,
                    mmap.MAP_SHARED, mmap.PROT_READ)
  erofs = struct_erofs.parse(
    mmmap[0x400:0x400+struct_erofs.sizeof()])

  if "0x%x" % erofs.magic == "0xe0f5e1e2" and erofs.blkszbits == 12:
    print("erofs")
  elif "0x%x" % erofs.magic == "0x0" and erofs.blkszbits == 0:
    print("super")


filename = argv[1]
check_erofs(filename)
