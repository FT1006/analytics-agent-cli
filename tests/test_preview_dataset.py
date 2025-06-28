"""Tests for preview_dataset function"""
import pytest
import pandas as pd
import json
import tempfile
import os


class TestPreviewDataset:
    """Test suite for preview_dataset function"""
    
    def test_preview_loaded_dataset(self):
        """Test previewing a dataset that has been loaded"""
        from staffer.functions.preview_dataset import preview_dataset
        from staffer.functions.load_dataset import load_dataset
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data
            test_data = pd.DataFrame({
                'date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05']),
                'product': ['A', 'B', 'A', 'C', 'B'],
                'quantity': [10, 15, 8, 12, 20],
                'price': [10.5, 15.75, 10.5, 22.25, 15.75],
                'region': ['North', 'South', 'East', 'West', 'North']
            })
            test_file = os.path.join(temp_dir, "test_data.csv")
            test_data.to_csv(test_file, index=False)
            
            # Load the dataset
            load_result = load_dataset(temp_dir, "test_data.csv", "sales_data")
            load_result_dict = json.loads(load_result)
            assert load_result_dict["status"] == "loaded"
            
            # Preview the dataset with default 5 rows
            result = preview_dataset(temp_dir, "sales_data")
            result_dict = json.loads(result)
            
            assert "dataset_name" in result_dict
            assert result_dict["dataset_name"] == "sales_data"
            assert "sample_size" in result_dict
            assert result_dict["sample_size"] == 5
            assert "total_rows" in result_dict
            assert result_dict["total_rows"] == 5
            assert "columns" in result_dict
            assert result_dict["columns"] == ['date', 'product', 'quantity', 'price', 'region']
            assert "sample_data" in result_dict
            assert len(result_dict["sample_data"]) == 5
            
            # Check first row data
            first_row = result_dict["sample_data"][0]
            assert first_row["product"] == "A"
            assert first_row["quantity"] == 10
            assert first_row["price"] == 10.5
            assert first_row["region"] == "North"
    
    def test_preview_with_custom_rows(self):
        """Test previewing dataset with custom number of rows"""
        from staffer.functions.preview_dataset import preview_dataset
        from staffer.functions.load_dataset import load_dataset
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data with more rows
            test_data = pd.DataFrame({
                'id': range(1, 21),
                'value': range(100, 120),
                'category': ['A', 'B', 'C', 'D'] * 5
            })
            test_file = os.path.join(temp_dir, "test_data.csv")
            test_data.to_csv(test_file, index=False)
            
            # Load the dataset
            load_dataset(temp_dir, "test_data.csv", "large_data")
            
            # Preview with 3 rows
            result = preview_dataset(temp_dir, "large_data", rows=3)
            result_dict = json.loads(result)
            
            assert result_dict["sample_size"] == 3
            assert result_dict["total_rows"] == 20
            assert len(result_dict["sample_data"]) == 3
            
            # Preview with 10 rows
            result = preview_dataset(temp_dir, "large_data", rows=10)
            result_dict = json.loads(result)
            
            assert result_dict["sample_size"] == 10
            assert len(result_dict["sample_data"]) == 10
    
    def test_preview_more_rows_than_available(self):
        """Test previewing more rows than available in dataset"""
        from staffer.functions.preview_dataset import preview_dataset
        from staffer.functions.load_dataset import load_dataset
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create small dataset
            test_data = pd.DataFrame({
                'id': [1, 2, 3],
                'name': ['Alice', 'Bob', 'Charlie']
            })
            test_file = os.path.join(temp_dir, "small_data.csv")
            test_data.to_csv(test_file, index=False)
            
            # Load the dataset
            load_dataset(temp_dir, "small_data.csv", "small_data")
            
            # Request 10 rows from 3-row dataset
            result = preview_dataset(temp_dir, "small_data", rows=10)
            result_dict = json.loads(result)
            
            assert result_dict["sample_size"] == 3  # Should return all available rows
            assert result_dict["total_rows"] == 3
            assert len(result_dict["sample_data"]) == 3
    
    def test_preview_missing_dataset(self):
        """Test previewing a dataset that doesn't exist"""
        from staffer.functions.preview_dataset import preview_dataset
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = preview_dataset(temp_dir, "nonexistent_data")
            result_dict = json.loads(result)
            
            assert "error" in result_dict
            assert "not loaded" in result_dict["error"]
    
    def test_preview_with_missing_inputs(self):
        """Test function with missing required inputs"""
        from staffer.functions.preview_dataset import preview_dataset
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Missing dataset_name (None)
            result = preview_dataset(temp_dir, None)
            result_dict = json.loads(result)
            assert "error" in result_dict
            
            # Missing working_directory (None)
            result = preview_dataset(None, "test")
            result_dict = json.loads(result)
            assert "error" in result_dict
    
    def test_preview_with_zero_rows(self):
        """Test requesting zero rows returns empty sample"""
        from staffer.functions.preview_dataset import preview_dataset
        from staffer.functions.load_dataset import load_dataset
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data
            test_data = pd.DataFrame({
                'id': [1, 2, 3],
                'value': [10, 20, 30]
            })
            test_file = os.path.join(temp_dir, "test_data.csv")
            test_data.to_csv(test_file, index=False)
            
            # Load the dataset
            load_dataset(temp_dir, "test_data.csv", "test_data")
            
            # Request 0 rows
            result = preview_dataset(temp_dir, "test_data", rows=0)
            result_dict = json.loads(result)
            
            assert result_dict["sample_size"] == 0
            assert result_dict["total_rows"] == 3
            assert len(result_dict["sample_data"]) == 0