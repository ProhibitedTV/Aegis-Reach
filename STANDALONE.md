# First Light Windows standalone release

The public developer package is the editable GameGuru MAX project. A Windows standalone is different: GameGuru MAX must perform **Save Standalone Game** so the engine runtime and the assets referenced by the mission are copied into a player build.

## Build machine requirements

Use a Windows x64 machine with:

- GameGuru MAX installed through Steam
- the licensed packs used by First Light installed locally (Military Pack, Industrial Collection, and MAX Collection)
- Python available as `python`
- Git and Git LFS
- GitHub CLI (`gh`) only if publishing from `PUBLISH STANDALONE.cmd`

The default export directory is:

`C:\AegisReachBuilds\First-Light`

Override it by setting `AEGIS_STANDALONE_DIR` before running the scripts.

## 1. Prepare and export

Run:

`BUILD STANDALONE.cmd`

The script runs the normal First Light rebuild/load-safety/preflight registration, launches the registered Aegis Reach project in GameGuru MAX, and opens the export directory.

Inside MAX:

1. Open the Aegis Reach Storyboard.
2. Confirm FIRST LIGHT is the intended playable mission.
3. Choose **Save Standalone Game**.
4. Export to `C:\AegisReachBuilds\First-Light` (or your `AEGIS_STANDALONE_DIR`).
5. Let the MAX export finish completely before verification.

Do not copy the repository itself into that directory. The standalone directory should be the output created by MAX.

## 2. Verify

Run:

`VERIFY STANDALONE.cmd`

`tools/firstlight_standalone.py` rejects a build when it cannot find a root Windows EXE, the First Light FPM, the Aegis Reach Lua runtime, or any of the three authored score masters. It also rejects obvious source/editor leakage, zero-byte runtime files, and implausibly small exports.

A passing verification writes `standalone-manifest.json` containing file sizes and SHA-256 hashes.

Verification is a packaging gate, not a substitute for playing the exported game. Before promoting a release, launch the standalone with GameGuru MAX closed and test it on a clean Windows environment when practical.

## 3. Package and publish locally

With GitHub CLI authenticated for `ProhibitedTV/Aegis-Reach`, run for example:

`PUBLISH STANDALONE.cmd v0.2.0-alpha`

That command:

1. verifies the standalone again;
2. creates `Aegis-Reach-First-Light-0.2.0-alpha-win64.zip` with ZIP64 support;
3. embeds a fresh `standalone-manifest.json` in the ZIP;
4. writes a `.sha256` sidecar and release notes;
5. refuses to overwrite an existing GitHub release tag; and
6. publishes the ZIP and checksum as a prerelease tied to the current source commit.

## Self-hosted GitHub Actions path

`.github/workflows/publish-standalone.yml` packages and publishes an **already exported** standalone directory from a Windows x64 self-hosted runner. It does not attempt to drive the GameGuru MAX GUI.

A useful setup is to install the repository runner on the same Windows build machine and leave the MAX export at `C:\AegisReachBuilds\First-Light`. After a successful manual export, dispatch **Publish Windows Standalone** and provide the release tag.

The runner needs `python`, `gh`, Git LFS, read access to the export directory, and permission to write the repository release. Running the Actions runner as a service is fine because the workflow only verifies/packages an existing export; it does not need an interactive desktop.

## Why the MAX step remains manual

The checked-in tooling can deterministically rebuild, preflight, register, verify, hash, package, and publish First Light. The remaining boundary is GameGuru MAX's own standalone exporter. Until MAX exposes a supported command-line standalone export, automating that button would depend on fragile desktop/UI automation and would be less reliable than keeping the engine-owned export step explicit.
