#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# File Name    :   extract_firmware.py
# Created Time :   2022/11/09 17:22:03
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

import glob
import gzip
import os
import re
import shutil
import zipfile

import zstandard
from loguru import logger

from utils.config import load_config, write_default_config
from utils.func import RunCommand, mkdir, remove, rmdir
from utils.print_wrapper import print

# tools #################
# generate config.ini if not exist
if not os.path.exists('./config.ini'):
  logger.info('Generate config.ini')
  write_default_config()

brotli = load_config('LINUX', 'brotli')
simg2img = load_config('LINUX', 'simg2img')
lpunpack = load_config('LINUX', 'lpunpack')
payload = load_config('LINUX', 'payload')
sdat2img = load_config('PYTHON', 'sdat2img')
PARTITIONS = load_config('MAIN', 'partitions').split(' ')

#########################


# functions #############
def extract_file_from_zip(input_zip, output, members=None):
  """extract some files from a zip file

  Args:
      input: input zip
      output: output folder
      members (optional): specify files to extract. Defaults to None.
  """
  try:
    logger.info('Extracting %s from %s to %s' % (members, input_zip, output))
    with zipfile.ZipFile(input_zip, 'r') as zf:
      zf.extractall(output, members=[members])
  except KeyError:
    logger.error("Can't extract %s from archive", members)


def zip_list(input_zip):
  """generate list of file in zip

  Args:
      input_zip: input zip

  Returns:
      list: sorted list
  """
  with zipfile.ZipFile(input_zip, 'r') as zf:
    list_files = zf.infolist()
    lf = []
    for f in list_files:
      lf.append(f.filename)
    return sorted(lf)


def gnuzip(input_zip, output):
  """Gunzips the given gzip compressed file to a given output file

  Args:
      input : input gzip file.
      output : output file.
  """
  with gzip.open(input_zip, "rb") as in_file, \
      open(output, "wb") as out_file:
    shutil.copyfileobj(in_file, out_file)


def zstd(input_zip, output):
  """Zstd the given zstd compressed file to a given output file

  Args:
      input : input gzip file.
      output : output file.
  """
  with zstandard.open(input_zip, "rb") as in_file, \
      open(output, "wb") as out_file:
    shutil.copyfileobj(in_file, out_file)


def extract_brotli(br_img, output):
  """Extract .br extention.

  must have [br_img.transfers.list] in the same directory

  Args:
      br_img : brotli image (eg: system.new.dat.br)
      output : output folder
  """
  # check if image.new.dat.br is exist befor converting
  if os.path.exists(br_img):
    basedir = os.path.realpath(os.path.dirname(br_img))
    output = os.path.realpath(output)
    sdat_img = br_img.split('.br')[0]
    img_name = os.path.basename(br_img).split('.')[0]
    # check if output folder exists (if not make it)
    if not os.path.exists(output):
      mkdir(output)

    logger.info("Convert %s.new.dat.br to %s.new.dat" % (img_name, img_name))
    cmd = [brotli, '-df', br_img]
    RunCommand(cmd)

    if os.path.exists(sdat_img):
      logger.info('Convertig %s.new.dat to %s.img' % (img_name, img_name))
      cmd = [
        'python', sdat2img, os.path.join(
          basedir, img_name+'.transfer.list'), sdat_img, os.path.join(output, img_name+'.img')
      ]
      RunCommand(cmd)

    if os.path.exists(os.path.join(output, img_name+'.img')):
      remove(br_img)
      remove(os.path.join(output, img_name+'.new.dat'))
      remove(os.path.join(output, img_name+'.transfer.list'))

  else:
    logger.info("Not found %s", br_img)


