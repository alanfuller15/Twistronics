from pathlib import Path
import json
import sys
import zipfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pytest
from package_release import verify_prior_tree, write_archive, sha


def prior_tree(tmp_path):
    p = tmp_path / 'prior'
    p.mkdir()
    (p / 'source.py').write_bytes(b'preserved\n')
    rows = {'source.py': dict(bytes=10, sha256=sha(b'preserved\n'))}
    (p / 'MANIFEST.json').write_text(json.dumps(dict(files=rows)))
    return p, sha((p / 'MANIFEST.json').read_bytes())


def test_preserved_tree_requires_no_reconstructed_zip(tmp_path):
    p, digest = prior_tree(tmp_path)
    assert verify_prior_tree(p, digest) == 1


@pytest.mark.parametrize('fault', ['file_changed', 'manifest_changed', 'missing', 'escape', 'symlink'])
def test_prior_provenance_errors_are_rejected(tmp_path, fault):
    p, digest = prior_tree(tmp_path)
    if fault == 'file_changed':
        (p / 'source.py').write_bytes(b'changed\n')
    elif fault == 'manifest_changed':
        (p / 'MANIFEST.json').write_text('{}')
    elif fault == 'missing':
        (p / 'source.py').unlink()
    elif fault == 'escape':
        (p / 'MANIFEST.json').write_text(json.dumps(dict(files={'../outside': dict(bytes=0, sha256=sha(b''))})))
        digest = sha((p / 'MANIFEST.json').read_bytes())
    else:
        (p / 'source.py').rename(p / 'real.py')
        (p / 'source.py').symlink_to('real.py')
    with pytest.raises((ValueError, FileNotFoundError)):
        verify_prior_tree(p, digest)


def test_output_parent_created_and_payload_preserved(tmp_path):
    dest = tmp_path / 'new/parents/release.zip'
    result = write_archive({'v054/data.bin': b'\x00\x01'}, dest)
    assert result['files'] == 2
    with zipfile.ZipFile(dest) as z:
        assert z.read('twistronics_v054_reconciled/v054/data.bin') == b'\x00\x01'
        m = json.loads(z.read('twistronics_v054_reconciled/TEAM_PACKAGE_MANIFEST.json'))
        assert m['files']['v054/data.bin']['sha256'] == sha(b'\x00\x01')
    with pytest.raises(ValueError, match='overwrite'):
        write_archive({'new': b'data'}, dest)


def test_unsafe_archive_names_are_rejected(tmp_path):
    with pytest.raises(ValueError, match='unsafe'):
        write_archive({'../escape': b'data'}, tmp_path / 'bad.zip')
