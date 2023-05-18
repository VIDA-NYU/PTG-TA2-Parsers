# OCARINA (NGC)

Repository containing scripts to parse Ocarina datasets into ARGUS format. 

---

#### Scripts

[*eye-parser.py*](https://github.com/VIDA-NYU/PTG-TA2-Parsers/blob/main/ngc-ocarina/eye-parser.py): Transforms data from the *hl2_gaze* into JSON files ready to be consumed by ARGUS.

[*perception-parser.py*](): TBD

[*reasoning-parser.py*](): TBD

#### Usage

[*eye-parser.py*](https://github.com/VIDA-NYU/PTG-TA2-Parsers/blob/main/ngc-ocarina/eye-parser.py): Takes a path for the SQLite file containing all information regarding a session (described by a pair of subject ID and trial ID). Outputs a JSON file with the formatted gaze information. 

**Example**: `python eye-parser.py -i /foo/0293_11.sqlite -o ./bar/0293_11`


