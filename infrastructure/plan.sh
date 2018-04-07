#!/bin/bash

if [ -z "$ENVIRONMENT" ]; then
    echo "Please set the ENVIRONMENT environment variable."
    exit 1
fi

cd $ENVIRONMENT

terraform plan \
    -var-file ../common.tfvars \
    $@

cd -
