"""Tests for analytics functions transformed from quick-data-mcp."""

import os
import pytest
import tempfile
import pandas as pd
from pathlib import Path
from staffer.functions.load_dataset import load_dataset, schema_load_dataset
from tests.factories import user, model, tool_resp, function_call


class TestLoadDataset:
    """Test load_dataset function."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        
        # Create test CSV file
        self.csv_data = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 30, 35],
            'salary': [50000, 60000, 70000],
            'department': ['Engineering', 'Sales', 'Engineering']
        })
        self.csv_file = os.path.join(self.test_dir, 'test_data.csv')
        self.csv_data.to_csv(self.csv_file, index=False)
        
        # Create test JSON file
        self.json_data = [
            {'product': 'Widget A', 'sales': 100, 'region': 'North'},
            {'product': 'Widget B', 'sales': 150, 'region': 'South'},
            {'product': 'Widget C', 'sales': 120, 'region': 'North'}
        ]
        self.json_file = os.path.join(self.test_dir, 'test_data.json')
        pd.DataFrame(self.json_data).to_json(self.json_file, orient='records')
        
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_load_csv_dataset_success(self):
        """Test loading CSV dataset successfully."""
        result = load_dataset(
            working_directory=self.test_dir,
            filepath='test_data.csv',
            dataset_name='test_csv'
        )
        
        assert result['status'] == 'loaded'
        assert result['dataset_name'] == 'test_csv'
        assert result['rows'] == 3
        assert result['columns'] == ['name', 'age', 'salary', 'department']
        assert result['format'] == 'csv'
        assert 'memory_usage' in result
        
    def test_load_json_dataset_success(self):
        """Test loading JSON dataset successfully."""
        result = load_dataset(
            working_directory=self.test_dir,
            filepath='test_data.json',
            dataset_name='test_json'
        )
        
        assert result['status'] == 'loaded'
        assert result['dataset_name'] == 'test_json'
        assert result['rows'] == 3
        assert result['columns'] == ['product', 'sales', 'region']
        assert result['format'] == 'json'
        
    def test_load_dataset_with_sampling(self):
        """Test loading dataset with sampling."""
        result = load_dataset(
            working_directory=self.test_dir,
            filepath='test_data.csv',
            dataset_name='test_sample',
            sample_size=2
        )
        
        assert result['status'] == 'loaded'
        assert result['rows'] == 2
        assert result['sampled'] is True
        assert result['original_rows'] == 3
        
    def test_load_dataset_file_not_found(self):
        """Test loading non-existent file."""
        result = load_dataset(
            working_directory=self.test_dir,
            filepath='nonexistent.csv',
            dataset_name='test_fail'
        )
        
        assert 'error' in result
        assert 'Failed to load dataset' in result['error']
        
    def test_load_dataset_security_outside_working_dir(self):
        """Test security check for files outside working directory."""
        result = load_dataset(
            working_directory=self.test_dir,
            filepath='../../../etc/passwd',
            dataset_name='test_security'
        )
        
        assert 'error' in result
        assert 'outside the permitted working directory' in result['error']
        
    def test_load_dataset_unsupported_format(self):
        """Test loading unsupported file format."""
        # Create a .txt file
        txt_file = os.path.join(self.test_dir, 'test.txt')
        with open(txt_file, 'w') as f:
            f.write('some text')
            
        result = load_dataset(
            working_directory=self.test_dir,
            filepath='test.txt',
            dataset_name='test_txt'
        )
        
        assert 'error' in result
        assert 'Unsupported file format' in result['error']
        
    def test_schema_load_dataset_declaration(self):
        """Test schema declaration for load_dataset function."""
        assert schema_load_dataset.name == 'load_dataset'
        assert schema_load_dataset.description
        
        # Check required parameters
        params = schema_load_dataset.parameters.properties
        assert 'filepath' in params
        assert 'dataset_name' in params
        
        # Check optional parameters
        assert 'sample_size' in params
        
        # Check required fields
        required = schema_load_dataset.parameters.required
        assert 'filepath' in required
        assert 'dataset_name' in required
        assert 'sample_size' not in required