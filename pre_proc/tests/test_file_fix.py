"""
test_file_fix.py

Unit tests for all FileFix concrete classes from file_fix.py
"""
import subprocess
import unittest

import mock

from pre_proc.exceptions import (AttributeNotFoundError,
                                 AttributeConversionError,
                                 ExistingAttributeError,
                                 InstanceVariableNotDefinedError)
from pre_proc.file_fix import (ParentBranchTimeDoubleFix,
                               ChildBranchTimeDoubleFix,
                               FurtherInfoUrlToHttps,
                               ParentBranchTimeAdd,
                               ChildBranchTimeAdd,
                               CellMeasuresAreacellaAdd,
                               CellMethodsAreaTimeMeanAdd)


class BaseTest(unittest.TestCase):
    """ Base class to setup a typical environment used by other tests """
    def setUp(self):
        """ Set up code run before every test """
        # mock any external calls
        patch = mock.patch('pre_proc.common.subprocess.check_output')
        self.mock_subprocess = patch.start()
        self.addCleanup(patch.stop)

        class MockedNamespace(object):
            def __exit__(self, *args):
                pass

            def __enter__(self):
                return self

        patch = mock.patch('pre_proc.file_fix.Dataset')
        self.mock_dataset = patch.start()
        self.mock_dataset.return_value = MockedNamespace()
        self.addCleanup(patch.stop)


class TestParentBranchTimeDoubleFix(BaseTest):
    """ Test ParentBranchTimeDoubleFix """
    def test_no_attribute_raises(self):
        """ Test if the required attribute isn't found in the netCDF """
        fix = ParentBranchTimeDoubleFix('1.nc', '/a')
        exception_text = ('Cannot find attribute branch_time_in_parent in '
                          'file 1.nc')
        self.assertRaisesRegexp(AttributeNotFoundError, exception_text,
                                fix.apply_fix)

    def test_wrong_attribute_type_raises(self):
        """ Test if the required attribute can't be converted """
        self.mock_dataset.return_value.branch_time_in_parent = 'pure_text'
        fix = ParentBranchTimeDoubleFix('1.nc', '/a')
        exception_text = ('Cannot convert attribute branch_time_in_parent to '
                          'new type float in file 1.nc')
        self.assertRaisesRegexp(AttributeConversionError, exception_text,
                                fix.apply_fix)

    def test_no_attribute_name_raises(self):
        """ Test whether missing attribute_name handled """
        self.mock_dataset.return_value.branch_time_in_parent = '1080.0'
        fix = ParentBranchTimeDoubleFix('1.nc', '/a')
        exception_text = ('ParentBranchTimeDoubleFix: attribute '
                          'attribute_name is not defined')
        fix._get_existing_value()
        fix._calculate_new_value()
        fix.attribute_name = None
        self.assertRaisesRegexp(InstanceVariableNotDefinedError,
                                exception_text, fix._run_ncatted)

    def test_no_visibility_raises(self):
        """ Test whether missing visibility handled """
        self.mock_dataset.return_value.branch_time_in_parent = '1080.0'
        fix = ParentBranchTimeDoubleFix('1.nc', '/a')
        fix.attribute_visibility = None
        exception_text = ('ParentBranchTimeDoubleFix: attribute '
                          'attribute_visibility is not defined')
        self.assertRaisesRegexp(InstanceVariableNotDefinedError,
                                exception_text, fix.apply_fix)

    def test_no_new_value_raises(self):
        """ Test whether missing new_value handled """
        self.mock_dataset.return_value.branch_time_in_parent = '1080.0'
        fix = ParentBranchTimeDoubleFix('1.nc', '/a')
        exception_text = ('ParentBranchTimeDoubleFix: attribute '
                          'new_value is not defined')
        fix._get_existing_value()
        fix._calculate_new_value()
        fix.new_value = None
        self.assertRaisesRegexp(InstanceVariableNotDefinedError,
                                exception_text, fix._run_ncatted)

    def test_subprocess_called_correctly(self):
        """
        Test that an external call's been made correctly for
        ParentBranchTimeDoubleFix
        """
        self.mock_dataset.return_value.branch_time_in_parent = '1080.0'
        fix = ParentBranchTimeDoubleFix('1.nc', '/a')
        fix.apply_fix()
        self.mock_subprocess.assert_called_once_with(
            'ncatted -h -a branch_time_in_parent,global,o,d,1080.0 '
            '/a/1.nc',
            stderr=subprocess.STDOUT,
            shell=True
        )


