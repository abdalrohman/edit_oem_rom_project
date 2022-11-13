#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# File Name    :   main.py
# Created Time :   2022/11/09 17:23:04
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
# pylint: disable=C0116
# pylint: disable=W0621
# pylint: disable=W0702
import argparse
import os
import sys
import time

from loguru import logger

import utils

# TODO fix check python version
# check python version
if not sys.version_info >= (3, 6):
  print("Python 3.6 or higher is required.")
  print("You are using Python {}.{}.".format(
    sys.version_info.major, sys.version_info.minor))
  sys.exit(1)

# initiat logs
utils.init_log('./logs/Log.log')

# check os
if sys.platform == "linux" or sys.platform == "linux2":
  logger.info(f"platform: {sys.platform}")
else:
  logger.info(f"Your platform {sys.platform} not supported.")
  sys.exit(1)

# check os arch
if utils.check_arch() == "AMD64" or utils.check_arch() == "ARM64":
  logger.info(f"Arch: {utils.check_arch()}")
else:
  logger.info(f"Your architecture {utils.check_arch()} not supported.")
  sys.exit(1)

__version__ = 'Edit_OEM_ROM_Project V1.0'


def init_folders(project):
  folders = utils.load_config('MAIN', 'proj_folders').split(' ')
  for f in folders:
    utils.mkdir(os.path.join(project, f))


def init_project(prj_name):
  logger.info("Project Name: {}", prj_name)

  data = {'main_project': os.path.join('Projects', prj_name)}
  utils.update_config('MAIN', data)

  if os.path.isdir(os.path.join('Projects', prj_name)):
    logger.warning("This project exist")
    choice = input("If you want to continu will delete this project [y/n]: ")
    if choice.lower() == 'y':
      logger.info('Remove project {}',
                  utils.load_config('MAIN', 'main_project'))
      utils.rmdir(os.path.join('Projects', prj_name))
      init_folders(utils.load_config('MAIN', 'main_project'))
    else:
      init_folders(utils.load_config('MAIN', 'main_project'))

  else:
    init_folders(utils.load_config('MAIN', 'main_project'))

  data = {'main_project': os.path.join('Projects', args.name)}
  return utils.update_config('MAIN', data)


def parser():
  parser = argparse.ArgumentParser(
    description='')
  parser.add_argument(
    '-n', dest='name', help='Specify project name and init folder project')
  parser.add_argument('-i', dest='input', help='Input zip')
  parser.add_argument('-u', dest='prj_name',
                      help='Update project name in config.ini')
  parser.add_argument('-l', dest='lst', action='store_true',
                      help='List of projects')
  parser.add_argument('-w', '--write-config', dest='write_config',
                      action='store_true', help='Write config.ini')
  parser.add_argument('-R', dest='raw', action='store_true',
                      help='Build ext4 image (linux only)')
  parser.add_argument('-S', dest='sparse', action='store_true',
                      help='Build Sparse image (linux only) with [-R]')
  parser.add_argument('-B', dest='brotli', action='store_true',
                      help='Build .sdat.br image (linux only) with [-RS]')
  parser.add_argument('--clean', dest='clean',
                      action='store_true', help='Clean up projects dir')
  parser.add_argument('--version', dest='version',
                      action='store_true', help='Display version')
  return parser


if __name__ == '__main__':
  # start_time
  start_time = time.time()

  # initiat logs
  utils.init_log('./logs/Log.log')

  # generate config.ini if not exist
  if not os.path.exists('./config.ini'):
    logger.info('Generate config.ini')
    utils.write_default_config()

  parser = parser()
  args = parser.parse_args()

  if len(sys.argv) < 2:
    logger.error("You must enter at least one aurgment!!!")
    parser.print_usage()
    sys.exit(1)

  if args.name:
    data = {'main_project': os.path.join('Projects', args.name)}
    utils.update_config('MAIN', data)
    init_project(args.name)

  if args.prj_name:
    data = {'main_project': os.path.join('Projects', args.prj_name)}
    utils.update_config('MAIN', data)
    logger.info(
      f"Updated project to [{utils.load_config('MAIN', 'main_project')}]")

  if args.write_config:
    logger.info('Update config.ini')
    utils.write_default_config()

  if args.clean:
    if os.path.exists("./Projects"):
      logger.info(f"Clean Prject directory: {os.path.join('./Projects')}")
      utils.rmdir("./Projects")
    sys.exit(0)

  if args.lst:
    logger.info('List of projects: ')
    number = 0
    for p in os.listdir('Projects'):
      logger.info(f"  {number}: {p}")
      number += 1
    sys.exit(0)

  # print version
  if args.version:
    logger.info(f"Version: {__version__}")
    sys.exit(0)

  main_project = utils.load_config('MAIN', 'main_project')

  if args.input:
    utils.extract_fw(args.input, os.path.join(main_project, 'Source'))
    utils.extract_img(main_project)
    utils.display_rom_info(main_project)

  if args.raw:
    raw = True
  else:
    raw = False

  if args.sparse:
    sparse = True
  else:
    sparse = False

  if args.brotli:
    brotli = True
  else:
    brotli = False

  if sparse or raw or brotli:
    utils.create_ext4.main(raw, sparse, brotli)

  runtime = (time.time() - start_time)
  from utils.print_wrapper import print

  print("")
  print("")
  print("")
  print("")
  print(f"Total Excution time: {runtime} seconds", color="white", tag="[SUCCESS]", tag_color="green")
