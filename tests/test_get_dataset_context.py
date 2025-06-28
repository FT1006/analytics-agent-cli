"""Tests for get_dataset_context function"""
import pytest
import pandas as pd
import json
import tempfile
import os


class TestGetDatasetContext:
    """Test suite for get_dataset_context function"""
    
    def test_get_context_for_multiple_loaded_datasets(self):
        """Test getting context for multiple datasets that have been loaded"""
        from staffer.functions.get_dataset_context import get_dataset_context
        from staffer.functions.load_dataset import load_dataset, loaded_datasets, dataset_schemas
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Clear global state to ensure clean test
            loaded_datasets.clear()
            dataset_schemas.clear()
            # Create first test dataset - sales data
            sales_data = pd.DataFrame({
                'date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03']),
                'product': ['A', 'B', 'A'],
                'quantity': [10, 15, 8],
                'price': [10.5, 15.75, 10.5],
                'region': ['North', 'South', 'East']
            })
            sales_file = os.path.join(temp_dir, "sales_data.csv")
            sales_data.to_csv(sales_file, index=False)
            
            # Create second test dataset - customer data
            customer_data = pd.DataFrame({
                'customer_id': [1, 2, 3, 4],
                'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
                'age': [25, 30, 35, 28],
                'score': [95.5, 87.2, 92.1, 88.7],
                'active': [True, False, True, True]
            })
            customer_file = os.path.join(temp_dir, "customer_data.csv")
            customer_data.to_csv(customer_file, index=False)
            
            # Load both datasets
            load_result1 = load_dataset(temp_dir, "sales_data.csv", "sales")
            load_result1_dict = json.loads(load_result1)
            assert load_result1_dict["status"] == "loaded"
            
            load_result2 = load_dataset(temp_dir, "customer_data.csv", "customers")
            load_result2_dict = json.loads(load_result2)
            assert load_result2_dict["status"] == "loaded"
            
            # Get context for all loaded datasets
            result = get_dataset_context(temp_dir)
            result_dict = json.loads(result)
            
            assert result_dict["status"] == "loaded"
            assert "datasets" in result_dict
            assert result_dict["total_datasets"] == 2
            
            # Check datasets array
            datasets = result_dict["datasets"]
            assert len(datasets) == 2
            
            # Find sales and customers datasets
            sales_dataset = next((d for d in datasets if d["name"] == "sales"), None)
            customers_dataset = next((d for d in datasets if d["name"] == "customers"), None)
            
            assert sales_dataset is not None
            assert customers_dataset is not None
            
            # Check sales dataset structure
            assert sales_dataset["rows"] == 3
            assert sales_dataset["columns"] == 5
            assert "memory_mb" in sales_dataset
            assert "column_types" in sales_dataset
            
            # Check customers dataset structure
            assert customers_dataset["rows"] == 4
            assert customers_dataset["columns"] == 5
            assert "memory_mb" in customers_dataset
            assert "column_types" in customers_dataset
            
            # Check column type counts
            sales_col_types = sales_dataset["column_types"]
            assert "numerical" in sales_col_types
            assert "categorical" in sales_col_types
            assert "temporal" in sales_col_types
            assert "identifier" in sales_col_types
            
            # Check total memory usage
            assert "total_memory_mb" in result_dict
            assert result_dict["total_memory_mb"] >= 0
    
    def test_get_context_for_no_loaded_datasets(self):
        """Test getting context when no datasets are loaded"""
        from staffer.functions.get_dataset_context import get_dataset_context
        from staffer.functions.load_dataset import loaded_datasets, dataset_schemas
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Clear global state to ensure clean test
            loaded_datasets.clear()
            dataset_schemas.clear()
            
            result = get_dataset_context(temp_dir)
            result_dict = json.loads(result)
            
            assert result_dict["status"] == "empty"
            assert result_dict["datasets"] == []
            assert result_dict["total_datasets"] == 0
            assert result_dict["total_memory_mb"] == 0
    
    def test_get_context_with_single_dataset(self):
        """Test getting context for a single loaded dataset"""
        from staffer.functions.get_dataset_context import get_dataset_context
        from staffer.functions.load_dataset import load_dataset, loaded_datasets, dataset_schemas
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Clear global state to ensure clean test
            loaded_datasets.clear()
            dataset_schemas.clear()
            
            # Create test data
            test_data = pd.DataFrame({
                'id': [1, 2, 3],
                'value': [10.5, 20.5, 30.5],
                'category': ['A', 'B', 'A']
            })
            test_file = os.path.join(temp_dir, "test_data.csv")
            test_data.to_csv(test_file, index=False)
            
            # Load the dataset
            load_dataset(temp_dir, "test_data.csv", "test_data")
            
            # Get context
            result = get_dataset_context(temp_dir)
            result_dict = json.loads(result)
            
            assert result_dict["status"] == "loaded"
            assert result_dict["total_datasets"] == 1
            assert len(result_dict["datasets"]) == 1
            
            dataset = result_dict["datasets"][0]
            assert dataset["name"] == "test_data"
            assert dataset["rows"] == 3
            assert dataset["columns"] == 3
    
    def test_get_context_with_missing_working_directory(self):
        """Test function with missing working directory"""
        from staffer.functions.get_dataset_context import get_dataset_context
        
        result = get_dataset_context(None)
        assert "error" in result.lower()
        assert "working directory cannot be none" in result.lower()
    
    def test_get_context_persistence_across_sessions(self):
        """Test that context is retrieved correctly after clearing in-memory data"""
        from staffer.functions.get_dataset_context import get_dataset_context
        from staffer.functions.load_dataset import load_dataset, loaded_datasets, dataset_schemas
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Clear global state to ensure clean test
            loaded_datasets.clear()
            dataset_schemas.clear()
            
            # Create and load test data
            test_data = pd.DataFrame({
                'name': ['Alice', 'Bob'],
                'age': [25, 30]
            })
            test_file = os.path.join(temp_dir, "test_data.csv")
            test_data.to_csv(test_file, index=False)
            
            load_dataset(temp_dir, "test_data.csv", "persistent_data")
            
            # Get context first time
            result1 = get_dataset_context(temp_dir)
            result1_dict = json.loads(result1)
            
            # Clear in-memory state to test persistence
            loaded_datasets.clear()
            dataset_schemas.clear()
            
            # Get context again - should reload from persisted files
            result2 = get_dataset_context(temp_dir)
            result2_dict = json.loads(result2)
            
            assert result2_dict["status"] == "loaded"
            assert result2_dict["total_datasets"] == 1
            assert result1_dict["total_datasets"] == result2_dict["total_datasets"]