def extract_super_img(input_img, output, type_img='sparse'):
  """extract super img

  Args:
      input_img (_type_): img input
      output (_type_): output directory
      type_img (str, optional): _description_. Defaults to 'sparse'.
  """
  raw_img = os.path.join(output, "super.raw")
  check_sparse = os.path.join(load_config('BASH', 'check_sparse'))

  if type_img == 'sparse':
    cmd = ['bash', check_sparse, input_img]
    check_sparse = RunCommand(cmd)
    if check_sparse[0].strip() == "sparse":
      logger.info("Extracting sparse super image...")
      cmd = [simg2img, input_img, raw_img]
      RunCommand(cmd)
    else:
      os.rename(input_img, raw_img)

    if os.path.exists(raw_img):
      remove(input_img)  # cleanup after extract

  elif type_img == 'gz':
    logger.info("Extracting gzip super image...")
    gnuzip(input_img, raw_img)
    if os.path.exists(raw_img):
      remove(input_img)  # cleanup after extract

  elif type_img == 'zstd':
    logger.info("Extracting zstd super image...")
    zstd(input_img, raw_img)
    if os.path.exists(raw_img):
      remove(input_img)  # cleanup after extract

  elif type_img == 'brotli':
    logger.info("Extracting brotli super image...")
    extract_brotli(input_img, output)
    os.rename(os.path.join(output, 'super.img'),
              os.path.join(output, 'super.raw'))

  else:
    logger.info("Not supported yet.")

  # extract images from super.img
  try:
    logger.info("Extracting raw super image...")
    if os.path.exists(raw_img):
      cmd = [lpunpack, raw_img, output]
      RunCommand(cmd)
      remove(raw_img)  # cleanup after extract

  except:  # pylint: disable=W0702
    logger.error("Error when extracting raw super image...")
    exit(1)


def extract_payload(img, output):
  """Unpack payload.bin

  Args:
      img (_type_): input img
      output (_type_): out dir
  """
  cmd = [payload, '-o', output, img]
  RunCommand(cmd, verbose=False)
  remove(img)


def extract_fw(input_zip, output_folder):
  """Extract firmware

  Args:
      input_zip (_type_): input rom zip
      output_folder (_type_): out dir
  """
  list_images = []
  list_zip = zip_list(input_zip)
  br = False
  super_img = False
  chunck = False
  list_other = ['vbmeta_system', 'vbmeta', 'boot', 'dtbo']

  for lz in list_zip:
    if re.search(r"(super.*)", lz) is not None:  # super
      super_img = True
      list_images.append(lz)

    elif lz == 'payload.bin':
      extract_file_from_zip(input_zip, output_folder, members=lz)
      extract_payload(os.path.join(
        output_folder, 'payload.bin'), output_folder)

    elif re.search(r"(.*.br)", lz) is not None:
      br = True

    elif re.search(r"(.*.img)", lz) is not None:
      for part in PARTITIONS:
        if part+'.img' == lz:
          extract_file_from_zip(input_zip, output_folder, members=lz)

    else:
      continue

  if super_img:
    for s in list_images:
      if len(list_images) == 1:
        if re.search(r"(super.img.gz)", s) is not None:
          logger.info("Gzip super image detected.")
          extract_file_from_zip(input_zip, output_folder, members=s)
          extract_super_img(os.path.join(
            output_folder, s), output_folder, type_img='gz')

        if re.search(r"(super.img.zst)", s) is not None:
          logger.info("Zstd super image detected.")
          extract_file_from_zip(input_zip, output_folder, members=s)
          extract_super_img(os.path.join(
            output_folder, s), output_folder, type_img='zstd')

        elif re.search(r'super.img$', s) is not None:  # sparse
          logger.info("Sparse super image detected.")
          extract_file_from_zip(input_zip, output_folder, members=s)
          extract_super_img(os.path.join(
            output_folder, s), output_folder)

      elif len(list_images) > 1:
        if re.search(r"(super.new.dat.br)", s) is not None:
          logger.info("Brotli super image detected.")
          extract_file_from_zip(input_zip, output_folder,
                                members='super.new.dat.br')
          extract_file_from_zip(input_zip, output_folder,
                                members='super.transfer.list')

          extract_super_img(os.path.join(
            output_folder, 'super.new.dat.br'), output_folder, type_img='brotli')

        else:  # Sparsechunk super.img
          chunck = True

    if chunck:
      logger.info("Sparsechunk super image detected.")
      list_chunk = []

      for c in list_images:
        extract_file_from_zip(input_zip, output_folder, members=c)
        list_chunk.append(os.path.join(output_folder, c))

      # sort list chunk according to numirical part
      list_chunk.sort(key=lambda test_string: list(
        map(int, re.findall(r'\d+', test_string)))[0])

      # merg chunck super img
      cmd = [simg2img, *list_chunk, os.path.join(output_folder, 'super.img')]
      RunCommand(cmd)

      # remove chunks apfter merge to super.img
      for c in list_chunk:
        remove(c)

      # extract super.img
      extract_super_img(os.path.join(
        output_folder, 'super.img'), output_folder)

  if br:
    extracted_list = PARTITIONS

    logger.info("Brotli images detected.")
    for br_img in extracted_list:
      for in_zip in list_zip:
        if in_zip == br_img+'.new.dat.br':
          extract_file_from_zip(input_zip, output_folder, members=in_zip)
          extract_file_from_zip(input_zip, output_folder,
                                members=br_img+'.transfer.list')
          extract_brotli(os.path.join(output_folder, in_zip), output_folder)

  # extract other images from zip file
  for other in list_zip:
    for lo in list_other:
      if re.search(rf"({lo}.*)", other) is not None:
        extract_file_from_zip(input_zip, output_folder, members=other)


