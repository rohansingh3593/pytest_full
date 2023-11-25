#!/bin/bash

set -e
#!/bin/bash

VALID_ARGS=$(getopt -o dm:e:h --long debug,mark:,extra:,help -- "$@")
if [[ $? -ne 0 ]]; then
    exit 1;
fi

eval set -- "$VALID_ARGS"

while [ : ]; do
   case "$1" in
      -d | --debug )
         set -x
         ;;
      -m | --mark )
         PYTEST_MARK="$2"
         shift 2
         ;;
      -e | --extra )
         PYTEST_EXTRA="$2"
         shift 2
         ;;
      -h | --help)
         echo "This script executes pytest (in the pytest venv) on pipeline builds.  The minimum parameters are -m."
         echo "              usually the artifacts directory from a AppServe pipeline build"
         echo " --mark       pytest marks (the -m pytest option, and passed directly to pytest)"
         echo " --extra      extra pytest options added to pytest command"
         exit 2
         ;;
      --)
         shift;
         break
         ;;
      *)
         echo "Unexpected option: $1"
         exit 1
         ;;
   esac

done

WORKDIR=$(pwd)
echo "Activate pytest venv"

env

SYSTEM_JOBTIMEOUT=${SYSTEM_JOBTIMEOUT:-20}

# Artifact directory contains the build results for the pipeline.
# We generally favor TargetDebug, but would allow any build target
CODE_COVERAGE=false
if [ -d ${ARTIFACT_DIR}/TargetCC/FinalPackage ]; then
   CODE_COVERAGE=true
   echo "Code coverage detected, Selecting"
   ARTIFACT_FINAL=${ARTIFACT_DIR}/TargetCC/FinalPackage
   export PYTEST_GCOV_DIR=`pwd`/gcov_data
   mkdir $PYTEST_GCOV_DIR
elif [ -d ${ARTIFACT_DIR}/TargetDebug/FinalPackage ]; then
   ARTIFACT_FINAL=${ARTIFACT_DIR}/TargetDebug/FinalPackage
else
   ARTIFACT_FINAL=${ARTIFACT_DIR}/TargetRelease/FinalPackage
fi
echo "Artifacts selected at ${ARTIFACT_FINAL}"

OUTPUT_DIR=$BUILD_ARTIFACTSTAGINGDIRECTORY

cd pytest-VGS-venv
./mkvenv
set +e
source pytest-python3.8/bin/activate
set -e

echo "run test, show trace and trace1"
cd $WORKDIR
pip install -r requirements.txt


fail=false
if [ "$SYSTEM_ACCESSTOKEN" == "" ]; then
   echo "PIPELINE or developer must set the SYSTEM_ACCESSTOKEN environment variable before using this script"
   fail=true
fi

if [ "$PYTEST_TEST_PLAN_ID" == "" ]; then
   echo "PIPELINE or developer must set the PYTEST_TEST_PLAN_ID environment variable before using this script"
   echo " for vgs use: 'export PYTEST_TEST_PLAN_ID=2901'"
   fail=true
fi

# use proxy for pipeline
# if [ "$AGENT_NAME" != "vm-use-diapp-kg" ]; then
#    PROXY=http://10.144.148.5
#    export HTTP_PROXY=$PROXY:3128
#    export HTTPS_PROXY=$PROXY:3128
#    export http_proxy=$PROXY:3128
#    export https_proxy=$PROXY:3128
# fi

if [ $fail == true ]; then
   exit 1
fi

DIR=$WORKDIR/output_artifacts/
if [ ! -d "$DIR" ]; then
   mkdir output_artifacts
fi

if [ "${PYTEST_LOG_LEVEL}" == "" ]; then
   PYTEST_LOG_LEVEL=INFO
fi

BUILD_JSON=$OUTPUT_DIR/vgs_info.json
# VGS_Test/Scripts/pipeline_info.py
./Scripts/pipeline_info.py --output $BUILD_JSON

