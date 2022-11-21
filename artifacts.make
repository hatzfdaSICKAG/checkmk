# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
#
CHECK_MK_RAW_PRECOMPILED_WERKS := $(REPO_PATH)/.werks/werks

JAVASCRIPT_MINI    := $(foreach jmini,main mobile side zxcvbn,$(REPO_PATH)/web/htdocs/js/$(jmini)_min.js)

THEMES             := facelift modern-dark
THEME_CSS_FILES    := $(addprefix $(REPO_PATH)/web/htdocs/themes/,$(addsuffix /theme.css,$(THEMES)))
THEME_JSON_FILES   := $(addprefix $(REPO_PATH)/web/htdocs/themes/,$(addsuffix /theme.json,$(THEMES)))
THEME_IMAGE_DIRS   := $(addprefix $(REPO_PATH)/web/htdocs/themes/,$(addsuffix /images,$(THEMES)))
THEME_RESOURCES    := $(THEME_CSS_FILES) $(THEME_JSON_FILES) $(THEME_IMAGE_DIRS)

# These artifacts are created independent of the distro the Checkmk package is
# built on either by an "upstream job" or while creating the source package
SOURCE_BUILT_LINUX_AGENTS := \
	$(REPO_PATH)/agents/check-mk-agent-$(VERSION)-1.noarch.rpm \
	$(REPO_PATH)/agents/check-mk-agent_$(VERSION)-1_all.deb \
	$(REPO_PATH)/agents/linux/cmk-agent-ctl
ifeq ($(ENTERPRISE),yes)
SOURCE_BUILT_LINUX_AGENTS := $(SOURCE_BUILT_LINUX_AGENTS) \
	$(REPO_PATH)/agents/plugins/cmk-update-agent \
	$(REPO_PATH)/agents/plugins/cmk-update-agent-32
endif
SOURCE_BUILT_OHM := \
	$(REPO_PATH)/agents/windows/OpenHardwareMonitorCLI.exe \
	$(REPO_PATH)/agents/windows/OpenHardwareMonitorLib.dll
SOURCE_BUILT_WINDOWS := \
	$(REPO_PATH)/agents/windows/check_mk_agent.msi \
	$(REPO_PATH)/agents/windows/python-3.4.cab \
	$(REPO_PATH)/agents/windows/python-3.cab \
	$(REPO_PATH)/agents/windows/unsign-msi.patch
SOURCE_BUILT_AGENTS := \
	$(SOURCE_BUILT_LINUX_AGENTS) \
	$(SOURCE_BUILT_OHM) \
	$(SOURCE_BUILT_WINDOWS)
