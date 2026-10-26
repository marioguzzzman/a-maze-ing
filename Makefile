PYTHON   ?= python3
CONFIG   ?= config.txt
MAIN     := a_maze_ing.py
MLX_DIR  := .mlx_build/mlx_CLXV
MLX_REPO := https://github.com/42school/mlx_CLXV.git
VENV     := .amazeing_env
VENV_PY  := $(VENV)/bin/python3
.PHONY: install run debug clean lint lint-strict build

# Needs these system packages already present (not installable from here,
# since install shouldn't silently run sudo):
#   build-essential git pkg-config libvulkan-dev vulkan-tools \
#   mesa-vulkan-drivers libxcb1-dev libxcb-keysyms1-dev libbsd-dev zlib1g-dev

install:
	$(PYTHON) -m venv $(VENV)
	$(VENV_PY) -m pip install --upgrade pip
	$(VENV_PY) -m pip install flake8 mypy build
# Installs *our own* mazegen package, editable, straight from source
# (reads pyproject.toml) so, this is a completely separate thing from
# the MLX wheel below.
	$(VENV_PY) -m pip install -e .
# Fetch MLX's own C source (or update it if already cloned), then
# run *its* Makefile to compile it and produce its own
# wheel at $(MLX_DIR)/mlx-*-py3-none-any.whl, which we then install.
	if [ -d $(MLX_DIR) ]; then \
		cd $(MLX_DIR) && git pull; \
	else \
		mkdir -p $(dir $(MLX_DIR)) && git clone --depth 1 $(MLX_REPO) $(MLX_DIR); \
	fi
	$(MAKE) -C $(MLX_DIR)
	$(VENV_PY) -m pip install $(MLX_DIR)/mlx-*-py3-none-any.whl

run:
	$(VENV_PY) $(MAIN) $(CONFIG)

debug:
	$(VENV_PY) -m pdb $(MAIN) $(CONFIG)

clean:
# Walk every file from here down, but skip straight past the venv
# entirely (-prune actions is similar to "don't look inside this directory") - we
# never want to touch anything in there. For everything else,
# find any directory named __pycache__ and delete it right away
# (-exec ... {} + batches all matches into as few `rm` calls as
# possible, instead of running `rm` once per match).
	find . -path ./$(VENV) -prune -o -type d -name "__pycache__" -exec rm -rf {} +
# Flat removal of a few fixed cache/build folders living at the
# project root - these aren't searched for, just deleted by name.
	rm -rf .mypy_cache .pytest_cache build dist *.egg-info

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
		--disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

# Needs `make install` to have run first - $(VENV_PY) and the `build`
# package it installed don't exist until then.
build:
	$(VENV_PY) -m build
	cp dist/mazegen-*.whl .
