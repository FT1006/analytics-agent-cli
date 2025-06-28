import pytest
import json
import os
import tempfile
import pandas as pd
from unittest.mock import patch, MagicMock
from staffer.functions.export_analysis_to_excel import export_analysis_to_excel


class TestExportAnalysisToExcel:
    """Test suite for export_analysis_to_excel function."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "analysis_results.xlsx")
        
    def teardown_method(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_export_correlation_analysis(self):
        """Test exporting correlation analysis results."""
        analysis_results = {
            "correlation_matrix": [[1.0, 0.8, -0.3], [0.8, 1.0, 0.2], [-0.3, 0.2, 1.0]],
            "columns": ["Sales", "Marketing", "Support"],
            "strong_correlations": [
                {"columns": ["Sales", "Marketing"], "value": 0.8},
                {"columns": ["Sales", "Support"], "value": -0.3}
            ],
            "analysis_type": "correlation"
        }
        
        with patch('staffer.functions.export_analysis_to_excel.write_data_to_excel') as mock_write:
            mock_write.return_value = json.dumps({"status": "success", "rows_written": 5})
            
            result = export_analysis_to_excel(
                self.temp_dir,
                analysis_results,
                "analysis_results.xlsx",
                "Correlations"
            )
            
            result_data = json.loads(result)
            assert result_data["status"] == "exported"
            assert result_data["file_path"] == "analysis_results.xlsx"
            assert result_data["sheet_name"] == "Correlations"
            assert result_data["analysis_type"] == "correlation"
            assert mock_write.call_count == 2  # Main data + metadata
    
    def test_export_segmentation_results(self):
        """Test exporting segmentation analysis results."""
        analysis_results = {
            "segment_data": [
                {"segment": "North", "count": 100, "revenue": 50000, "avg_order": 500},
                {"segment": "South", "count": 80, "revenue": 40000, "avg_order": 500},
                {"segment": "East", "count": 120, "revenue": 72000, "avg_order": 600}
            ],
            "summary": {
                "total_segments": 3,
                "total_count": 300,
                "total_revenue": 162000
            },
            "analysis_type": "segmentation"
        }
        
        with patch('staffer.functions.export_analysis_to_excel.write_data_to_excel') as mock_write:
            mock_write.return_value = json.dumps({"status": "success", "rows_written": 4})
            
            result = export_analysis_to_excel(
                self.temp_dir,
                analysis_results,
                "segments.xlsx"
            )
            
            result_data = json.loads(result)
            assert result_data["status"] == "exported"
            assert result_data["file_path"] == "segments.xlsx"
            assert result_data["sheet_name"] == "Analysis"  # Default
            assert result_data["analysis_type"] == "segmentation"
    
    def test_export_distribution_analysis(self):
        """Test exporting distribution analysis results."""
        analysis_results = {
            "distribution": {
                "bins": [0, 10, 20, 30, 40, 50],
                "counts": [5, 15, 25, 20, 10],
                "percentages": [6.67, 20.0, 33.33, 26.67, 13.33]
            },
            "statistics": {
                "mean": 25.5,
                "median": 25,
                "std": 10.2,
                "min": 0,
                "max": 50
            },
            "analysis_type": "distribution"
        }
        
        with patch('staffer.functions.export_analysis_to_excel.write_data_to_excel') as mock_write:
            mock_write.return_value = json.dumps({"status": "success", "rows_written": 6})
            
            result = export_analysis_to_excel(
                self.temp_dir,
                analysis_results,
                "distribution.xlsx",
                "Distribution"
            )
            
            result_data = json.loads(result)
            assert result_data["status"] == "exported"
            assert result_data["analysis_type"] == "distribution"
    
    def test_export_generic_analysis(self):
        """Test exporting generic analysis results without specific type."""
        analysis_results = {
            "data": [
                {"metric": "Total Sales", "value": 100000},
                {"metric": "Avg Order Value", "value": 250},
                {"metric": "Customer Count", "value": 400}
            ],
            "metadata": {
                "date": "2024-01-01",
                "period": "Q1 2024"
            }
        }
        
        with patch('staffer.functions.export_analysis_to_excel.write_data_to_excel') as mock_write:
            mock_write.return_value = json.dumps({"status": "success", "rows_written": 3})
            
            result = export_analysis_to_excel(
                self.temp_dir,
                analysis_results,
                "metrics.xlsx"
            )
            
            result_data = json.loads(result)
            assert result_data["status"] == "exported"
            assert result_data["analysis_type"] == "generic"
    
    def test_invalid_working_directory(self):
        """Test handling of invalid working directory."""
        result = export_analysis_to_excel(
            "/invalid/path",
            {"data": []},
            "output.xlsx"
        )
        
        result_data = json.loads(result)
        assert result_data["status"] == "error"
        assert "Working directory does not exist" in result_data["error"]
    
    def test_empty_analysis_results(self):
        """Test handling of empty analysis results."""
        with patch('staffer.functions.export_analysis_to_excel.write_data_to_excel') as mock_write:
            mock_write.return_value = json.dumps({"status": "success", "rows_written": 0})
            
            result = export_analysis_to_excel(
                self.temp_dir,
                {},
                "empty.xlsx"
            )
            
            result_data = json.loads(result)
            assert result_data["status"] == "exported"
            assert result_data["rows_written"] == 0
    
    def test_file_path_security(self):
        """Test that file paths are restricted to working directory."""
        result = export_analysis_to_excel(
            self.temp_dir,
            {"data": []},
            "../../../etc/passwd"
        )
        
        result_data = json.loads(result)
        assert result_data["status"] == "error"
        assert "Invalid file path" in result_data["error"]
    
    def test_complex_nested_results(self):
        """Test exporting complex nested analysis results."""
        analysis_results = {
            "time_series": {
                "dates": ["2024-01", "2024-02", "2024-03"],
                "values": [1000, 1200, 1100],
                "forecast": [1150, 1250, 1300]
            },
            "seasonality": {
                "pattern": "monthly",
                "strength": 0.75
            },
            "analysis_type": "time_series"
        }
        
        with patch('staffer.functions.export_analysis_to_excel.write_data_to_excel') as mock_write:
            mock_write.return_value = json.dumps({"status": "success", "rows_written": 3})
            
            result = export_analysis_to_excel(
                self.temp_dir,
                analysis_results,
                "timeseries.xlsx"
            )
            
            result_data = json.loads(result)
            assert result_data["status"] == "exported"
            assert result_data["analysis_type"] == "time_series"
    
    def test_metadata_sheet_creation(self):
        """Test that metadata sheet is created with analysis summary."""
        analysis_results = {
            "data": [{"a": 1, "b": 2}],
            "analysis_type": "test",
            "timestamp": "2024-01-01T10:00:00"
        }
        
        with patch('staffer.functions.export_analysis_to_excel.write_data_to_excel') as mock_write:
            mock_write.return_value = json.dumps({"status": "success", "rows_written": 1})
            
            result = export_analysis_to_excel(
                self.temp_dir,
                analysis_results,
                "with_metadata.xlsx"
            )
            
            # Check that write_data_to_excel was called twice (data + metadata)
            assert mock_write.call_count == 2
            
            # Check metadata call
            metadata_call = mock_write.call_args_list[1]
            assert metadata_call[0][1] == "with_metadata.xlsx"  # file_path is 2nd arg
            assert metadata_call[0][2] == "Metadata"  # sheet_name is 3rd arg