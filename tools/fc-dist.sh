#!/bin/bash

export GRAFANA='flashcat'
export BINARY_PREFIX='fc-'
export RELEASE_TAG='v1.0.0-rc1'

make dist
#make agent-image
