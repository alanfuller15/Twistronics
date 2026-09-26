"""Apply a frozen job's resource limits before exec; never shell-expand argv."""
import json
import os
import resource
import sys
from pathlib import Path


def main():
    request = json.loads(Path(sys.argv[1]).read_text())
    limits = request['limits']
    for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS',
                'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'BLIS_NUM_THREADS'):
        if os.environ.get(key) != '1':
            raise RuntimeError('SINGLE_THREAD_ENV_REQUIRED:' + key)
    for which, key in ((resource.RLIMIT_AS, 'address_space_bytes'),
                       (resource.RLIMIT_FSIZE, 'file_bytes')):
        resource.setrlimit(which, (limits[key], limits[key]))
    os.chdir(request['cwd'])
    os.execvpe(request['argv'][0], request['argv'], os.environ)


if __name__ == '__main__':
    main()