def extract_img(main_project):
  """"Extract super/erofs/ext4 images"""
  for part in PARTITIONS:
    ext4_info = os.path.join(load_config('PYTHON', 'ext4_info'))
    erofs_info = os.path.join(load_config('PYTHON', 'erofs_info'))
    extract_ext4 = os.path.join(load_config('PYTHON', 'extract_ext4'))
    erofs = os.path.join(load_config('LINUX', 'erofs'))
    check_super_erofs = os.path.join(
      load_config('PYTHON', 'check_super_erofs'))

    input_img = os.path.join(main_project, 'Source', part+'.img')
    info_dir = os.path.join(main_project, 'Config')
    out_dir = os.path.join(main_project, 'Output', part)
    source_dir = os.path.join(main_project, 'Source')

    # if type of img data try to extract super img with other name
    if os.path.isfile(input_img):
      cmd = ['python', check_super_erofs, input_img]
      check = RunCommand(cmd)

      if check[0].strip() == "super":
        extract_super_img(input_img, source_dir)

      elif check[0].strip() == "erofs":
        erofs_out = os.path.join(main_project, 'Output')
        logger.info("File system Type: {} :: erofs", input_img)
        logger.info("Extract {} to {}", input_img, erofs_out)
        cmd = [erofs, '-i', input_img, '-o', erofs_out, '-f', '-x']
        RunCommand(cmd, verbose=True)
        os.rename(os.path.join(erofs_out, 'config', part+'_file_contexts'),
                  os.path.join(info_dir, part+'_file_contexts.txt'))
        os.rename(os.path.join(erofs_out, 'config', part+'_fs_config'),
                  os.path.join(info_dir, part+'_filesystem_config.txt'))
        cmd = ['python', erofs_info, input_img, info_dir, erofs_out]
        RunCommand(cmd)
        remove(input_img)
        rmdir(os.path.join(erofs_out, 'config'))

      else:
        logger.info("File system Type: {} :: ext4", input_img)
        mkdir(out_dir)
        logger.info("Extract information {}", part)
        cmd = ['python', ext4_info, input_img, info_dir]
        RunCommand(cmd)
        logger.info("Extract {} to {}", input_img, out_dir)
        cmd = ['python', extract_ext4, input_img, out_dir]
        RunCommand(cmd)
        remove(input_img)


