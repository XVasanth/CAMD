#!/usr/bin/env python
"""
Setup script for CAD Educational Assessment System
Handles environment setup and dependency installation
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Display welcome banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════╗
    ║     🎓 CAD Educational Assessment System Setup 🎓      ║
    ╠═══════════════════════════════════════════════════════╣
    ║  Automated setup for CAD evaluation & plagiarism      ║
    ║  detection system                                     ║
    ╚═══════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check if Python version meets requirements"""
    print("\n📌 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Current version: {sys.version}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def create_virtual_environment():
    """Create virtual environment if it doesn't exist"""
    print("\n📌 Setting up virtual environment...")
    
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        return False

def get_pip_command():
    """Get the appropriate pip command for the OS"""
    system = platform.system()
    
    if system == "Windows":
        pip_path = Path("venv/Scripts/pip.exe")
    else:
        pip_path = Path("venv/bin/pip")
    
    if pip_path.exists():
        return str(pip_path)
    else:
        return "pip"

def install_dependencies():
    """Install required Python packages"""
    print("\n📌 Installing dependencies...")
    
    pip_cmd = get_pip_command()
    
    # Upgrade pip first
    print("  Upgrading pip...")
    subprocess.run([pip_cmd, "install", "--upgrade", "pip"], 
                  capture_output=True)
    
    # Core dependencies
    core_packages = [
        "streamlit>=1.28.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "trimesh[easy]>=4.0.0",  # with easy extras
        "scikit-learn>=1.3.0",
        "plotly>=5.17.0",
        "scipy>=1.11.0",
        "networkx>=3.1"
    ]
    
    # Install core packages
    print("  Installing core packages...")
    for package in core_packages:
        print(f"    Installing {package}...")
        result = subprocess.run([pip_cmd, "install", package], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"    ⚠️  Warning: Issue installing {package}")
            print(f"        {result.stderr}")
    
    # Optional packages (don't fail if they can't be installed)
    optional_packages = [
        ("pymeshlab", "Advanced mesh repair"),
        ("cascadio", "STEP file conversion")
    ]
    
    print("\n  Installing optional packages...")
    for package, description in optional_packages:
        print(f"    Installing {package} ({description})...")
        result = subprocess.run([pip_cmd, "install", package], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"    ✅ {package} installed")
        else:
            print(f"    ⚠️  {package} not available (optional)")
    
    print("\n✅ Dependencies installation complete")
    return True

def create_directories():
    """Create necessary directories"""
    print("\n📌 Creating project directories...")
    
    directories = [
        "sample_models/teacher",
        "sample_models/students",
        "reports"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Created: {dir_path}")

def create_sample_files():
    """Create sample configuration files"""
    print("\n📌 Creating sample files...")
    
    # Create .gitignore
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
venv/
env/
.env

# Streamlit
.streamlit/secrets.toml

# Reports
reports/*.md
reports/*.pdf
reports/*.zip

# CAD files
*.step
*.stp
*.iges
*.igs
*.STEP

# OS
.DS_Store
Thumbs.db
*.swp
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    print("  ✅ Created .gitignore")
    
    # Create .streamlit/config.toml
    streamlit_dir = Path(".streamlit")
    streamlit_dir.mkdir(exist_ok=True)
    
    config_content = """
[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 200
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
"""
    
    with open(streamlit_dir / "config.toml", "w") as f:
        f.write(config_content)
    print("  ✅ Created Streamlit config")

def test_installation():
    """Test if the installation was successful"""
    print("\n📌 Testing installation...")
    
    pip_cmd = get_pip_command()
    
    # Test imports
    test_script = """
import sys
try:
    import streamlit
    import trimesh
    import plotly
    import numpy
    import pandas
    import sklearn
    print("✅ All core modules imported successfully")
    sys.exit(0)
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
"""
    
    # Get Python executable from venv
    if platform.system() == "Windows":
        python_cmd = "venv/Scripts/python.exe"
    else:
        python_cmd = "venv/bin/python"
    
    result = subprocess.run([python_cmd, "-c", test_script], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print(result.stdout)
        return True
    else:
        print(result.stdout)
        print(result.stderr)
        return False

def print_instructions():
    """Print usage instructions"""
    
    system = platform.system()
    
    if system == "Windows":
        activate_cmd = "venv\\Scripts\\activate"
    else:
        activate_cmd = "source venv/bin/activate"
    
    instructions = f"""
    ╔═══════════════════════════════════════════════════════╗
    ║                  ✅ Setup Complete! ✅                 ║
    ╚═══════════════════════════════════════════════════════╝
    
    🚀 To run the application:
    
    1. Activate the virtual environment:
       {activate_cmd}
    
    2. Run the Streamlit app:
       streamlit run app.py
    
    3. Open your browser to:
       http://localhost:8501
    
    📁 Project Structure:
       • app.py           - Main application
       • sample_models/   - Place your CAD files here
       • reports/         - Generated reports saved here
    
    📖 For more information:
       • README.md        - Full documentation
       • requirements.txt - Package dependencies
    
    💡 Tips:
       • Upload teacher reference model first
       • Support formats: OBJ, STL, PLY, OFF
       • STEP files require cascadio (optional)
    """
    
    print(instructions)

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Setup failed: Python version requirement not met")
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        print("\n❌ Setup failed: Could not create virtual environment")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed: Could not install dependencies")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Create sample files
    create_sample_files()
    
    # Test installation
    if not test_installation():
        print("\n⚠️  Warning: Some imports failed. Check error messages above.")
    
    # Print instructions
    print_instructions()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)
