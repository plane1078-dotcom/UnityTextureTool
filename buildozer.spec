[app]

# (str) Title of your application
title = Unity Texture Tool

# (str) Package name
package.name = unitytexturetool

# (str) Package domain (needed for android/ios packaging)
package.domain = org.ziyou

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json

# (list) List of inclusions using pattern matching
source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let empty to not exclude anything)
source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = tests,bin,venv,.git

# (list) List of exclusions using pattern matching
source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning (method 1)
version = 0.1

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,kivymd,pillow,UnityPy,plyer,pyjnius,android

# (str) Custom source folders for requirements
# Sets custom source for any requirements with recipes
# requirements.source.kivy = ../../kivy

# (str) Presplash of the application
# presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
# icon.filename = %(source.dir)s/data/icon.png

# (list) Supported orientations
orientation = portrait

# (str) Fullscreen mode: auto, True, False
fullscreen = 0

# (str) Background color of app icon (for adaptive icon on Android 8+)
icon.adaptive_color = #1976D2

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86_64, x86
android.archs = arm64-v8a

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 24

# (int) Android NDK version to use
# android.ndk = 25b

# (int) Android SDK version to use
# android.sdk = 34

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
# android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
# android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded.)
# android.ant_path =

# (bool) If True, then skip trying to update the Android sdk
# android.skip_update = False

# (bool) If True, then automatically accept SDK license agreements
android.accept_sdk_license = True

# (str) Android entry point, default is ok for Kivy-based app
# android.entrypoint = org.kivy.android.PythonActivity

# (str) Full name including backward slashes to the java
# android.add_activity =

# (str) python-for-android branch to use, defaults to master
# p4a.branch = master

# (str) python-for-android specific fork to use, defaults to upstream
# p4a.fork = kivy

# (str) python-for-android-url not set means using default official repository
# p4a.url =

# (str) python-for-android local directory
# p4a.local_recipes =

# (str) The directory in which python-for-android should look for your own build recipes (if any)
# p4a.recipe_dir =

# (str) Setup for the Splash Screen on landscape, portrait or all
# android.landscape_splash = 0
# android.portrait_splash = 0
# android.splash = 0

# (list) Permissions
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_IMAGES

# (list) features (adds uses-feature -tags to manifest)
# android.features = android.hardware.usb.host

# (bool) If True, application will use a service (meaning it will
# run in background and never really close)
# android.services = 0

# (list) add java compile options
# android.add_compile_options = --add-exports=java.base/sun.nio.ch=ALL-UNNAMED

# (list) Gradle dependencies
# android.gradle_dependencies =

# (list) Java classes to add as activities to the manifest.
# android.add_activities =

# (list) Java classes to add as services to the manifest.
# android.add_services =

# (list) Java classes to add as receivers to the manifest.
# android.add_receivers =

# (list) Java classes to add as providers to the manifest.
# android.add_providers =

# (str) presplash color
# android.presplash_color = #1976D2

# (str) presplash text
# android.presplash_text = Unity Texture Tool

# (bool) Indicate whether the screen should stay on
# android.wakelock = 0

# (list) The Android stl to use for C++ dependencies
# android.stl = c++_shared

# (bool) If True, the app supports the work manager
# android.work_manager = 0

# (str) The Android Gradle plugin version
# android.gradle_plugin_version = 8.1.0

# (str) The Android Gradle wrapper version
# android.gradle_wrapper_version = 8.4

# (bool) If True, allow to override the android gradle configuration
# android.allow_gradle_override = False

# (str) Android logcat filters to use
# android.logcat_filters = *:S python:D

# (bool) If True, enable AndroidX support
# android.enable_androidx = True

# (bool) If True, enable Jetifier
# android.jetifier = True

# (bool) If True, enable Android App Bundle (AAB) instead of APK
# android.release_artifact = aab

# (str) Key alias for signing the release APK/AAB
# android.release_keyalias =

# (str) Keystore file for signing the release APK/AAB
# android.release_keystore =

# (str) Key password for signing the release APK/AAB
# android.release_keypass =

# (str) Keystore password for signing the release APK/AAB
# android.release_keystorepass =

# (str) Google Play Console service account JSON key file
# p4a.service =


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab) storage
# bin_dir = ./bin

#    -----------------------------------------------------------------------------
#    List as sections
#
#    You can define all the "list" as [section:key].
#    Each line will be considered as a option to the list.
#    Let's take [app] / source.exclude_patterns.
#    Instead of doing:
#
#        [app]
#        source.exclude_patterns = license,data/audio/*.wav,data/images/original/*
#
#    This can be translated into:
#
#        [app:source.exclude_patterns]
#        license
#        data/audio/*.wav
#        data/images/original/*
#


#    -----------------------------------------------------------------------------
#    Profiles
#
#    You can extend section / key with a profile
#    For example, you want to deploy a demo version of your application without
#    HD content. You could first change the title to add "(demo)" in the name
#    and extend the excluded directories to remove the HD content.
#
#        [app@demo]
#        title = My Application (demo)
#
#        [app:source.exclude_patterns@demo]
#        images/hd/*
#
#    Then, invoke the command line with the "demo" profile:
#
#        buildozer --profile demo android debug
