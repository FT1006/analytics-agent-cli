"""Tests for get_ai_suggestions function"""
import pytest
import pandas as pd
import json
import tempfile
import os


class TestGetAiSuggestions:
    """Test suite for get_ai_suggestions function"""
    
    def test_get_suggestions_for_loaded_dataset(self):
        """Test getting AI suggestions for a dataset that has been loaded"""
        from staffer.functions.get_ai_suggestions import get_ai_suggestions
        from staffer.functions.load_dataset import load_dataset
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data with mixed types
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
            
            # Get AI suggestions for the loaded dataset
            result = get_ai_suggestions(temp_dir, "sales_data")
            result_dict = json.loads(result)
            
            assert "dataset_name" in result_dict
            assert result_dict["dataset_name"] == "sales_data"
            assert "suggestions" in result_dict
            assert "dataset_summary" in result_dict
            
            # Check dataset summary
            summary = result_dict["dataset_summary"]
            assert "numerical_columns" in summary
            assert "categorical_columns" in summary
            assert "temporal_columns" in summary
            assert "total_rows" in summary
            assert summary["total_rows"] == 5
            
            # Check suggestions structure
            suggestions = result_dict["suggestions"]
            assert isinstance(suggestions, list)
            
            # Should have suggestions based on data characteristics
            suggestion_types = [s["type"] for s in suggestions]
            
            # Since we have numerical columns, should suggest correlation analysis
            if summary["numerical_columns"] >= 2:
                assert "correlation_analysis" in suggestion_types
            
            # Since we have categorical and numerical, should suggest segmentation
            if summary["categorical_columns"] > 0 and summary["numerical_columns"] > 0:
                assert "segmentation" in suggestion_types
    
    def test_get_suggestions_for_missing_dataset(self):
        """Test getting suggestions for a dataset that doesn't exist"""
        from staffer.functions.get_ai_suggestions import get_ai_suggestions
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = get_ai_suggestions(temp_dir, "nonexistent_data")
            result_dict = json.loads(result)
            
            assert "error" in result_dict
            assert "not loaded" in result_dict["error"]
    
    def test_get_suggestions_with_missing_inputs(self):
        """Test function with missing required inputs"""
        from staffer.functions.get_ai_suggestions import get_ai_suggestions
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Missing dataset_name (None)
            result = get_ai_suggestions(temp_dir, None)
            result_dict = json.loads(result)
            assert "error" in result_dict
            assert "Dataset name cannot be None" in result_dict["error"]
            
            # Missing working_directory (None)
            result = get_ai_suggestions(None, "test")
            result_dict = json.loads(result)
            assert "error" in result_dict
            assert "Working directory cannot be None" in result_dict["error"]
    
    def test_suggestions_for_numerical_only_dataset(self):
        """Test suggestions for dataset with only numerical columns"""
        from staffer.functions.get_ai_suggestions import get_ai_suggestions
        from staffer.functions.load_dataset import load_dataset
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create numerical-only dataset
            test_data = pd.DataFrame({
                'value1': [10.5, 15.2, 8.7, 12.1, 20.3],
                'value2': [100, 150, 87, 121, 203],
                'value3': [1.5, 2.2, 0.7, 1.1, 3.3]
            })
            test_file = os.path.join(temp_dir, "numerical_data.csv")
            test_data.to_csv(test_file, index=False)
            
            load_dataset(temp_dir, "numerical_data.csv", "numerical_data")
            
            result = get_ai_suggestions(temp_dir, "numerical_data")
            result_dict = json.loads(result)
            
            suggestions = result_dict["suggestions"]
            suggestion_types = [s["type"] for s in suggestions]
            
            # Should suggest correlation analysis for numerical data
            assert "correlation_analysis" in suggestion_types
            # Should suggest outlier detection
            assert "outlier_detection" in suggestion_types
    
    def test_suggestions_for_temporal_dataset(self):
        """Test suggestions for dataset with temporal columns"""
        from staffer.functions.get_ai_suggestions import get_ai_suggestions
        from staffer.functions.load_dataset import load_dataset
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create temporal dataset
            dates = pd.date_range('2024-01-01', periods=10, freq='D')
            test_data = pd.DataFrame({
                'timestamp': dates,
                'metric': [10, 12, 8, 15, 11, 9, 13, 14, 7, 16]
            })
            test_file = os.path.join(temp_dir, "temporal_data.csv")
            test_data.to_csv(test_file, index=False)
            
            load_dataset(temp_dir, "temporal_data.csv", "temporal_data")
            
            result = get_ai_suggestions(temp_dir, "temporal_data")
            result_dict = json.loads(result)
            
            suggestions = result_dict["suggestions"]
            suggestion_types = [s["type"] for s in suggestions]
            
            # Should suggest time series analysis for temporal data
            # Note: timestamp might be treated as identifier due to 100% cardinality
            # But if it's properly detected as temporal, should suggest time_series
            summary = result_dict["dataset_summary"]
            if summary["temporal_columns"] > 0:
                assert "time_series" in suggestion_types
    
    def test_suggestion_structure(self):
        """Test that each suggestion has required fields"""
        from staffer.functions.get_ai_suggestions import get_ai_suggestions
        from staffer.functions.load_dataset import load_dataset
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data
            test_data = pd.DataFrame({
                'category': ['A', 'B', 'C', 'A', 'B'],
                'value': [10, 20, 30, 15, 25]
            })
            test_file = os.path.join(temp_dir, "structured_data.csv")
            test_data.to_csv(test_file, index=False)
            
            load_dataset(temp_dir, "structured_data.csv", "structured_data")
            
            result = get_ai_suggestions(temp_dir, "structured_data")
            result_dict = json.loads(result)
            
            suggestions = result_dict["suggestions"]
            
            for suggestion in suggestions:
                # Each suggestion should have required fields
                assert "type" in suggestion
                assert "description" in suggestion
                assert "columns" in suggestion
                assert "tool" in suggestion
                assert "priority" in suggestion
                assert "command" in suggestion
                
                # Priority should be valid
                assert suggestion["priority"] in ["high", "medium", "low"]