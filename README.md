## Describe edX Course Content Data
[Detail description from edX](http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/course_structure.html#course-structure)

This folder contains code to generate README.md to describe edX course content file exported from edX interface.

### 1. Setup
cd to current directory and run

	source setup.sh

(If you want this setup script to run automatically, add a line to your .bashrc)

### 2. Using makeDoc.py
* Export your course from edX
* Unzip the exported .tar.gz file
* cd into the unzipped folder
* run makeDoc.py

		makeDoc.py
	
* The script will generate a README.md to describe your course content.
