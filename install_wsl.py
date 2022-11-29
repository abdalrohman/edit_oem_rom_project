#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# File Name    :   install_wsl.py
# Created Time :   2022/11/29 12:23:15
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


import os
import sys

from loguru import logger
from utils.config import load_config
from utils.func import RunCommand, init_log, mkdir, remove

# initiate logs
init_log('./logs/Log.log')

_7z_bin = load_config('LINUX', '7z')
_7z_file = os.path.join('wsl', 'eorp.7z.001')
tar_file = os.path.join('wsl', 'eorp.tar')
installation_dir = os.path.join('wsl', 'eorp')

if os.path.exists(_7z_file):
  zstd_extract = [_7z_bin, 'x', _7z_file, '-owsl', '-y']
  RunCommand(zstd_extract)
else:
  logger.info(f"Aborting [{_7z_file}] not found!!")
  sys.exit(1)


if not os.path.isdir(installation_dir):
  mkdir(installation_dir)

if os.path.exists(tar_file):
  # wsl --import <Distro> <InstallLocation> <FileName> --version <Version>
  wsl_install = ['wsl', '--import', 'eorp_test',
                 installation_dir, tar_file, '--version', '1']
  RunCommand(wsl_install)
  if os.path.exists(tar_file):
    remove(tar_file)
else:
  logger.info(f"Aborting [{tar_file}] not found!!")
  sys.exit(1)