class TestChildBranchTimeDoubleFix(BaseTest):
    """ Test ChildBranchTimeDoubleFix """
    def test_no_attribute_raises(self):
        """ Test if the required attribute isn't found in the netCDF """
        fix = ChildBranchTimeDoubleFix('1.nc', '/a')
        exception_text = ('Cannot find attribute branch_time_in_child in '
                          'file 1.nc')
        self.assertRaisesRegexp(AttributeNotFoundError, exception_text,
                                fix.apply_fix)

    def test_wrong_attribute_type_raises(self):
        """ Test if the required attribute can't be converted """
        self.mock_dataset.return_value.branch_time_in_child = 'pure_text'
        fix = ChildBranchTimeDoubleFix('1.nc', '/a')
        exception_text = ('Cannot convert attribute branch_time_in_child to '
                          'new type float in file 1.nc')
        self.assertRaisesRegexp(AttributeConversionError, exception_text,
                                fix.apply_fix)

    def test_subprocess_called_correctly(self):
        """
        Test that an external call's been made correctly for
        ChildBranchTimeDoubleFix
        """
        self.mock_dataset.return_value.branch_time_in_child = '0.0'
        fix = ChildBranchTimeDoubleFix('1.nc', '/a')
        fix.apply_fix()
        self.mock_subprocess.assert_called_once_with(
            'ncatted -h -a branch_time_in_child,global,o,d,0.0 '
            '/a/1.nc',
            stderr=subprocess.STDOUT,
            shell=True
        )


class TestFurtherInfoUrlToHttps(BaseTest):
    """ Test FurtherInfoUrlToHttps """
    def test_no_attribute_raises(self):
        """ Test if the required attribute isn't found in the netCDF """
        fix = FurtherInfoUrlToHttps('1.nc', '/a')
        exception_text = ('Cannot find attribute further_info_url in '
                          'file 1.nc')
        self.assertRaisesRegexp(AttributeNotFoundError, exception_text,
                                fix.apply_fix)

    def test_not_http(self):
        """ Test exception is raised if it doesn't start with http """
        self.mock_dataset.return_value.further_info_url = 'https://a.url/'
        fix = FurtherInfoUrlToHttps('1.nc', '/a')
        exception_text = ('Existing further_info_url attribute does not start '
                          'with http:')
        self.assertRaisesRegexp(ExistingAttributeError, exception_text,
                                fix.apply_fix)

    def test_subprocess_called_correctly_further_info_url(self):
        """
        Test that an external call's been made correctly for
        FurtherInfoUrlToHttps
        """
        self.mock_dataset.return_value.further_info_url = (
            'http://furtherinfo.es-doc.org/part1.part2'
        )
        fix = FurtherInfoUrlToHttps('1.nc', '/a')
        fix.apply_fix()
        self.mock_subprocess.assert_called_once_with(
            "ncatted -h -a further_info_url,global,o,c,"
            "'https://furtherinfo.es-doc.org/part1.part2' "
            "/a/1.nc",
            stderr=subprocess.STDOUT,
            shell=True
        )


class TestParentBranchTimeAdd(BaseTest):
    """ Test ParentBranchTimeAdd """
    def test_subprocess_called_correctly(self):
        """
        Test that an external call's been made correctly for
        ParentBranchTimeAdd
        """
        fix = ParentBranchTimeAdd('1.nc', '/a')
        fix.apply_fix()
        self.mock_subprocess.assert_called_once_with(
            'ncatted -h -a branch_time_in_parent,global,o,d,0.0 '
            '/a/1.nc',
            stderr=subprocess.STDOUT,
            shell=True
        )


class TestChildBranchTimeAdd(BaseTest):
    """ Test ChildBranchTimeAdd """
    def test_subprocess_called_correctly(self):
        """
        Test that an external call's been made correctly for
        ChildBranchTimeAdd
        """
        fix = ChildBranchTimeAdd('1.nc', '/a')
        fix.apply_fix()
        self.mock_subprocess.assert_called_once_with(
            'ncatted -h -a branch_time_in_child,global,o,d,0.0 '
            '/a/1.nc',
            stderr=subprocess.STDOUT,
            shell=True
        )


class TestCellMeasuresAreacellaAdd(BaseTest):
    """ Test CellMeasuresAreacellaAdd """
    def test_subprocess_called_correctly(self):
        """
        Test that an external call's been made correctly for
        CellMeasuresAreacellaAdd
        """
        fix = CellMeasuresAreacellaAdd('tas_components.nc', '/a')
        fix.apply_fix()
        self.mock_subprocess.assert_called_once_with(
            "ncatted -h -a cell_measures,tas,o,c,'area: areacella' "
            "/a/tas_components.nc",
            stderr=subprocess.STDOUT,
            shell=True
        )


class TestCellMethodsAreaTimeMeanAdd(BaseTest):
    """ Test CellMethodsAreaTimeMeanAdd """
    def test_subprocess_called_correctly(self):
        """
        Test that an external call's been made correctly for
        CellMethodsAreaTimeMeanAdd
        """
        fix = CellMethodsAreaTimeMeanAdd('tas_components.nc', '/a')
        fix.apply_fix()
        self.mock_subprocess.assert_called_once_with(
            "ncatted -h -a cell_methods,global,o,c,'area: time: mean' "
            "/a/tas_components.nc",
            stderr=subprocess.STDOUT,
            shell=True
        )


if __name__ == '__main__':
    unittest.main()
