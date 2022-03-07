#!/bin/bash

export GRAFANA='flashcat'
export BINARY_PREFIX='fc-'
export RELEASE_TAG='fc-v0.1.0'

make dist
