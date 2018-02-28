"""
file_fix.py

The workers that fix the netCDF files
"""
from abc import ABCMeta, abstractmethod
import os

from netCDF4 import Dataset

from pre_proc.common import run_command
from pre_proc.exceptions import (AttributeNotFoundError,
                                     AttributeConversionError)


class FileFix(object):
    """
    The abstract base class that all fixes are made from
    """
    __metaclass__ = ABCMeta

    def __init__(self, filename, directory):
        """
        Initialise the class

        :param list filename: The basename of the file to process.
        :param str directory: The directory that the file is currently in.
        """
        self.filename = filename
        self.directory = directory

    @abstractmethod
    def apply_fix(self):
        pass


class AttEdFix(FileFix):
    """
    An abstract base class for fixes that require the use of `ncatted` to
    fix a metadata attribute.
    """
    __metaclass__ = ABCMeta

    def __init__(self, filename, directory):
        """
        Initialise the class
        """
        super(AttEdFix, self).__init__(filename, directory)
        # The name of the attribute to fix
        self.attribute_name = None
        # The var_nm to pass to ncatted, e.g. global for a global
        # attribute
        self.attribute_visibility = None
        # The var_nm to pass to ncatted, e.g. global for a global
        # attribute
        self.attribute_type = None

        # The current and replacement values of the required attributes
        self.existing_value = None
        self.new_value = None

    def apply_fix(self):
        """
        Fix the specified attribute on the file
        """
        self._get_existing_value()
        self._calculate_new_value()
        self._run_ncatted()

    def _get_existing_value(self):
        """
        Get the value of the existing attribute from the current file
        """
        filepath = os.path.join(self.directory, self.filename)
        with Dataset(filepath) as rootgrp:
            self.existing_value = getattr(rootgrp, self.attribute_name, None)

        if self.existing_value is None:
            raise AttributeNotFoundError(self.filename, self.attribute_name)

    @abstractmethod
    def _calculate_new_value(self):
        """
        From the existing value of the attribute, calculate the new value
        """
        pass

    def _run_ncatted(self):
        """
        Run the command

        :param str filename: The name of the input file to fix
        """
        # Aiming for:
        # ncatted -h -a branch_time_in_parent,global,o,d,10800.0
        cmd = 'ncatted -h -a {},{},{},{},{} {}'.format(
            self.attribute_name,
            self.attribute_visibility,
            'o',
            self.attribute_type,
            self.new_value,
            os.path.join(self.directory, self.filename)
        )
        run_command(cmd)


class ParentBranchTimeDoubleFix(AttEdFix):
    """
    Make the global attribute `branch_time_in_parent` a double
    """
    def __init__(self, filename, directory):
        """
        Initialise the class

        :param str filename: The basename of the file to process.
        :param str directory: The directory that the file is currently in.
        """
        super(ParentBranchTimeDoubleFix, self).__init__(filename, directory)
        self.attribute_name = 'branch_time_in_parent'
        self.attribute_visibility = 'global'
        self.attribute_type = 'd'

    def _calculate_new_value(self):
        """
        The new value is the existing string converted to a double.

        :param str filename: The name of the input file to fix
        """
        try:
            self.new_value = float(self.existing_value)
        except ValueError:
            raise AttributeConversionError(self.attribute_name, 'float',
                                           self.filename)


class ChildBranchTimeDoubleFix(AttEdFix):
    """
    Make the global attribute `branch_time_in_child` a double
    """
    def __init__(self, filename, directory):
        """
        Initialise the class

        :param list filename: The basename of the file to process.
        :param str directory: The directory that the file is currently in.
        """
        super(ChildBranchTimeDoubleFix, self).__init__(filename, directory)
        self.attribute_name = 'branch_time_in_child'
        self.attribute_visibility = 'global'
        self.attribute_type = 'd'

    def _calculate_new_value(self):
        """
        The new value is the existing string converted to a double.

        :param str filename: The name of the input file to fix
        """
        try:
            self.new_value = float(self.existing_value)
        except ValueError:
            raise AttributeConversionError(self.attribute_name, 'float',
                                           self.filename)