CMD=$(cat <<EOF
pytest -v -vl --log-cli-level ${PYTEST_LOG_LEVEL} -m "${PYTEST_MARK}" ${PYTEST_EXTRA} \
   --html="$OUTPUT_DIR/report.html"  --self-contained-html \
   --artifact-output-dir=${OUTPUT_DIR} \
   --log-cli-format="##[%(levelname)s] %(processName)-.20s %(reltime)s %(asctime)s (%(filename)30s:%(lineno)-3s) %(message)s" \
   --log-cli-date-format="%Y-%m-%d %H:%M:%S" \
   --durations=0 \
   test
EOF
)
set +e
echo $CMD
eval $CMD
PYTEST_RET=$?
set -e

# create GCOV report
GCOV_DATA=${ARTIFACT_FINAL}/VGS-gcov.tar.gz
if [ ! -f $GCOV_DATA ]; then
   GCOV_DATA=${ARTIFACT_FINAL}/../VGS-gcov.tar.gz
fi

# create tarball of test results (WARNING: AzureDevOps does not like test file names)
#tar cf ${OUTPUT_DIR}/tests.tar.gz -C ${OUTPUT_DIR} $(pwd)/tests
#rm -rf ${OUTPUT_DIR}/tests

if [ false == true ]; then
   pip install gcovr
   COUNT=1
   COLLATE=`ls ${ARTIFACT_FINAL}/*-VGS-collect.tar.gz`
   wget  http://museplatform.itron.com/MUSE/release_MUSE_7_0/Phase1Build/Stable/Toolchain-armv7l-gcc5.3-common/toolchain-armv7l-timesys-linux-uclibcgnueabi.tar.xz
   tar xf toolchain-armv7l-timesys-linux-uclibcgnueabi.tar.xz
   OPTS="--gcov-executable `pwd`/bin/armv7l-timesys-linux-uclibcgnueabi-gcov"

   # extract the build source repo (Should be DI.AppServices) source code for the report
   SOURCE_HASH=`jq -r .source_version $BUILD_JSON`
   SOURCE_REPO=`jq -r .repository.url $BUILD_JSON`

   mkdir -p VGS_Automation_and_COE_Testing Team/VGS/Workspace
   cd VGS_Automation_and_COE_Testing Team/VGS/Workspace
   git clone $SOURCE_REPO TargetCC
   cd TargetCC
   git checkout $SOURCE_HASH
   cd $WORKDIR

   for TARBALL in $COLLATE
   do
      GCOV_DIR=$OUTPUT_DIR/gcov-collect-$COUNT
      GCOV_RUN=$OUTPUT_DIR/run-$COUNT.json
      COUNT=$((COUNT+1))
      mkdir -p $GCOV_DIR/VGS_Automation_and_COE_Testing Team/VGS/Workspace/TargetCC/Workspace/TargetCC
      # get gcda files
      tar xmvf $TARBALL  --no-same-owner --no-same-permissions -C $GCOV_DIR .
      # get gcno files
      tar xmf $GCOV_DATA --no-same-owner --no-same-permissions -C $GCOV_DIR/VGS_Automation_and_COE_Testing Team/VGS/Workspace/TargetCC/Workspace/TargetCC

      cd $GCOV_DIR
      # create coverage data for specific run
      gcovr -r `pwd` $OPTS --json $GCOV_RUN
      #rm -rf gcov_data
      cd $WORKDIR
   done

   # merge all results into one report
   gcovr -r `pwd` $OPTS --add-tracefile "$OUTPUT_DIR/run-*.json" --html-details "$OUTPUT_DIR/coverage.html"
   gcovr -r `pwd` $OPTS --add-tracefile "$OUTPUT_DIR/run-*.json" --xml-pretty -o "$OUTPUT_DIR/Cobertura.xml"
fi

exit $PYTEST_RET
#scripts/ads_push_results.py