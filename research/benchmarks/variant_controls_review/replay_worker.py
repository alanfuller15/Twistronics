"""Run unchanged partner entrypoint, with call accounting but no numerical patches."""
from pathlib import Path
import collections,json,os,runpy,sys,time
work=Path(sys.argv[1]).resolve(); out=Path(sys.argv[2]).resolve()
sys.path.insert(0,str(work));os.chdir(work)
counts=collections.Counter(); started=time.perf_counter()
def profile(frame,event,arg):
    if event!='call': return
    file=Path(frame.f_code.co_filename)
    if file.parent==work or (file.name=='_decomp.py' and frame.f_code.co_name=='eigh'):
        counts[file.name+':'+frame.f_code.co_name]+=1
sys.setprofile(profile)
try:
    runpy.run_path(str(work/'run_controls.py'),run_name='__main__')
finally:
    sys.setprofile(None)
    out.write_text(json.dumps({'elapsed_s':time.perf_counter()-started,'scope':'Python function entry counts; eigh is the SciPy Python wrapper, not its internal LAPACK work. Constructors and native H calls are separately counted.','calls':dict(sorted(counts.items()))},indent=2)+'\n')
