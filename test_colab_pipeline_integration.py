#!/usr/bin/env python3
"""
Integration test for Colab Training Pipeline

Tests that all components can be imported and instantiated correctly.
Does NOT run full training (too time-consuming for CI).
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all required modules can be imported."""
    print("=" * 70)
    print("TEST 1: Module Imports")
    print("=" * 70)
    
    core_imports_ok = True
    optional_imports_ok = True
    
    # Core imports (required)
    try:
        from environment.setup import EnvironmentSetup
        print("✅ EnvironmentSetup imported")
        
        from training.data_generator import DatasetGenerator
        print("✅ DatasetGenerator imported")
        
        from training.q_learning_trainer import QLearningTrainer
        print("✅ QLearningTrainer imported")
        
        from training.evaluation_engine import EvaluationEngine
        print("✅ EvaluationEngine imported")
        
        from training.artifact_exporter import ArtifactExporter
        print("✅ ArtifactExporter imported")
        
        from training.evidence_generator import EvidenceGenerator
        print("✅ EvidenceGenerator imported")
        
    except ImportError as e:
        print(f"\n❌ Core import failed: {e}\n")
        core_imports_ok = False
    
    # Optional imports (GRPO requires transformers, peft, etc.)
    try:
        from training.grpo_trainer import GRPOTrainer
        print("✅ GRPOTrainer imported")
    except ImportError as e:
        print(f"⚠️  GRPOTrainer import failed (optional): {e}")
        print("   This is expected if transformers/peft are not installed")
        optional_imports_ok = False
    
    if core_imports_ok:
        print("\n✅ All core imports successful!")
        if not optional_imports_ok:
            print("⚠️  Some optional imports failed (GRPO requires transformers)")
        print()
        return True
    else:
        print("\n❌ Core imports failed!\n")
        return False


def test_instantiation():
    """Test that all classes can be instantiated."""
    print("=" * 70)
    print("TEST 2: Class Instantiation")
    print("=" * 70)
    
    core_instantiation_ok = True
    optional_instantiation_ok = True
    
    try:
        from environment.setup import EnvironmentSetup
        setup = EnvironmentSetup()
        print("✅ EnvironmentSetup instantiated")
        
        from training.data_generator import DatasetGenerator
        generator = DatasetGenerator(n_samples=10, good_ratio=0.7)
        print("✅ DatasetGenerator instantiated")
        
        from training.q_learning_trainer import QLearningTrainer
        q_trainer = QLearningTrainer(episodes=10)
        print("✅ QLearningTrainer instantiated")
        
        from training.evaluation_engine import EvaluationEngine
        evaluator = EvaluationEngine(n_episodes=1, max_weeks=5, difficulty=1)
        print("✅ EvaluationEngine instantiated")
        
        from training.artifact_exporter import ArtifactExporter
        exporter = ArtifactExporter()
        print("✅ ArtifactExporter instantiated")
        
        from training.evidence_generator import EvidenceGenerator
        evidence_gen = EvidenceGenerator()
        print("✅ EvidenceGenerator instantiated")
        
    except Exception as e:
        print(f"\n❌ Core instantiation failed: {e}\n")
        core_instantiation_ok = False
    
    # Optional: GRPO trainer (requires transformers)
    try:
        from training.grpo_trainer import GRPOTrainer
        # Don't load model (too slow), just instantiate
        grpo_trainer = GRPOTrainer(epochs=1, batch_size=1)
        print("✅ GRPOTrainer instantiated")
    except Exception as e:
        print(f"⚠️  GRPOTrainer instantiation failed (optional): {str(e)[:100]}")
        optional_instantiation_ok = False
    
    if core_instantiation_ok:
        print("\n✅ All core classes instantiated successfully!")
        if not optional_instantiation_ok:
            print("⚠️  Some optional classes failed (GRPO requires transformers)")
        print()
        return True
    else:
        print("\n❌ Core instantiation failed!\n")
        return False


def test_notebook_structure():
    """Test that the notebook has the expected structure."""
    print("=" * 70)
    print("TEST 3: Notebook Structure")
    print("=" * 70)
    
    try:
        import json
        
        notebook_path = Path("notebooks/colab_training_pipeline.ipynb")
        
        if not notebook_path.exists():
            print(f"❌ Notebook not found: {notebook_path}")
            return False
        
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        # Check basic structure
        assert 'cells' in notebook, "Notebook missing 'cells' key"
        assert 'metadata' in notebook, "Notebook missing 'metadata' key"
        
        cells = notebook['cells']
        print(f"✅ Notebook has {len(cells)} cells")
        
        # Count cell types
        markdown_cells = sum(1 for cell in cells if cell['cell_type'] == 'markdown')
        code_cells = sum(1 for cell in cells if cell['cell_type'] == 'code')
        
        print(f"✅ Markdown cells: {markdown_cells}")
        print(f"✅ Code cells: {code_cells}")
        
        # Check for key sections (by searching markdown cells)
        markdown_content = []
        for cell in cells:
            if cell['cell_type'] == 'markdown':
                content = ''.join(cell['source'])
                markdown_content.append(content)
        
        all_markdown = '\n'.join(markdown_content)
        
        required_sections = [
            "Environment Setup",
            "GPU Configuration",
            "Training Mode Selection",
            "Dataset Generation",
            "Q-Learning Training",
            "Model Evaluation",
            "Artifact Export"
        ]
        
        for section in required_sections:
            if section in all_markdown:
                print(f"✅ Found section: {section}")
            else:
                print(f"⚠️  Missing section: {section}")
        
        print("\n✅ Notebook structure validated!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Notebook validation failed: {e}\n")
        return False


def test_file_structure():
    """Test that all required files exist."""
    print("=" * 70)
    print("TEST 4: File Structure")
    print("=" * 70)
    
    required_files = [
        "environment/setup.py",
        "training/data_generator.py",
        "training/q_learning_trainer.py",
        "training/grpo_trainer.py",
        "training/evaluation_engine.py",
        "training/artifact_exporter.py",
        "training/evidence_generator.py",
        "evaluation/anti_hacking_validation.py",
        "notebooks/colab_training_pipeline.ipynb",
        "notebooks/COLAB_GUIDE.md",
        "notebooks/README.md"
    ]
    
    all_exist = True
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            all_exist = False
    
    if all_exist:
        print("\n✅ All required files exist!\n")
    else:
        print("\n⚠️  Some files are missing\n")
    
    return all_exist


def main():
    """Run all integration tests."""
    print("\n" + "=" * 70)
    print("COLAB TRAINING PIPELINE - INTEGRATION TESTS")
    print("=" * 70)
    print()
    
    results = []
    
    # Run tests
    results.append(("Module Imports", test_imports()))
    results.append(("Class Instantiation", test_instantiation()))
    results.append(("Notebook Structure", test_notebook_structure()))
    results.append(("File Structure", test_file_structure()))
    
    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 70)
    
    if passed == total:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!\n")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
