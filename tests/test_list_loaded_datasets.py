"""Tests for list_loaded_datasets analytic function."""

import pytest
import os
import tempfile
import json
import pandas as pd

from staffer.functions.list_loaded_datasets import list_loaded_datasets


class TestListLoadedDatasets:
    """Test suite for list_loaded_datasets function."""
    
    def test_list_loaded_datasets_empty(self):
        """Test listing when no datasets are loaded."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = list_loaded_datasets(temp_dir)
            result_dict = json.loads(result)
            
            assert result_dict['status'] == 'success'
            assert result_dict['datasets'] == []
            assert result_dict['total_datasets'] == 0
            
    def test_list_loaded_datasets_with_memory_state(self):
        """Test listing datasets from memory state."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Load some test datasets first
            from staffer.functions.load_dataset import load_dataset, loaded_datasets
            
            # Clear any existing state
            loaded_datasets.clear()
            
            # Create test data
            test_data1 = pd.DataFrame({
                'name': ['Alice', 'Bob'],
                'age': [25, 30]
            })
            test_data2 = pd.DataFrame({
                'product': ['A', 'B', 'C'],
                'price': [10, 20, 30],
                'category': ['X', 'Y', 'Z']
            })
            
            csv_file1 = os.path.join(temp_dir, 'users.csv')
            csv_file2 = os.path.join(temp_dir, 'products.csv')
            test_data1.to_csv(csv_file1, index=False)
            test_data2.to_csv(csv_file2, index=False)
            
            # Load datasets
            load_dataset(temp_dir, 'users.csv', 'users')
            load_dataset(temp_dir, 'products.csv', 'products')
            
            # Test listing
            result = list_loaded_datasets(temp_dir)
            result_dict = json.loads(result)
            
            assert result_dict['status'] == 'success'
            assert result_dict['total_datasets'] == 2
            assert len(result_dict['datasets']) == 2
            
            # Find datasets by name
            users_dataset = next(d for d in result_dict['datasets'] if d['name'] == 'users')
            products_dataset = next(d for d in result_dict['datasets'] if d['name'] == 'products')
            
            assert users_dataset['rows'] == 2
            assert users_dataset['columns'] == ['name', 'age']
            assert 'memory_usage_mb' in users_dataset
            assert 'loaded_at' in users_dataset
            
            assert products_dataset['rows'] == 3
            assert products_dataset['columns'] == ['product', 'price', 'category']
            
    def test_list_loaded_datasets_fallback_to_registry(self):
        """Test listing datasets when memory is cleared but registry exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Load a dataset first
            from staffer.functions.load_dataset import load_dataset, loaded_datasets
            
            test_data = pd.DataFrame({
                'id': [1, 2, 3],
                'value': ['A', 'B', 'C']
            })
            csv_file = os.path.join(temp_dir, 'test.csv')
            test_data.to_csv(csv_file, index=False)
            
            load_dataset(temp_dir, 'test.csv', 'registry_test')
            
            # Clear memory to simulate restart
            loaded_datasets.clear()
            
            # Test listing (should reload from registry)
            result = list_loaded_datasets(temp_dir)
            result_dict = json.loads(result)
            
            assert result_dict['status'] == 'success'
            assert result_dict['total_datasets'] == 1
            assert len(result_dict['datasets']) == 1
            
            dataset = result_dict['datasets'][0]
            assert dataset['name'] == 'registry_test'
            assert dataset['rows'] == 3
            assert dataset['columns'] == ['id', 'value']
            
    def test_list_loaded_datasets_security_validation(self):
        """Test security validation for working directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test with None working_directory
            result = list_loaded_datasets(None)
            assert 'Error:' in result
            assert 'Working directory cannot be None' in result
            
    def test_list_loaded_datasets_no_registry_file(self):
        """Test behavior when no registry file exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Clear any existing state from previous tests
            from staffer.functions.load_dataset import loaded_datasets
            loaded_datasets.clear()
            
            result = list_loaded_datasets(temp_dir)
            result_dict = json.loads(result)
            
            assert result_dict['status'] == 'success'
            assert result_dict['datasets'] == []
            assert result_dict['total_datasets'] == 0