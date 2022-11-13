#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# File Name    :   erofs.py
# Created Time :   2022/11/11 16:59:33
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
# pylint: disable=W0702
# pylint: disable=E0401
# pylint: disable=W1514
# pylint: disable=E1101


import datetime
import mmap
import os
import re
import subprocess
import sys
import time

from construct import Array, Int8ul, Int16ul, Int32ul, Int64ul, Struct
from loguru import logger

BLOCK_SIZE = 4096

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


def __run_command(arg, **kwargs):
  """Runs the given command and returns the output.

  Args:
    arg: The command represented as a list of strings.
    kwargs: Any additional args to be passed to subprocess.Popen(), such as env,
        stdin, etc. stdout and stderr will default to subprocess.PIPE and
        subprocess.STDOUT respectively unless caller specifies any of them.

  Returns:
    string: output.

  Raises:
    RuntimeError: On non-zero exit from the command.
  """
  start_time = time.time()
  logger.info("Running: {}", " ".join(arg))

  if 'stdout' not in kwargs and 'stderr' not in kwargs:
    kwargs['stdout'] = subprocess.PIPE
    kwargs['stderr'] = subprocess.STDOUT
  if 'universal_newlines' not in kwargs:
    kwargs['universal_newlines'] = True

  proc = subprocess.Popen(arg, **kwargs)
  output, _ = proc.communicate()

  runtime = (time.time() - start_time)
  logger.info("Excution time: {} seconds", runtime)

  if output is None:
    output = ""

  if proc.returncode != 0:
    logger.exception(
      "Failed to run command '{}' (exit code {}):\n{}", " ".join(
        arg), proc.returncode, output
    )
    exit(1)

  return output, proc.returncode


def __dir_size(path):
  """Returns the number of bytes that "path" occupies on host.
  :param path: The directory or file to calculate size on.
  :return: The number of bytes based on a 1K block_size.
  """
  logger.info(f"Calculate size of {path}")

  cmd = ["du", "-b", "-k", "-s", path]
  output = __run_command(cmd)
  return int(output[0].split()[0]) * 1024


def __open_file(fn):
  """Open file"""
  return open(fn, 'rb')


def __check_erofs(input_img: str):
  """Check if erofs filesystem"""
  file_handle = __open_file(input_img)
  mmmap = mmap.mmap(file_handle.fileno(), 0,
                    mmap.MAP_SHARED, mmap.PROT_READ)
  erofs = struct_erofs.parse(
    mmmap[0x400:0x400+struct_erofs.sizeof()])

  try:
    if "0x%x" % erofs.magic == "0xe0f5e1e2" and erofs.blkszbits == 12:
      pass
    else:
      raise Exception("Not erofs filesystem")
  except:
    logger.exception("Not erofs filesystem")


def __appendf(msg, out_file):
  """Write to file"""
  with open(out_file, 'w', encoding='UTF-8') as file:
    file.write('{}\n'.format(msg))


def __file_name(file_path):
  """get filename"""
  name = os.path.basename(file_path).split('.')[0]
  return name


