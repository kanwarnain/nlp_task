#!/usr/bin/env python3
"""
Setup script for Shell FAQ Retrieval System
"""

import os
import subprocess
import sys


def install_dependencies():
  """Install required Python packages"""
  print("📦 Installing Python dependencies...")
  try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("✅ Dependencies installed successfully!")
    return True
  except subprocess.CalledProcessError as e:
    print(f"❌ Failed to install dependencies: {e}")
    return False


def check_env_vars():
  """Check for required environment variables"""
  print("🔑 Checking environment variables...")

  if not os.getenv("OPENAI_API_KEY"):
    print("⚠️  OPENAI_API_KEY not found in environment")
    print("Please set your OpenAI API key:")
    print("  export OPENAI_API_KEY=your_key_here")
    print("Or create a .env file with:")
    print("  echo 'OPENAI_API_KEY=your_key_here' > .env")
    return False
  else:
    print("✅ OPENAI_API_KEY found")
    return True


def build_faq_index():
  """Build the initial FAQ index"""
  print("🔍 Building FAQ index...")
  try:
    subprocess.check_call([sys.executable, "cli.py", "build"])
    print("✅ FAQ index built successfully!")
    return True
  except subprocess.CalledProcessError as e:
    print(f"❌ Failed to build FAQ index: {e}")
    return False


def main():
  print("🛢️  Shell FAQ Retrieval System Setup")
  print("=" * 50)

  # Check if we're in the right directory
  if not os.path.exists("shell-retail/faq/"):
    print("❌ FAQ directory not found. Please run this from the project root.")
    sys.exit(1)

  # Install dependencies
  if not install_dependencies():
    sys.exit(1)

  # Check environment
  env_ok = check_env_vars()

  # Build index if environment is ready
  if env_ok:
    if not build_faq_index():
      print("⚠️  Index building failed, but you can try manually later:")
      print("  python cli.py build")

  print("\n🎉 Setup complete!")
  print("\nUsage:")
  print("  CLI: python cli.py ask 'How do I download the Shell app?'")
  print("  Chat: python cli.py chat --show-sources")
  print("  Web: streamlit run app.py")

  if not env_ok:
    print("\n💡 Remember to set your OPENAI_API_KEY before using the system!")


if __name__ == "__main__":
  main()
