# Building and publishing

The extension is built inside a checkout of [keiyoushi/extensions-source](https://github.com/keiyoushi/extensions-source),
which provides the Gradle build, KSP code generation, `KeiSource` core and JAR packaging. v1.6.1 was built from
commit `f1edb0341163935686ba09a444eef092287779f3` (2026-10-25).

The scripts assume the layout used for the original build. Short paths matter on Windows because of path-length limits.

| Path | Contents |
|---|---|
| `C:\eabuild\extensions-source` | Keiyoushi checkout |
| `C:\eabuild\android-sdk` | Android SDK: `platforms;android-37.0`, `build-tools;37.0.0` |
| `C:\eabuild\signing` | `eahentai.jks`, `signing.env`, `cert.sha256`. **Never commit; back these up** |
| `C:\eabuild\store` | Clone of this repo on the `repo` branch |

## One-time setup
1. JDK 17+ (built with Temurin 21).
2. Android command-line tools from Google. Then install the SDK packages through a package file, because
   `sdkmanager.bat` splits arguments on `;`:
   ```
   sdkmanager.bat --sdk_root=C:\eabuild\android-sdk --licenses
   sdkmanager.bat --sdk_root=C:\eabuild\android-sdk --package_file=pk.txt   # pk.txt: platforms;android-37.0 / build-tools;37.0.0
   ```
3. `git clone --depth 1 https://github.com/keiyoushi/extensions-source C:\eabuild\extensions-source` (with `core.longpaths=true`).
4. Copy `extension/eahentai` to `extensions-source/src/en/eahentai`. In `settings.gradle.kts`, comment out
   `loadAllIndividualExtensions()` and add `loadIndividualExtension("en", "eahentai")`.
5. Signing key (one time; **reuse it for every update**, or users must uninstall and reinstall):
   ```
   keytool -genkeypair -keystore eahentai.jks -storetype PKCS12 -alias eahentai -keyalg RSA -keysize 4096 -validity 36500
   ```
   `signing.env` holds `KEY_STORE_PASSWORD`, `ALIAS`, `KEY_PASSWORD`. `cert.sha256` is the SHA-256 of the DER certificate
   (`keytool -exportcert ... | sha256sum`).

## Release an update
1. Edit the code in `extensions-source/src/en/eahentai` and **bump `versionCode`** in `build.gradle.kts`.
   The version name becomes `1.6.<versionCode>`.
2. `bash tools/build.sh`. It runs spotlessApply, then `:src:en:eahentai:assembleRelease`, which produces
   `build/outputs/apk/release/*.apk` and `build/outputs/jar/release/*.jar`.
3. Optional test: start a disposable Suwayomi (`java -Dsuwayomi.tachidesk.config.server.rootDir=<empty dir> -jar Suwayomi-Server.jar`
   with `tools/test/server.conf` in that dir), then run `python tools/test/e2e.py`. Update the version expected in `e2e.py`.
4. `bash tools/publish.sh "Release 1.6.N"` regenerates `index.json`/`index.pb`/`index.html`, copies the APK, JAR and icon,
   and pushes the `repo` branch.
5. Copy the changed source back into `extension/eahentai/` on `main` and commit.

Suwayomi offers the update after its next extension list refresh.

## Store format notes
- `index.pb` is a gzipped protobuf of `tools/index.proto` (Keiyoushi/tachiyomix schema, with `jarUrl` as field 501).
  `make_index.py` is a dependency-free encoder. Its output was checked byte-for-byte against Keiyoushi's published
  `index.pb` (714,014 bytes, identical).
- Suwayomi (≥ the version that added `jarUrl`) installs the JAR when `jarUrl` is set, and only falls back to the APK otherwise.
