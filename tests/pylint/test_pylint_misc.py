#!/usr/bin/python
# encoding: utf-8

import os
import sys

from testlib import cmk_path, cmc_path, cme_path
import testlib.pylint_cmk as pylint_cmk

def test_pylint_misc():
    # Only specify the path to python packages or modules here
    modules_or_packages = [
        # Check_MK base
        "cmk_base",
        # TODO: Check if this kind of "overlay" really works.
        # TODO: Why do we have e.g. a symlink cmk_base/cee -> enterprise/cmk_base/cee?
        "enterprise/cmk_base/automations/cee.py",
        "enterprise/cmk_base/cee",
        "enterprise/cmk_base/default_config/cee.py",
        "enterprise/cmk_base/modes/cee.py",
        "managed/cmk_base/default_config/cme.py",

        # cmk module level
        # TODO: This checks the whole cmk hierarchy, including things like
        # cmk.gui.plugins.cron etc. Do we really want that here?
        # TODO: Funny links there, see above.
        "cmk",
        "enterprise/cmk/cee",

        # GUI specific
        "web/app/index.wsgi",
        "enterprise/cmk/gui/cee",
        "managed/cmk/gui/cme",
    ]

    # We use our own search logic to find scripts without python extension
    search_paths = [
        "omd/packages/omd",
        "bin",
        "notifications",
        "agents/plugins",
        "agents/special",
        "active_checks",
        "enterprise/agents/plugins",
        "enterprise/bin",
        "enterprise/misc",
    ]

    for path in search_paths:
        for fname in pylint_cmk.get_pylint_files(path, "*"):
           modules_or_packages.append(path + "/" + fname)

    exit_code = pylint_cmk.run_pylint(cmk_path(), modules_or_packages)
    assert exit_code == 0, "PyLint found an error"
