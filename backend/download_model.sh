
#!/bin/sh
set -e

echo "Checking Git LFS availability..."

if ! command -v git-lfs >/dev/null 2>&1; then
    echo "Git LFS is not installed."
    exit 1
fi

echo "Downloading LFS model files..."
git lfs pull

echo "Checking model file..."

MODEL="models/india_grid_forecaster.pkl"

if [ ! -f "$MODEL" ]; then
    echo "Model file not found: $MODEL"
    exit 1
fi

if head -c 100 "$MODEL" | grep -q "git-lfs.github.com/spec"; then
    echo "ERROR: Model is still a Git LFS pointer."
    exit 1
fi

echo "Model downloaded successfully."
