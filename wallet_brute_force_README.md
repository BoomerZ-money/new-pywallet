# Bitcoin Wallet Password Brute Force Tool

This advanced tool attempts to brute force a Bitcoin wallet password using the encrypted master key and salt, with visual feedback, detailed progress information, and optimized performance for different CPU architectures.

## Features

- **Visual Progress Bar**: See real-time progress of the brute force attempt
- **Single-line Mode**: Clean progress display on a single line with live updates
- **Colorized Output**: Color-coded information for better readability
- **Detailed Statistics**: Speed, progress percentage, and estimated time remaining
- **Smart Password Generation**: Uses frequency analysis to try more likely passwords first
- **Consecutive Character Limiting**: Reduce search space by limiting repeated characters
- **Architecture Optimization**: Special optimizations for M1/M2/M3 and Intel processors
- **Checkpointing**: Save progress and resume long-running brute force attempts
- **System Information**: Details about your system's capabilities
- **Multi-processing**: Utilizes all available CPU cores for maximum performance

## Installation Instructions

### Prerequisites
- Python 3.6 or higher
- pip (Python package installer)
- C++ compiler (for some optimizations)

### Basic Installation (All Platforms)
```bash
pip install -r requirements_brute_force.txt
```

### Platform-Specific Installations

#### Apple Silicon (M1/M2/M3/M4)
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required system packages
brew install python@3.9 openssl readline

# Install Python requirements with Metal support
pip install -r requirements_brute_force.txt

# Optional: Install additional Apple-specific optimizations
xcode-select --install
pip install tensorflow-macos tensorflow-metal
```

#### Intel/AMD (x86_64)
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y build-essential python3-dev opencl-headers ocl-icd-opencl-dev

# Install Intel optimizations
pip install -r requirements_brute_force.txt
pip install intel-tensorflow  # Optional: for better performance

# For NVIDIA GPU support
# First install NVIDIA drivers and CUDA toolkit from https://developer.nvidia.com/cuda-downloads
pip install nvidia-pyindex
pip install nvidia-tensorflow  # Optional: for GPU acceleration
```

#### Windows
```powershell
# Install Visual Studio Build Tools (if not already installed)
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Install base requirements
pip install -r requirements_brute_force.txt

# For NVIDIA GPU support
# 1. Install NVIDIA drivers
# 2. Install CUDA toolkit from https://developer.nvidia.com/cuda-downloads
# 3. Run:
pip install nvidia-pyindex
pip install nvidia-tensorflow
```

### GPU Acceleration Setup

#### Apple Silicon (M1/M2/M3) - Metal Support
The tool includes native Metal support for Apple Silicon, providing significant performance improvements:

1. **Metal Framework Setup**
```bash
# Install Metal dependencies
pip install tensorflow-macos tensorflow-metal metal-python

# Verify Metal availability
python3 -c "import tensorflow as tf; print('Metal GPU available:', bool(tf.config.list_physical_devices('GPU')))"
```

2. **Performance Optimization**
- Uses batch processing optimized for Metal (10240 passwords per batch)
- Automatic memory management to prevent GPU memory issues
- Parallel processing with Metal-specific optimizations
- Automatic fallback to CPU if GPU acceleration fails

3. **Usage with Metal**
```bash
# Enable Metal support and run with GPU acceleration
python wallet_brute_force.py --use_gpu --optimize_for=m3

# For maximum performance
python wallet_brute_force.py --use_gpu --optimize_for=m3 --processes=8 --smart
```

4. **Metal-Specific Features**
- Automatic detection of Apple Silicon processors
- Dynamic batch size adjustment based on available GPU memory
- Optimized tensor operations for password processing
- Efficient memory handling for long-running operations

5. **Monitoring Metal Performance**
```bash
# Show GPU utilization during processing
sudo powermetrics --samplers gpu_power -i500 -n1
```

#### NVIDIA GPUs
1. Install NVIDIA drivers for your GPU
2. Install CUDA Toolkit (11.0 or higher recommended)
3. Install additional requirements:
```bash
pip install nvidia-cuda-runtime-cu12 nvidia-cublas-cu12 nvidia-cudnn-cu12
```

#### AMD GPUs
1. Install ROCm (Linux only) or AMD GPU drivers
2. Install additional requirements:
```bash
pip install rocm-python torch-rocm  # Linux only
```

#### Intel GPUs
1. Install Intel OpenCL Runtime
2. Install additional requirements:
```bash
pip install intel-compute-runtime
```

### Architecture-Specific Optimizations

#### Apple Silicon Optimization
The tool includes several optimizations specific to Apple Silicon:

1. **Metal Acceleration**
- Utilizes Apple's Metal framework for GPU computation
- Optimized tensor operations for password processing
- Efficient batch processing with Metal-specific parameters
- Automatic hardware detection and configuration

2. **Memory Management**
- Dynamic batch sizing based on available GPU memory
- Efficient memory allocation for Metal operations
- Automatic garbage collection to prevent memory leaks

