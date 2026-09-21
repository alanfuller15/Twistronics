import json,sys,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest
from protocol import verify_preserved
from package_release import write_archive,sha


@pytest.mark.parametrize('fault',['changed','missing','symlink','manifest','escape'])
def test_preservation_errors_rejected(tmp_path,fault):
    p=tmp_path/'a';p.write_bytes(b'original');m=tmp_path/'manifest.json'
    m.write_text(json.dumps({'files':{'a':{'bytes':8,'sha256':sha(b'original')}}}));h=sha(m.read_bytes())
    assert verify_preserved(tmp_path,m,h)==1
    if fault=='changed':p.write_bytes(b'changed!')
    elif fault=='missing':p.unlink()
    elif fault=='symlink':p.rename(tmp_path/'real');p.symlink_to('real')
    elif fault=='manifest':m.write_text('{}')
    else:
        m.write_text(json.dumps({'files':{'../escape':{'bytes':0,'sha256':sha(b'')}}}));h=sha(m.read_bytes())
    with pytest.raises((ValueError,FileNotFoundError)):verify_preserved(tmp_path,m,h)


def test_archive_deterministic_and_no_overwrite(tmp_path):
    payload={'v060/data.bin':b'\x00\x01'};a=tmp_path/'new/a.zip';b=tmp_path/'new/b.zip'
    first=write_archive(payload,a);second=write_archive(payload,b)
    assert first['sha256']==second['sha256']
    with zipfile.ZipFile(a) as z:
        assert z.read('twistronics_v060_reconciled/v060/data.bin')==b'\x00\x01'
        assert len(z.namelist())==2
    with pytest.raises(ValueError,match='overwrite'):write_archive(payload,a)
    with pytest.raises(ValueError,match='unsafe'):write_archive({'../escape':b'x'},tmp_path/'bad.zip')
