import torch

print("=" * 60)
print("GPU Check for CivicMind")
print("=" * 60)
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU count: {torch.cuda.device_count()}")
    print(f"Current GPU: {torch.cuda.current_device()}")
    print(f"GPU name: {torch.cuda.get_device_name(0)}")
    props = torch.cuda.get_device_properties(0)
    print(f"GPU memory: {props.total_memory / 1e9:.1f} GB")
    print(f"Compute capability: {props.major}.{props.minor}")
    print(f"BF16 supported: {torch.cuda.is_bf16_supported()}")
    print("\n✅ Your GPU is ready for training!")
else:
    print("\n❌ No GPU detected!")
    print("\nTo use your GPU:")
    print("1. Install NVIDIA drivers: nvidia-smi")
    print("2. Install CUDA toolkit")
    print("3. Reinstall PyTorch with CUDA:")
    print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")

print("=" * 60)
