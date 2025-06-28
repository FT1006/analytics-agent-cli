"""Tests for load_dataset analytic function."""

import pytest
import os
import tempfile
import json
import pandas as pd

from staffer.functions.load_dataset import load_dataset


class TestLoadDataset:
    """Test suite for load_dataset function."""
    
    def test_load_csv_dataset_success(self):
        """Test loading a CSV dataset successfully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test CSV file
            test_data = pd.DataFrame({
                'name': ['Alice', 'Bob', 'Charlie'],
                'age': [25, 30, 35],
                'city': ['NY', 'LA', 'Chicago']
            })
            csv_file = os.path.join(temp_dir, 'test_data.csv')
            test_data.to_csv(csv_file, index=False)
            
            # Load dataset
            result = load_dataset(temp_dir, 'test_data.csv', 'customers')
            
            # Parse JSON result
            result_dict = json.loads(result)
            
            # Verify success
            assert result_dict['status'] == 'loaded'
            assert result_dict['dataset_name'] == 'customers'
            assert result_dict['rows'] == 3
            assert result_dict['columns'] == ['name', 'age', 'city']
            assert result_dict['format'] == 'csv'
            
            # Verify state directory was created
            analytics_dir = os.path.join(temp_dir, '.staffer_analytics')
            assert os.path.exists(analytics_dir)
            
            # Verify dataset was saved
            saved_dataset = os.path.join(analytics_dir, 'datasets', 'customers.csv')
            assert os.path.exists(saved_dataset)
            
            # Verify schema was saved
            saved_schema = os.path.join(analytics_dir, 'schemas', 'customers.json')
            assert os.path.exists(saved_schema)
            
    def test_load_dataset_file_outside_working_directory(self):
        """Test security: reject files outside working directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try to access file outside working directory
            result = load_dataset(temp_dir, '../secret.csv', 'hack')
            
            # Should return error
            assert 'Error: Cannot access' in result
            assert 'outside the permitted working directory' in result
            
    def test_load_dataset_file_not_found(self):
        """Test error handling for non-existent file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = load_dataset(temp_dir, 'nonexistent.csv', 'missing')
            
            # Should return error
            assert 'Error:' in result