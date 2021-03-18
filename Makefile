# **************************************************************************** #
# General Make configuration

# This suppresses make's command echoing. This suppression produces a cleaner output. 
# If you need to see the full commands being issued by make, comment this out.
MAKEFLAGS += -s

# **************************************************************************** #

# grab and export environment variables from .env
include .env
export

# **************************************************************************** #
# Targets

#
build: venv
	$(VENV_PYTHON) -m build

#
publish: venv
	$(VENV_PYTHON) -m twine upload --repository testpypi dist/* -u __token__

#
tests: venv
	echo running tests

# remove build artifacts
clean:
	-$(RM) build
	-$(RM) dist
	-$(RM) codex_engine_pyqt.egg-info


# **************************************************************************** #
# python venv settings
VENV_NAME := .venv

ifeq ($(OS),Windows_NT)
	VENV_DIR := $(VENV_NAME)
	VENV := $(VENV_DIR)\Scripts
	PYTHON := python
	VENV_PYTHON := $(VENV)\$(PYTHON)
	RM := rd /s /q
else
	VENV_DIR := $(VENV_NAME)
	VENV := $(VENV_DIR)/bin
	PYTHON := python3
	VENV_PYTHON := $(VENV)/$(PYTHON)
	RM := rm -rf
endif

# Add this as a requirement to any make target that relies on the venv
.PHONY: venv
venv: $(VENV_DIR)

# Create the venv if it doesn't exist
$(VENV_DIR):
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -r requirements.txt

# deletes the venv
clean_venv:
	$(RM) $(VENV_DIR)

# deletes the venv and rebuilds it
reset_venv: clean_venv venv