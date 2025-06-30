"""Tests for load_dataset tool."""

import pytest
import os
import tempfile
import json
import pandas as pd
from staffer.functions.analytics.tools.load_dataset_tool import load_dataset
from function_bank.mcp_server.models.schemas import loaded_datasets, dataset_schemas


def setup_function():
    """Clear datasets before each test."""
    loaded_datasets.clear()
    dataset_schemas.clear()


def test_load_csv_dataset():
    """Test loading a CSV dataset."""
    # Create test CSV
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("name,age,score\nAlice,25,95.5\nBob,30,87.2\nCharlie,35,92.1\n")
        csv_path = f.name
    
    try:
        result = load_dataset(csv_path, "test_data")
        
        # Verify successful loading
        assert result["status"] == "loaded"
        assert result["dataset_name"] == "test_data"
        assert result["rows"] == 3
        assert result["columns"] == ["name", "age", "score"]
        assert "test_data" in loaded_datasets
        assert "test_data" in dataset_schemas
        
    finally:
        os.unlink(csv_path)


def test_load_json_dataset():
    """Test loading a JSON dataset."""
    # Create test JSON
    test_data = [
        {"product": "Widget A", "sales": 1000, "region": "North"},
        {"product": "Widget B", "sales": 1500, "region": "South"}
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        json_path = f.name
    
    try:
        result = load_dataset(json_path, "sales_data")
        
        # Verify successful loading
        assert result["status"] == "loaded"
        assert result["dataset_name"] == "sales_data"
        assert result["rows"] == 2
        assert result["columns"] == ["product", "sales", "region"]
        
    finally:
        os.unlink(json_path)


def test_sampling_functionality():
    """Test dataset sampling."""
    # Create larger CSV for sampling
    data = pd.DataFrame({
        'id': range(100),
        'value': range(100, 200)
    })
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        data.to_csv(f.name, index=False)
        csv_path = f.name
    
    try:
        result = load_dataset(csv_path, "big_data", sample_size=10)
        
        # Verify sampling worked
        assert result["rows"] == 10
        assert result["sampled"] == True
        assert result["original_rows"] == 100
        assert len(loaded_datasets["big_data"]) == 10
        
    finally:
        os.unlink(csv_path)


def test_file_not_found():
    """Test error handling for missing file."""
    result = load_dataset("nonexistent.csv", "missing_data")
    
    assert result["status"] == "error"
    assert "Failed to load dataset" in result["message"]


def test_invalid_file_format():
    """Test error handling for unsupported file format."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("not a valid dataset format")
        txt_path = f.name
    
    try:
        result = load_dataset(txt_path, "invalid_data")
        
        assert result["status"] == "error"
        assert "Failed to load dataset" in result["message"]
        
    finally:
        os.unlink(txt_path)