"""Tests for load_dataset_from_excel function."""

import os
import json
import tempfile
import pytest
import pandas as pd
from pathlib import Path

from staffer.functions.load_dataset_from_excel import load_dataset_from_excel


def test_load_dataset_from_excel_success():
    """Test successful loading of Excel data into analytics memory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test Excel file with pandas
        test_data = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'product': ['Widget A', 'Widget B', 'Widget A'], 
            'revenue': [100.0, 150.0, 120.0]
        })
        
        excel_file = os.path.join(temp_dir, 'sales.xlsx')
        test_data.to_excel(excel_file, sheet_name='Q1_Sales', index=False)
        
        # Test the function
        result_str = load_dataset_from_excel(
            working_directory=temp_dir,
            file_path='sales.xlsx',
            dataset_name='excel_data',
            sheet_name='Q1_Sales'
        )
        
        # Parse the result
        result = json.loads(result_str)
        
        # Verify the result
        assert result['status'] == 'loaded'
        assert result['dataset_name'] == 'excel_data'
        assert result['source_file'] == 'sales.xlsx'
        assert result['sheet_name'] == 'Q1_Sales'
        assert result['rows'] == 3
        assert result['columns'] == ['date', 'product', 'revenue']
        assert result['format'] == 'excel'


def test_load_dataset_from_excel_default_sheet():
    """Test loading Excel data with default sheet name."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test Excel file
        test_data = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['A', 'B', 'C']
        })
        
        excel_file = os.path.join(temp_dir, 'test.xlsx')
        test_data.to_excel(excel_file, index=False)  # Default sheet name is 'Sheet1'
        
        # Test with sheet_name=None (should use default)
        result_str = load_dataset_from_excel(
            working_directory=temp_dir,
            file_path='test.xlsx',
            dataset_name='test_data'
        )
        
        result = json.loads(result_str)
        assert result['status'] == 'loaded'
        assert result['sheet_name'] == 'Sheet1'


def test_load_dataset_from_excel_file_not_found():
    """Test error handling when Excel file doesn't exist."""
    with tempfile.TemporaryDirectory() as temp_dir:
        result = load_dataset_from_excel(
            working_directory=temp_dir,
            file_path='nonexistent.xlsx',
            dataset_name='test_data'
        )
        
        assert "Error:" in result
        assert "does not exist" in result


def test_load_dataset_from_excel_invalid_sheet():
    """Test error handling when sheet doesn't exist."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test Excel file
        test_data = pd.DataFrame({'col1': [1, 2, 3]})
        excel_file = os.path.join(temp_dir, 'test.xlsx')
        test_data.to_excel(excel_file, index=False)
        
        result = load_dataset_from_excel(
            working_directory=temp_dir,
            file_path='test.xlsx',
            dataset_name='test_data',
            sheet_name='NonExistentSheet'
        )
        
        assert "Error:" in result
        assert "not found in workbook" in result


def test_load_dataset_from_excel_security_validation():
    """Test security validation prevents access outside working directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        result = load_dataset_from_excel(
            working_directory=temp_dir,
            file_path='../malicious.xlsx',
            dataset_name='test_data'
        )
        
        assert "Error:" in result
        assert "outside the permitted working directory" in result


def test_load_dataset_from_excel_analytics_persistence():
    """Test that dataset is properly persisted in analytics directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test Excel file
        test_data = pd.DataFrame({
            'id': [1, 2, 3],
            'value': [10, 20, 30]
        })
        
        excel_file = os.path.join(temp_dir, 'test.xlsx')
        test_data.to_excel(excel_file, index=False)
        
        # Load dataset
        result_str = load_dataset_from_excel(
            working_directory=temp_dir,
            file_path='test.xlsx',
            dataset_name='persistent_data'
        )
        
        result = json.loads(result_str)
        assert result['status'] == 'loaded'
        
        # Verify analytics directory structure was created
        analytics_dir = os.path.join(temp_dir, '.staffer_analytics')
        assert os.path.exists(analytics_dir)
        assert os.path.exists(os.path.join(analytics_dir, 'datasets'))
        assert os.path.exists(os.path.join(analytics_dir, 'schemas'))
        
        # Verify dataset file was created
        dataset_file = os.path.join(analytics_dir, 'datasets', 'persistent_data.csv')
        assert os.path.exists(dataset_file)
        
        # Verify schema file was created
        schema_file = os.path.join(analytics_dir, 'schemas', 'persistent_data.json')
        assert os.path.exists(schema_file)


def test_load_dataset_from_excel_empty_dataset_name():
    """Test error handling for empty dataset name."""
    with tempfile.TemporaryDirectory() as temp_dir:
        result = load_dataset_from_excel(
            working_directory=temp_dir,
            file_path='test.xlsx',
            dataset_name=''
        )
        
        assert "Error:" in result
        assert "dataset_name cannot be empty" in result


def test_load_dataset_from_excel_empty_headers():
    """Test error handling for Excel with no valid headers."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create Excel file with empty headers
        test_data = pd.DataFrame({
            None: [1, 2, 3],
            '': [4, 5, 6]
        })
        
        excel_file = os.path.join(temp_dir, 'empty_headers.xlsx')
        test_data.to_excel(excel_file, index=False)
        
        result = load_dataset_from_excel(
            working_directory=temp_dir,
            file_path='empty_headers.xlsx',
            dataset_name='test_data'
        )
        
        assert "Error:" in result
        assert "no valid column headers" in result