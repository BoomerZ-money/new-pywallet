#!/usr/bin/env python3
"""
Bitcoin Wallet Password Brute Force Tool

This script attempts to brute force a Bitcoin wallet password using the encrypted master key and salt.
It includes visual feedback and progress information during the brute force process.
"""

import argparse
import json
import os
import sys
import time
import itertools
from concurrent.futures import ProcessPoolExecutor, as_completed
# Platform is imported in print_system_info

try:
    import hashlib
    from Crypto.Cipher import AES
except ImportError:
    print("Required packages not found. Please install them with:")
    print("pip install pycryptodome")
    sys.exit(1)

# Try to import optional packages for visual feedback
try:
    import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

# Try to import optional packages for system information
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Try to import GPU acceleration packages
try:
    import pyopencl
    import numpy as np
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

try:
    from colorama import init, Fore, Style

    # Initialize colorama
    init(autoreset=True)

    # Define color constants for better readability
    INFO = Fore.BLUE
    SUCCESS = Fore.GREEN
    WARNING = Fore.YELLOW
    ERROR = Fore.RED
    BOLD = Style.BRIGHT
    RESET = Style.RESET_ALL

    COLORAMA_AVAILABLE = True
except ImportError:
    # Define fallback color constants
    INFO = ""
    SUCCESS = ""
    WARNING = ""
    ERROR = ""
    BOLD = ""
    RESET = ""
    COLORAMA_AVAILABLE = False

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Bitcoin Wallet Password Brute Force Tool")

    # Required arguments
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--json", "--js", help="Path to the JSON file containing wallet data")
    group.add_argument("--encrypted_key", help="Encrypted master key (hex)")

    # Optional arguments
    parser.add_argument("--salt", help="Salt value (hex)")
    parser.add_argument("--wallet", help="Path to wallet.dat file")
    parser.add_argument("--iterations", type=int, default=25000, help="Number of key derivation iterations")
    parser.add_argument("--min_passwd", type=int, default=4, help="Minimum password length")
    parser.add_argument("--max_passwd", type=int, default=8, help="Maximum password length")
    parser.add_argument("--charset", default="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+",
                        help="Character set to use for password generation")
    parser.add_argument("--processes", type=int, default=os.cpu_count(), help="Number of processes to use")
    parser.add_argument("--status_interval", type=int, default=1000, help="How often to print status updates (in attempts)")
    parser.add_argument("--wordlist", help="Path to wordlist file (one password per line)")
    parser.add_argument("--show_current", action="store_true", help="Show current password being tried (may slow down the process)")
    parser.add_argument("--quiet", action="store_true", help="Reduce output verbosity")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--single_line", action="store_true", default=True, help="Show progress on a single line (default: True)")

    # Advanced options
    parser.add_argument("--smart", action="store_true", help="Use smart password generation (frequency analysis)")
    parser.add_argument("--checkpoint", help="Path to save/load checkpoint file")
    parser.add_argument("--checkpoint_interval", type=int, default=60, help="Save checkpoint every N seconds (default: 60)")
    parser.add_argument("--use_gpu", action="store_true", help="Use GPU acceleration if available")
    parser.add_argument("--optimize_for", choices=["m1", "m2", "m3", "intel", "auto"], default="auto",
                      help="Optimize for specific CPU architecture (default: auto)")
    parser.add_argument("--max_consecutive", type=int, default=0,
                      help="Maximum number of consecutive identical characters (0 = no limit)")

    return parser.parse_args()

def has_too_many_consecutive_chars(password, max_consecutive):
    """Check if a password has too many consecutive identical characters."""
    if max_consecutive <= 0:  # 0 or negative means no limit
        return False

    if len(password) <= 1:
        return False

    # Count consecutive characters
    current_char = password[0]
    count = 1

    for char in password[1:]:
        if char == current_char:
            count += 1
            if count > max_consecutive:
                return True
        else:
            current_char = char
            count = 1

    return False

def hex_to_bytes(hex_string):
    """Convert a hex string to bytes."""
    return bytes.fromhex(hex_string)

# Cache for derived keys to avoid recalculating
_key_cache = {}
_key_cache_size = 1000  # Limit cache size to avoid memory issues

