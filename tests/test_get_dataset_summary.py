"""Tests for get_dataset_summary function"""
import pytest
import pandas as pd
import json
import tempfile
import os


class TestGetDatasetSummary:
    """Test suite for get_dataset_summary function"""
    
    def test_get_summary_for_loaded_dataset(self):
        """Test getting summary for a dataset that has been loaded"""
        from staffer.functions.get_dataset_summary import get_dataset_summary
        from staffer.functions.load_dataset import load_dataset
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data with mixed types
            test_data = pd.DataFrame({
                'date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05']),
                'product': ['A', 'B', 'A', 'C', 'B'],
                'quantity': [10, 15, 8, 12, 20],
                'price': [10.5, 15.75, 10.5, 22.25, 15.75],
                'region': ['North', 'South', 'East', 'West', 'North'],
                'discount': [0.1, 0.0, 0.15, 0.0, 0.2]
            })
            test_file = os.path.join(temp_dir, "test_data.csv")
            test_data.to_csv(test_file, index=False)
            
            # Load the dataset
            load_result = load_dataset(temp_dir, "test_data.csv", "sales_data")
            load_result_dict = json.loads(load_result)
            assert load_result_dict["status"] == "loaded"
            
            # Get summary for the loaded dataset
            result = get_dataset_summary(temp_dir, "sales_data")
            result_dict = json.loads(result)
            
            # Check basic info
            assert "dataset_name" in result_dict
            assert result_dict["dataset_name"] == "sales_data"
            assert "shape" in result_dict
            assert result_dict["shape"] == [5, 6]
            assert "memory_usage_mb" in result_dict
            assert isinstance(result_dict["memory_usage_mb"], (int, float))
            
            # Check numerical summary
            assert "numerical_summary" in result_dict
            numerical_summary = result_dict["numerical_summary"]
            assert "quantity" in numerical_summary
            assert "price" in numerical_summary
            assert "discount" in numerical_summary
            
            # Check quantity statistics
            quantity_stats = numerical_summary["quantity"]
            assert "count" in quantity_stats
            assert "mean" in quantity_stats
            assert "std" in quantity_stats
            assert "min" in quantity_stats
            assert "25%" in quantity_stats
            assert "50%" in quantity_stats
            assert "75%" in quantity_stats
            assert "max" in quantity_stats
            assert quantity_stats["count"] == 5.0
            assert quantity_stats["mean"] == 13.0  # (10+15+8+12+20)/5
            assert quantity_stats["min"] == 8.0
            assert quantity_stats["max"] == 20.0
            
            # Check categorical summary
            assert "categorical_summary" in result_dict
            categorical_summary = result_dict["categorical_summary"]
            assert "product" in categorical_summary
            assert "region" in categorical_summary
            
            # Check product category details
            product_summary = categorical_summary["product"]
            assert "unique_count" in product_summary
            assert "top_values" in product_summary
            assert "null_count" in product_summary
            assert product_summary["unique_count"] == 3  # A, B, C
            assert product_summary["null_count"] == 0
            
            # Check top values
            top_values = product_summary["top_values"]
            assert len(top_values) <= 5
            assert "A" in top_values or "B" in top_values  # Both appear twice
            
            # Check missing data summary
            assert "missing_data" in result_dict
            missing_data = result_dict["missing_data"]
            assert "total_missing" in missing_data
            assert "columns_with_missing" in missing_data
            assert missing_data["total_missing"] == 0  # No missing values in our test data
    
    def test_get_summary_for_missing_dataset(self):
        """Test getting summary for a dataset that doesn't exist"""
        from staffer.functions.get_dataset_summary import get_dataset_summary
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = get_dataset_summary(temp_dir, "nonexistent_data")
            result_dict = json.loads(result)
            
            assert "error" in result_dict
            assert "not found" in result_dict["error"].lower() or "failed" in result_dict["error"].lower()
    
    def test_get_summary_with_missing_inputs(self):
        """Test function with missing required inputs"""
        from staffer.functions.get_dataset_summary import get_dataset_summary
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Missing dataset_name (None)
            result = get_dataset_summary(temp_dir, None)
            result_dict = json.loads(result)
            assert "error" in result_dict
            
            # Missing working_directory (None)
            result = get_dataset_summary(None, "test")
            result_dict = json.loads(result)
            assert "error" in result_dict
    
    def test_get_summary_with_missing_values(self):
        """Test summary with datasets containing missing values"""
        from staffer.functions.get_dataset_summary import get_dataset_summary
        from staffer.functions.load_dataset import load_dataset
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data with nulls
            test_data = pd.DataFrame({
                'id': [1, 2, 3, 4, 5],
                'value': [10.5, None, 30.5, None, 50.5],
                'category': ['A', 'B', None, 'D', None],
                'score': [85, 90, None, 88, 92]
            })
            
            test_file = os.path.join(temp_dir, "missing_data.csv")
            test_data.to_csv(test_file, index=False)
            
            # Load dataset
            load_dataset(temp_dir, "missing_data.csv", "missing_data")
            
            # Get summary
            result = get_dataset_summary(temp_dir, "missing_data")
            result_dict = json.loads(result)
            
            # Check missing data is properly reported
            missing_data = result_dict["missing_data"]
            assert missing_data["total_missing"] == 5  # 2 in value, 2 in category, 1 in score
            assert "value" in missing_data["columns_with_missing"]
            assert "category" in missing_data["columns_with_missing"]
            assert "score" in missing_data["columns_with_missing"]
            assert missing_data["columns_with_missing"]["value"] == 2
            assert missing_data["columns_with_missing"]["category"] == 2
            assert missing_data["columns_with_missing"]["score"] == 1
            
            # Check numerical summary handles missing values correctly
            numerical_summary = result_dict["numerical_summary"]
            assert numerical_summary["value"]["count"] == 3.0  # Only non-null values
            assert numerical_summary["score"]["count"] == 4.0  # Only non-null values
    
    def test_get_summary_with_only_categorical_data(self):
        """Test summary with dataset containing only categorical columns"""
        from staffer.functions.get_dataset_summary import get_dataset_summary
        from staffer.functions.load_dataset import load_dataset
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data with only categorical columns
            test_data = pd.DataFrame({
                'color': ['red', 'blue', 'red', 'green', 'blue', 'red'],
                'size': ['S', 'M', 'L', 'M', 'S', 'XL'],
                'category': ['A', 'A', 'B', 'B', 'C', 'C']
            })
            
            test_file = os.path.join(temp_dir, "categorical_data.csv")
            test_data.to_csv(test_file, index=False)
            
            # Load dataset
            load_dataset(temp_dir, "categorical_data.csv", "categorical_data")
            
            # Get summary
            result = get_dataset_summary(temp_dir, "categorical_data")
            result_dict = json.loads(result)
            
            # Should not have numerical summary
            assert "numerical_summary" not in result_dict or result_dict["numerical_summary"] == {}
            
            # Should have categorical summary
            assert "categorical_summary" in result_dict
            assert len(result_dict["categorical_summary"]) == 3
            
            # Check color summary
            color_summary = result_dict["categorical_summary"]["color"]
            assert color_summary["unique_count"] == 3  # red, blue, green
            assert "red" in color_summary["top_values"]
            assert color_summary["top_values"]["red"] == 3  # red appears 3 times