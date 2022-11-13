#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# File Name    :   test_print_wrapper.py
# Created Time :   2022/11/12 10:50:29
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
import sys
from io import StringIO

from utils.print_wrapper import print

default_ending = "\x1b[0m\n"


def test_print_with_no_args():
  capturedOutput = StringIO()
  sys.stdout = capturedOutput
  print("print with no args")
  assert capturedOutput.getvalue() == "print with no args" + default_ending
  sys.stdout = sys.__stdout__


def test_print_with_tag():
  capturedOutput = StringIO()
  sys.stdout = capturedOutput
  print("print with tag", tag="tag")
  assert capturedOutput.getvalue() == "[tag] print with tag" + default_ending
  sys.stdout = sys.__stdout__


def test_print_with_f_string():
  capturedOutput = StringIO()
  sys.stdout = capturedOutput
  f_string = "print with f-string"
  print(f"{f_string}")
  assert capturedOutput.getvalue() == "print with f-string" + default_ending
  sys.stdout = sys.__stdout__


test_print_with_no_args()
test_print_with_tag()
test_print_with_f_string()