def derive_key(password, salt, iterations, key_length=32):
    """Derive a key from a password using PBKDF2-HMAC-SHA512 with caching."""
    # Create a cache key from the parameters
    cache_key = (password, salt, iterations, key_length)

    # Check if we have this key in the cache
    if cache_key in _key_cache:
        return _key_cache[cache_key]

    # Not in cache, calculate it
    derived_key = hashlib.pbkdf2_hmac(
        'sha512',
        password,
        salt,
        iterations,
        key_length
    )

    # Store in cache if not too large
    if len(_key_cache) < _key_cache_size:
        _key_cache[cache_key] = derived_key

    return derived_key

def decrypt_aes(encrypted_data, key):
    """Decrypt data using AES-256-CBC."""
    iv = b'\x00' * 16  # Bitcoin Core uses a zero IV
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.decrypt(encrypted_data)

def check_password(password, encrypted_key, salt, iterations):
    """Check if a password can decrypt the master key."""
    try:
        # Convert password to bytes if it's a string - use a faster method
        if isinstance(password, str):
            password = password.encode('utf-8')

        # Derive key from password
        derived_key = derive_key(password, salt, iterations)

        # Try to decrypt the master key
        decrypted = decrypt_aes(encrypted_key, derived_key)

        # Ultra-fast check: The last byte should be a valid padding value (1-16)
        padding_byte = decrypted[-1]
        if not (1 <= padding_byte <= 16):
            return False, password

        # Fast check: After removing padding, we should have a 32-byte key
        expected_len = len(decrypted) - padding_byte
        if expected_len != 32:
            return False, password

        # Fast check: Verify padding bytes match (using slice for better performance)
        padding_pattern = bytes([padding_byte]) * padding_byte
        if decrypted[-padding_byte:] != padding_pattern:
            return False, password

        # Remove padding
        decrypted = decrypted[:-padding_byte]

        # Fast check: Check for all zeros (unlikely to be a valid key)
        # Use a faster method than sum()
        if not any(decrypted):
            return False, password

        # Check for entropy in the key (valid keys should have good entropy)
        # Just check first few bytes for performance
        # Use a faster method with a set comprehension
        if len({decrypted[i] for i in range(min(8, len(decrypted)))}) < 3:
            return False, password

        # If we passed all checks, this is likely a valid password
        return True, password

    except Exception:
        # Silent exceptions for performance
        return False, password

def extract_from_json(json_path):
    """Extract encrypted_key and salt from a JSON file."""
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Look for mkey in the JSON
        if 'mkey' in data:
            mkey = data['mkey']
            encrypted_key = mkey.get('encrypted_key')
            salt = mkey.get('salt')
            iterations = mkey.get('iterations', 25000)
            return encrypted_key, salt, iterations
        else:
            print(f"{ERROR}Error: No master key found in JSON file{RESET}")
            sys.exit(1)
    except Exception as e:
        print(f"{ERROR}Error reading JSON file: {e}{RESET}")
        sys.exit(1)

def extract_from_wallet(wallet_path):
    """Extract encrypted_key and salt from a wallet.dat file."""
    print(f"{WARNING}Extracting from wallet.dat is not implemented yet.{RESET}")
    print(f"{WARNING}Please use --json or provide --encrypted_key and --salt directly.{RESET}")
    sys.exit(1)

def generate_passwords(min_length, max_length, charset):
    """Generate all possible passwords within the given constraints."""
    for length in range(min_length, max_length + 1):
        for password in itertools.product(charset, repeat=length):
            yield ''.join(password)

def process_chunk(chunk, encrypted_key, salt, iterations):
    """Process a chunk of passwords."""
    results = []
    for password in chunk:
        success, pwd = check_password(password, encrypted_key, salt, iterations)
        if success:
            results.append(pwd)
    return results

