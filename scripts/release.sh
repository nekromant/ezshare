#!/bin/bash

version=`toml get --toml-path pyproject.toml project.version`
nextversion=$(echo ${version} | awk -F. -v OFS=. '{$NF += 1 ; print}')
toml set --toml-path pyproject.toml project.version $nextversion
git add pyproject.toml
git commit -s -m "v${nextversion} release"
git push origin master
python3 -m build
twine check dist/*
twine upload dist/*
