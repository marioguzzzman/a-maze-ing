PYTHON   ?= python3
CONFIG   ?= config.txt
MAIN     := a_maze_ing.py
MLX_DIR  := .mlx_build/mlx_CLXV
MLX_REPO := https://github.com/42school/mlx_CLXV.git
VENV     := .amazeing_env
VENV_PY  := $(VENV)/bin/python

.PHONY: install run debug clean lint lint-strict build

# Needs these system packages already present (not installable from here,
# since install shouldn't silently run sudo):
#   build-essential git pkg-config libvulkan-dev vulkan-tools \
#   mesa-vulkan-drivers libxcb1-dev libxcb-keysyms1-dev libbsd-dev zlib1g-dev

install:
	$(PYTHON) -m venv $(VENV)
	$(VENV_PY) -m pip install --upgrade pip
	$(VENV_PY) -m pip install flake8 mypy build
	$(VENV_PY) -m pip install -e .
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
	find . -path ./.venv -prune -o -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache build dist *.egg-info

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
		--disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

build:
	$(PYTHON) -m build
	cp dist/mazegen-*.whl .