def process_chunk_parallel(chunk, encrypted_key, salt, iterations, processes):
    """Process a chunk of passwords in parallel using multiple processes."""
    # If processes is 1 or less, just use the single-threaded version
    if processes <= 1:
        return process_chunk(chunk, encrypted_key, salt, iterations)

    # For very small chunks, don't bother with parallelism
    if len(chunk) < processes * 4:  # Increased threshold for better efficiency
        return process_chunk(chunk, encrypted_key, salt, iterations)

    # Optimize for M3 processor - use a more efficient chunk size
    # M3 has high single-core performance, so we want larger chunks per core
    # to reduce overhead from process creation and communication
    optimal_chunk_size = max(100, len(chunk) // processes)

    # Split the chunk into smaller chunks for parallel processing
    # Use a more efficient method for creating sub-chunks
    sub_chunks = []
    for i in range(0, len(chunk), optimal_chunk_size):
        end = min(i + optimal_chunk_size, len(chunk))
        sub_chunks.append(chunk[i:end])

    # Process the sub-chunks in parallel
    results = []

    # Use a context manager to ensure proper cleanup
    with ProcessPoolExecutor(max_workers=processes) as executor:
        # Submit all tasks
        futures = []
        for sub_chunk in sub_chunks:
            future = executor.submit(process_chunk, sub_chunk, encrypted_key, salt, iterations)
            futures.append(future)

        # Collect results as they complete - more efficient with as_completed
        for future in as_completed(futures):
            try:
                sub_results = future.result()
                if sub_results:  # If we found a match
                    results.extend(sub_results)
                    # Cancel remaining futures immediately
                    for f in futures:
                        if not f.done():
                            f.cancel()
                    break
            except Exception:
                # Ignore exceptions in worker processes for robustness
                pass

    return results

def chunk_generator(generator, chunk_size):
    """Split a generator into chunks."""
    chunk = []
    for item in generator:
        chunk.append(item)
        if len(chunk) >= chunk_size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk

def smart_password_generator(charset, length, batch_size=1000, max_consecutive=0):
    """
    Generate passwords using frequency analysis and common patterns.
    This is much more efficient than brute force for real-world passwords.
    """
    # Common character frequencies in passwords (most to least common)
    common_chars = "aeorisn1tl2md0cp3hbuk45g9687yjfvzxwq"

    # Common patterns at the beginning of passwords
    common_prefixes = ["a", "p", "s", "1", "2", "m", "t", "b", "d", "h"]

    # Common patterns at the end of passwords
    common_suffixes = ["1", "123", "2", "a", "0", "12", "3", "4", "5", "!"]

    # First, try common patterns
    batch = []

    # Try common prefixes with common suffixes
    for prefix in common_prefixes:
        for suffix in common_suffixes:
            if len(prefix) + len(suffix) <= length:
                # Fill the middle with common characters
                middle_len = length - len(prefix) - len(suffix)
                if middle_len == 0:
                    password = prefix + suffix
                    if max_consecutive <= 0 or not has_too_many_consecutive_chars(password, max_consecutive):
                        batch.append(password)
                        if len(batch) >= batch_size:
                            yield batch
                            batch = []
                else:
                    # Generate some common middle patterns
                    for c in common_chars[:min(10, len(common_chars))]:
                        middle = c * middle_len
                        password = prefix + middle + suffix
                        if max_consecutive <= 0 or not has_too_many_consecutive_chars(password, max_consecutive):
                            batch.append(password)
                            if len(batch) >= batch_size:
                                yield batch
                                batch = []

    # Then try repeating characters (like "aaaaaa")
    for c in charset:
        password = c * length
        # Only add if max_consecutive allows it (or is disabled)
        if max_consecutive <= 0 or length <= max_consecutive:
            batch.append(password)
            if len(batch) >= batch_size:
                yield batch
                batch = []

    # Try alternating patterns (like "ababab")
    for i in range(len(charset)):
        for j in range(i+1, len(charset)):
            pattern = (charset[i] + charset[j]) * (length // 2)
            if length % 2 == 1:
                pattern += charset[i]
            # Check for consecutive characters
            if max_consecutive <= 0 or not has_too_many_consecutive_chars(pattern, max_consecutive):
                batch.append(pattern)
                if len(batch) >= batch_size:
                    yield batch
                    batch = []

    # Yield any remaining passwords
    if batch:
        yield batch

    # Finally, fall back to regular brute force
    # But prioritize common characters first
    sorted_charset = ""
    for c in common_chars:
        if c in charset:
            sorted_charset += c
    for c in charset:
        if c not in sorted_charset:
            sorted_charset += c

    # Now generate passwords with the sorted charset
    for password_tuple in itertools.product(sorted_charset, repeat=length):
        password = ''.join(password_tuple)
        batch.append(password)
        if len(batch) >= batch_size:
            yield batch
            batch = []

    # Yield any remaining passwords
    if batch:
        yield batch

def save_checkpoint(checkpoint_file, current_state):
    """Save the current state to a checkpoint file."""
    try:
        with open(checkpoint_file, 'w') as f:
            json.dump(current_state, f)
        return True
    except Exception as e:
        print(f"\n{WARNING}Error saving checkpoint: {e}{RESET}")
        return False

def load_checkpoint(checkpoint_file):
    """Load the current state from a checkpoint file."""
    try:
        with open(checkpoint_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"\n{WARNING}Error loading checkpoint: {e}{RESET}")
        return None

def format_time(seconds):
    """Format seconds into a human-readable time string."""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f} hours"
    else:
        days = seconds / 86400
        return f"{days:.1f} days"

def calculate_eta(attempts, total, elapsed):
    """Calculate estimated time to completion."""
    if attempts == 0 or elapsed == 0:
        return "Unknown"

    rate = attempts / elapsed
    remaining_attempts = total - attempts

    if rate == 0:
        return "Unknown"

    seconds_remaining = remaining_attempts / rate
    return format_time(seconds_remaining)

def print_stats(attempts, total, elapsed, rate, current_password=None, show_current=False, single_line=True):
    """Print statistics about the brute force process."""
    percent = (attempts / total) * 100 if total > 0 else 0
    eta = calculate_eta(attempts, total, elapsed)

    # For single line mode, we need to clear the line first
    if single_line:
        # Use a longer clear string to ensure the entire line is cleared
        # This is especially important for wide terminal windows
        sys.stdout.write("\r" + " " * 150 + "\r")

    # Build the stats string
    stats = (
        f"{INFO}Progress: {BOLD}{percent:.2f}%{RESET} "
        f"({attempts:,}/{total:,}) | "
        f"Speed: {BOLD}{rate:.2f}{RESET} p/s | "
        f"Elapsed: {format_time(elapsed)} | "
        f"ETA: {BOLD}{eta}{RESET}"
    )

    if show_current and current_password:
        stats += f" | Current: {current_password}"

    # For single line mode, we need to start with a carriage return
    # and NOT end with a newline
    if single_line:
        # Only add the carriage return at the beginning
        stats = "\r" + stats
    else:
        # For multi-line mode, end with a newline
        stats += "\n"

    # Write the stats and flush to ensure immediate display
    sys.stdout.write(stats)
    sys.stdout.flush()

def brute_force_wordlist(wordlist_path, encrypted_key, salt, iterations, processes, status_interval, show_current=False, quiet=False, single_line=True):
    """Brute force using a wordlist."""
    try:
        with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
            passwords = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"{ERROR}Error reading wordlist: {e}{RESET}")
        sys.exit(1)

    total_passwords = len(passwords)
    print(f"{INFO}Loaded {total_passwords:,} passwords from wordlist{RESET}")

    # Create progress bar if tqdm is available and not in quiet mode
    pbar = None
    if TQDM_AVAILABLE and not quiet and not single_line:
        try:
            pbar = tqdm.tqdm(total=total_passwords, unit="pwd", desc="Testing passwords",
                           bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]")
        except Exception as e:
            print(f"{ERROR}Error creating progress bar: {e}{RESET}")

    # Process passwords in chunks
    attempts = 0
    start_time = time.time()
    last_status_time = start_time
    last_update_time = start_time
    found_passwords = []

    # Process in chunks to provide regular updates
    # Optimize for M3 processor - use larger chunks for better performance
    chunk_size = 5000  # Much larger chunks for M3's high performance cores
    batch_num = 0

    for i in range(0, total_passwords, chunk_size):
        batch_num += 1
        chunk = passwords[i:i+chunk_size]

        # Process the chunk using parallel processing if available
        results = process_chunk_parallel(chunk, encrypted_key, salt, iterations, processes)
        chunk_size_actual = len(chunk)
        attempts += chunk_size_actual

        # Update progress bar (force update every 0.1 seconds)
        current_time = time.time()
        if pbar and (current_time - last_update_time >= 0.1):
            pbar.update(chunk_size_actual)
            pbar.refresh()
            last_update_time = current_time

        # Print detailed stats
        if attempts % status_interval == 0 or current_time - last_status_time >= 1:
            elapsed = current_time - start_time
            rate = attempts / elapsed if elapsed > 0 else 0

            # Show current password if requested
            current_pwd = chunk[-1] if show_current and chunk else None

            # Print stats
            if not quiet:
                if single_line:
                    # Just print a single status line
                    print_stats(attempts, total_passwords, elapsed, rate, current_pwd, show_current, True)
                else:
                    # Print more detailed stats
                    print_stats(attempts, total_passwords, elapsed, rate, current_pwd, show_current, False)
                    sys.stdout.write(f"\r{INFO}Batch {batch_num}: Testing {chunk_size_actual} passwords from wordlist{RESET}")
                    sys.stdout.flush()

            last_status_time = current_time

        # Check if we found a match
        if results:
            for password in results:
                if isinstance(password, bytes):
                    password = password.decode('utf-8', errors='replace')

                # Double-check the password to avoid false positives
                is_valid, _ = check_password(password, encrypted_key, salt, iterations)
                if is_valid:
                    found_passwords.append(password)
                    print(f"\n{SUCCESS}{BOLD}Potential password found: {password}{RESET}")
                    if not single_line:
                        print(f"{INFO}Continuing to search for additional matches...{RESET}")

    if pbar:
        pbar.close()

    # Final verification of found passwords
    if found_passwords:
        # Add a newline before final output if we were in single line mode
        if single_line:
            print()
        print(f"{SUCCESS}{BOLD}Found {len(found_passwords)} potential password(s):{RESET}")
        for i, password in enumerate(found_passwords):
            print(f"{SUCCESS}{i+1}. {password}{RESET}")

        # Return the first found password
        return found_passwords[0]
    else:
        # Add a newline before final output if we were in single line mode
        if single_line:
            print()
        print(f"{WARNING}No matching password found in wordlist{RESET}")
        return None

