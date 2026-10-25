#!/bin/bash
# Builds the EAHentai extension (release, signed) from C:\eabuild\extensions-source.
set -e
cd /c/eabuild/extensions-source
# signingkey.jks is git-ignored by extensions-source; it is copied in only for the build.
cp /c/eabuild/signing/eahentai.jks signingkey.jks
set -a; . /c/eabuild/signing/signing.env; set +a
export ANDROID_HOME='C:\eabuild\android-sdk'
export GRADLE_USER_HOME='C:\eabuild\gradle-home'
./gradlew --no-daemon -q spotlessApply
./gradlew --no-daemon :src:en:eahentai:assembleRelease "$@"
