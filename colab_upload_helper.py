"""
Helper script to upload Civicmind folder to Google Colab
Add this as the FIRST cell in your Colab notebook for easy setup
"""

# Cell 1: Upload Helper (Add this as the FIRST cell in Colab)
print("=" * 70)
print("CIVICMIND COLAB SETUP HELPER")
print("=" * 70)
print()

import os
import sys

# Check if we're in Colab
IN_COLAB = 'google.colab' in sys.modules

if IN_COLAB:
    print("✅ Running in Google Colab")
    print()
    
    # Check if Civicmind folder exists
    if os.path.exists('Civicmind'):
        print("✅ Civicmind folder found!")
        print(f"   Location: {os.path.abspath('Civicmind')}")
        print()
        print("You're all set! Continue to the next cell.")
    else:
        print("⚠️  Civicmind folder not found!")
        print()
        print("=" * 70)
        print("SETUP OPTIONS:")
        print("=" * 70)
        print()
        print("📋 OPTION 1: Upload Files (Recommended)")
        print("-" * 70)
        print("1. Click the folder icon (📁) in the left sidebar")
        print("2. Click the upload button (📤)")
        print("3. Select and upload the entire 'Civicmind' folder")
        print("4. Wait for upload to complete (~2-3 minutes)")
        print("5. Re-run this cell to verify")
        print()
        print("📋 OPTION 2: Clone from GitHub")
        print("-" * 70)
        print("Run this command in a new cell:")
        print("!git clone https://github.com/YOUR_USERNAME/civicmind.git Civicmind")
        print("(Replace YOUR_USERNAME with your GitHub username)")
        print()
        print("=" * 70)
        
        # Offer to use file upload widget
        try:
            from google.colab import files
            print()
            print("💡 TIP: You can also upload a ZIP file of the Civicmind folder")
            print("   Then run: !unzip Civicmind.zip")
        except:
            pass
else:
    print("ℹ️  Not running in Colab - skipping setup check")
    print("   This helper is only needed for Google Colab")

print()
print("=" * 70)
