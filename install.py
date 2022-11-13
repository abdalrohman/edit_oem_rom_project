#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# File Name    :   install.py
# Created Time :   2022/11/13 02:40:36
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
import platform
import re
import sys
import time
from pathlib import Path

from utils.config import load_config
from utils.func import RunCommand, init_log
from utils.print_wrapper import print


# initiat logs
init_log('./logs/Log.log')


def in_wsl() -> bool:
  """Check if running on wsl"""
  if re.search(r'microsoft-standard-WSL2', platform.uname().release):
    return True
  elif re.search(r'.*-Microsoft', platform.uname().release):
    return True

  return False


def is_win() -> bool:
  """Check if running on windows"""
  if re.search(r'Windows', platform.uname().system):
    return True

  return False


def is_linux() -> bool:
  """Check if running on linux"""
  if re.search(r'Linux', platform.uname().system):
    return True

  return False


if is_linux():
  if in_wsl():
    print("Running on wsl")
    fastboot = load_config('LINUX', 'fastboot_wsl')
    pass
  else:
    print("Running on linux")
    fastboot = load_config('LINUX', 'fastboot')
    pass

if is_win():
  print("Not support win try to run on wsl")
  sys.exit(1)

# start_time
start_time = time.time()

source_dir = os.path.join(load_config('MAIN', 'main_project'), "source")
build_dir = os.path.join(load_config('MAIN', 'main_project'), 'Build')
PARTITIONS = load_config('MAIN', 'partitions').split(' ')
OTHER_PART = "boot dtbo vbmeta vbmeta_system".split()

if not os.path.isfile(fastboot):
  sys.exit(1)

for part in PARTITIONS:
  for path in Path(build_dir).rglob(f'{part}.img'):
    RunCommand([fastboot, 'flash', part, str(path)],
               verbose=True, stdout=sys.stdout)


for part in OTHER_PART:
  for path in Path(source_dir).rglob(f'{part}.img'):
    RunCommand([fastboot, 'flash', part, str(path)],
               verbose=True, stdout=sys.stdout)


print(
  "It will delete all your files and photos stored on internal storage.\n\ttype [y] to confirm!! \n\tpress Enter/any key to exit!!",
  tag="[Dangerous]",
  tag_color="red",
  color="white"
)
ans = input("")
if ans.lower() == 'y':
  RunCommand([fastboot, 'erase', 'metadata'], verbose=True)
  RunCommand([fastboot, 'erase', 'userdata'], verbose=True)

ans = input("If you want to reboot [y/n]")
reboot = input("Reboot to system[s] or rycovery[r]?")
if ans.lower() == 'y':
  if reboot.lower() == 's':
    RunCommand([fastboot, 'reboot'], verbose=True)
  elif reboot.lower() == 'r':
    RunCommand([fastboot, 'reboot', 'recovery'], verbose=True)

runtime = (time.time() - start_time)

print("")
print("")
print("")
print("")
print(f"Total Excution time: {runtime} seconds",
      color="white", tag="[SUCCESS]", tag_color="green")
