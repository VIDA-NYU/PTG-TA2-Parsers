# OCARINA (NGC)

Repository containing scripts to parse Ocarina datasets into ARGUS format. 

---

#### Scripts

[*eye-parser.py*](https://github.com/VIDA-NYU/PTG-TA2-Parsers/blob/main/ngc-ocarina/eye-parser.py): Transforms data from the *hl2_gaze* into JSON files ready to be consumed by ARGUS.

[*perception-parser.py*](https://github.com/VIDA-NYU/PTG-TA2-Parsers/blob/main/ngc-ocarina/perception-parser.py): Transforms data from the *hl2_rgb_bounding_boxes* into a JSON file ready to be consumed by ARGUS. This includes detected objects.


[*reasoning-parser.py*](https://github.com/VIDA-NYU/PTG-TA2-Parsers/blob/main/ngc-ocarina/reasoning-parser.py): Transforms data from the *hl2_rgb_bounding_boxes* into a JSON file ready to be consumed by ARGUS. This includes actions (events) and steps.

[*generate-metadata.py*](https://github.com/VIDA-NYU/PTG-TA2-Parsers/blob/main/ngc-ocarina/generate-metadata.py): This scripts aims to generate the following metadata: duration_sec, first-entry, and last-entry, based on ``video`` and ``detic:image.json`` files. This must be executed AFTER the script ``perception-parser.py`` is run.

#### Usage

[*eye-parser.py*](https://github.com/VIDA-NYU/PTG-TA2-Parsers/blob/main/ngc-ocarina/eye-parser.py): Takes a path for the SQLite file containing all information regarding a session (described by a pair of subject ID and trial ID). Outputs a JSON file with the formatted gaze information. 

**Example**: `python eye-parser.py -i /foo/0293_11.sqlite -o ./bar/0293_11`

[*perception-parser.py*](https://github.com/VIDA-NYU/PTG-TA2-Parsers/blob/main/ngc-ocarina/perception-parser.py): Takes a path for the SQLite file containing bounding box information for objects of interest. Outputs a JSON file with the formatted perception information. 

**Example**: `python perception-parser.py -i /foo/0293_11.sqlite -o ./bar/0293_11`

[*reasoning-parser.py*](https://github.com/VIDA-NYU/PTG-TA2-Parsers/blob/main/ngc-ocarina/reasoning-parser.py): Takes a path for the SQLite file containing infromation reagrding the mission computer logs which include recordings of all physical interactions the subject made with the SIL during each trial. Outputs two JSON files with the formatted reasoning information. The first JSON file includes the actions, and the second JSON file includes the steps.

**Example**: `reasoning-parser.py -i /foo/0293_11.sqlite -o ./bar/0293_11`

[*generate-metadata.py*](https://github.com/VIDA-NYU/PTG-TA2-Parsers/blob/main/ngc-ocarina/generate-metadata.py): Takes a path for the video file of a session. Outputs a JSON file with the following metadata: duration_sec, first-entry, and last-entry, based on the ``video`` and ``detic:image.json`` files. This must be executed AFTER the script ``perception-parser.py`` is run since ``detic:image.json`` file is required.

**Example**: `generate-metadata.py -i /foo/ngc_0293_13.mp4 -o ./bar/0293_11`

**Example**: `TBD`


[*perception-parser.py*](https://github.com/VIDA-NYU/PTG-TA2-Parsers/blob/main/ngc-ocarina/eye-parser.py): TBD

**Example**: `TBD`


## Running ARGUS Locally

----

## Prerequisites

Tested with **Docker 24.0** and **docker-compose 1.29.2**


## Installation Steps

- Clone TIM repos into your local machine

```
git \
  -c submodule."ptg-server-ml".update=none \
  clone git@github.com:VIDA-NYU/ptg-api-server.git --recurse-submodules

```

- Set environment variables

```
cd ptg-api-server
cp .env.sample .env
```

- Set NGC branch
```
cd tim-dashboard
git checkout ngc-integration-local
cd ..
```

- Start containers
```
make api dash
```

- You should see the image below by accessing [localhost:3000](localhost:3000)

![ARGUS Interface](https://github.com/VIDA-NYU/PTG-TA2-Parsers/blob/main/argus.png?raw=true)