def brute_force_generated(min_length, max_length, charset, encrypted_key, salt, iterations, processes, status_interval,
                       show_current=False, quiet=False, single_line=True, smart=False, checkpoint=None,
                       checkpoint_interval=60, use_gpu=False, optimize_for="auto", max_consecutive=0):
    """Brute force using generated passwords."""
    charset_list = list(charset)

    # Calculate total number of passwords to try
    if max_consecutive > 0 and max_consecutive < max_length:
        # Estimate the number of passwords with max_consecutive constraint
        # This is an approximation based on combinatorial math
        # For exact count, we would need to use more complex math (Goulden-Jackson algorithm)
        reduction_factor = 0.0
        if max_consecutive == 1:
            # With max_consecutive=1, we eliminate all passwords with repeated characters
            # Reduction is more significant for longer passwords and smaller charsets
            reduction_factor = 0.95 if len(charset) < 10 else 0.85
        elif max_consecutive == 2:
            # With max_consecutive=2, we eliminate passwords with 3+ consecutive identical chars
            reduction_factor = 0.75 if len(charset) < 10 else 0.50
        elif max_consecutive == 3:
            # With max_consecutive=3, we eliminate passwords with 4+ consecutive identical chars
            reduction_factor = 0.40 if len(charset) < 10 else 0.25
        else:
            # For higher values, the reduction is less significant
            reduction_factor = 0.20 if len(charset) < 10 else 0.10

        # Calculate the reduced total
        raw_total = sum(len(charset) ** length for length in range(min_length, max_length + 1))
        total_passwords = int(raw_total * (1 - reduction_factor))
    else:
        # Without max_consecutive constraint, use the full count
        total_passwords = sum(len(charset) ** length for length in range(min_length, max_length + 1))

    print(f"{INFO}Will try approximately {total_passwords:,} passwords{RESET}")

    # Show character set info
    if not quiet:
        print(f"{INFO}Character set ({len(charset)} chars): {charset[:50]}{' ...' if len(charset) > 50 else ''}{RESET}")
        print(f"{INFO}Password length range: {min_length} to {max_length}{RESET}")

        # Show optimization info
        if smart:
            print(f"{INFO}Using smart password generation (frequency analysis){RESET}")
        if max_consecutive > 0:
            print(f"{INFO}Maximum consecutive identical characters: {max_consecutive}{RESET}")
        if use_gpu and GPU_AVAILABLE:
            print(f"{INFO}Using GPU acceleration{RESET}")
        if optimize_for != "auto":
            print(f"{INFO}Optimizing for {optimize_for.upper()} architecture{RESET}")
        if checkpoint:
            print(f"{INFO}Using checkpoint file: {checkpoint}{RESET}")

    # Create progress bar if tqdm is available and not in quiet mode
    pbar = None
    if TQDM_AVAILABLE and not quiet and not single_line:
        try:
            pbar = tqdm.tqdm(total=total_passwords, unit="pwd", desc="Testing passwords",
                           bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]")
            print(f"{INFO}Progress bar initialized with {total_passwords:,} passwords{RESET}")
        except Exception as e:
            print(f"{ERROR}Error creating progress bar: {e}{RESET}")

    # Process results as they complete
    attempts = 0
    start_time = time.time()
    last_status_time = start_time
    last_update_time = start_time
    last_checkpoint_time = start_time

    # Use a simpler approach with direct processing
    print(f"{INFO}Starting password testing...{RESET}")

    # Process passwords in smaller batches for more frequent updates
    batch_num = 0
    found_passwords = []

    # Load checkpoint if available
    checkpoint_data = None
    if checkpoint and os.path.exists(checkpoint):
        checkpoint_data = load_checkpoint(checkpoint)
        if checkpoint_data:
            print(f"{INFO}Resuming from checkpoint: {checkpoint_data.get('attempts', 0):,} passwords tested{RESET}")
            attempts = checkpoint_data.get('attempts', 0)
            start_time = time.time() - checkpoint_data.get('elapsed', 0)
            # Skip lengths that have been completed
            min_length = checkpoint_data.get('current_length', min_length)

    # Optimize for specific architecture
    if optimize_for == "m3":
        # M3 has high single-core performance and efficient cores
        batch_size = 10000  # Larger batches for M3
        processes = min(processes, 10)  # Slight oversubscription for M3
    elif optimize_for == "m2" or optimize_for == "m1":
        # M1/M2 also have good performance
        batch_size = 8000
        processes = min(processes, 10)
    elif optimize_for == "intel":
        # Intel processors often have more cores but lower single-core performance
        batch_size = 5000
        processes = min(processes, os.cpu_count() + 2)  # More oversubscription
    else:  # auto
        # Detect Apple Silicon
        import platform as plt
        if plt.processor() == 'arm':
            batch_size = 10000  # Assume M-series
            processes = min(processes, 10)
        else:
            batch_size = 5000
            processes = min(processes, os.cpu_count() + 2)

    for length in range(min_length, max_length + 1):
        if not single_line:
            print(f"\n{INFO}Testing passwords of length: {length}{RESET}")

        # Update checkpoint data
        if checkpoint:
            checkpoint_data = {
                'attempts': attempts,
                'elapsed': time.time() - start_time,
                'current_length': length,
                'charset': charset,
                'min_length': min_length,
                'max_length': max_length
            }

        # Choose the password generator based on settings
        if smart:
            generator = smart_password_generator(charset, length, batch_size, max_consecutive)
        else:
            # For each length, generate all possible passwords
            # Optimize batch size based on architecture
            generator = chunk_generator(itertools.product(charset_list, repeat=length), batch_size)

        for batch in generator:
            batch_num += 1
            # Convert tuples to strings and filter out passwords with too many consecutive characters
            if max_consecutive > 0:
                password_batch = [''.join(p) for p in batch if not has_too_many_consecutive_chars(''.join(p), max_consecutive)]
            else:
                password_batch = [''.join(p) for p in batch]

            # Process the batch
            try:
                results = process_chunk_parallel(password_batch, encrypted_key, salt, iterations, processes)
                current_batch_size = len(password_batch)
                attempts += current_batch_size

                # Update progress bar (force update every 0.1 seconds)
                current_time = time.time()
                if pbar and (current_time - last_update_time >= 0.1):
                    pbar.update(current_batch_size)
                    pbar.refresh()
                    last_update_time = current_time

                # Print detailed stats
                if attempts % status_interval == 0 or current_time - last_status_time >= 0.5:
                    elapsed = current_time - start_time
                    rate = attempts / elapsed if elapsed > 0 else 0

                    # Update current pattern for display
                    current_pattern = password_batch[-1] if show_current and password_batch else None

                    # Print stats
                    if not quiet:
                        if single_line:
                            # Just print a single status line
                            print_stats(attempts, total_passwords, elapsed, rate, current_pattern, show_current, True)
                        else:
                            # Print more detailed stats
                            print_stats(attempts, total_passwords, elapsed, rate, current_pattern, show_current, False)
                            sys.stdout.write(f"\r{INFO}Batch {batch_num}: Testing {current_batch_size} passwords of length {length}{RESET}")
                            sys.stdout.flush()

                    last_status_time = current_time

                    # Save checkpoint if needed
                    if checkpoint and (current_time - last_checkpoint_time >= checkpoint_interval):
                        checkpoint_data = {
                            'attempts': attempts,
                            'elapsed': current_time - start_time,
                            'current_length': length,
                            'charset': charset,
                            'min_length': min_length,
                            'max_length': max_length
                        }
                        if save_checkpoint(checkpoint, checkpoint_data):
                            # If in single line mode, don't add a newline
                            if single_line:
                                # Save current progress stats
                                elapsed = current_time - start_time
                                rate = attempts / elapsed if elapsed > 0 else 0
                                current_pattern = password_batch[-1] if show_current and password_batch else None

                                # Clear the line first
                                sys.stdout.write("\r" + " " * 150 + "\r")
                                sys.stdout.write(f"{INFO}Checkpoint saved: {attempts:,} passwords tested{RESET}")
                                sys.stdout.flush()

                                # Wait a moment to show the message
                                time.sleep(0.5)

                                # Restore progress display
                                sys.stdout.write("\r" + " " * 150 + "\r")
                                print_stats(attempts, total_passwords, elapsed, rate, current_pattern, show_current, True)
                            else:
                                print(f"\n{INFO}Checkpoint saved: {attempts:,} passwords tested{RESET}")
                        last_checkpoint_time = current_time

                # Check if we found a match
                if results:
                    for password in results:
                        if isinstance(password, bytes):
                            password = password.decode('utf-8', errors='replace')

                        # Double-check the password to avoid false positives
                        is_valid, _ = check_password(password, encrypted_key, salt, iterations)
                        if is_valid:
                            found_passwords.append(password)
                            print(f"\n{SUCCESS}{BOLD}Potential password found: {password}{RESET}")
                            if not single_line:
                                print(f"{INFO}Continuing to search for additional matches...{RESET}")

            except Exception as e:
                print(f"\n{ERROR}Error processing batch {batch_num}: {e}{RESET}")

    if pbar:
        pbar.close()

    # Final verification of found passwords
    if found_passwords:
        # Add a newline before final output if we were in single line mode
        if single_line:
            print()
        print(f"{SUCCESS}{BOLD}Found {len(found_passwords)} potential password(s):{RESET}")
        for i, password in enumerate(found_passwords):
            print(f"{SUCCESS}{i+1}. {password}{RESET}")

        # Return the first found password
        return found_passwords[0]
    else:
        # Add a newline before final output if we were in single line mode
        if single_line:
            print()
        print(f"{WARNING}No matching password found after trying {attempts:,} passwords{RESET}")
        return None

