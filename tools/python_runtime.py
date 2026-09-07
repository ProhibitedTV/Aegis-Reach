from pathlib import Path
import os, sys, subprocess, shutil


def ensure_lua51_runtime(script):
    """Relaunch through a verified interpreter capable of loading our Lua 5.1 ABI."""
    vendor = Path(script).resolve().parent / 'vendor'
    sys.path.insert(0, str(vendor))
    try:
        from lupa.lua51 import LuaRuntime
        return LuaRuntime
    except (ImportError, ModuleNotFoundError) as original:
        candidates = []
        if os.environ.get('AEGIS_PYTHON'):
            candidates.append([os.environ['AEGIS_PYTHON']])
        if shutil.which('py'):
            candidates.append(['py', '-3.12'])
        candidates.extend([str(p)] for p in sorted((Path.home()/'.cache/codex-runtimes').glob('*/dependencies/python/python.exe')))
        candidates.extend([str(p)] for p in sorted((Path.home()/'AppData/Local/Programs/Python').glob('Python312*/python.exe')))
        for command in candidates:
            probe = subprocess.run(command + ['-c', 'import sys;sys.path.insert(0,sys.argv[1]);from lupa.lua51 import LuaRuntime;assert sys.version_info[:2]==(3,12)', str(vendor)], capture_output=True)
            if probe.returncode == 0:
                print('Using verified CPython 3.12 / Lua 5.1 runtime.', flush=True)
                raise SystemExit(subprocess.call(command + [str(Path(script).resolve()), *sys.argv[1:]]))
        raise SystemExit('Install 64-bit CPython 3.12 or set AEGIS_PYTHON to its executable. Lua 5.1 could not load: '+str(original))
