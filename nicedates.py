#!/usr/bin/env python3

import sys
import subprocess
import re
from datetime import datetime, timedelta

def format_nice_date(date_str):
    """Convert date string to nice relative format."""
    try:
        # Try various taskwarrior date output formats
        for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d.%m.%Y", "%Y-%m-%d %H:%M:%S"]:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                break
            except ValueError:
                continue
        else:
            return date_str
    except (ValueError, TypeError):
        return date_str
    
    now = datetime.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    task_date = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    
    delta_days = (task_date - today).days
    
    # Yesterday, Today, Tomorrow
    if delta_days == -1:
        return "Yesterday"
    elif delta_days == 0:
        return "Today"
    elif delta_days == 1:
        return "Tomorrow"
    
    # Within next 6 days: day name
    elif 2 <= delta_days <= 7:
        return dt.strftime("%A")
    
    # Same year: MonthDay format (no leading zero)
    elif dt.year == now.year:
        month = dt.strftime("%b")
        day = dt.day
        return f"{month}{day}"
    
    # Different year: Month Day-YY format
    else:
        month = dt.strftime("%b")
        day = dt.day
        year_short = str(dt.year)[2:]
        return f"{month} {day}-{year_short}"

def strip_ansi(text):
    """Remove ANSI color codes from text."""
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    return ansi_escape.sub('', text)

def replace_dates(line):
    """Replace dates in a line with nice format, preserving column alignment."""
    # Match common date patterns, including with time
    patterns = [
        (r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', 19),  # 2026-01-03 12:00:00
        (r'\d{4}-\d{2}-\d{2}', 10),  # 2026-01-03
        (r'\d{2}/\d{2}/\d{4}', 10),  # 01/03/2026
        (r'\d{1,2}/\d{1,2}/\d{4}', 10),  # 1/3/2026
        (r'\d{2}\.\d{2}\.\d{4}', 10), # 03.01.2026
        (r'\d{1,2}\.\d{1,2}\.\d{4}', 10), # 3.1.2026
    ]
    
    # We need to preserve ANSI codes while replacing dates
    # Work with stripped version to find dates, then apply to original
    stripped = strip_ansi(line)
    
    # Collect all replacements with their positions in stripped text
    replacements = []
    
    for pattern, default_width in patterns:
        for match in re.finditer(pattern, stripped):
            date_str = match.group()
            nice_date = format_nice_date(date_str)
            
            # Pad to maintain column alignment
            original_width = len(date_str)
            nice_width = len(nice_date)
            
            if nice_width < original_width:
                # Pad with spaces on the right
                nice_date = nice_date + ' ' * (original_width - nice_width)
            elif nice_width > original_width:
                # Truncate if somehow longer (shouldn't happen often)
                nice_date = nice_date[:original_width]
            
            replacements.append((match.start(), match.end(), nice_date))
    
    # Sort by position and apply in reverse to maintain indices
    replacements.sort(reverse=True)
    
    # Now apply to original line (with ANSI codes)
    # We need to map positions in stripped text to positions in original
    result = line
    ansi_offset = 0
    stripped_pos = 0
    original_pos = 0
    
    # Build a mapping of stripped positions to original positions
    pos_map = {}
    i = 0
    j = 0
    ansi_pattern = re.compile(r'\x1b\[[0-9;]*m')
    
    while i < len(line):
        # Check if we're at an ANSI code
        ansi_match = ansi_pattern.match(line[i:])
        if ansi_match:
            # Skip the ANSI code
            i += ansi_match.end()
        else:
            # Regular character
            pos_map[j] = i
            i += 1
            j += 1
    pos_map[j] = len(line)  # End position
    
    # Apply replacements using the position map
    for start, end, replacement in replacements:
        if start in pos_map and end in pos_map:
            orig_start = pos_map[start]
            orig_end = pos_map[end]
            result = result[:orig_start] + replacement + result[orig_end:]
            
            # Update the position map for subsequent replacements
            offset = len(replacement) - (orig_end - orig_start)
            new_pos_map = {}
            for k, v in pos_map.items():
                if v < orig_start:
                    new_pos_map[k] = v
                elif v >= orig_end:
                    new_pos_map[k] = v + offset
            pos_map = new_pos_map
    
    return result

def main():
    """Main wrapper entry point."""
    # Build taskwarrior command
    args = sys.argv[1:]  # Get all arguments after script name
    
    # Always add forcecolor to preserve colors through the pipe
    args = ['rc._forcecolor=on'] + args
    
    # Run taskwarrior with a pseudo-TTY to preserve width and colors
    try:
        # Use script command to provide a pty, which makes task think it's interactive
        import os
        import pty
        import select
        
        # Get terminal size
        rows, cols = os.get_terminal_size()
        
        # Set up environment
        env = os.environ.copy()
        env['COLUMNS'] = str(cols)
        env['LINES'] = str(rows)
        
        # Create a pseudo-terminal
        master, slave = pty.openpty()
        
        # Start taskwarrior process
        proc = subprocess.Popen(
            ['task'] + args,
            stdin=slave,
            stdout=slave,
            stderr=slave,
            env=env
        )
        
        os.close(slave)
        
        # Read output and process it
        output = b''
        while True:
            ready, _, _ = select.select([master], [], [], 0.1)
            if ready:
                try:
                    chunk = os.read(master, 1024)
                    if not chunk:
                        break
                    output += chunk
                except OSError:
                    break
            elif proc.poll() is not None:
                # Process finished, read any remaining output
                try:
                    chunk = os.read(master, 1024)
                    output += chunk
                except OSError:
                    pass
                break
        
        os.close(master)
        proc.wait()
        
        # Decode and process output
        text_output = output.decode('utf-8', errors='replace')
        output_lines = text_output.split('\n')
        for line in output_lines:
            print(replace_dates(line))
        
        sys.exit(proc.returncode)
        
    except Exception as e:
        # Fallback to simple method if pty fails
        print(f"PTY method failed, using fallback: {e}", file=sys.stderr)
        result = subprocess.run(
            ['task'] + args,
            capture_output=True,
            text=True
        )
        
        output_lines = result.stdout.split('\n')
        for line in output_lines:
            print(replace_dates(line))
        
        if result.stderr:
            print(result.stderr, end='', file=sys.stderr)
        
        sys.exit(result.returncode)

if __name__ == "__main__":
    main()
