#!/bin/sh

# If any command fails in the bellow script, exit with error
set -e

# Set the name of the folder that will be created in the parent
# folder of your repo folder, and which will temporarily
# hold the generated content.
temp_folder="_gh-pages-temp"
echo $temp_folder

# Make sure our main code runs only if we push the master branch
if [ "$(git rev-parse --symbolic-full-name --abbrev-ref HEAD)" == "master" ]; then
	# Store the last commit message from master branch
	last_message=$(git show -s --format=%s master)

	# Build our Jekyll site
        echo 'starting building'
	jekyll build

	# Move the generated site in our temp folder
	mv _site ../${temp_folder}

	# Checkout the gh-pages branch and clean it's contents
	git checkout gh-pages
	rm -rf *

	# Copy the site content from the temp folder and remove the temp folder
	cp -r ../${temp_folder}/* .
	rm -rf ../${temp_folder}

	# Commit and push our generated site to GitHub
	git add -A
	git commit -m "Built \`$last_message\`"
	git push origin gh-pages

	# Go back to the master branch
	git checkout master
else
	echo "Not master branch. Skipping build"
fi