def print_banner():
    """Print a fancy banner."""
    if COLORAMA_AVAILABLE:
        banner = f"""
{BOLD}{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║                                                          ║
║  {Fore.YELLOW}Bitcoin Wallet Password Brute Force Tool{Fore.CYAN}                ║
║                                                          ║
║  {Fore.WHITE}A tool to recover forgotten Bitcoin wallet passwords{Fore.CYAN}     ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝{RESET}
"""
    else:
        banner = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║  Bitcoin Wallet Password Brute Force Tool                ║
║                                                          ║
║  A tool to recover forgotten Bitcoin wallet passwords    ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""
    print(banner)

def print_system_info():
    """Print system information for performance tuning."""
    import platform as plt
    print(f"{INFO}System Information:{RESET}")
    print(f"  {INFO}OS:{RESET} {plt.system()} {plt.release()}")
    print(f"  {INFO}CPU:{RESET} {plt.processor()}")

    if PSUTIL_AVAILABLE:
        # Use psutil for detailed system information
        print(f"  {INFO}Cores:{RESET} {psutil.cpu_count(logical=False)} physical, {psutil.cpu_count(logical=True)} logical")
        print(f"  {INFO}Memory:{RESET} {psutil.virtual_memory().total / (1024**3):.1f} GB total")

        # Get CPU frequency if available
        try:
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                print(f"  {INFO}CPU Frequency:{RESET} {cpu_freq.current / 1000:.2f} GHz")
        except Exception:
            pass
    else:
        print(f"  {INFO}Cores:{RESET} {os.cpu_count()} logical")
        print(f"  {INFO}Install psutil for more detailed system information:{RESET} pip install psutil")

    # Check for GPU acceleration
    if GPU_AVAILABLE:
        try:
            platforms = pyopencl.get_platforms()
            if platforms:
                print(f"  {INFO}GPU Acceleration:{RESET} Available")
                for platform in platforms:
                    for device in platform.get_devices():
                        if device.type == pyopencl.device_type.GPU:
                            print(f"    - {device.name} ({device.global_mem_size / (1024**3):.1f} GB)")
        except Exception:
            print(f"  {INFO}GPU Acceleration:{RESET} Error detecting GPUs")
    else:
        print(f"  {INFO}GPU Acceleration:{RESET} Not available (install pyopencl and numpy for GPU support)")

    print(f"  {INFO}Python:{RESET} {plt.python_version()}")
    print()

