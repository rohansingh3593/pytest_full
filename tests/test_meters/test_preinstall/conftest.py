#!/usr/bin/env python3
"""
This code provides a run-time environment for pre-installed AS tests

The caller can assume that the di-package we provide will be installed when the
preinstalled_meter fixture is used.

The framework also provides gcov setup and harvesting

"""

from tempfile import TemporaryDirectory
import pytest
import logging
from tests.test_meters.utils import ParallelMeterWithDebug, filter_ps
import threading
import multiprocessing
import hashlib
import os
import time
import tarfile
import glob
import re
import requests, zipfile
from itron.meter.Gen5Meter import SSHGen5Meter

LOGGER = logging.getLogger(__name__)
repack_lock = multiprocessing.Lock()
repack_list = {}
templist = {}


# Note, this is defined in the build rules for DI-AppServices
# and can't be changed without changing the gcov directory option
GCOV_TARGET_DIR = "/mnt/common/DI-AppServices-gcov"
def get_path(func):
     if type(func).__name__ == 'function' :
         return func.__code__.co_filename
     else:
         raise ValueError("'func' must be a function")


def pid_of_dataserver(meter : SSHGen5Meter) -> int:
    """ Get process ID of dataserver daemon, or None if not running """
    stat = meter.get_process("DataServer_Daemon")
    pid = None
    for line in stat:
        if line[2] == 'dserver_':
            pid = line[0]
            break
    return pid


