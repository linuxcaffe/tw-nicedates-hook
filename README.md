# nicedates

A Taskwarrior wrapper that transforms date displays into human-friendly relative formats while preserving colors and formatting.

## What It Does

`nicedates` makes Taskwarrior dates easier to read at a glance by displaying them relative to today:

- **Yesterday** / **Today** / **Tomorrow** - for those specific days
- **Monday**, **Tuesday**, etc. - for dates 2-7 days out
- **Jan13**, **Feb27** - for dates in the current year
- **Apr 1-27**, **May 19-27** - for dates in other years (with 2-digit year)

### Before
```
ID Due        Description
1  2026-01-03 Review proposal
2  2026-01-06 Team meeting
3  2026-02-15 Submit report
4  2027-04-01 Annual review
```

### After
```
ID Due       Description
1  Today     Review proposal
2  Monday    Team meeting
3  Feb15     Submit report
4  Apr 1-27  Annual review
```

## Installation

1. Download the script:
```bash
curl -o ~/bin/nicedates https://raw.githubusercontent.com/yourusername/nicedates/main/nicedates
chmod +x ~/bin/nicedates
```

2. Make sure `~/bin` is in your PATH, or place the script somewhere that is (like `/usr/local/bin`)

3. Use it as a drop-in replacement for `task`:
```bash
nicedates list
nicedates next
nicedates add "New task" due:tomorrow
```

### Optional: Alias It

Add this to your `~/.bashrc` or `~/.zshrc` to always use nicedates:
```bash
alias task='nicedates'
```

Then just use `task` commands as normal!

## How It Works

`nicedates` is a wrapper script that:

1. **Captures terminal properties** - Uses a pseudo-TTY to preserve Taskwarrior's full terminal width and color output
2. **Runs Taskwarrior** - Executes your command with all arguments passed through
3. **Transforms dates** - Parses the output and replaces date strings with relative formats
4. **Preserves alignment** - Pads transformed dates to maintain column alignment
5. **Maintains colors** - Carefully handles ANSI color codes to keep your beautiful Taskwarrior themes intact

### Supported Date Formats

The script recognizes and transforms these date formats:
- ISO format: `2026-01-03`
- US format: `01/03/2026` or `1/3/2026`
- European format: `03.01.2026` or `3.1.2026`
- With timestamps: `2026-01-03 12:00:00`

### Technical Details

- Written in Python 3
- Uses `pty` (pseudo-terminal) to trick Taskwarrior into full terminal mode
- Preserves ANSI color codes through regex-based position mapping
- Maintains original column widths through space padding

## Requirements

- Python 3.6+
- Taskwarrior 2.x or 3.x
- Unix-like system (Linux, macOS, BSD)

## Compatibility

Works with all Taskwarrior commands and reports. Simply prefix any `task` command with `nicedates` (or use the alias).

## Troubleshooting

**Dates aren't being transformed:**
- Check that the date format matches one of the supported patterns
- Try running with `task rc.dateformat=...` to see what format Taskwarrior is using

**Colors are missing:**
- Make sure your terminal supports ANSI colors
- Check that your Taskwarrior color theme is configured

**Columns are misaligned:**
- This may happen with custom report formats - let me know and I can add support!

## Contributing

Issues and pull requests welcome! If you find a date format that isn't being transformed, please share an example.

## License

MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
