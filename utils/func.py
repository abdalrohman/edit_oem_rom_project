#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# File Name    :   utils.py
# Created Time :   2022/11/09 17:22:25
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
import shutil
import subprocess
import sys
import time

from loguru import logger


def check_arch():
  """Check os architecture

  Returns:
      string: architecture
  """
  if platform.machine() == "aarch64":
    return "ARM64"
  elif platform.machine() == "x86_64":
    return "AMD64"
  else:
    return platform.machine()


def init_log(log_file=None):
  """Initiate log file

  Args:
      log_file (path): Defaults to None.
  """
  if log_file is not None:
    config = {
      "handlers": [
        {"sink": log_file,
         "format": "[{time:HH:mm:ss}] [{function}|{name}|{file}|{line}] took {elapsed} :: {message} ", 'backtrace': 'True', 'diagnose': 'True', 'enqueue': 'True', 'rotation': "12:00"
         },
        {"sink": sys.stdout,
         "format": "<g>[{time:HH:mm:ss}]</g> <level>{message}</level>", 'level': 'INFO'}
      ]
    }
    logger.configure(**config)
  else:
    config = {
      "handlers": [
        {"sink": sys.stdout,
         "format": "<g>[{time:HH:mm:ss}]</g> <level>{message}</level>", 'level': 'INFO'}
      ]
    }
    logger.configure(**config)


def RunCommand(arg, verbose=True, **kwargs):
  """Runs the given command and returns the output.

  Args:
    arg: The command represented as a list of strings.
    verbose: Whether the commands should be shown. Default True.
    kwargs: Any additional args to be passed to subprocess.Popen(), such as env,
        stdin, etc. stdout and stderr will default to subprocess.PIPE and
        subprocess.STDOUT respectively unless caller specifies any of them.

  Returns:
    string: output.

  Raises:
    RuntimeError: On non-zero exit from the command.
  """
  start_time = time.time()
  if verbose:
    logger.info("Running: {}", " ".join(arg))

  if 'stdout' not in kwargs and 'stderr' not in kwargs:
    kwargs['stdout'] = subprocess.PIPE
    kwargs['stderr'] = subprocess.STDOUT
  if 'universal_newlines' not in kwargs:
    kwargs['universal_newlines'] = True

  proc = subprocess.Popen(arg, **kwargs)
  try:
    output, _ = proc.communicate()
  except KeyboardInterrupt:
    logger.info("\nTerminating...")
    sys.exit(1)

  runtime = (time.time() - start_time)
  if verbose:
    logger.info("Excution time: {} seconds", runtime)

  if output is None:
    output = ""

  if proc.returncode != 0:
    logger.exception(
      "Failed to run command '{}' (exit code {}):\n{}", " ".join(
        arg), proc.returncode, output
    )
    sys.exit(proc.returncode)

  return output, proc.returncode


def mkdir(dir_name):
  """like mkdir -p in gnu linux.
  ex: mkdir('test/1/2/3')

  Args:
      dir_name (dir_name): Specify directory name.
  """
  if not os.path.exists(dir_name):
    logger.info("Create [{}]", dir_name)
    os.makedirs(dir_name)
    return 0
  return 1


def rmdir(dir_name):
  """Remove directory

  Args:
      dir_name (dir_name): Specify directory name.
  """
  if os.path.exists(dir_name):
    logger.info("Remove dir [{}]", dir_name)
    shutil.rmtree(dir_name, ignore_errors=True)
    return 0
  return 1


def remove(file_name):
  """Remove file

  Args:
      dir_name (file_name): Specify file name.
  """
  if os.path.exists(file_name):
    logger.info("Remove file [{}]", file_name)
    os.remove(file_name)
    return 0
  return 1


def dir_size(path, verbose_mode=False):
  """Returns the number of bytes that "path" occupies on host.
  :param path: The directory or file to calculate size on.
  :return: The number of bytes based on a 1K block_size.
  """
  if verbose_mode:
    print(f"Calculate size of {path}")

  cmd = ["du", "-b", "-k", "-s", path]
  output = RunCommand(cmd, verbose=False)
  return int(output[0].split()[0]) * 1024


def count(path, verbose_mode=False):
  """Returns count of files and dirs in "path".
  :param path: The directory or file to calculate size on.
  :return: The number files and dirs.
  """
  if verbose_mode:
    print(f"Calculate file count in {path}")

  count = 0
  # Iterate directory
  for root_dir, cur_dir, files in os.walk(rf'{path}'):
    count += len(files)
    count += len(cur_dir)

  return count


def cat(in_file, out_file):
  """Work like cat command in gnu"""
  with open(in_file, 'r', encoding='UTF-8') as file:
    lines = file.read()

  with open(out_file, 'a', encoding='UTF-8') as file:
    file.write(lines)
