#!/bin/bash

rm -rf lambda-package
mkdir lambda-package
cd lambda-package

cp -R $VIRTUAL_ENV/lib/python2.7/site-packages/* .
cp ../lambda_function.py .
zip -r ../lambda-package.zip .