class TrackGcovData:
    """ this class will record the results of the code coverage.   The
    class is registered as a hook to the parallel class when the meter
    is ready to be released.  This allows code coverage information to be
    accumulated from all of the tests from this meter, then added to the
    output
    """
    def __init__(self, di_artifacts, meter, session_dir, logger, artifact_output_dir):
        self.di_artifacts = di_artifacts
        self.meter = meter
        self.session_dir = session_dir
        self.logger = logger
        self.artifact_output_dir = artifact_output_dir

    def __del__(self):
        self.logger.info("Note: TrackGcovData collector was deleted")

    def collect(self, meter_ip, logger, session_dir):
        """! collect gcov data in a tarball then
             download to the host

            this is called by the parallel plugin when the
            meter is no longer going to be used
        """
        logger.info("Collecting gcov results from meter")
        with ParallelMeterWithDebug(meter_ip,logger) as meter_context:
            logger.info("creating tarball of gcov data")
            # stop and restart dataserver, this will flush it's coverage information

            pid = pid_of_dataserver(meter_context)
            if pid:
                # terminate dataserver so we can collect the gcov data
                meter_context.command(f'kill -2 {pid}')
                end_time = time.time() + 120 # wait 2 minutes maximum for DataServer to stop
                while pid and end_time > time.time():
                    logger.info(f"wait for dataserver to die")
                    time.sleep(5)
                    pid = pid_of_dataserver(meter_context)
                # NOTE: it is possible that monit re-starts dataserver after it dies
                # if this happens, then maybe we just remove this assert
                assert pid is None, "Could not kill DataServer in order to collect gcov results.  "
            output = meter_context.command('monit start dataserv')

            # Collect the gcov data generated by DataServer_Daemon from meter
            logger.info(f"tar czf /tmp/DI-AppServices-collect.tar.gz -C {GCOV_TARGET_DIR} .")
            code, data = meter_context.command_with_code(f"tar czf /tmp/DI-AppServices-collect.tar.gz -C {GCOV_TARGET_DIR} .",timeout=120)
            assert code == 0
            logger.debug(data)
            outdir = os.path.join(session_dir, meter_context.meter_name)
            os.makedirs(outdir,exist_ok=True)
            outfile = os.path.join(outdir,  "DI-AppServices-collect.tar.gz")
            logger.info("downloading tarball of gcov data to %s", outfile)
            meter_context.get_file(f"/tmp/DI-AppServices-collect.tar.gz", outfile)
            meter_context.command("rm -f /tmp/DI-AppServices-collect.tar.gz")

            if self.artifact_output_dir:
                target = os.path.join(self.artifact_output_dir, f'{str(meter_ip)}-DI-AppServices-collect.tar.gz')
                rel_src = os.path.relpath(outfile, os.path.dirname(target))
                logger.info("linking %s to %s tarball of gcov data", rel_src, target)
                try:
                    os.symlink(rel_src, target)
                except FileExistsError:
                    logging.warning("Output file %s exists, deleting", target)
                    os.unlink(target)
                    os.symlink(rel_src, target)

    def on_exit_callback(self, meter):
        """! this function is called when the parallel
        plugin is about release the meter (via the register_exit_handler)
        """
        self.collect(meter, self.logger, self.session_dir)

    def deploy_gcov_data(self, meter_context, gcov_data, logger):
        """! gcov requires that a directory already be created with correct access

        We deploy the .gcno and .o files to thee meter (mostly to create the directory
        structure needed for DataServer_Daemon and libs to store the coverage data
        """

        logger.trace("Deploy gcov context directory %s to meter", GCOV_TARGET_DIR)

        # TargetCC has this directory baked in, so this can't change
        meter_context.command(f"rm -rf {GCOV_TARGET_DIR}")
        meter_context.command(f"mkdir -m 777 -p {GCOV_TARGET_DIR}")

        # extract tarball to tempdir to get directory structure and build
        # directory structure on meter
        with TemporaryDirectory() as tmpdir:
            logger.info("extracting %s to %s", gcov_data, tmpdir)
            with tarfile.open(name=gcov_data,mode='r:gz') as t:
                t.extractall(tmpdir)
            logger.info("enumerating directory %s", tmpdir)
            all_dirs = []
            # sadly, the staging directory can have a infinite recurse link in it
            for root, dirs, files in os.walk(tmpdir, topdown=False, followlinks=False):
                for name in dirs:
                    p = os.path.join(root, name)
                    all_dirs.append(p)
            #git
            #files = glob.glob(os.path.join(tmpdir, "**/"), recursive=True, )
            logger.info("Creating directory structure on meter for %s directories", len(dirs))

            # make this faster by doing groups of 10
            cache = []
            cmd = f"mkdir -m 777 -p "
            count = 0
            for file in all_dirs:
                if os.path.isdir(file) and not os.path.islink(file):
                    dir = os.path.join(GCOV_TARGET_DIR, os.path.relpath(file, tmpdir))
                    cmd = cmd + " " + dir
                    count += 1
                    # do 10 at a time
                    if count > 10:
                        cache.append(cmd)
                        count = 0
                        cmd = f"mkdir -m 777 -p "
            if count:
                cache.append(cmd)

            for cmd in cache:
                try:
                    logger.info(cmd)
                    code,_ = meter_context.command_with_code(cmd)
                    if code != 0:
                        logger.error("Error %s creating directory %s on meter", code, cmd)
                except Exception as e:
                    logger.exception("Error creating dirpath %s", dir)

        meter_context.command(f"chmod a+rw -R {GCOV_TARGET_DIR}")

def get_gcov_build_data(di_artifacts):
    gcov_data = os.path.join(di_artifacts, 'DI-AppServices-gcov.tar.gz')
    if not os.path.exists(gcov_data):
        gcov_data = os.path.join(di_artifacts,'..', 'DI-AppServices-gcov.tar.gz')
    if os.path.exists(gcov_data):
        return gcov_data
    return None

def hook_gcov_data(di_artifacts, meter_context, session_dir, meter_exit_handler, logger, artifact_output_dir):
    gcov_data = get_gcov_build_data(di_artifacts)
    if gcov_data:
        logger.info("Using existing gcov data.  Hooking meter cleanup")
        context = TrackGcovData(di_artifacts, meter_context.meter_name, session_dir, logger, artifact_output_dir)

        # register with parallel plugin to collect the results before releasing the meter
        meter_exit_handler.register_exit_handler_by_name('gcov_context',context.on_exit_callback)

