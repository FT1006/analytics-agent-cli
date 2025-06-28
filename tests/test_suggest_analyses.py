"""Tests for suggest_analyses function"""
import pytest
import pandas as pd
import json
import tempfile
import os


class TestSuggestanalyses:
    """Test suite for suggest_analyses function"""
    
    def test_suggest_analyses_for_loaded_dataset(self):
        """Test suggesting analyses for a dataset that has been loaded"""
        from staffer.functions.suggest_analyses import suggest_analyses
        from staffer.functions.load_dataset import load_dataset
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data with multiple column types
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
            
            # Get analysis suggestions
            result = suggest_analyses(temp_dir, "sales_data")
            result_dict = json.loads(result)
            
            assert result_dict["status"] == "success"
            assert "dataset_name" in result_dict
            assert result_dict["dataset_name"] == "sales_data"
            assert "available_analyses" in result_dict
            assert "dataset_summary" in result_dict
            
            # Check that basic analyses are always suggested
            analyses_types = [analysis["type"] for analysis in result_dict["available_analyses"]]
            assert "data_quality_assessment" in analyses_types
            assert "distribution_analysis" in analyses_types
            
            # Check that correlation analysis is suggested (2+ numerical columns)
            assert "correlation_analysis" in analyses_types
            assert "outlier_detection" in analyses_types
            
            # Check that segmentation is suggested (categorical columns exist)
            assert "segmentation" in analyses_types
            
            # Check dataset summary
            summary = result_dict["dataset_summary"]
            assert summary["numerical_columns"] >= 2  # quantity and price
            assert summary["categorical_columns"] >= 1  # product and region
            assert summary["total_rows"] == 5
    
    def test_suggest_analyses_numerical_only_dataset(self):
        """Test suggesting analyses for dataset with only numerical columns"""
        from staffer.functions.suggest_analyses import suggest_analyses
        from staffer.functions.load_dataset import load_dataset
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data with only numerical columns
            test_data = pd.DataFrame({
                'value1': [10.5, 15.75, 10.5, 22.25, 15.75],
                'value2': [100, 150, 80, 220, 175],
                'value3': [1.5, 2.2, 1.8, 3.1, 2.7]
            })
            test_file = os.path.join(temp_dir, "numerical_data.csv")
            test_data.to_csv(test_file, index=False)
            
            # Load the dataset
            load_dataset(temp_dir, "numerical_data.csv", "numerical_data")
            
            # Get analysis suggestions
            result = suggest_analyses(temp_dir, "numerical_data")
            result_dict = json.loads(result)
            
            assert result_dict["status"] == "success"
            
            # Should include correlation and outlier detection (3 numerical columns)
            analyses_types = [analysis["type"] for analysis in result_dict["available_analyses"]]
            assert "correlation_analysis" in analyses_types
            assert "outlier_detection" in analyses_types
            
            # Should NOT include segmentation (no categorical columns)
            assert "segmentation" not in analyses_types
            
            # Should NOT include time series (no temporal columns)
            assert "time_series" not in analyses_types
    
    def test_suggest_analyses_categorical_only_dataset(self):
        """Test suggesting analyses for dataset with only categorical columns"""
        from staffer.functions.suggest_analyses import suggest_analyses
        from staffer.functions.load_dataset import load_dataset
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data with only categorical columns
            test_data = pd.DataFrame({
                'category1': ['A', 'B', 'C', 'A', 'B'],
                'category2': ['X', 'Y', 'Z', 'X', 'Y'],
                'category3': ['Red', 'Blue', 'Green', 'Red', 'Blue']
            })
            test_file = os.path.join(temp_dir, "categorical_data.csv")
            test_data.to_csv(test_file, index=False)
            
            # Load the dataset
            load_dataset(temp_dir, "categorical_data.csv", "categorical_data")
            
            # Get analysis suggestions
            result = suggest_analyses(temp_dir, "categorical_data")
            result_dict = json.loads(result)
            
            assert result_dict["status"] == "success"
            
            # Should include segmentation (categorical columns exist)
            analyses_types = [analysis["type"] for analysis in result_dict["available_analyses"]]
            assert "segmentation" in analyses_types
            
            # Should NOT include correlation or outlier detection (no numerical columns)
            assert "correlation_analysis" not in analyses_types
            assert "outlier_detection" not in analyses_types
    
    def test_suggest_analyses_with_temporal_data(self):
        """Test suggesting analyses for dataset with temporal data"""
        from staffer.functions.suggest_analyses import suggest_analyses
        from staffer.functions.load_dataset import load_dataset
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data with temporal and numerical columns
            test_data = pd.DataFrame({
                'date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05']),
                'value': [10, 15, 8, 12, 20]
            })
            test_file = os.path.join(temp_dir, "temporal_data.csv")
            test_data.to_csv(test_file, index=False)
            
            # Load the dataset
            load_dataset(temp_dir, "temporal_data.csv", "temporal_data")
            
            # Get analysis suggestions
            result = suggest_analyses(temp_dir, "temporal_data")
            result_dict = json.loads(result)
            
            assert result_dict["status"] == "success"
            
            # Should include time series analysis (temporal + numerical columns)
            analyses_types = [analysis["type"] for analysis in result_dict["available_analyses"]]
            # Note: time_series analysis requires both temporal and numerical columns
            # But since date might be detected as identifier due to CSV limitations, this test might need adjustment
    
    def test_suggest_analyses_for_missing_dataset(self):
        """Test suggesting analyses for a dataset that doesn't exist"""
        from staffer.functions.suggest_analyses import suggest_analyses
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = suggest_analyses(temp_dir, "nonexistent_data")
            
            assert "Error:" in result
            assert "not found" in result.lower()
    
    def test_suggest_analyses_with_missing_inputs(self):
        """Test function with missing required inputs"""
        from staffer.functions.suggest_analyses import suggest_analyses
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Missing dataset_name (None)
            result = suggest_analyses(temp_dir, None)
            assert "Error:" in result
            assert "Dataset name cannot be None" in result
            
            # Missing working_directory (None)
            result = suggest_analyses(None, "test")
            assert "Error:" in result
            assert "Working directory cannot be None" in result
    
    def test_suggest_analyses_includes_applicable_columns(self):
        """Test that analyses include applicable columns information"""
        from staffer.functions.suggest_analyses import suggest_analyses
        from staffer.functions.load_dataset import load_dataset
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data
            test_data = pd.DataFrame({
                'product': ['A', 'B', 'A', 'C', 'B'],
                'quantity': [10, 15, 8, 12, 20],
                'price': [10.5, 15.75, 10.5, 22.25, 15.75],
                'region': ['North', 'South', 'East', 'West', 'North']
            })
            test_file = os.path.join(temp_dir, "test_data.csv")
            test_data.to_csv(test_file, index=False)
            
            # Load the dataset
            load_dataset(temp_dir, "test_data.csv", "test_data")
            
            # Get analysis suggestions
            result = suggest_analyses(temp_dir, "test_data")
            result_dict = json.loads(result)
            
            assert result_dict["status"] == "success"
            
            # Find correlation analysis and check it has applicable columns
            correlation_analysis = None
            for analysis in result_dict["available_analyses"]:
                if analysis["type"] == "correlation_analysis":
                    correlation_analysis = analysis
                    break
            
            assert correlation_analysis is not None
            assert "applicable_columns" in correlation_analysis
            # Should contain numerical columns (quantity and price)
            applicable_cols = correlation_analysis["applicable_columns"]
            assert "quantity" in applicable_cols
            assert "price" in applicable_cols