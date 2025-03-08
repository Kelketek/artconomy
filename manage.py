#!/usr/bin/env python
import os
import platform
import sys

import coverage

if 'test' in sys.argv and platform.system().lower() == 'darwin':
    os.environ.setdefault('OBJC_DISABLE_INITIALIZE_FORK_SAFETY', 'YES')

if __name__ == "__main__":
    if 'test' in sys.argv:
        if '--no-coverage' not in sys.argv:
            os.environ['COVERAGE_PROCESS_START'] = './.coveragerc'
            coverage.process_startup()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.conf.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