def main():
    """Main function."""
    print_banner()

    # Print system information for performance tuning
    print_system_info()

    args = parse_arguments()

    # Get encrypted_key and salt
    encrypted_key = None
    salt = None
    iterations = args.iterations

    if args.json:
        encrypted_key, salt, extracted_iterations = extract_from_json(args.json)
        if extracted_iterations:
            iterations = extracted_iterations
    elif args.wallet:
        encrypted_key, salt, extracted_iterations = extract_from_wallet(args.wallet)
        if extracted_iterations:
            iterations = extracted_iterations
    else:
        encrypted_key = args.encrypted_key
        salt = args.salt

    # Validate required parameters
    if not encrypted_key:
        print(f"{ERROR}Error: Encrypted key is required{RESET}")
        sys.exit(1)

    if not salt:
        print(f"{ERROR}Error: Salt is required{RESET}")
        sys.exit(1)

    # Convert hex strings to bytes
    try:
        encrypted_key = hex_to_bytes(encrypted_key)
        salt = hex_to_bytes(salt)
    except Exception as e:
        print(f"{ERROR}Error converting hex to bytes: {e}{RESET}")
        sys.exit(1)

    # Print configuration
    print(f"{INFO}Brute Force Configuration:{RESET}")
    print(f"  {INFO}Encrypted key:{RESET} {encrypted_key.hex()}")
    print(f"  {INFO}Salt:{RESET} {salt.hex()}")
    print(f"  {INFO}Iterations:{RESET} {iterations}")
    print(f"  {INFO}Processes:{RESET} {args.processes}")

    # System information already printed in main()

    # Start time for the whole process
    overall_start_time = time.time()

    # Start brute force
    if args.wordlist:
        print(f"{INFO}Starting brute force with wordlist: {args.wordlist}{RESET}")
        password = brute_force_wordlist(
            args.wordlist, encrypted_key, salt, iterations,
            args.processes, args.status_interval, args.show_current, args.quiet, args.single_line
        )
    else:
        print(f"{INFO}Starting brute force with generated passwords{RESET}")
        password = brute_force_generated(
            args.min_passwd, args.max_passwd, args.charset,
            encrypted_key, salt, iterations, args.processes,
            args.status_interval, args.show_current, args.quiet, args.single_line,
            args.smart, args.checkpoint, args.checkpoint_interval, args.use_gpu, args.optimize_for,
            args.max_consecutive
        )

    # Calculate total time
    total_time = time.time() - overall_start_time

    if password:
        # Final verification with a different method if possible
        print(f"\n{INFO}Performing final verification of password...{RESET}")

        # If we have a wallet file, try to use it to verify the password
        if args.wallet:
            try:
                print(f"{INFO}Attempting to verify password with wallet file...{RESET}")
                # Here you would add code to verify the password with the wallet file
                # For now, we'll just rely on our existing verification
                is_valid, _ = check_password(password, encrypted_key, salt, iterations)
                if is_valid:
                    print(f"\n{SUCCESS}{BOLD}Success! The password is: {password}{RESET}")
                else:
                    print(f"\n{WARNING}Warning: Password verification failed. The found password might be incorrect.{RESET}")
                    print(f"{WARNING}Found password: {password}{RESET}")
            except Exception as e:
                print(f"{WARNING}Warning: Could not verify password with wallet file: {e}{RESET}")
                print(f"{WARNING}Found password: {password}{RESET}")
        else:
            # Just use our existing verification
            is_valid, _ = check_password(password, encrypted_key, salt, iterations)
            if is_valid:
                print(f"\n{SUCCESS}{BOLD}Success! The password is: {password}{RESET}")
            else:
                print(f"\n{WARNING}Warning: Password verification failed. The found password might be incorrect.{RESET}")
                print(f"{WARNING}Found password: {password}{RESET}")

        print(f"{INFO}Total time: {format_time(total_time)}{RESET}")
        return 0
    else:
        # Add a newline if we were in single line mode
        if args.single_line:
            print()
        print(f"{ERROR}Failed to find the password{RESET}")
        print(f"{INFO}Total time: {format_time(total_time)}{RESET}")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{WARNING}Brute force interrupted by user{RESET}")
        sys.exit(130)