def deploy_gcov_data(di_artifacts, meter_context, session_dir, meter_exit_handler, logger, artifact_output_dir):
    # for pipeline builds this file is up one level.  For developer builds, it is in the
    # package directory.  So check both places
    gcov_data = get_gcov_build_data(di_artifacts)
    if gcov_data:
        logger.info("Deploying gcov tarball to meter")
        context = TrackGcovData(di_artifacts, meter_context.meter_name, session_dir, logger, artifact_output_dir)
        context.deploy_gcov_data(meter_context, gcov_data, logger)

        # register with parallel plugin to collect the results before releasing the meter
        meter_exit_handler.register_exit_handler_by_name('gcov_context',context.on_exit_callback)


@pytest.fixture(scope='function')
def preinstalled_meter(meter, logger, appserve_artifacts, meter_exit_handler) -> ParallelMeterWithDebug:
    """! sets up a pre-installed meter

    This fixture will install the correct version if AppServices, then it will register with the meter_exit_handler to
    perform data harvesting after all tests have been run on the meter.  This includes extracting meter log files,
    harvesting gcov data and other important data.

    This will fixture will be called for each thread/meter pair
    """
    logger.debug("DI Package: %s - Meter %s", appserve_artifacts.di_package, meter)
    if meter:
        with ParallelMeterWithDebug(meter,logger) as meter_context:

            install_appserve(meter_context, logger, appserve_artifacts, meter_exit_handler)
            verify_appserve(meter_context, logger)

            yield meter_context
            logging.info("Preinstalled meter finished: %s", meter)


def verify_appserve(meter_context, logger):
    """ function to verify that appserve is runing """
    timeout = time.time() + 60

    # wait for dataserver to start, if it doesn't start after 1 minute, then
    # someone probably killed it.
    while time.time() < timeout:
        ds = filter_ps(meter_context, "DataServer_Daemon")
        logger.trace("DataServer process: %s", ds)
        if not ds or not re.search("DataServer_Daemon", ds[0][4]):
            time.sleep(10)
        else:
            break

    # fourth column of ps is dataserver and args, check for no-hash option
    if not ds or not re.search("DataServer_Daemon", ds[0][4]):
        # now stop dataserver and re-start it in no-hash mode
        logging.warning("DataServer was not running when expected to be.  Re-Starting")
        out = meter_context.command("monit start DataServer")



def install_appserve(meter_context, logger, appserve_artifacts, meter_exit_handler):
    """ function to validate appserve is correctly installed on the DUT """
    fwver, asver = meter_context.version_info()
    logger.debug("FW version: %s", fwver)
    logger.debug("DI Version: %s", asver)
    logger.info("DI Version: %s package version: %s", asver, appserve_artifacts.di_version)

    tbl = meter_context.get_table("FWINFORMATION")
    found=None
    hash=None
    for item in tbl:
        if re.search("appservicesLR",item['PATH']):
            found=item
    if not found:
        print('AS Hash: not found')
    else:
        hash = found['UNSIGNEDHASH']
        logging.info("AS hash on meter: %s", hash)

    if appserve_artifacts.di_version != asver or appserve_artifacts.di_package_sha != hash:
        deploy_gcov_data(appserve_artifacts.di_artifacts, meter_context, appserve_artifacts.session_dir,
            meter_exit_handler, logger, appserve_artifacts.artifact_output_dir)

        logger.trace("Installing DI Package %s (curver: %s)",appserve_artifacts.di_package, asver)
        meter_context.install(file=appserve_artifacts.di_package)
    else:
        hook_gcov_data(appserve_artifacts.di_artifacts, meter_context, appserve_artifacts.session_dir,
            meter_exit_handler, logger, appserve_artifacts.artifact_output_dir)

    # make sure appserve is running (some tests kill it)



