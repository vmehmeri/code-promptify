# First, commit code changes, then run: 
bumpversion minor
rm -rf dist build *.egg-info
python setup.py sdist bdist_wheel
twine upload dist/*
