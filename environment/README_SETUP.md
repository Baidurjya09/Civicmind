# EnvironmentSetup Class Documentation

## Overview

The `EnvironmentSetup` class provides automated environment detection, dependency installation, and verification for the CivicMind training pipeline. It's designed to work seamlessly across Google Colab, Kaggle, and local environments.

## Features

- **Environment Detection**: Automatically detects Colab, Kaggle, or local runtime
- **Dependency Installation**: Installs packages from requirements.txt with retry logic
- **Import Verification**: Checks that critical packages can be imported
- **Environment Summary**: Provides detailed information about Python, PyTorch, and GPU
- **Retry Logic**: Exponential backoff (1s, 2s, 4s) for failed installations

## Usage

### Basic Usage

```python
from environment.setup import EnvironmentSetup

# Create instance
setup = EnvironmentSetup()

# Detect environment
env = setup.detect_environment()
print(f"Running on: {env}")  # "colab", "kaggle", or "local"

# Install dependencies
success = setup.install_dependencies("requirements.txt")
if success:
    print("✅ Dependencies installed!")

# Verify imports
results = setup.verify_imports()
# Returns: {"torch": True, "transformers": True, "datasets": True, "peft": True}

# Display environment summary
setup.display_summary()
```

### In Google Colab Notebook

```python
# Cell 1: Environment Setup
from environment.setup import EnvironmentSetup

setup = EnvironmentSetup()

# Detect environment
env = setup.detect_environment()
print(f"📍 Running on: {env}")

# Install dependencies
print("📦 Installing dependencies...")
success = setup.install_dependencies("requirements.txt")

if not success:
    print("❌ Failed to install dependencies. Please check your internet connection.")
    raise RuntimeError("Dependency installation failed")

# Verify imports
print("\n🔍 Verifying critical imports...")
import_results = setup.verify_imports()

failed_imports = [pkg for pkg, status in import_results.items() if not status]
if failed_imports:
    print(f"⚠️  Failed to import: {', '.join(failed_imports)}")
    print("   Retrying installation...")
    setup.install_dependencies("requirements.txt")

# Display summary
setup.display_summary()
```

## API Reference

### `detect_environment() -> str`

Detects the runtime environment.

**Returns:**
- `"colab"` - Running in Google Colab
- `"kaggle"` - Running in Kaggle
- `"local"` - Running locally

**Detection Logic:**
- Checks for `google.colab` in `sys.modules` for Colab
- Checks for `/kaggle` directory for Kaggle
- Defaults to `"local"` otherwise

### `install_dependencies(requirements_path: str = "requirements.txt") -> bool`

Installs dependencies from requirements.txt with retry logic.

**Parameters:**
- `requirements_path` (str): Path to requirements.txt file

**Returns:**
- `True` if installation succeeded
- `False` if installation failed after 3 attempts

**Retry Logic:**
- Attempt 1: Immediate
- Attempt 2: Wait 1 second
- Attempt 3: Wait 2 seconds
- Attempt 4: Wait 4 seconds (if needed)

**Timeout:** 5 minutes per attempt

### `verify_imports() -> Dict[str, bool]`

Verifies that critical packages can be imported.

**Returns:**
Dictionary mapping package names to import success status:
```python
{
    "torch": True,
    "transformers": False,
    "datasets": True,
    "peft": True
}
```

**Checked Packages:**
- `torch` - PyTorch
- `transformers` - Hugging Face Transformers
- `datasets` - Hugging Face Datasets
- `peft` - Parameter-Efficient Fine-Tuning

### `get_environment_summary() -> Dict[str, str]`

Gets summary of the environment configuration.

**Returns:**
Dictionary with environment information:
```python
{
    "environment": "colab",
    "python_version": "3.10.12",
    "pytorch_version": "2.1.0+cu121",
    "device_type": "cuda",
    "gpu_name": "Tesla T4",
    "gpu_memory": "15.00 GB"
}
```

**Keys:**
- `environment` - Runtime environment (colab/kaggle/local)
- `python_version` - Python version (e.g., "3.10.12")
- `pytorch_version` - PyTorch version (e.g., "2.1.0+cu121")
- `device_type` - "cuda" or "cpu"
- `gpu_name` - GPU name (only if CUDA available)
- `gpu_memory` - GPU memory in GB (only if CUDA available)

### `display_summary() -> None`

Displays environment summary in a formatted way.

**Output Example:**
```
==================================================
🚀 Environment Summary
==================================================
Environment:      colab
Python Version:   3.10.12
PyTorch Version:  2.1.0+cu121
Device Type:      cuda
GPU Name:         Tesla T4
GPU Memory:       15.00 GB
==================================================
```

## Error Handling

### Installation Failures

The `install_dependencies()` method handles various failure scenarios:

1. **Network Issues**: Retries with exponential backoff
2. **Timeout**: 5-minute timeout per attempt, then retry
3. **Package Not Found**: Shows specific error message
4. **Permission Errors**: Shows error and suggests solutions

### Import Failures

The `verify_imports()` method catches `ImportError` exceptions and returns `False` for failed imports, allowing the caller to handle missing packages gracefully.

## Requirements

The class checks for these critical packages:
- `torch>=2.1.0` - PyTorch for deep learning
- `transformers>=4.36.0` - Hugging Face Transformers
- `datasets>=2.16.0` - Hugging Face Datasets
- `peft>=0.7.0` - Parameter-Efficient Fine-Tuning

## Testing

### Unit Tests

Run unit tests with pytest:
```bash
pytest environment/test_setup.py -v
```

### Integration Tests

Run integration tests:
```bash
python test_environment_setup_integration.py
```

### Manual Testing

Test individual methods:
```python
from environment.setup import EnvironmentSetup

setup = EnvironmentSetup()

# Test environment detection
print(setup.detect_environment())

# Test import verification
print(setup.verify_imports())

# Test environment summary
print(setup.get_environment_summary())
```

## Implementation Details

### Environment Detection

```python
def detect_environment(self) -> Literal["colab", "kaggle", "local"]:
    # Check for Google Colab
    if "google.colab" in sys.modules:
        return "colab"
    
    # Check for Kaggle
    if os.path.exists("/kaggle"):
        return "kaggle"
    
    # Default to local
    return "local"
```

### Retry Logic

```python
max_retries = 3
backoff_times = [1, 2, 4]  # Exponential backoff

for attempt in range(max_retries):
    try:
        # Attempt installation
        result = subprocess.run([...])
        if result.returncode == 0:
            return True
    except Exception as e:
        if attempt < max_retries - 1:
            wait_time = backoff_times[attempt]
            time.sleep(wait_time)
```

## Related Requirements

This class implements the following requirements from the spec:

- **Requirement 1.1**: Environment detection (Colab, Kaggle, local)
- **Requirement 1.2**: Dependency installation within 2 minutes
- **Requirement 1.5**: Verify critical imports
- **Requirement 1.7**: Display environment summary
- **Requirement 11.2**: Retry with exponential backoff
- **Requirement 11.4**: Display specific error messages

## Future Enhancements

Potential improvements for future versions:

1. **Progress Bar**: Add tqdm progress bar for installation
2. **Selective Installation**: Install only missing packages
3. **Version Checking**: Verify package versions match requirements
4. **Dependency Graph**: Show dependency tree for debugging
5. **Cache Support**: Use pip cache for faster reinstallation
6. **Virtual Environment**: Support for venv/conda environments

## License

Part of the CivicMind project. See main LICENSE file for details.
