"""
Abu Monya WebView APK Builder
==============================
This script builds an Android APK using the Android SDK build tools.
It does NOT require Android Studio — only the Android SDK command-line tools.

Requirements:
  - Java JDK 17+ (https://adoptium.net/)
  - Android SDK command-line tools (https://developer.android.com/studio#command-line-tools-only)
  - Set ANDROID_HOME environment variable

Usage:
  python build_apk.py

Output:
  AbuMonyaApp/output/AbuMonya.apk
"""

import os
import sys
import subprocess
import shutil
import zipfile

# ── Configuration ─────────────────────────────────────────────────────────────
APP_NAME        = "AbuMonya"
PACKAGE_NAME    = "com.abumonyaagency.app"
VERSION_CODE    = "1"
VERSION_NAME    = "1.0"
MIN_SDK         = "21"
TARGET_SDK      = "34"
COMPILE_SDK     = "34"
WEBSITE_URL     = "https://abumonyaagency.com"

# ── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR  = SCRIPT_DIR
OUTPUT_DIR   = os.path.join(PROJECT_DIR, "output")
ANDROID_HOME = os.environ.get("ANDROID_HOME", os.path.expanduser("~/AppData/Local/Android/Sdk"))


def check_requirements():
    """Check that Java and SDK tools are available."""
    print("🔍 Checking requirements...")

    # Java
    try:
        result = subprocess.run(["java", "-version"], capture_output=True, text=True)
        print(f"  ✅ Java found: {result.stderr.splitlines()[0] if result.stderr else 'OK'}")
    except FileNotFoundError:
        print("  ❌ Java not found. Please install JDK 17+ from https://adoptium.net/")
        sys.exit(1)

    # Android SDK
    if not os.path.isdir(ANDROID_HOME):
        print(f"  ❌ Android SDK not found at: {ANDROID_HOME}")
        print("     Set the ANDROID_HOME environment variable to your SDK path.")
        print("     Download: https://developer.android.com/studio#command-line-tools-only")
        sys.exit(1)
    else:
        print(f"  ✅ Android SDK found: {ANDROID_HOME}")

    print()


def find_build_tool(tool_name):
    """Locate an Android build tool in the SDK."""
    build_tools_dir = os.path.join(ANDROID_HOME, "build-tools")
    if not os.path.isdir(build_tools_dir):
        return None
    versions = sorted(os.listdir(build_tools_dir), reverse=True)
    for version in versions:
        tool = os.path.join(build_tools_dir, version, tool_name)
        if os.name == "nt":
            tool_exe = tool + ".exe"
            if os.path.isfile(tool_exe):
                return tool_exe
            bat = tool + ".bat"
            if os.path.isfile(bat):
                return bat
        if os.path.isfile(tool):
            return tool
    return None


def find_platform_jar():
    """Find android.jar for the target SDK."""
    platforms_dir = os.path.join(ANDROID_HOME, "platforms")
    if not os.path.isdir(platforms_dir):
        return None
    target = f"android-{COMPILE_SDK}"
    jar = os.path.join(platforms_dir, target, "android.jar")
    if os.path.isfile(jar):
        return jar
    # Try any available platform
    for p in sorted(os.listdir(platforms_dir), reverse=True):
        jar = os.path.join(platforms_dir, p, "android.jar")
        if os.path.isfile(jar):
            return jar
    return None


def run(cmd, cwd=None, check=True):
    """Run a shell command and print output."""
    print(f"  ▶ {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, cwd=cwd or PROJECT_DIR,
                            capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if check and result.returncode != 0:
        print(f"\n❌ Command failed (code {result.returncode})")
        sys.exit(1)
    return result


def use_gradle_build():
    """Build the APK using Gradle (preferred method with Android Studio project)."""
    print("🔨 Building APK with Gradle...")
    gradle_project = os.path.join(SCRIPT_DIR, "AbuMonyaApp")

    if not os.path.isdir(gradle_project):
        print(f"  ❌ Android project not found at: {gradle_project}")
        sys.exit(1)

    gradlew = os.path.join(gradle_project, "gradlew.bat" if os.name == "nt" else "gradlew")

    # Download gradle wrapper jar if missing
    wrapper_jar = os.path.join(gradle_project, "gradle", "wrapper", "gradle-wrapper.jar")
    if not os.path.isfile(wrapper_jar):
        print("  ⚠️  Gradle wrapper JAR missing — downloading...")
        _download_gradle_wrapper(wrapper_jar)

    print("  Building release APK (this may take a few minutes on first run)...")
    run([gradlew, "assembleRelease", "--no-daemon"], cwd=gradle_project)

    # Find the output APK
    for root, dirs, files in os.walk(gradle_project):
        for f in files:
            if f.endswith(".apk"):
                src = os.path.join(root, f)
                os.makedirs(OUTPUT_DIR, exist_ok=True)
                dest = os.path.join(OUTPUT_DIR, f"{APP_NAME}.apk")
                shutil.copy2(src, dest)
                print(f"\n✅ APK built successfully!")
                print(f"   📦 Output: {dest}")
                return dest

    print("❌ No APK file found after build.")
    sys.exit(1)


def _download_gradle_wrapper(dest_path):
    """Download the gradle-wrapper.jar from Maven Central."""
    import urllib.request
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    url = "https://raw.githubusercontent.com/nickmccurdy/gradle-wrapper/main/gradle/wrapper/gradle-wrapper.jar"
    try:
        urllib.request.urlretrieve(url, dest_path)
        print(f"  ✅ Gradle wrapper downloaded.")
    except Exception as e:
        print(f"  ❌ Could not download gradle-wrapper.jar: {e}")
        print("     Please run Android Studio and open the AbuMonyaApp project to sync it.")
        sys.exit(1)


def main():
    print("=" * 60)
    print("  Abu Monya Agency — WebView APK Builder")
    print("=" * 60)
    print()

    check_requirements()
    apk_path = use_gradle_build()

    print()
    print("=" * 60)
    print("  🎉 Done! Your APK is ready to install:")
    print(f"  {apk_path}")
    print()
    print("  To install on a connected Android device:")
    print(f"  adb install \"{apk_path}\"")
    print("=" * 60)


if __name__ == "__main__":
    main()
