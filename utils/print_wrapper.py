#!/usr/bin/env python3
# -*-coding:utf-8 -*-
# File Name    :   print_wrapper.py
# Created Time :   2022/11/12 09:40:23
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
import builtins
import sys


class PrintClass:
  """Wrapper for print method to display color on shell"""

  def __init__(self, *args, **kwargs) -> None:
    self.args = args
    self.kwargs = kwargs

  __colors = {
    "purple": "\033[95m",
    "blue": "\033[94m",
    "green": "\033[92m",
    "yellow": "\033[33m",
    "red": "\033[31m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "black": "\033[30m",
    "white": "\033[37m",
  }

  __formats = {
    "bold": "\033[1m",
    "underline": "\033[4m",
    "blink": "\033[5m"
  }

  @property
  def __color_off(self):
    """Reset color in shell"""
    return "\033[0m"

  def __color(self, color):
    """Return the color from list colors or use default"""
    return self.__colors.get(color, self.__color_off)

  def __format_text(self, fmt: str):
    """Format text"""
    return self.__formats.get(fmt, self.__color_off)

  def print(self):
    """Print method"""
    color = self.kwargs.pop("color", None)
    tag = self.kwargs.pop("tag", None)
    tag_color = self.kwargs.pop("tag_color", None)
    fmt = self.kwargs.pop("format", None)

    for arg in self.args:
      # text input
      result = "".join(str(arg))

    if color:
      result = self.__color(color) + result

    if tag:
      result = f"{tag} {result}"

    if tag_color:
      result = self.__color(tag_color) + result

    if fmt:
      builtins.print(self.__format_text(fmt), file=sys.stdout, end="")

    result += self.__color_off
    builtins.print(result, **self.kwargs)


def print(*args, **kwargs):  # pylint: disable=W0622
  """Print Wrapper

  Args:
    arg: text input.
    kwargs: Any additional args to be passed to print().

  """
  printcolor = PrintClass(*args, **kwargs)
  printcolor.print()
