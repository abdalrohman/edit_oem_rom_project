#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# File Name    :   create_ext4.py
# Created Time :   2022/11/09 17:21:44
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
# pylint: disable=W1514
# pylint: disable=W0702
import os
import re
import shutil
import subprocess
import sys
import time

from loguru import logger

from utils.config import load_config
from utils.func import RunCommand, cat, remove

mke2fs = load_config('LINUX', 'mke2fs')
mke2fs_conf = load_config('LINUX', 'mke2fs_conf')
e2fsdroid = load_config('LINUX', 'e2fsdroid')
img2simg = load_config('LINUX', 'img2simg')
brotli_tool = load_config('LINUX', 'brotli')
img2sdat = load_config('PYTHON', 'img2sdat')
config_dir = os.path.join(load_config('MAIN', 'main_project'), 'Config')
build_dir = os.path.join(load_config('MAIN', 'main_project'), 'Build')
out_dir = os.path.join(load_config('MAIN', 'main_project'), 'Output')
main_project = load_config('MAIN', 'main_project')


def dump_data(file):
  """
  search for data from output of tune2fs command
  """
  uuid_searche = 'Filesystem UUID:'
  inode_size_searche = 'Inode size:'
  reserved_percent_searche = 'Reserved block count:'
  block_size_searche = 'Block size:'
  inode_count_searche = 'Inode count:'
  part_size_searche = 'Partition Size:'

  with open(file, 'r') as file:
    lines = file.readlines()

    for l in lines:
      if uuid_searche in l:
        uuid = l.split(':')[1].strip()
      if inode_size_searche in l:
        inode_size = l.split(':')[1].strip()
      if reserved_percent_searche in l:
        reserved_percent = l.split(':')[1].strip()
      if block_size_searche in l:
        block_size = l.split(':')[1].strip()
      if inode_count_searche in l:
        inode_count = l.split(':')[1].strip()
      if part_size_searche in l:
        part_size = l.split(':')[1].strip()

  return (uuid, inode_size, inode_count, block_size, reserved_percent, part_size)


def find_in_list(words_list, input_list, sperate=','):
  """Find element of first list in second list

  Args:
      words_list (_type_): first list
      input_list (_type_): second list
      sperate (str, optional): specify sperator. Defaults to ','.

  Returns:
      True: if find elements of words_list in input_list
      False: if any element in words_list not found in input_list
  """
  words_list = words_list.split(sperate)

  for w in words_list:
    for i in input_list:
      if re.search(rf"({w})", i) is not None:
        return True

  return False


def __print_images():
  """return list of images to build

  Returns:
      user choice: list
  """
  list_build = []

  logger.info(f"Images list in {main_project}: ")
  for part in os.listdir(out_dir):
    if os.path.exists(os.path.join(config_dir, part+"_file_contexts.txt")) \
      and os.path.exists(os.path.join(config_dir, part+"_filesystem_config.txt")) \
        and os.path.exists(os.path.join(config_dir, part+"_filesystem_features.txt")):
      logger.info(f'  {part}')
      list_build.append(part)

  logger.info('  all/a')
  logger.info('  exit/press enter')

  choice = input(
    "\nType name of image you want to build it [eg: system, odm]: ")
  choice = choice.lower()

  if choice in ('all', 'a'):
    choice = list_build
  elif find_in_list(choice, list_build) is False and choice not in ('all', 'a'):
    logger.info("Terminating...")
    sys.exit(0)
  else:
    choice = choice.split(',')

  return choice


def run_command(cmd, env):
  """Runs the given command.

  Args:
    cmd: the command represented as a list of strings.
    env: a dictionary of additional environment variables.
  Returns:
    A tuple of the output and the exit code.
  """
  start_time = time.time()
  logger.info("Env: {}", env)
  logger.info("Running: {}", " ".join(cmd))

  env_copy = os.environ.copy()
  env_copy.update(env)

  p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       env=env_copy)
  output, _ = p.communicate()

  runtime = (time.time() - start_time)
  logger.info("Excution time: {} seconds", runtime)

  return output, p.returncode