def __write_fetures(input_img, config_dir, output_path):
  """Write erofs fetures to _filesystem_features.txt"""
  __check_erofs(input_img)
  fetures = []
  fs_context = []
  fs_config = []
  file_name = __file_name(os.path.basename(input_img))
  file_features = os.path.join(
    config_dir, file_name + '_filesystem_features.txt')
  fs_config_file = os.path.join(
    config_dir, file_name + '_filesystem_config.txt')
  fs_context_file = os.path.join(
    config_dir, file_name + '_file_contexts.txt')

  file_handle = __open_file(input_img)
  mmmap = mmap.mmap(file_handle.fileno(), 0,
                    mmap.MAP_SHARED, mmap.PROT_READ)
  erofs = struct_erofs.parse(
    mmmap[0x400:0x400+struct_erofs.sizeof()])

  # file_size = os.stat(file_handle.fileno()).st_size
  partition_size = __dir_size(os.path.join(output_path, file_name))
  # get 40mb extra to partition size
  partition_size = partition_size + 41943040
  uuid = [erofs.uuid[:4], erofs.uuid[4: 6],
          erofs.uuid[6: 8], erofs.uuid[8: 10], erofs.uuid[10:]]
  uuid = "-".join("".join("{0:02X}".format(c) for c in part) for part in uuid)
  reserved_size = int(erofs.reserved)
  created_date = datetime.datetime.fromtimestamp(erofs.build_time)
  created_date = created_date.strftime('%a %b %-d %H:%M:%S %Y')
  magic_number = "0x%x" % erofs.magic
  inod_count = erofs.inos
  # get more inode count to prevent build error
  inod_count = inod_count + 2000
  inod_size = 256

  fetures.append('Filesystem UUID:'+' '*11 + f'{uuid}')
  fetures.append('Filesystem magic number:'+' '*3 + f'{magic_number}')
  fetures.append('Inode size:'+' '*16 + f'{inod_size}')
  fetures.append('Reserved block count:'+' '*6 + f'{reserved_size}')
  fetures.append('Block size:'+' '*16 + f'{BLOCK_SIZE}')
  fetures.append('Inode count:'+' '*15 + f'{inod_count}')
  fetures.append('Filesystem created:'+' '*8 + f'{created_date}')
  fetures.append('Partition Size:' + ' '*12 + f'{partition_size}')
  # write to file
  __appendf('\n'.join(fetures), file_features)

  #################################################
  if file_name in ('vendor', 'odm'):
    fs_context.append('/ u:object_r:vendor_file:s0')
    fs_context.append(
      f'/{file_name}(/.*)? u:object_r:vendor_file:s0')

  else:
    fs_context.append('/ u:object_r:rootfs:s0')
    fs_context.append(
      f'/{file_name}(/.*)? u:object_r:rootfs:s0')

  if file_name == 'system':
    fs_context.append('/lost+found        u:object_r:rootfs:s0')
  else:
    fs_context.append(
      f'/{file_name}/lost+found        u:object_r:rootfs:s0')

  # replace . with \. in list
  fs_context = [ele.replace('.', r'\.') for ele in fs_context]
  # replace + with \+ in list
  fs_context = [ele.replace('+', r'\+') for ele in fs_context]

  with open(fs_context_file, 'r', encoding='UTF-8') as file:
    lines = file.readlines()

    for l in lines:
      # remove perfix from beginig
      if l.startswith(f'/{file_name}/'):
        l = re.sub(rf'^/{file_name}', '', l)
        fs_context.append(l.strip())

  # remove \n from list
  fs_context = [i for n, i in enumerate(fs_context) if i not in fs_context[:n]]

  # remove empty string fro list
  fs_context = list(filter(None, fs_context))

  fs_context.sort()
  # write contexts to file
  __appendf('\n'.join(fs_context), fs_context_file)

  #################################################
  with open(fs_config_file, 'r', encoding='UTF-8') as file:
    lines = file.readlines()

    for l in lines:
      path = l.split(' ')[0]
      uid = l.split(' ')[1]
      gid = l.split(' ')[2]
      perm = l.split(' ')[3]

      # remove prefix from path for make ext4 filesystem
      if path.startswith(f'{file_name}/'):
        path = re.sub(rf'^{file_name}/', '', path)
        if path != "":

          # fix symlink
          if os.path.islink(os.path.join(output_path, file_name, path)):
            link = os.readlink(os.path.join(output_path, file_name, path))
            fs_config.append(
              f"{path.strip()} {uid.strip()} {gid.strip()} {perm.strip()} {link}")
          else:
            fs_config.append(
              f"{path.strip()} {uid.strip()} {gid.strip()} {perm.strip()}")

  if file_name == 'vendor':
    fs_config.append('/ 0 2000 0755')
    fs_config.append(f'{file_name} 0 2000 0755')

  else:
    fs_config.append('/ 0 0 0755')
    fs_config.append(f'{file_name} 0 0 0755')

  # remove \n from list
  fs_config = [i for n, i in enumerate(fs_config) if i not in fs_config[:n]]

  # remove empty string fro list
  fs_config = list(filter(None, fs_config))

  fs_config.sort()
  # write config list to file
  __appendf('\n'.join(fs_config), fs_config_file)


if __name__ == '__main__':

  if len(sys.argv) < 4:
    print(f'USAGE: {sys.argv[0]} image_path config_path')
  else:
    image = os.path.realpath(sys.argv[1])
    config = os.path.realpath(sys.argv[2])
    output = os.path.realpath(sys.argv[3])
    __write_fetures(image, config, output)
