Testing. But for this to work, it has to go round-trip from repo to registry to tw -I, to be valid. We will need corresponding changes to make-awesome --install function, which creates the meta and installer. Currently, during --install, if [5] wrapper is selected, then prompt for flag-word (just enter for none) and script name, needs to prompt for type, and the .meta has to correspond. I've uploaded make-awesome, have a look. If you're running low on context, make detailed notes on what needs changing.
Feb 20
Viewed 5 files
Done

Good — I have the complete picture. Context is getting long so let me write precise change notes now, then ask if you want me to generate the updated file.
make-awesome.py — Required Changes for filter wrapper support

Version bump: 4.6.0 → 4.7.0
1. ProjectInfo class (~line 527)

Add one new field:
python

self.wrapper_type = "command"  # 'command' or 'filter'

2. prompt_for_metadata() — reading existing .meta (~line 722)

After the wrapper.script= read block, add:
python

elif line.startswith('wrapper.type='):
    info.wrapper_type = line.split('=', 1)[1].strip()

3. prompt_for_metadata() — wrapper prompts (~line 758, after keyword+script prompts)

After the script prompt block, add:
python

# Wrapper type prompt
current_type = info.wrapper_type or 'command'
response = input(f"Wrapper type — (1) command, (2) filter [{current_type}]: ").strip()
type_map = {'1': 'command', '2': 'filter'}
info.wrapper_type = type_map.get(response, current_type)

For filter type: keyword is still used as the toggle command name, but the prompt text should clarify it's also used as the tw nicedates toggle keyword. No other changes to the keyword/script prompts needed.
4. generate_meta_file() (~line 915)

After wrapper.script= line, add:
python

f.write(f"wrapper.type={info.wrapper_type}\n")

5. generate_installer() — install function, wrapper registration (~line 1103)

Change the .tw_wrappers echo line from:
python

f.write(f'        echo "{info.wrapper_keyword}|{info.wrapper_script}|{info.description}" >> "$WRAPPERS_FILE"\n')

To:
python

f.write(f'        echo "{info.wrapper_keyword}|{info.wrapper_script}|{info.description}|{info.wrapper_type}" >> "$WRAPPERS_FILE"\n')

6. Script filename in installer — nicedates-specific issue

The installer currently downloads nicedates.py and registers nicedates.py in .tw_wrappers. Since we're dropping the .py extension, the repo file must be named nicedates (no extension), and the installer must reference it as nicedates. This is handled automatically since make-awesome uses the actual filename from the repo — so just rename the file in the repo before running --install again.

That's 5 targeted changes, all in make-awesome.py, totalling about 8 lines changed/added. Want me to generate the updated file now?

Yes, and we can assume the nicedates name-change, proceed!
12:01 a.m.
Edited 7 files, ran 3 commands
+1-1
+1-1
+4-3
+6-4
+18-10
+4-3
+11-11
Done

All 5 changes confirmed. Copy to outputs:
Ran a command, read a file
Done

make-awesome.py v4.7.0 — changes summary:

All minimal and targeted — 5 spots touched:

    ProjectInfo — wrapper_type = "command" default field added
    .meta reader — picks up existing wrapper.type= on re-run (so defaults are preserved)
    Prompt — after script name, shows (1) command / (2) filter with examples; also accepts typing command or filter directly; defaults to existing value on re-run
    generate_meta_file() — writes wrapper.type=filter (or command) after wrapper.script=
    generate_installer() — appends |filter (or |command) to the .tw_wrappers echo line; install message now says nicedates -> nicedates (filter)

Your workflow for nicedates:

    Rename nicedates.py → nicedates in the repo
    Run make-awesome --install → when prompted for wrapper type, enter 2 (filter)
    Run make-awesome --push
    tw -I nicedates on target machine — .tw_wrappers entry will now have |filter
    tw next should pipe through nicedates automatically

The existing annn entry in .tw_wrappers has no type field — tw defaults it to command, so no change needed there.
Make awesome
PY 

[make] [OK] Push complete!
 djp  yoga  ~/dev/tw-nicedates-hook  main  tw -l
