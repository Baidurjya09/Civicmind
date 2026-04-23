#!/usr/bin/env python
"""
CivicMind — Setup Verification Script
Run this after installation to verify everything works.

Usage: python verify_setup.py
"""

import sys
import os
from pathlib import Path


def check_python_version():
    """Verify Python 3.10+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        return False, f"Python {version.major}.{version.minor} (need 3.10+)"
    return True, f"Python {version.major}.{version.minor}.{version.micro}"


def check_imports():
    """Verify all required packages are installed"""
    required = {
        "torch": "PyTorch",
        "transformers": "Transformers",
        "datasets": "Datasets",
        "fastapi": "FastAPI",
        "streamlit": "Streamlit",
        "pandas": "Pandas",
        "numpy": "NumPy",
    }
    
    results = {}
    for module, name in required.items():
        try:
            mod = __import__(module)
            version = getattr(mod, "__version__", "unknown")
            results[name] = (True, version)
        except ImportError:
            results[name] = (False, "not installed")
    
    return results


def check_cuda():
    """Verify CUDA/GPU availability"""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory / 1e9
            return True, f"{gpu_name} ({vram:.1f} GB VRAM)"
        else:
            return False, "No GPU detected (CPU mode only)"
    except Exception as e:
        return False, f"Error: {e}"


def check_project_structure():
    """Verify all required directories and files exist"""
    required_paths = [
        "environment/civic_env.py",
        "agents/agent_definitions.py",
        "agents/rebel_agent.py",
        "rewards/reward_model.py",
        "apis/mock_apis.py",
        "training/data_generator.py",
        "training/train_grpo.py",
        "demo/dashboard.py",
        "evaluate.py",
        "requirements.txt",
        "README.md",
    ]
    
    missing = []
    for path in required_paths:
        if not Path(path).exists():
            missing.append(path)
    
    if missing:
        return False, f"Missing {len(missing)} files"
    return True, f"All {len(required_paths)} files present"


def check_environment_import():
    """Try importing the main environment"""
    try:
        sys.path.insert(0, os.getcwd())
        from environment.civic_env import CivicMindEnv, CivicMindConfig
        return True, "Environment imports successfully"
    except Exception as e:
        return False, f"Import error: {e}"


def check_quick_run():
    """Try running a minimal episode"""
    try:
        sys.path.insert(0, os.getcwd())
        from environment.civic_env import CivicMindEnv, CivicMindConfig
        from evaluate import random_policy
        
        env = CivicMindEnv(CivicMindConfig(
            max_weeks=2,
            difficulty=1,
            seed=42,
        ))
        obs = env.reset()
        
        actions = {aid: random_policy(aid, obs[aid]) for aid in env.AGENT_IDS}
        obs, reward, done, info = env.step(actions)
        
        if 0 <= reward <= 1:
            return True, f"Episode ran successfully (reward={reward:.4f})"
        else:
            return False, f"Invalid reward: {reward}"
    except Exception as e:
        return False, f"Runtime error: {e}"


def print_result(name, status, message):
    """Print a formatted check result"""
    icon = "✅" if status else "❌"
    print(f"  {icon} {name:<25} {message}")


def main():
    print("=" * 70)
    print("  CivicMind — Setup Verification")
    print("=" * 70)
    print()
    
    all_passed = True
    
    # Python version
    status, msg = check_python_version()
    print_result("Python Version", status, msg)
    all_passed &= status
    
    # Package imports
    print()
    print("  Package Imports:")
    import_results = check_imports()
    for name, (status, version) in import_results.items():
        print_result(f"  {name}", status, version)
        all_passed &= status
    
    # CUDA/GPU
    print()
    status, msg = check_cuda()
    print_result("GPU/CUDA", status, msg)
    if not status:
        print("    ⚠️  Training will be slow without GPU (demo mode only)")
    
    # Project structure
    print()
    status, msg = check_project_structure()
    print_result("Project Structure", status, msg)
    all_passed &= status
    
    # Environment import
    print()
    status, msg = check_environment_import()
    print_result("Environment Import", status, msg)
    all_passed &= status
    
    # Quick run test
    print()
    print("  Running quick test episode...")
    status, msg = check_quick_run()
    print_result("Quick Run Test", status, msg)
    all_passed &= status
    
    # Summary
    print()
    print("=" * 70)
    if all_passed:
        print("  ✅ All checks passed! CivicMind is ready to use.")
        print()
        print("  Next steps:")
        print("    • Run demo:  python evaluate.py --mode compare")
        print("    • Train:     ./run_local.sh train")
        print("    • Dashboard: streamlit run demo/dashboard.py")
    else:
        print("  ❌ Some checks failed. Please fix the issues above.")
        print()
        print("  Common fixes:")
        print("    • Install packages: pip install -r requirements.txt")
        print("    • Install project:  pip install -e .")
        print("    • Check CUDA:       nvidia-smi")
    print("=" * 70)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