def display_rom_info(proj_dir: str):
  """Display rom info after extracted"""
  if not os.path.exists(proj_dir):
    return 1
  build_prop_path = []

  # find all build.prop files
  # if os.path.exists(os.path.join(f'{proj_dir}/odm')):
  #   for file in glob.glob(f"{proj_dir}/odm/**/build.prop", recursive=True):
  #     build_prop_path.append(file.strip())
  # elif os.path.exists(os.path.join(f'{proj_dir}/vendor')):
  #   for file in glob.glob(f"{proj_dir}/vendor/**/build.prop", recursive=True):
  #     build_prop_path.append(file.strip())

  # FIXME rename part_a to part on output folder
  out_dir = os.path.join(proj_dir, 'Output')
  list_output = os.listdir(out_dir)

  for part in list_output:
    if part.endswith('_a'):
      remove_suffix = os.path.join(out_dir, part.removesuffix('_a'))
      cmd = ['mv', os.path.join(out_dir, part), remove_suffix]
      RunCommand(cmd)

  if os.path.exists("".join(glob.glob(f"{proj_dir}/**/system"))):
    for file in glob.glob(f"{proj_dir}/**/system/build.prop", recursive=True):
      build_prop_path.append(file.strip())
  else:
    return 1

  # find ro.product.system.manufacturer=
  for prop_path in build_prop_path:
    # Open file
    with open(f'{prop_path}', 'r', encoding='UTF-8') as file:
      MANUFACTURER = re.search(r'.*manufacturer=(.*)', file.read())
      # close file
      file.close()

  for prop_path in build_prop_path:
    # Open file
    with open(f'{prop_path}', 'r', encoding='UTF-8') as file:
      # ro.product.odm.brand=
      BRAND = re.search(r'.*brand=(.*)', file.read())
      # close file
      file.close()

  for prop_path in build_prop_path:
    # Open file
    with open(f'{prop_path}', 'r', encoding='UTF-8') as file:
      # ro.product.odm.model=
      MODEL = re.search(r'.*model=(.*)', file.read())
      # close file
      file.close()

  # ro.product.odm.device=
  for prop_path in build_prop_path:
    # Open file
    with open(f'{prop_path}', 'r', encoding='UTF-8') as file:
      DEVICE = re.search(r'.*device=(.*)', file.read())
      # close file
      file.close()

  # # ro.build.product=
  # for prop_path in build_prop_path:
  #   # Open file
  #   with open(f'{prop_path}', 'r', encoding='UTF-8') as file:
  #     PRODUCT = re.search(r'.*product=(.*)', file.read())
  #     # close file
  #     file.close()

  # ro.system.build.date=
  for prop_path in build_prop_path:
    # Open file
    with open(f'{prop_path}', 'r', encoding='UTF-8') as file:
      BUILD_DATE = re.search(r'.*date=(.*)', file.read())
      # close file
      file.close()

  # ro.system.build.fingerprint=
  for prop_path in build_prop_path:
    # Open file
    with open(f'{prop_path}', 'r', encoding='UTF-8') as file:
      FINGERPRINT = re.search(r'.*fingerprint=(.*)', file.read())
      # close file
      file.close()

  # ro.build.version.security_patch=
  for prop_path in build_prop_path:
    # Open file
    with open(f'{prop_path}', 'r', encoding='UTF-8') as file:
      SECURITY_PATCH = re.search(r'.*security_patch=(.*)', file.read())
      # close file
      file.close()

  print("")
  print("")
  print("")
  print("")
  print(f"{MANUFACTURER.group(1) if MANUFACTURER is not None else MANUFACTURER}", tag="MANUFACTURER   ==>",
        tag_color="yellow", color="blue")
  print(f"{BRAND.group(1) if BRAND is not None else BRAND}", tag="BRAND          ==>",
        tag_color="yellow", color="blue")
  print(f"{MODEL.group(1) if MODEL is not None else MODEL}", tag="MODEL          ==>",
        tag_color="yellow", color="blue")
  # print(f"{PRODUCT.group(1) if PRODUCT is not None else PRODUCT}", tag="PRODUCT        ==>",
  #       tag_color="yellow", color="blue")
  print(f"{DEVICE.group(1) if DEVICE is not None else DEVICE}", tag="DEVICE         ==>",
        tag_color="yellow", color="blue")
  print(f"{BUILD_DATE.group(1) if BUILD_DATE is not None else BUILD_DATE}", tag="BUILD_DATE     ==>",
        tag_color="yellow", color="blue")
  print(f"{FINGERPRINT.group(1) if FINGERPRINT is not None else FINGERPRINT}", tag="FINGERPRINT    ==>",
        tag_color="yellow", color="blue")
  print(f"{SECURITY_PATCH.group(1) if SECURITY_PATCH is not None else SECURITY_PATCH}", tag="SECURITY_PATCH ==>",
        tag_color="yellow", color="blue")
