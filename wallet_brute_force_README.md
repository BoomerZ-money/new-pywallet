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

## Requirements

- Python 3.6 or higher
- Required packages:
  - pycryptodome
  - tqdm (for progress bars)
  - colorama (for colored output)
  - psutil (for system information)
  - numpy and pyopencl (optional, for GPU acceleration)

Install the required packages:

```bash
pip install pycryptodome tqdm colorama psutil
```

For GPU acceleration (optional):
```bash
pip install numpy pyopencl
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

## Limitations

- The wallet.dat direct extraction is not implemented yet. Use the JSON output from PyWallet instead.
- There's no guarantee that the password will be found, especially if it's complex or not covered by your search parameters.
- The verification of successful decryption is based on heuristics and may occasionally report false positives.
- GPU acceleration is experimental and requires additional setup.
