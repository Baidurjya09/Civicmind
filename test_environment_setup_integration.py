"""
Integration test for EnvironmentSetup class

This script tests the complete functionality of the EnvironmentSetup class
without requiring pytest.
"""

from environment.setup import EnvironmentSetup


def test_environment_detection():
    """Test environment detection"""
    print("Testing environment detection...")
    setup = EnvironmentSetup()
    env = setup.detect_environment()
    print(f"✅ Environment detected: {env}")
    assert env in ["colab", "kaggle", "local"], f"Invalid environment: {env}"
    return True


def test_import_verification():
    """Test import verification"""
    print("\nTesting import verification...")
    setup = EnvironmentSetup()
    results = setup.verify_imports()
    
    # Check that results is a dictionary with expected keys
    expected_packages = ["torch", "transformers", "datasets", "peft"]
    for package in expected_packages:
        assert package in results, f"Missing package in results: {package}"
        print(f"  {package}: {'✅' if results[package] else '❌'}")
    
    print("✅ Import verification completed")
    return True


def test_environment_summary():
    """Test environment summary generation"""
    print("\nTesting environment summary...")
    setup = EnvironmentSetup()
    summary = setup.get_environment_summary()
    
    # Check required keys
    required_keys = ["python_version", "pytorch_version", "device_type", "environment"]
    for key in required_keys:
        assert key in summary, f"Missing key in summary: {key}"
    
    print("✅ Environment summary generated successfully")
    print(f"  Python: {summary['python_version']}")
    print(f"  PyTorch: {summary['pytorch_version']}")
    print(f"  Device: {summary['device_type']}")
    print(f"  Environment: {summary['environment']}")
    
    if summary['device_type'] == 'cuda':
        print(f"  GPU: {summary.get('gpu_name', 'Unknown')}")
        print(f"  VRAM: {summary.get('gpu_memory', 'Unknown')}")
    
    return True


def test_display_summary():
    """Test formatted display of environment summary"""
    print("\nTesting display summary...")
    setup = EnvironmentSetup()
    setup.display_summary()
    print("✅ Display summary completed")
    return True


def main():
    """Run all integration tests"""
    print("="*60)
    print("EnvironmentSetup Integration Tests")
    print("="*60)
    
    tests = [
        test_environment_detection,
        test_import_verification,
        test_environment_summary,
        test_display_summary,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed: {test.__name__}")
            print(f"   Error: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60)
    
    if failed == 0:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    exit(main())