def __make_ext4(raw=False, sparse=False, brotli=False):
  """Make ext4 filesystem"""

  images_build = __print_images()

  for part in images_build:
    if raw:
      if os.path.exists(os.path.join(out_dir, part)):
        file_features = os.path.join(
          config_dir, part+'_filesystem_features.txt')
        try:
          uuid, inode_size, inode_count, block_size, reserved_percent, part_size = dump_data(
            file_features)
        except UnboundLocalError:
          logger.exception(
            f"Check {os.path.join(config_dir, part+'_filesystem_features.txt')}")
          sys.exit(1)

        # truncate output file since mke2fs will keep verity section in existing file
        with open(os.path.join(build_dir, part+'.img'), 'w') as output:
          output.truncate()

        # run mke2fs
        if part in ('system', 'system_a'):
          mke2fs_cmd = [
            mke2fs, '-O', '^has_journal', '-L', part, '-N',
            inode_count, '-I', inode_size, '-M', '/', '-m', reserved_percent, '-U', uuid,
            '-t', 'ext4', '-b', block_size, os.path.join(
              build_dir, part+'.img'), str(int(part_size) // int(block_size))
          ]

        else:
          mke2fs_cmd = [
            mke2fs, '-O', '^has_journal', '-L', part, '-N', inode_count, '-I', inode_size, '-M', '/' +
            part, '-m', reserved_percent, '-U', uuid,
            '-t', 'ext4', '-b', block_size, os.path.join(
              build_dir, part+'.img'), str(int(part_size) // int(block_size))
          ]

        mke2fs_env = {"MKE2FS_CONFIG": "./bin/mke2fs.conf",
                      "E2FSPROGS_FAKE_TIME": "1230768000"}

        output, ret = run_command(mke2fs_cmd, mke2fs_env)
        if ret != 0:
          logger.error(f"Failed to run mke2fs: {output}")
          sys.exit(4)

        # run e2fsdroid
        e2fsdroid_env = {"E2FSPROGS_FAKE_TIME": "1230768000"}

        if part in ('system', 'system_a'):
          e2fsdroid_cmd = [
            e2fsdroid, '-e', '-T', '1230768000', '-C',
            os.path.join(config_dir, part+'_filesystem_config.txt'), '-S',
            os.path.join(config_dir, part+'_file_contexts.txt'), '-S',
            os.path.join(config_dir, 'file_contexts.txt'), '-f',
            os.path.join(out_dir, part), '-a', '/',
            os.path.join(build_dir, part+'.img')
          ]

        else:
          try:
            e2fsdroid_cmd = [
              e2fsdroid, '-e', '-T', '1230768000', '-C',
              os.path.join(config_dir, part+'_filesystem_config.txt'), '-S',
              os.path.join(config_dir, part+'_file_contexts.txt'), '-S',
              os.path.join(config_dir, 'file_contexts.txt'), '-f',
              os.path.join(out_dir, part), '-a', '/'+part,
              os.path.join(build_dir, part+'.img')
            ]

          except:
            logger.info(
              f"Try without ({os.path.join(config_dir, part+'_filesystem_config.txt')})")
            e2fsdroid_cmd = [
              e2fsdroid, '-e', '-T', '1230768000', '-S',
              os.path.join(config_dir, part+'_file_contexts.txt'), '-S',
              os.path.join(config_dir, 'file_contexts.txt'), '-f',
              os.path.join(out_dir, part), '-a', '/'+part,
              os.path.join(build_dir, part+'.img')
            ]

        output, ret = run_command(e2fsdroid_cmd, e2fsdroid_env)
        if ret != 0:
          logger.error(f"Failed to run e2fsdroid_cmd: {output}")
          remove(os.path.join(build_dir, part+'.img'))
          sys.exit(4)
        print('')

    if sparse:
      raw_img = os.path.join(build_dir, part+'.img')
      sparse_img = os.path.join(build_dir, part+'.sparse')
      if os.path.exists(raw_img):
        logger.info('Convert raw image to sparse...')
        cmd = [img2simg, raw_img, sparse_img]
        RunCommand(cmd, verbose=True)

      if os.path.isfile(sparse_img):
        remove(raw_img)

    if brotli:
      sparse_img = os.path.join(build_dir, part+'.sparse')
      sdat_img = os.path.join(build_dir, part+'.new.dat')
      if os.path.exists(sparse_img):
        logger.info('Convert sparse image to sdat...')
        cmd = ['python', img2sdat, '-o', build_dir,
               '-p', part, sparse_img, '402653184']
        RunCommand(cmd, verbose=True)

        if os.path.isfile(sdat_img):
          remove(sparse_img)

        logger.info('Compress with brotli...')
        cmd = [brotli_tool, '-q', '6', '-v', '-f', sdat_img]
        RunCommand(cmd, verbose=True)

        if os.path.isfile(sdat_img+'.br'):
          remove(sdat_img)


def main(raw=False, sparse=False, brotli=False):
  """Main"""
  vendor_context = os.path.join(
    out_dir, 'vendor/etc/selinux/vendor_file_contexts')
  system_context = os.path.join(
    out_dir, 'system/system/etc/selinux/plat_file_contexts')
  file_context = os.path.join(config_dir, 'file_contexts.txt')

  if not os.path.exists(file_context):
    if os.path.exists(system_context) and os.path.exists(vendor_context):
      cat(system_context, file_context)

      cat(vendor_context, file_context)

    elif os.path.exists(system_context):
      cat(system_context, file_context)

    elif os.path.exists(vendor_context):
      cat(system_context, file_context)

    else:
      logger.error(
        f"{file_context} Not found!!")
      sys.exit(1)

  __make_ext4(raw, sparse, brotli)
