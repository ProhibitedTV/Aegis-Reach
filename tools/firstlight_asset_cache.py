"""Invalidate only original First Light compiled meshes when authored bytes change.

MAX's own timestamp checks remain useful, but checkouts can preserve timestamps.
This content stamp is local launch bookkeeping, never native visual approval.
"""
from pathlib import Path
import hashlib
import json


def contained_file(folder, path):
    resolved = path.resolve()
    if resolved.parent != folder or path.is_symlink():
        raise ValueError(f"Asset escapes original-art directory: {path}")
    return resolved


def synchronize(folder, stamp):
    folder = Path(folder).resolve(strict=True)
    stamp = Path(stamp)
    # The generated set shares atlases. A changed atlas invalidates the set so
    # no compiled material can silently keep the previous texture assignment.
    inputs = sorted((p for p in folder.iterdir()
                     if p.suffix.lower() in {'.fpe', '.x', '.png'}), key=lambda p: p.name)
    digest = hashlib.sha256()
    caches = []
    for path in inputs:
        contained_file(folder, path)
        digest.update(path.name.encode('utf-8') + b'\0')
        digest.update(path.read_bytes())
        digest.update(b'\0')
        if path.suffix.lower() != '.fpe':
            continue
        fields = dict(line.split('=', 1) for line in path.read_text().splitlines()
                      if '=' in line and not line.lstrip().startswith(';'))
        fields = {key.strip().lower(): value.strip() for key, value in fields.items()}
        model = fields.get('model', '')
        # Only generated sibling X models are owned here. Never follow an FPE
        # reference into installed DLC or remove unrelated compiled objects.
        if model != path.with_suffix('.x').name:
            raise ValueError(f"Expected generated sibling model for {path.name}: {model}")
        source = contained_file(folder, folder / model)
        if not source.is_file():
            raise FileNotFoundError(source)
        cache = source.with_suffix('.dbo')
        contained_file(folder, cache)
        if cache.exists() and not cache.is_file():
            raise ValueError(f"Compiled mesh is not a regular file: {cache}")
        caches.append(cache)
    if not caches:
        raise ValueError('No owned original meshes found; refusing to stamp an empty set')
    signature = digest.hexdigest()
    try:
        prior = json.loads(stamp.read_text())
    except (FileNotFoundError, ValueError):
        prior = {}
    changed = prior.get('schema') != 1 or prior.get('source_sha256') != signature
    removed = []
    if changed:
        # All source and destination paths have been validated before mutation.
        for cache in caches:
            if cache.is_file():
                cache.unlink()
                removed.append(cache.name)
    report = {'schema': 1, 'source_sha256': signature,
              'asset_count': len(caches), 'invalidated': removed}
    stamp.parent.mkdir(parents=True, exist_ok=True)
    temporary = stamp.with_suffix('.tmp')
    temporary.write_text(json.dumps(report, indent=2))
    temporary.replace(stamp)
    return report


def main():
    from native_format import ROOT
    report = synchronize(ROOT / 'Aegis Reach/Files/entitybank/Aegis Reach/First Light',
                         ROOT / '.local-review/firstlight-asset-cache.json')
    print('FIRST LIGHT // ORIGINAL ART', report['source_sha256'][:16])
    print('Owned meshes:', report['asset_count'], '| compiled copies invalidated:',
          len(report['invalidated']))


if __name__ == '__main__':
    main()