[tw] Available applications:
[tw] [ ] agenda-edate (v1.0.0) [agenda, edate, reports, hook]
[tw] [*] annn (v0.5.0) [annotation, list, edit, wrapper]
[tw] [ ] annnotate (v0.5.0) [annotation, list, edit, wrapper]
[tw] [*] need-priority (v0.4.5) [priority, needs, focus, hook]
[tw] [ ] nicedates (v1.0.1) [nice, readable, dates, time, reports, wrapper]
[tw] [*] recurrence-overhaul (v2.7.0) [recurrence, period, chain, time, reports, hook]
[tw] [*] resched (v1.0.0) [sched, review, script]
[tw] [*] t (v1.0.0) [time, tracking, timedot, hledger, script]
[tw] [*] tod-filter (v0.1.1) [time, blocks, tags, filter, focus, hook]
[tw] [*] urgency-tweaker (v1.0.0) [urgency, tweak, core, projects, tags, udas, scripts]
[tw] [*] wikitags (v1.0.0) [wiki, tags, hook]
[tw] Legend: [*] = installed, [ ] = available
 djp  yoga  ~/dev/tw-nicedates-hook  main  tw -I nicedates
[tw] Installing nicedates v1.0.1...
[tw] Creating directories...
[tw] Downloading files...
curl: (23) Failure writing output to destination
[tw] [FAIL] Failed to download nicedates
[tw] [X] Installation failed: nicedates
 djp  yoga  ~/dev/tw-nicedates-hook  main  vi nicedates.meta 

name=nicedates
version=1.0.1
type=wrapper
description=Transforms report dates to human readable; Today, Friday, Feb20, etc
repo=https://github.com/linuxcaffe/tw-nicedates-hook
base_url=https://raw.githubusercontent.com/linuxcaffe/tw-nicedates-hook/main
files=nicedates:script,nicedates.rc:config,README.md:doc
tags=nice, readable, dates, time, reports, wrapper
checksums=50a98ac33c60ecc8cb4ef1d8a6fee44359157f674758226c1d2059bade16b138,939467003ddba4bf30426ea93ecac081b1ec9ca33c861aa3340dd6ef64bfe545,b249b70d8ed80efe86739574960b5dc31157086d01f9531261a82903ca0098d1
author=Designed by linuxcaffe, coded by Claude
license=MIT
requires_taskwarrior=2.6.0
wrapper.keyword=--dates
wrapper.script=nicedates
wrapper.type=filter

So close.. will fix next context. Realized can't have keyword and script the same, make install unusable! I hope --dates is fine. Any notes to future self?
1:00 a.m.

Great progress! Notes for next session:

The curl failure: The installer downloads nicedates (no extension) but curl may be failing because the GitHub raw URL for a file named nicedates (no extension) returns a content-type that curl's -o rejects. Quick fix: ensure the file is committed to the repo with no extension and the raw URL resolves correctly — test with curl -fsSL https://raw.githubusercontent.com/linuxcaffe/tw-nicedates-hook/main/nicedates manually.

keyword vs script same name: Good catch. The keyword (--dates or nicedates) is the tw dispatch word; the script is the executable filename. They were the same (nicedates) which confused make-awesome's prompt logic. --dates as keyword works but note tw's find_keyword scans args for bare words — a -- prefix might cause issues since args starting with -- are skipped as flags. Consider nicedate or dates as keyword instead. Check find_keyword in tw — it skips args starting with -.

.tw_wrappers entry to manually fix for now:

nicedates|nicedates|description|filter

The keyword here is just the toggle command name (tw nicedates → toggle). For filter type, the keyword is only used for the toggle dispatch, not for scanning report args.

Column width issue — still outstanding. Task pads columns to dateformat width (Y-M-D H:N:S = 19 chars). Plan: after PTY capture, detect columns that are all-spaces after position ~10 and trim trailing spaces from date replacements.

Summary of files at last known good state:

    tw v2.9.0 — filter wrapper architecture done
    nicedates v1.0.1 — standalone works, tw pipe mode ready
    nicedates.rc v1.0.0 — good
    make-awesome.py v4.7.0 — filter type prompt done

======================
 djp  yoga  ~/dev/tw-nicedates-hook  main  nicedates next
Traceback (most recent call last):
  File "/home/djp/.task/scripts/nicedates", line 616, in <module>
    main()
NameError: name 'main' is not defined. Did you mean: 'min'?

broken in simple wrapper mode
