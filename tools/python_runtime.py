from pathlib import Path
import os, sys, subprocess, shutil


def _ensure_runtime(script, module_name, label):
    """Relaunch through a verified interpreter capable of loading a vendored Lupa ABI."""
    vendor = Path(script).resolve().parent / 'vendor'
    sys.path.insert(0, str(vendor))
    try:
        module = __import__('lupa.' + module_name, fromlist=['LuaRuntime'])
        return module.LuaRuntime
    except (ImportError, ModuleNotFoundError) as original:
        candidates = []
        if os.environ.get('AEGIS_PYTHON'):
            candidates.append([os.environ['AEGIS_PYTHON']])
        if shutil.which('py'):
            candidates.append(['py', '-3.12'])
        candidates.extend([str(p)] for p in sorted((Path.home()/'.cache/codex-runtimes').glob('*/dependencies/python/python.exe')))
        candidates.extend([str(p)] for p in sorted((Path.home()/'AppData/Local/Programs/Python').glob('Python312*/python.exe')))
        probe_code = (
            'import sys;sys.path.insert(0,sys.argv[1]);'
            f'from lupa.{module_name} import LuaRuntime;'
            'assert sys.version_info[:2]==(3,12)'
        )
        for command in candidates:
            probe = subprocess.run(command + ['-c', probe_code, str(vendor)], capture_output=True)
            if probe.returncode == 0:
                print(f'Using verified CPython 3.12 / {label} runtime.', flush=True)
                raise SystemExit(subprocess.call(command + [str(Path(script).resolve()), *sys.argv[1:]]))
        raise SystemExit(
            f'Install 64-bit CPython 3.12 or set AEGIS_PYTHON to its executable. '
            f'{label} could not load: {original}'
        )


def ensure_max_lua_runtime(script):
    """Return Lua 5.2, matching the Lua 5.2.3 runtime shipped in GameGuru MAX source."""
    return _ensure_runtime(script, 'lua52', 'Lua 5.2')


def ensure_lua51_runtime(script):
    """Legacy entry point retained for existing tests; now uses MAX's real Lua 5.2 ABI."""
    return ensure_max_lua_runtime(script)
