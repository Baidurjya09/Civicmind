"""
Environment Setup Module for Google Colab Training Pipeline

This module provides the EnvironmentSetup class that handles:
- Runtime environment detection (Colab, Kaggle, local)
- Dependency installation with retry logic
- Import verification for critical packages
- Environment summary generation
"""

import sys
import os
import subprocess
import time
import importlib
from typing import Dict, Literal


class EnvironmentSetup:
    """
    Handles environment detection, dependency installation, and verification
    for the CivicMind training pipeline.
    """
    
    def __init__(self):
        """Initialize EnvironmentSetup."""
        self.environment_type = None
        self.python_version = None
        self.pytorch_version = None
        self.device_type = None
    
    def detect_environment(self) -> Literal["colab", "kaggle", "local"]:
        """
        Detect the runtime environment.
        
        Returns:
            str: One of "colab", "kaggle", or "local"
        """
        # Check for Google Colab
        if "google.colab" in sys.modules:
            self.environment_type = "colab"
            return "colab"
        
        # Check for Kaggle
        if os.path.exists("/kaggle"):
            self.environment_type = "kaggle"
            return "kaggle"
        
        # Default to local
        self.environment_type = "local"
        return "local"
    
    def install_dependencies(self, requirements_path: str = "requirements.txt") -> bool:
        """
        Install dependencies from requirements.txt with retry logic.
        
        Args:
            requirements_path: Path to requirements.txt file
            
        Returns:
            bool: True if installation succeeded, False otherwise
        """
        max_retries = 3
        backoff_times = [1, 2, 4]  # Exponential backoff: 1s, 2s, 4s
        
        for attempt in range(max_retries):
            try:
                print(f"📦 Installing dependencies (attempt {attempt + 1}/{max_retries})...")
                
                # Run pip install
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", requirements_path],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    print("✅ Dependencies installed successfully!")
                    return True
                else:
                    print(f"⚠️  Installation failed with return code {result.returncode}")
                    if result.stderr:
                        print(f"   Error: {result.stderr[:200]}")  # Show first 200 chars
                    
                    # If not last attempt, wait and retry
                    if attempt < max_retries - 1:
                        wait_time = backoff_times[attempt]
                        print(f"   Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    
            except subprocess.TimeoutExpired:
                print(f"⚠️  Installation timed out after 5 minutes")
                if attempt < max_retries - 1:
                    wait_time = backoff_times[attempt]
                    print(f"   Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    
            except Exception as e:
                print(f"⚠️  Installation failed with error: {e}")
                if attempt < max_retries - 1:
                    wait_time = backoff_times[attempt]
                    print(f"   Retrying in {wait_time}s...")
                    time.sleep(wait_time)
        
        print("❌ Failed to install dependencies after 3 attempts")
        return False
    
    def verify_imports(self) -> Dict[str, bool]:
        """
        Verify that critical packages can be imported.
        
        Returns:
            dict: Dictionary mapping package names to import success status
        """
        critical_packages = ["torch", "transformers", "datasets", "peft"]
        results = {}
        
        print("🔍 Verifying critical imports...")
        
        for package in critical_packages:
            try:
                importlib.import_module(package)
                results[package] = True
                print(f"   ✅ {package}")
            except ImportError as e:
                results[package] = False
                print(f"   ❌ {package}: {e}")
        
        return results
    
    def get_environment_summary(self) -> Dict[str, str]:
        """
        Get summary of the environment configuration.
        
        Returns:
            dict: Dictionary with Python version, PyTorch version, and device type
        """
        summary = {}
        
        # Python version
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        summary["python_version"] = self.python_version
        
        # PyTorch version
        try:
            import torch
            self.pytorch_version = torch.__version__
            summary["pytorch_version"] = self.pytorch_version
            
            # Device type
            if torch.cuda.is_available():
                self.device_type = "cuda"
                summary["device_type"] = "cuda"
                summary["gpu_name"] = torch.cuda.get_device_name(0)
                summary["gpu_memory"] = f"{torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB"
            else:
                self.device_type = "cpu"
                summary["device_type"] = "cpu"
                
        except ImportError:
            summary["pytorch_version"] = "Not installed"
            summary["device_type"] = "Unknown"
        
        # Environment type
        if self.environment_type is None:
            self.detect_environment()
        summary["environment"] = self.environment_type
        
        return summary
    
    def display_summary(self) -> None:
        """Display environment summary in a formatted way."""
        summary = self.get_environment_summary()
        
        print("\n" + "="*50)
        print("🚀 Environment Summary")
        print("="*50)
        print(f"Environment:      {summary.get('environment', 'Unknown')}")
        print(f"Python Version:   {summary.get('python_version', 'Unknown')}")
        print(f"PyTorch Version:  {summary.get('pytorch_version', 'Unknown')}")
        print(f"Device Type:      {summary.get('device_type', 'Unknown')}")
        
        if summary.get('device_type') == 'cuda':
            print(f"GPU Name:         {summary.get('gpu_name', 'Unknown')}")
            print(f"GPU Memory:       {summary.get('gpu_memory', 'Unknown')}")
        
        print("="*50 + "\n")
