#!/bin/bash

set -x
ScriptDir=$(dirname $0)
${ScriptDir}/mk_pipeline_venv.sh -m "ci_test"
