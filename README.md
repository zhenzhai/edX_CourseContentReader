## Describe edX Course Content Data

This folder contains code to generate README.md to describe edX course content file exported from edX interface.

### 1. Setup
cd to current directory and run

	source setup.sh

(If you want this setup script to run automatically, add a line to your .bashrc)

#### You need to have Python2

### 2. Using makeDoc.py
* Export your course from edX
* Unzip the exported .tar.gz file
* cd into the uncompressed folder
* run makeDoc.py

	makeDoc.py
	
* The script will generate a README.md to describe your course content.
