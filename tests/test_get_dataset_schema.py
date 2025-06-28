"""Tests for get_dataset_schema function"""
import pytest
import pandas as pd
import json
import tempfile
import os


class TestGetDatasetSchema:
    """Test suite for get_dataset_schema function"""
    
    def test_get_schema_for_loaded_dataset(self):
        """Test getting schema for a dataset that has been loaded"""
        from staffer.functions.get_dataset_schema import get_dataset_schema
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
            
            # Get schema for the loaded dataset
            result = get_dataset_schema(temp_dir, "sales_data")
            result_dict = json.loads(result)
            
            assert result_dict["status"] == "success"
            assert "schema" in result_dict
            
            schema = result_dict["schema"]
            assert schema["name"] == "sales_data"  # Field is 'name', not 'dataset_name'
            assert "columns" in schema
            assert len(schema["columns"]) == 5
            
            # Check column details - columns is a dict, not a list
            columns = schema["columns"]
            assert "date" in columns
            assert "product" in columns
            assert "quantity" in columns
            assert "price" in columns
            assert "region" in columns
            
            # Check column metadata (note: date becomes string object after CSV save/load)
            # Since date has 100% cardinality (5 unique in 5 rows), it's classified as identifier
            assert columns["date"]["suggested_role"] == "identifier"  # Expected due to CSV limitation
            assert columns["product"]["suggested_role"] == "categorical"
            assert columns["quantity"]["suggested_role"] == "numerical" 
            assert columns["price"]["suggested_role"] == "numerical"
            assert columns["region"]["suggested_role"] == "categorical"
            
            # Check additional schema info
            assert schema["row_count"] == 5
    
    def test_get_schema_for_missing_dataset(self):
        """Test getting schema for a dataset that doesn't exist"""
        from staffer.functions.get_dataset_schema import get_dataset_schema
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = get_dataset_schema(temp_dir, "nonexistent_data")
            
            assert "Error:" in result
            assert "not found" in result.lower()
    
    def test_get_schema_with_missing_inputs(self):
        """Test function with missing required inputs"""
        from staffer.functions.get_dataset_schema import get_dataset_schema
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Missing dataset_name (None)
            result = get_dataset_schema(temp_dir, None)
            assert "Error:" in result
            assert "Dataset name cannot be None" in result
            
            # Missing working_directory (None)
            result = get_dataset_schema(None, "test")
            assert "Error:" in result
            assert "Working directory cannot be None" in result
    
    def test_get_schema_with_nullable_columns(self):
        """Test schema detection with nullable columns"""
        from staffer.functions.get_dataset_schema import get_dataset_schema
        from staffer.functions.load_dataset import load_dataset
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data with nulls
            test_data = pd.DataFrame({
                'id': [1, 2, 3, 4, 5],
                'value': [10.5, None, 30.5, None, 50.5],
                'category': ['A', 'B', None, 'D', None],
                'date': pd.to_datetime(['2024-01-01', None, '2024-01-03', '2024-01-04', None])
            })
            
            test_file = os.path.join(temp_dir, "nullable_data.csv")
            test_data.to_csv(test_file, index=False)
            
            # Load dataset
            load_dataset(temp_dir, "nullable_data.csv", "nullable_data")
            
            # Get schema
            result = get_dataset_schema(temp_dir, "nullable_data")
            result_dict = json.loads(result)
            
            assert result_dict["status"] == "success"
            columns = result_dict["schema"]["columns"]
            
            # Check null percentages (existing schema uses null_percentage, not null_count)
            assert columns["value"]["null_percentage"] > 0  # 2 out of 5 = 40%
            assert columns["category"]["null_percentage"] > 0  # 2 out of 5 = 40%
    
    def test_get_schema_persistence(self):
        """Test that schema is persisted and can be retrieved"""
        from staffer.functions.get_dataset_schema import get_dataset_schema
        from staffer.functions.load_dataset import load_dataset
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create and load test data
            test_data = pd.DataFrame({
                'name': ['Alice', 'Bob', 'Charlie'],
                'age': [25, 30, 35],
                'score': [95.5, 87.2, 92.1]
            })
            test_file = os.path.join(temp_dir, "test_data.csv")
            test_data.to_csv(test_file, index=False)
            
            load_dataset(temp_dir, "test_data.csv", "persistent_data")
            
            # Get schema first time
            result1 = get_dataset_schema(temp_dir, "persistent_data")
            result1_dict = json.loads(result1)
            
            # Clear in-memory state to test persistence
            from staffer.functions.load_dataset import dataset_schemas
            dataset_schemas.clear()
            
            # Get schema again - should load from persisted file
            result2 = get_dataset_schema(temp_dir, "persistent_data")
            result2_dict = json.loads(result2)
            
            assert result2_dict["status"] == "success"
            assert result1_dict["schema"] == result2_dict["schema"]