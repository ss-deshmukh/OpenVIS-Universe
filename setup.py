#!/usr/bin/env python3
"""
Setup script for Polkadot OpenGov Voting Galaxy Visualization
"""

import subprocess
import sys
import os

def install_requirements():
    """Install Python requirements"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Python requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False
    return True

def run_data_extraction():
    """Run the data extraction script"""
    try:
        subprocess.check_call([sys.executable, "neo4j_data_extractor.py"])
        print("✅ Data extraction completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during data extraction: {e}")
        return False
    return True

def main():
    print("🚀 Setting up Polkadot OpenGov Voting Galaxy Visualization")
    print("=" * 60)
    
    # Install requirements
    print("📦 Installing Python requirements...")
    if not install_requirements():
        return
    
    # Run data extraction
    print("🔍 Extracting data from Neo4j...")
    if not run_data_extraction():
        return
    
    print("\n✨ Setup complete!")
    print("📁 Files created:")
    print("   - polkadot_voting_data.json (visualization data)")
    print("   - voting_galaxy.html (3D visualization)")
    print("\n🌐 To view the visualization:")
    print("   1. Open voting_galaxy.html in a web browser")
    print("   2. Or serve it with: python -m http.server 8000")
    print("   3. Then visit: http://localhost:8000/voting_galaxy.html")

if __name__ == "__main__":
    main() 