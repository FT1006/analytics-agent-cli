"""Tests for list_loaded_datasets_tool function following MCP pattern."""

import pytest
import os
import tempfile
import json
import pandas as pd

from staffer.functions.analytics.tools.list_loaded_datasets_tool import list_loaded_datasets_tool
from staffer.functions.analytics.tools.load_dataset_tool import load_dataset_tool


class TestListLoadedDatasetsTool:
    """Test suite for list_loaded_datasets_tool function."""
    
    def test_list_empty_datasets(self):
        """Test listing when no datasets are loaded."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Clear any existing datasets
            from staffer.functions.analytics.tools.load_dataset import loaded_datasets
            loaded_datasets.clear()
            
            # List datasets (should be empty)
            result = list_loaded_datasets_tool(temp_dir, {})
            
            # Parse JSON result
            result_dict = json.loads(result)
            
            # Verify empty list
            assert result_dict['loaded_datasets'] == []
            assert result_dict['total_datasets'] == 0
            assert result_dict['total_memory_mb'] == 0.0
            
    def test_list_single_dataset(self):
        """Test listing after loading one dataset."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Clear any existing datasets
            from staffer.functions.analytics.tools.load_dataset import loaded_datasets
            loaded_datasets.clear()
            
            # Create and load test dataset
            test_data = pd.DataFrame({
                'id': range(1, 11),
                'value': [i * 10 for i in range(1, 11)]
            })
            csv_file = os.path.join(temp_dir, 'test_data.csv')
            test_data.to_csv(csv_file, index=False)
            
            # Load dataset
            load_result = load_dataset_tool(temp_dir, {
                'file_path': 'test_data.csv',
                'dataset_name': 'test_dataset'
            })
            
            # List datasets
            result = list_loaded_datasets_tool(temp_dir, {})
            
            # Parse JSON result
            result_dict = json.loads(result)
            
            # Verify single dataset
            assert result_dict['total_datasets'] == 1
            assert len(result_dict['loaded_datasets']) == 1
            
            dataset_info = result_dict['loaded_datasets'][0]
            assert dataset_info['name'] == 'test_dataset'
            assert dataset_info['rows'] == 10
            assert dataset_info['columns'] == 2
            assert 'memory_mb' in dataset_info
            assert dataset_info['memory_mb'] > 0
            
            assert result_dict['total_memory_mb'] > 0
            
    def test_list_multiple_datasets(self):
        """Test listing multiple loaded datasets."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Clear any existing datasets
            from staffer.functions.analytics.tools.load_dataset import loaded_datasets
            loaded_datasets.clear()
            
            # Create and load first dataset
            test_data1 = pd.DataFrame({
                'name': ['Alice', 'Bob', 'Charlie'],
                'score': [95, 87, 92]
            })
            csv_file1 = os.path.join(temp_dir, 'students.csv')
            test_data1.to_csv(csv_file1, index=False)
            
            load_dataset_tool(temp_dir, {
                'file_path': 'students.csv',
                'dataset_name': 'students'
            })
            
            # Create and load second dataset
            test_data2 = pd.DataFrame({
                'product': ['Widget', 'Gadget', 'Doohickey', 'Thingamajig'],
                'price': [19.99, 29.99, 39.99, 49.99],
                'stock': [100, 50, 25, 10]
            })
            csv_file2 = os.path.join(temp_dir, 'products.csv')
            test_data2.to_csv(csv_file2, index=False)
            
            load_dataset_tool(temp_dir, {
                'file_path': 'products.csv',
                'dataset_name': 'products'
            })
            
            # List datasets
            result = list_loaded_datasets_tool(temp_dir, {})
            
            # Parse JSON result
            result_dict = json.loads(result)
            
            # Verify multiple datasets
            assert result_dict['total_datasets'] == 2
            assert len(result_dict['loaded_datasets']) == 2
            
            # Find datasets by name
            datasets_by_name = {d['name']: d for d in result_dict['loaded_datasets']}
            
            assert 'students' in datasets_by_name
            assert datasets_by_name['students']['rows'] == 3
            assert datasets_by_name['students']['columns'] == 2
            
            assert 'products' in datasets_by_name
            assert datasets_by_name['products']['rows'] == 4
            assert datasets_by_name['products']['columns'] == 3
            
            # Verify total memory is sum of individual
            total_memory = sum(d['memory_mb'] for d in result_dict['loaded_datasets'])
            assert abs(result_dict['total_memory_mb'] - total_memory) < 0.01
            
    def test_list_with_sampled_dataset(self):
        """Test listing includes sampled datasets correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Clear any existing datasets
            from staffer.functions.analytics.tools.load_dataset import loaded_datasets
            loaded_datasets.clear()
            
            # Create large dataset
            test_data = pd.DataFrame({
                'id': range(1, 1001),
                'value': [i * 10 for i in range(1, 1001)]
            })
            csv_file = os.path.join(temp_dir, 'large_data.csv')
            test_data.to_csv(csv_file, index=False)
            
            # Load with sampling
            load_dataset_tool(temp_dir, {
                'file_path': 'large_data.csv',
                'dataset_name': 'sampled_data',
                'sample_size': 100
            })
            
            # List datasets
            result = list_loaded_datasets_tool(temp_dir, {})
            
            # Parse JSON result
            result_dict = json.loads(result)
            
            # Verify sampled dataset shows sampled size
            assert result_dict['total_datasets'] == 1
            dataset_info = result_dict['loaded_datasets'][0]
            assert dataset_info['name'] == 'sampled_data'
            assert dataset_info['rows'] == 100  # Sampled size, not original
            
    def test_mcp_compatibility(self):
        """Test that the function follows MCP pattern (no args needed)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Should work with empty args dict
            result = list_loaded_datasets_tool(temp_dir, {})
            result_dict = json.loads(result)
            
            # Should have MCP-compatible structure
            assert 'loaded_datasets' in result_dict
            assert 'total_datasets' in result_dict
            assert 'total_memory_mb' in result_dict