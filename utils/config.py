#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# File Name    :   config.py
# Created Time :   2022/11/09 17:22:38
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

import configparser

from loguru import logger

from utils.func import check_arch


def __write_config(section, data, config_file='config.ini'):
  """open config.ini to write data"""
  config = configparser.ConfigParser(delimiters=':')
  config.read(config_file)

  config[section] = data

  with open(config_file, 'w') as configfile:  # pylint: disable=W1514
    config.write(configfile)

  return 0


def update_config(section, data, config_file='config.ini'):
  """Update config in config.ini"""
  config = configparser.ConfigParser(delimiters=':')
  config.read(config_file)

  if config.has_section(section):
    for key, value in data.items():
      config.set(section, key, value)

    with open(config_file, 'w') as configfile:  # pylint: disable=W1514
      config.write(configfile)
    return 0
  else:
    logger.info(f'Not found section {section} in {config_file}')
    exit(1)


def load_config(section, key, config_file='config.ini'):
  """Load config from config.ini"""
  config = configparser.ConfigParser(delimiters=':')
  config.read(config_file)
  value = config[section].get(key)

  return value


def write_default_config():
  """write default config"""

  main = {
    'main_project': 'Projects/',
    'partitions': 'odm system vendor product system_ext cust odm_a vendor_a product_a system_ext_a system_a odm_dlkm vendor_dlkm my_bigball my_carrier my_engineering my_heytap my_manifest my_product my_region my_stock odm_dlkm_a vendor_dlkm_a my_bigball_a my_carrier_a my_engineering_a my_heytap_a my_manifest_a my_product_a my_region_a my_stock_a',
    'proj_folders': 'Config Build Backup Source Output'
  }

  if check_arch() == "AMD64":
    linux = {
      'brotli': 'bin/amd64/brotli',
      'payload': 'bin/amd64/payload-dumper-go',
      'mke2fs': 'bin/amd64/mke2fs',
      'mke2fs_conf': 'bin/amd64/mke2fs.conf',
      'e2fsdroid': 'bin/amd64/e2fsdroid',
      'img2simg': 'bin/amd64/img2simg',
      'simg2img': 'bin/amd64/simg2img',
      'lpunpack': 'bin/amd64/lpunpack',
      'fastboot': 'bin/amd64/fastboot',
      'fastboot_wsl': 'bin/amd64/fastboot.exe',
      'erofs': 'bin/amd64/extract.erofs',
    }
  elif check_arch() == "ARM64":
    linux = {
      'brotli': 'bin/arm64/brotli',
      'payload': 'bin/arm64/payload-dumper-go',
      'mke2fs': 'bin/arm64/mke2fs',
      'mke2fs_conf': 'bin/arm64/mke2fs.conf',
      'e2fsdroid': 'bin/arm64/e2fsdroid',
      'img2simg': 'bin/arm64/img2simg',
      'simg2img': 'bin/arm64/simg2img',
      'lpunpack': 'bin/arm64/lpunpack',
      'erofs': 'bin/arm64/extract.erofs',
    }

  bash = {
    'check_sparse': 'bin/bash/check_sparse',
  }

  python = {
    'ext4_info': 'bin/python/ext4_info.py',
    'erofs_info': 'bin/python/erofs_info.py',
    'extract_ext4': 'bin/python/extract_ext4.py',
    'img2sdat': 'bin/python/img2sdat/img2sdat.py',
    'sdat2img': 'bin/python/sdat2img.py',
    'check_super_erofs': 'bin/python/check_super_erofs.py'
  }

  __write_config('MAIN', main)
  __write_config('LINUX', linux)
  __write_config('BASH', bash)
  __write_config('PYTHON', python)