3. **Performance Tuning**
```bash
# Enable all Metal optimizations
export PYTORCH_ENABLE_MPS_FALLBACK=1
export TF_FORCE_GPU_ALLOW_GROWTH=true

# Run with optimal settings for M1/M2/M3
python wallet_brute_force.py --use_gpu --optimize_for=m3 --processes=8
```

4. **Troubleshooting Metal Issues**
If you encounter Metal-related issues:

```bash
# Verify Metal support
python3 -c "import tensorflow as tf; print(tf.config.list_physical_devices())"

# Check Metal device status
system_profiler SPDisplaysDataType

# Reset Metal device if needed
sudo killall -9 metalcompiler
```

Common Metal-specific issues and solutions:
- **Metal device not found**: Ensure macOS is updated to the latest version
- **Out of memory errors**: Reduce batch size using `--batch_size` parameter
- **Performance degradation**: Monitor GPU temperature and throttling
- **Initialization failures**: Reset Metal compiler and retry

5. **Performance Monitoring**
Monitor Metal GPU performance:
```bash
# Basic GPU monitoring
sudo powermetrics --samplers gpu_power

# Detailed performance metrics
sudo powermetrics --samplers gpu_power,gpu_compute -i500
```

### Verifying Installation

Test your installation by running:
```bash
python wallet_brute_force.py --test
```

This will perform a quick test of all installed components and optimizations.

### Troubleshooting

#### Common Issues

1. **OpenCL not found**
```bash
# Linux
sudo apt-get install ocl-icd-opencl-dev

# macOS
brew install opencl-headers

# Windows
# Install GPU vendor's development kit
```

2. **Compilation errors**
```bash
# Linux
sudo apt-get install python3-dev build-essential

# macOS
xcode-select --install

# Windows
# Install Visual Studio Build Tools
```

3. **GPU not detected**
```bash
# Check GPU support
python -c "import pyopencl; print(pyopencl.get_platforms())"
```

### Performance Optimization Tips

1. **For Apple Silicon (M1/M2/M3)**
```bash
# Enable Metal support
export PYTORCH_ENABLE_MPS_FALLBACK=1

# Run with optimized settings
python wallet_brute_force.py --optimize_for=m3 --use_gpu
```

2. **For Intel/AMD Systems**
```bash
# Enable Intel MKL optimizations
export MKL_NUM_THREADS=8
export OMP_NUM_THREADS=8

# Run with optimized settings
python wallet_brute_force.py --optimize_for=intel --processes=8
```

3. **For Systems with NVIDIA GPUs**
```bash
# Set CUDA device
export CUDA_VISIBLE_DEVICES=0

# Run with GPU acceleration
python wallet_brute_force.py --use_gpu --optimize_for=auto
```

## Usage

### Basic Usage

```bash
python wallet_brute_force.py --json=wallet_dump.json
```

or

```bash
python wallet_brute_force.py --encrypted_key=f42768ebcfc7060f72069b0d976e8ca08ff0c52d3026ac8b949fdc64444d4daecbde19f8bfb3fb4b3e199fdb5aff8339 --salt=b5ba03e404f1d79d
```

### Parameters

| Parameter | Description |
|-----------|-------------|
| `--json` | Path to the JSON file containing wallet data (must contain mkey with encrypted_key and salt) |
| `--encrypted_key` | Encrypted master key in hexadecimal format |
| `--salt` | Salt value in hexadecimal format |
| `--wallet` | Path to wallet.dat file (not implemented yet) |
| `--iterations` | Number of key derivation iterations (default: 25000) |
| `--min_passwd` | Minimum password length (default: 4) |
| `--max_passwd` | Maximum password length (default: 8) |
| `--charset` | Character set to use for password generation (default includes lowercase, uppercase, digits, and common symbols) |
| `--processes` | Number of processes to use (default: number of CPU cores) |
| `--status_interval` | How often to print status updates in number of attempts (default: 1000) |
| `--wordlist` | Path to wordlist file (one password per line) |
| `--show_current` | Show current password being tried (may slow down the process) |
| `--quiet` | Reduce output verbosity |
| `--debug` | Enable debug output |
| `--single_line` | Show progress on a single line (default: True) |

### Advanced Parameters

| Parameter | Description |
|-----------|-------------|
| `--smart` | Use smart password generation with frequency analysis |
| `--checkpoint` | Path to save/load checkpoint file |
| `--checkpoint_interval` | Save checkpoint every N seconds (default: 60) |
| `--use_gpu` | Use GPU acceleration if available |
| `--optimize_for` | Optimize for specific CPU architecture: m1, m2, m3, intel, or auto (default: auto) |
| `--max_consecutive` | Maximum number of consecutive identical characters (0 = no limit) |

### Examples

#### Using a JSON file from wallet dump

```bash
python wallet_brute_force.py --json=wallet_dump.json --min_passwd=6 --max_passwd=10
```

#### Using direct values with visual feedback

```bash
python wallet_brute_force.py --encrypted_key=f42768ebcfc7060f72069b0d976e8ca08ff0c52d3026ac8b949fdc64444d4daecbde19f8bfb3fb4b3e199fdb5aff8339 --salt=b5ba03e404f1d79d --min_passwd=5 --max_passwd=8 --show_current
```

