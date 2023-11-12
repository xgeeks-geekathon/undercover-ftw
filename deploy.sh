#!/bin/bash

git pull origin main
./opa build ./bundles/policies.rego -o ./bundles/bundle.tar.gz
