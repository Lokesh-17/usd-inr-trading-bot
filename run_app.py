#!/usr/bin/env python3

import subprocess
import sys
import os

def main():
    """Run the EduCareer+ application"""
    
    # Add local bin to PATH
    local_bin = os.path.expanduser("~/.local/bin")
    if local_bin not in os.environ.get("PATH", ""):
        os.environ["PATH"] = f"{os.environ.get('PATH', '')}:{local_bin}"
    
    print("🚀 Starting EduCareer+ Job Portal...")
    print("📍 Access the application at: http://localhost:8501")
    print("💡 Use Ctrl+C to stop the application")
    print("-" * 50)
    
    try:
        # Run streamlit
        cmd = [
            "streamlit", "run", "educareer_plus.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ]
        
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running application: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Streamlit not found. Please install dependencies:")
        print("pip3 install --break-system-packages streamlit pandas plotly numpy scikit-learn streamlit-option-menu")
        sys.exit(1)

if __name__ == "__main__":
    main()