"""
Artifact Exporter for CivicMind Training Pipeline
Packages all training artifacts for download and submission.
"""

import os
import zipfile
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class ArtifactExporter:
    """
    Artifact exporter for CivicMind training pipeline.
    
    Collects and packages all training artifacts into a downloadable zip file:
    - Trained model checkpoints
    - Evaluation results (JSON)
    - Training plots (PNG)
    - Validation reports
    - Dataset files
    
    Usage:
        exporter = ArtifactExporter()
        artifacts = exporter.collect_artifacts()
        archive_path = exporter.create_archive()
        exporter.trigger_download()  # Colab/Kaggle specific
    """
    
    def __init__(self):
        """Initialize artifact exporter."""
        self.artifacts = []
        self.archive_path = None
    
    def collect_artifacts(self, base_dirs: List[str] = None) -> List[str]:
        """
        Collect all artifact file paths.
        
        Args:
            base_dirs: List of base directories to search (defaults to standard locations)
            
        Returns:
            List of file paths that exist
        """
        if base_dirs is None:
            base_dirs = [
                "training/checkpoints",
                "evaluation/artifacts",
                "evidence/eval",
                "evidence/plots",
            ]
        
        self.artifacts = []
        
        for base_dir in base_dirs:
            if not os.path.exists(base_dir):
                continue
            
            # Walk directory tree
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    self.artifacts.append(file_path)
        
        print(f"📦 Collected {len(self.artifacts)} artifact files:")
        
        # Group by directory for display
        by_dir = {}
        for path in self.artifacts:
            dir_name = os.path.dirname(path)
            if dir_name not in by_dir:
                by_dir[dir_name] = []
            by_dir[dir_name].append(os.path.basename(path))
        
        for dir_name, files in sorted(by_dir.items()):
            print(f"   {dir_name}/")
            for file in sorted(files):
                file_path = os.path.join(dir_name, file)
                size_kb = os.path.getsize(file_path) / 1024
                print(f"      - {file} ({size_kb:.1f} KB)")
        
        return self.artifacts
    
    def create_archive(self, output_name: str = None) -> str:
        """
        Create zip archive with timestamp name.
        
        Args:
            output_name: Optional custom archive name (defaults to timestamped name)
            
        Returns:
            Path to created archive
        """
        if not self.artifacts:
            raise ValueError("No artifacts collected. Call collect_artifacts() first.")
        
        # Generate archive name with timestamp
        if output_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"civicmind_results_{timestamp}.zip"
        
        # Ensure .zip extension
        if not output_name.endswith('.zip'):
            output_name += '.zip'
        
        self.archive_path = output_name
        
        print(f"\n📦 Creating archive: {self.archive_path}")
        
        # Create zip file
        with zipfile.ZipFile(self.archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in self.artifacts:
                # Add file to zip with relative path
                arcname = file_path
                zipf.write(file_path, arcname=arcname)
                print(f"   Added: {arcname}")
        
        # Verify archive
        if not os.path.exists(self.archive_path):
            raise FileNotFoundError(f"Archive was not created: {self.archive_path}")
        
        archive_size_mb = os.path.getsize(self.archive_path) / (1024 * 1024)
        print(f"\n✅ Archive created successfully!")
        print(f"   Path: {self.archive_path}")
        print(f"   Size: {archive_size_mb:.2f} MB")
        print(f"   Files: {len(self.artifacts)}")
        
        return self.archive_path
    
    def get_archive_info(self) -> Dict[str, Any]:
        """
        Get information about the created archive.
        
        Returns:
            Dictionary with archive metadata
        """
        if not self.archive_path or not os.path.exists(self.archive_path):
            return {
                "exists": False,
                "path": self.archive_path,
                "size_mb": 0,
                "file_count": 0,
                "contents": []
            }
        
        archive_size_mb = os.path.getsize(self.archive_path) / (1024 * 1024)
        
        # Get contents summary
        contents = []
        with zipfile.ZipFile(self.archive_path, 'r') as zipf:
            for info in zipf.filelist:
                contents.append({
                    "filename": info.filename,
                    "size_kb": info.file_size / 1024,
                    "compressed_kb": info.compress_size / 1024,
                })
        
        return {
            "exists": True,
            "path": self.archive_path,
            "size_mb": round(archive_size_mb, 2),
            "file_count": len(contents),
            "contents": contents
        }
    
    def trigger_download(self) -> None:
        """
        Trigger download in Colab or Kaggle environment.
        
        For Colab: Uses files.download()
        For Kaggle: Copies to /kaggle/working/ for output
        For local: Displays path information
        """
        if not self.archive_path or not os.path.exists(self.archive_path):
            raise FileNotFoundError("No archive to download. Call create_archive() first.")
        
        # Detect environment
        import sys
        
        if 'google.colab' in sys.modules:
            # Google Colab
            print("\n📥 Triggering download in Google Colab...")
            try:
                from google.colab import files
                files.download(self.archive_path)
                print(f"✅ Download triggered: {self.archive_path}")
            except Exception as e:
                print(f"⚠️  Download failed: {e}")
                print(f"   You can manually download from: {self.archive_path}")
        
        elif os.path.exists('/kaggle'):
            # Kaggle
            print("\n📥 Copying to Kaggle output directory...")
            try:
                output_dir = '/kaggle/working'
                output_path = os.path.join(output_dir, os.path.basename(self.archive_path))
                
                import shutil
                shutil.copy2(self.archive_path, output_path)
                
                print(f"✅ Archive copied to: {output_path}")
                print(f"   It will be available in the Kaggle output after the notebook completes.")
            except Exception as e:
                print(f"⚠️  Copy failed: {e}")
                print(f"   You can manually access: {self.archive_path}")
        
        else:
            # Local environment
            print("\n📁 Running in local environment")
            print(f"   Archive location: {os.path.abspath(self.archive_path)}")
            print(f"   You can manually copy or move this file as needed.")
    
    def create_manifest(self, output_path: str = "artifact_manifest.json") -> str:
        """
        Create a manifest file listing all artifacts.
        
        Args:
            output_path: Path for manifest file
            
        Returns:
            Path to manifest file
        """
        manifest = {
            "created_at": datetime.now().isoformat(),
            "archive_path": self.archive_path,
            "total_files": len(self.artifacts),
            "files": []
        }
        
        for file_path in self.artifacts:
            if os.path.exists(file_path):
                manifest["files"].append({
                    "path": file_path,
                    "size_kb": round(os.path.getsize(file_path) / 1024, 2),
                    "type": os.path.splitext(file_path)[1]
                })
        
        with open(output_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✅ Manifest created: {output_path}")
        return output_path


if __name__ == "__main__":
    """Quick test of artifact exporter"""
    print("Testing ArtifactExporter...")
    print()
    
    exporter = ArtifactExporter()
    
    # Collect artifacts
    artifacts = exporter.collect_artifacts()
    
    if artifacts:
        # Create archive
        archive_path = exporter.create_archive()
        
        # Display info
        info = exporter.get_archive_info()
        print(f"\nArchive info:")
        print(f"  Size: {info['size_mb']} MB")
        print(f"  Files: {info['file_count']}")
        
        print("\n✅ Test complete!")
    else:
        print("⚠️  No artifacts found to package")