#### Using a wordlist with reduced CPU usage

```bash
python wallet_brute_force.py --json=wallet_dump.json --wordlist=common_passwords.txt --processes=4
```

#### Limiting character set for faster processing

```bash
python wallet_brute_force.py --encrypted_key=f42768ebcfc7060f72069b0d976e8ca08ff0c52d3026ac8b949fdc64444d4daecbde19f8bfb3fb4b3e199fdb5aff8339 --salt=b5ba03e404f1d79d --charset="abcdefghijklmnopqrstuvwxyz0123456789"
```

#### Using smart password generation and architecture optimization

```bash
python wallet_brute_force.py --json=wallet_dump.json --smart --optimize_for=m3 --processes=8
```

#### Limiting consecutive characters to reduce search space

```bash
python wallet_brute_force.py --json=wallet_dump.json --charset="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" --max_consecutive=2
```

#### Using checkpointing for long-running jobs

```bash
python wallet_brute_force.py --json=wallet_dump.json --min_passwd=8 --max_passwd=12 --checkpoint=./checkpoint.json
```

## Advanced Features

### Smart Password Generation

The `--smart` option uses frequency analysis and common patterns to prioritize passwords that are more likely to be correct:

- Tries common password patterns first (common prefixes and suffixes)
- Prioritizes characters based on frequency in real-world passwords
- Tests repeating and alternating patterns early
- Falls back to regular brute force with optimized character ordering

### Consecutive Character Limiting

The `--max_consecutive` parameter significantly reduces the search space by eliminating passwords with too many consecutive identical characters:

- `--max_consecutive=1`: No repeated characters allowed (e.g., "abcdef" is valid, but "aabcde" is not)
- `--max_consecutive=2`: At most 2 consecutive identical characters (e.g., "aabcde" is valid, but "aaabcd" is not)
- `--max_consecutive=0`: No limit (default behavior)

This can reduce the search space by 50-95% depending on the character set and limit chosen.

### Architecture Optimization

The `--optimize_for` parameter tunes the tool for specific CPU architectures:

- `m1`, `m2`, `m3`: Optimized for Apple Silicon with larger batch sizes and slight oversubscription
- `intel`: Optimized for Intel processors with different parallelization strategies
- `auto`: Automatically detects and applies the best settings for your CPU

### Checkpointing

For long-running brute force attempts, the tool can save progress and resume later:

- `--checkpoint=./file.json`: Specifies the file to save checkpoint data
- `--checkpoint_interval=60`: How often to save checkpoint data (in seconds)

If the script is interrupted, it will automatically resume from the last checkpoint when restarted with the same parameters.

## Visual Features

### Progress Bar

The tool displays a progress bar showing:
- Percentage complete
- Number of passwords tried vs. total
- Current speed (passwords per second)
- Elapsed time
- Estimated time remaining

### Color Coding

- **Blue**: Information messages
- **Green**: Success messages and progress bar
- **Yellow**: Warnings
- **Red**: Errors

### System Information

The tool displays information about your system:
- Operating system
- CPU model and architecture
- Number of CPU cores (physical and logical)
- Available memory
- CPU frequency
- GPU information (if available)
- Python version

## Performance Considerations

- The script uses multiprocessing to utilize multiple CPU cores.
- The `--optimize_for` parameter can significantly improve performance on specific architectures.
- The `--max_consecutive` parameter can dramatically reduce the search space for large character sets.
- The `--smart` option prioritizes more likely passwords first, potentially finding matches faster.
- For M3 processors, using `--processes=8` with `--optimize_for=m3` provides optimal performance.
- The number of iterations in the key derivation function significantly affects performance. Bitcoin Core typically uses 25000 iterations.
- For longer passwords or larger character sets, the number of possible combinations grows exponentially, making a brute force approach impractical.
- Using a wordlist of common passwords or passwords you think might be correct is often more efficient than a pure brute force approach.

## Security and Legal Considerations

- This tool should only be used on your own wallets or with explicit permission.
- Unauthorized attempts to access others' wallets may be illegal.
- The tool does not transmit any data over the network; all processing is done locally.

## Limitations and Known Issues

### Wallet.dat Extraction
- Direct wallet.dat extraction is not implemented in this tool. For wallet.dat handling, please refer to:
  - [PyWallet Original Implementation](README.md) - Contains the legacy wallet.dat extraction code
  - [PyWallet Refactored Version](README_refactored.md) - Features improved wallet.dat handling with modern architecture
- Currently, the brute force tool requires the encrypted master key and salt to be provided directly or through a JSON file
- For extracting these values from wallet.dat, use the main PyWallet tool with:
  ```bash
  # Using original implementation
  python pywallet3.py --dumpwallet --wallet=/path/to/wallet.dat
  
  # Using refactored implementation
  python -m pywallet_refactored dump --wallet=/path/to/wallet.dat --output=keys.json
  ```

### Other Limitations
- Maximum password length might be constrained by available memory when using GPU acceleration
- Some GPU optimizations may not be available on older hardware
- Performance may vary significantly based on hardware capabilities and chosen character set
