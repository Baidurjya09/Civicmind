"""
Unit tests for EnvironmentSetup class
"""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from environment.setup import EnvironmentSetup


class TestEnvironmentSetup:
    """Test suite for EnvironmentSetup class"""
    
    def test_detect_environment_colab(self):
        """Test environment detection for Google Colab"""
        setup = EnvironmentSetup()
        
        # Mock google.colab in sys.modules
        with patch.dict(sys.modules, {"google.colab": MagicMock()}):
            env = setup.detect_environment()
            assert env == "colab"
            assert setup.environment_type == "colab"
    
    def test_detect_environment_kaggle(self):
        """Test environment detection for Kaggle"""
        setup = EnvironmentSetup()
        
        # Mock /kaggle directory existence
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = True
            # Ensure google.colab is not in sys.modules
            with patch.dict(sys.modules, {}, clear=False):
                if "google.colab" in sys.modules:
                    del sys.modules["google.colab"]
                env = setup.detect_environment()
                assert env == "kaggle"
                assert setup.environment_type == "kaggle"
    
    def test_detect_environment_local(self):
        """Test environment detection for local environment"""
        setup = EnvironmentSetup()
        
        # Mock no Colab and no Kaggle
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = False
            with patch.dict(sys.modules, {}, clear=False):
                if "google.colab" in sys.modules:
                    del sys.modules["google.colab"]
                env = setup.detect_environment()
                assert env == "local"
                assert setup.environment_type == "local"
    
    def test_verify_imports_success(self):
        """Test import verification when all packages are available"""
        setup = EnvironmentSetup()
        
        # Mock successful imports
        with patch("importlib.import_module") as mock_import:
            mock_import.return_value = MagicMock()
            results = setup.verify_imports()
            
            assert results["torch"] == True
            assert results["transformers"] == True
            assert results["datasets"] == True
            assert results["peft"] == True
    
    def test_verify_imports_failure(self):
        """Test import verification when packages are missing"""
        setup = EnvironmentSetup()
        
        # Mock failed imports
        with patch("importlib.import_module") as mock_import:
            mock_import.side_effect = ImportError("Package not found")
            results = setup.verify_imports()
            
            assert results["torch"] == False
            assert results["transformers"] == False
            assert results["datasets"] == False
            assert results["peft"] == False
    
    def test_get_environment_summary_with_cuda(self):
        """Test environment summary generation with CUDA available"""
        setup = EnvironmentSetup()
        
        # Mock torch with CUDA
        mock_torch = MagicMock()
        mock_torch.__version__ = "2.1.0"
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.get_device_name.return_value = "Tesla T4"
        mock_torch.cuda.get_device_properties.return_value.total_memory = 16e9
        
        with patch.dict(sys.modules, {"torch": mock_torch}):
            summary = setup.get_environment_summary()
            
            assert "python_version" in summary
            assert summary["pytorch_version"] == "2.1.0"
            assert summary["device_type"] == "cuda"
            assert summary["gpu_name"] == "Tesla T4"
            assert "16.00 GB" in summary["gpu_memory"]
    
    def test_get_environment_summary_cpu_only(self):
        """Test environment summary generation without CUDA"""
        setup = EnvironmentSetup()
        
        # Mock torch without CUDA
        mock_torch = MagicMock()
        mock_torch.__version__ = "2.1.0"
        mock_torch.cuda.is_available.return_value = False
        
        with patch.dict(sys.modules, {"torch": mock_torch}):
            summary = setup.get_environment_summary()
            
            assert "python_version" in summary
            assert summary["pytorch_version"] == "2.1.0"
            assert summary["device_type"] == "cpu"
            assert "gpu_name" not in summary
    
    def test_get_environment_summary_no_torch(self):
        """Test environment summary when PyTorch is not installed"""
        setup = EnvironmentSetup()
        
        # Mock torch import failure
        with patch("importlib.import_module") as mock_import:
            mock_import.side_effect = ImportError("No module named 'torch'")
            
            # Temporarily remove torch from sys.modules if present
            torch_backup = sys.modules.get("torch")
            if "torch" in sys.modules:
                del sys.modules["torch"]
            
            try:
                summary = setup.get_environment_summary()
                assert summary["pytorch_version"] == "Not installed"
                assert summary["device_type"] == "Unknown"
            finally:
                # Restore torch if it was present
                if torch_backup:
                    sys.modules["torch"] = torch_backup


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
