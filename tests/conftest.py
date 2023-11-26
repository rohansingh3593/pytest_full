#!/usr/bin/env python3
# content of conftest.py

import pytest
import os
import git
import logging
import glob
import re
import  datetime

import json
import zipfile
import tarfile
from itron.meter.FwMan import decrypt
import hashlib
from itron.meter.Gen5Meter import SSHGen5Meter
from tests.utils import LockFile

import subprocess
import modulefinder
import  concurrent.futures
import threading
import traceback
import time
import shutil

LOGGER = logging.getLogger(__name__)

def pytest_addoption(parser):
    parser.addoption(
        "--di-artifacts", action="store", default="artifacts/bionic-x86_64/TargetDebug/FinalPackage", help="DI AppServices Package directory"
    )
    parser.addoption(
        "--di-artifacts2k", action="store", default=None, help="DI AppServices Package directory"
    )
    parser.addoption(
        "--artifact-output-dir", action="store", default=None, help="location to store artifacts"
    )
    parser.addoption(
        "--gmr-meters", action="store_true", default=False, help="gmr meter before use"
    )
    parser.addoption(
        "--coldstart", action="store_true", default=False, help="coldstart meter to fw version before use"
    )
    parser.addoption(
        "--fix-fw", action="store_true", default=False, help="if fw version not correct, then coldstart meter"
    )
    parser.addoption(
        "--fw-ver", action="store", default="10.5.787.1", help="fw version required on meter"
    )
    parser.addoption(
        "--mark-changed", action="store_true", default=False, help="mark changed files (from fork in git) with 'changed'"
    )

def add_if_not_disabled(item):
    for mark in item.own_markers:
        if mark.name == "disable_changed":
            return False
    item.add_marker("changed")
    return True

def find_changed(items):

    ret = subprocess.run('git merge-base --fork-point origin/master'.split(), capture_output=True)
    # for already merged PRs, this can return up to date (1). in this case we can use
    # merge-base -a to get the immediate merge parent
    if ret.returncode == 1:
        print('fork-point shows nothing, probably already merged to head: ', str(ret))
        ret = subprocess.run('git merge-base -a origin/master HEAD'.split(), capture_output=True)
        print('Second try: ', str(ret))

    assert ret.returncode == 0, "Error checking git for changes"

    fork_point = ret.stdout.decode('utf-8').splitlines()
    assert len(fork_point) == 1 # not sure what to do for this case
    fork_point = fork_point[0]


    ret = subprocess.run(f'git diff --name-only --relative --diff-filter AMR {fork_point} --name-only -- tests'.split(), capture_output=True)
    if ret.returncode:
        print('Git function failed: ', str(ret))
    assert ret.returncode == 0, "Error checking git for changes"
    changed_files = ret.stdout.decode('utf-8').splitlines()

    print("Changes from git for this branch:")
    for change in changed_files:
        print(change)
    print("End of source code changes.  Scanning for dependencies")

    changed=[]
    others=[]
    for x in changed_files:
        if os.path.basename(x).startswith("test_"):
            changed.append(x)
        else: # os.path.basename(x) == 'conftest.py':
            others.append(x)

    # for tests, simply iterate through the cases and mark them
    for file in changed:
        for item in items:
            if item.fspath.samefile(file):
                if add_if_not_disabled(item):
                    print("--mark-changed flagged %s" % (item.nodeid))


    lock = threading.Lock()

    def process_item(lock, item):

        tfile = item.fspath.strpath
        try:
            mf = modulefinder.ModuleFinder()
            mf.run_script(tfile)
            for name, mod in mf.modules.items():
                path = mod.__file__
                if path: # built in modules have no path
                    for touched in others:
                        if os.path.samefile(path, touched):
                            with lock:
                                if add_if_not_disabled(item):
                                    print("--mark-changed flagged %s due to %s,  %s module dependency " % (item.nodeid, name, os.path.relpath(mod.__file__, os.getcwd())))
                                else:
                                    print("skipping disabled %s due to %s,  %s module dependency " % (item.nodeid, name, os.path.relpath(mod.__file__, os.getcwd())))


        except KeyboardInterrupt:
            raise
        except BaseException as e:
            with lock:
                print("\033[93mWARNING: \033[0m Exception processing dependencies for %s, usually this is due to missing __init__.py for an imported module. see. https://bugs.python.org/issue40350" % (item.nodeid))
                print("--mark-changed flagged %s due to inability to process file" % (item.nodeid) )
                traceback.print_exc()
                s = str(e)
                print(s)

    # TODO: sadly, the modulefinder is not thread safe. Something in the caching throws key index errors
    # so there must be a dictionary that needs syncronization locks
    if False:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            futures = []
            for item in items:
                future = executor.submit(process_item, lock, item)
                futures.append(future)
            count = 0
            for future in concurrent.futures.as_completed(futures):
                with lock:
                    print("find changes progress: %.2f%%   \r" % (float(count)/float(len(items))*100) )
                    count += 1
    else:
        for item in items:
            process_item(lock, item)

@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(session, config, items):
    """ The purpose of this function is to mark test cases with the "changed" mark if they have changed
        from the branch head.  This allows running only tests that have changed or are only part of the
        branch.  This is registered as first, so later item checking can see the "changed" mark.
        This feature must be enabled by using "-m changed --mark-changed" or an equivalent option
        """

    if config.getoption("--mark-changed"):
        cache = "mark-changed-cache.json"
        if os.path.exists(cache):
            with open(cache,"r") as f:
                changed = json.load(fp=f)

            for item in items:
                if item.nodeid in changed:
                    changed.remove(item.nodeid)
                    add_if_not_disabled(item)

            assert not changed, "items that were changed are not in the item list"

        else:
            find_changed(items)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield

    if call.when == 'call':
        if call.excinfo is not None:
            # if excinfor is not None, indicate that this test item is failed test case
            logging.error("Test Case: {}.{} Failed.".format(item.location[0], item.location[2]))
            logging.error("Error: \n{}".format(call.excinfo))

    return outcome

@pytest.fixture(scope='session')
def di_artifacts(request):
    return request.config.getoption("--di-artifacts")

@pytest.fixture(scope='session')
def di_artifacts_2k(request):
    path = request.config.getoption("--di-artifacts2k")
    if path is None:
        path = request.config.getoption("--di-artifacts")
        match = re.search("/Target(Debug|Release|CC)(/|$)",path)
        if match:
            ver = match.group(1) if match.group(1) != "CC" else "Debug"
            path = path.replace(match.group(0), f"/Target{ver}2K{match.group(2)}")
        else:
            LOGGER.error("--di-artifacts2k was not specified, and can't figure out how to find it")
    return path


@pytest.fixture(scope='session')
def artifact_output_dir(request):
    dir = request.config.getoption("--artifact-output-dir")
    if not dir:
        dir = request.session.fspath
    return dir

# start time of session

# need to allocate this before pytest parallel plugin starts up and forks processes, so here goes
session_lock = LockFile("pytest_session.lock", LOGGER)

"""
CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
TRACE=25
TRACE1=24
TRACE2=23
TRACE3=22
TRACE4=21
INFO = 20
DEBUG = 10
NOTSET = 0
"""
# show trace warnings errors, etc.  limit output to Major areas
LOG_TRACE=25
logging.addLevelName(LOG_TRACE, "TRACE")
def log_trace(self, message, *args, **kws):
    if self.isEnabledFor(LOG_TRACE):
        self._log(LOG_TRACE, message, args, **kws)
logging.Logger.trace = log_trace

# show slightly more information (limit use to Minor areas)
LOG_TRACE1=24
logging.addLevelName(LOG_TRACE1, "TRACE1")
def log_trace1(self, message, *args, **kws):
    if self.isEnabledFor(LOG_TRACE):
        self._log(LOG_TRACE, message, args, **kws)
logging.Logger.trace1 = log_trace1

LOG_TRACE2=23
logging.addLevelName(LOG_TRACE2, "TRACE2")
def log_trace2(self, message, *args, **kws):
    if self.isEnabledFor(LOG_TRACE):
        self._log(LOG_TRACE, message, args, **kws)
logging.Logger.trace2 = log_trace2

LOG_TRACE3=22
logging.addLevelName(LOG_TRACE3, "TRACE3")
def log_trace3(self, message, *args, **kws):
    if self.isEnabledFor(LOG_TRACE):
        self._log(LOG_TRACE, message, args, **kws)
logging.Logger.trace3 = log_trace3

LOG_TRACE4=21
logging.addLevelName(LOG_TRACE4, "TRACE4")
def log_trace4(self, message, *args, **kws):
    if self.isEnabledFor(LOG_TRACE):
        self._log(LOG_TRACE, message, args, **kws)
logging.Logger.trace4 = log_trace4

###  Add reltime format to messages,  this requires modifying the base class of the logger,
###  as the logger does not provide any extensibility
def monkeypatched_format(self, record):
    relsec = record.relativeCreated/1000
    relmin = relsec / 60
    relsec =(relmin - int(relmin)) * 60
    record.reltime = "{0:3d}m {1:6.3f}s ".format(int(relmin),relsec)
    return self.old_format(record)

# fix new formatters
logging.Formatter.old_format = logging.Formatter.format
logging.Formatter.format = monkeypatched_format

# patch existing handlers
loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
for log in loggers:
    for handler in log.handlers:
        handler.old_format = handler.format
        handler.format = monkeypatched_format

@pytest.hookimpl
def pytest_configure(config):
    logging_plugin = config.pluginmanager.get_plugin("logging-plugin")

    # Change color on existing log level
    if logging_plugin and logging_plugin.log_cli_handler:
        logging_plugin.log_cli_handler.formatter.add_color_level(LOG_TRACE, "cyan")

class ContextAdapter(logging.LoggerAdapter):
    def process(self,msg,kwargs):
        return '(%s) %s' % (self.extra['meter'],msg)  ,kwargs
    def trace(self, msg, *args, **kwargs):
        self.log(LOG_TRACE, msg, *args, **kwargs)
    def trace1(self, msg, *args, **kwargs):
        self.log(LOG_TRACE1, msg, *args, **kwargs)
    def trace2(self, msg, *args, **kwargs):
        self.log(LOG_TRACE2, msg, *args, **kwargs)
    def trace3(self, msg, *args, **kwargs):
        self.log(LOG_TRACE3, msg, *args, **kwargs)
    def trace4(self, msg, *args, **kwargs):
        self.log(LOG_TRACE4, msg, *args, **kwargs)

@pytest.fixture(scope='session')
def session_name(worker_id):
    if ('PYTEST_XDIST_METER_TARGET' in os.environ):
        name = os.environ["PYTEST_XDIST_METER_TARGET"]
    else:
        name = worker_id
    return name

def create_logger(request, logname, session_name):
    log = logging.getLogger('test_logger')
    fileh = logging.FileHandler(logname)
    format = request.config.getini("log_file_format")
    level = request.config.getini("log_file_level")
    if level:
        level = logging.getLevelName(level.upper()) if not level.isnumeric() else int(level)
        logging.getLogger().setLevel(level)

    if format:
        formatter = logging.Formatter(format)
        fileh.setFormatter(formatter)

    log.addHandler(fileh)

    log2 = ContextAdapter(log, extra={'meter': session_name})
    return log2, fileh

@pytest.fixture(autouse=True, scope='session')
def session_logger(request, session_dir, session_name):
    logname=os.path.join(session_dir, f"worker-{session_name}.log")
    log2,fileh = create_logger(request, logname, session_name)
    yield log2
    log2.logger.removeHandler(fileh)

@pytest.fixture(autouse=True,scope='function')
def logger(logname, request, session_name):
    log = session_logger
    log2,fileh = create_logger(request, logname, session_name)
    log2.trace("===============================Starting test %s", request.node.nodeid)

    yield log2
    log2.trace("===============================Ending test")
    log2.logger.removeHandler(fileh)

@pytest.hookimpl(trylast=True)
def pytest_exception_interact(node, call, report):
    log = logging.getLogger('test_logger')
    name = node.nodeid
    info = call.excinfo.getrepr(showlocals=True, style='long', abspath=False, tbfilter=True, funcargs=True, truncate_locals=True, chain=True)
    info = str(info)
    log.exception("Exception during %s(%s): %s", call.when, name, info)
    return report

@pytest.fixture(autouse=True,scope='module')
def module_logger(session_dir, request, session_name):
    module_name = request.module.__name__
    modulelog = os.path.join(session_dir, f"module_{module_name}.log")
    log2,fileh = create_logger(request, modulelog, session_name)
    log2.trace("===============================Starting module %s", module_name)

    yield log2
    log2.trace("===============================Ending module")
    log2.logger.removeHandler(fileh)

@pytest.fixture(scope='function')
def testname(request):
    return request.node.nodeid.replace('/','.')

@pytest.fixture(autouse=True,scope='function')
def logname(workdir):
    return os.path.join(workdir,f"results.log")

@pytest.fixture(scope='session')
def global_session_data(testrun_uid, worker_id, tmp_path_factory):
    """ this fixture provides a global session file that can share information
        betweeen workers.  Must be accessed with a session_lock. """

    # put stuff here that can be shared between every worker
    shared_singleton_data = {
        "session_date": time.time()
    }
    root_tmp_dir = tmp_path_factory.getbasetemp().parent
    fn = root_tmp_dir / "session_share.json"
    if worker_id == "master":
        json.dump(shared_singleton_data, fn)
    else:
        with session_lock:
            # if file already created, we are done
            if not fn.is_file():
                with open(fn,'w') as fp:
                    json.dump(shared_singleton_data, fp)
    return fn

@pytest.fixture(scope='session')
def session_date(global_session_data):

    with session_lock:
        with open(global_session_data, "r") as fp:
            shared = json.load(fp)
        session_start = datetime.datetime.fromtimestamp(shared['session_date'])

    strdate = session_start.strftime("%Y-%m-%d_%H_%M_%S")
    return strdate

@pytest.fixture(scope='session')
def session_dir(session_date,request):
    log_dir = request.config.getoption("--artifact-output-dir")
    if not log_dir:
        log_dir = os.path.join(request.session.fspath, f"session-{session_date}")
    os.makedirs(log_dir,exist_ok = True)
    return log_dir

@pytest.fixture(scope='session')
def autorun_file(request, session_dir):
    directory = []
    yield directory

    for index in range(len(directory)):
        if '&' in directory[index]:
            directory[index] = directory[index].split('&')[0]

    with session_lock:
        count = 0
        for count in range(0,100):
            filename = os.path.join(session_dir, f"replay_{count}.sh")
            if not os.path.exists(filename):
                break
        with open(filename, 'w') as f:
            seps='\\\n    '
            f.write(f"""
#!/bin/bash

scriptdir=$(dirname,$0)
cd $scriptdir/{os.path.relpath(os.path.curdir, session_dir)}
mypy \
    {seps.join(directory)}
""")

@pytest.fixture(scope='function', autouse=True)
def replay(request, autorun_file):
    test_name = request.node.nodeid
    autorun_file.append(test_name)

@pytest.fixture(scope='function')
def workdir(request, testname, session_date, session_dir):
    sanitized_name = testname
    for x in ":[{}]":
        sanitized_name = sanitized_name.replace(x, '-')
    sanitized_name = ''.join(x for x in sanitized_name if x.isalnum() or x in "._- ")
    dir = os.path.join(session_dir, f"workdir-{sanitized_name}")
    LOGGER.info("Workdir: %s", dir)
    os.makedirs(dir,exist_ok = True)
    return dir

@pytest.fixture(scope='session')
def cache_dir(request):
    dir = os.path.join(os.getcwd(), "session_cache")
    LOGGER.info("cachedir: %s", dir)
    os.makedirs(dir,exist_ok = True)
    return dir

def get_gittop():
    repo = git.Repo('.', search_parent_directories=True)
    GITTOP=repo.working_tree_dir
    LOGGER.info("GitTOP: %s",GITTOP)
    return GITTOP

@pytest.fixture(scope='session')
def gittop():
    return get_gittop()

@pytest.fixture(scope='session')
def di_version(di_package):
    m=re.search("Package-([0123456789.]+)_", di_package)
    return m.group(1)

@pytest.fixture(scope='session')
def di_version_2k(di_package_2k):
    m=re.search("Package-([0123456789.]+)_", di_package_2k)
    return m.group(1)

@pytest.fixture(scope='session')
def di_package(di_artifacts):
    dir = os.path.join(di_artifacts,'DI-AppServices-Package-*.zip')
    files = glob.glob(dir)
    assert len(files) > 0, "DI-AppServices-Package-*.zip file missing.  Did you forget to specify --di-artifacts option?"
    assert len(files) == 1, "too many DI-AppServices-Package-*.zip files.  You need to clean the artifacts from prior builds."
    package=files[0]
    LOGGER.info("DI Package: %s", package)
    return package

@pytest.fixture(scope='session')
def di_package_2k(di_artifacts_2k):
    dir = os.path.join(di_artifacts_2k,'DI-AppServices-Package-*.zip')
    files = glob.glob(dir)
    assert len(files) > 0, "DI-AppServices-Package-*.zip file missing.  Did you forget to specify --di-artifacts option?"
    assert len(files) == 1, "too many DI-AppServices-Package-*.zip files.  You need to clean the artifacts from prior builds."
    package=files[0]
    LOGGER.info("DI 2K Package: %s", package)

    return package

def sync_meter_time(meter,logger, info, offset=datetime.timedelta(seconds=0)):
    """ testing sometimes changes the meter time.  This function
        syncronizes the time from pytest to the meter

        @param: offset integer difference requested for meter
        """
    def get_diff(meter, offset):
        remote_time = int(meter.command("date -u '+%s'")[0])
        cur = time.time()
        diff = remote_time - offset - cur
        return diff

    diff = get_diff(meter,offset.total_seconds())
    info["pretest_time_diff"] = diff

    if abs(diff) > 60:
        now = datetime.datetime.now(tz=datetime.timezone.utc) + offset
        correct = datetime.datetime.strftime(now, "%Y.%m.%d-%H:%M:%S")
        cmd = f"date -u -s {correct};/sbin/hwclock -w"
        res = meter.command(cmd)
        logger.warning("Time on meter updated: %s", cmd)
        diff = get_diff(meter,offset.total_seconds())
        assert abs(diff) < 60

    info["sync_time_diff"] = diff

@pytest.fixture(scope='session')
def fw_ver(request):
    fw_ver=request.config.getoption("--fw-ver")
    return fw_ver


def init_meter(request, meter, session_dir, appserve_artifacts, logger, fw_ver):
    """ This function is called once per meter when the regression test starts
        and will ensure that the meter has the correct version of firmware,
        correct time and is in a nominal state at the start of testing

    """
    init_log = os.path.join(session_dir, f'meter_{meter}_init_state.json')
    if not os.path.exists(init_log):
        os.makedirs(session_dir, exist_ok=True)
        with SSHGen5Meter(meter, logger) as meter_context:
            fwver, asver = meter_context.version_info()
            js = {
                "pretest_fw_ver": fwver, "pretest_as_ver": asver,
                "test_version": dict((key, str(value)) for key, value in appserve_artifacts.__dict__.items()
                                     if not callable(value) and not key.startswith('__')),
                "options": dict((key, str(value)) for key, value in request.config.option.__dict__.items()
                                if not callable(value) and not key.startswith('__')),
            }
            sync_meter_time(meter_context, logger, js)
            with open(init_log, "w") as f:
                json.dump(js, f)

            if (request.config.getoption("--gmr-meters")):
                logger.trace("GMR Meter %s before use", meter)
                meter_context.gmr()
            coldstart_fw = request.config.getoption("--coldstart")
            if coldstart_fw or (
                fw_ver != fwver and request.config.getoption("--fix-fw")
            ):
                logger.trace("Coldstart Meter %s before use", meter)
                meter_context.coldstart(version=fw_ver)

@pytest.fixture(scope='session')
def meter(request, session_dir, appserve_artifacts, fw_ver):
    # parallel/xdist plugin adds this, so we just need to fetch it
    assert "PYTEST_XDIST_METER_TARGET" in os.environ, "Error, you must specify meters for this test"
    meter = os.environ["PYTEST_XDIST_METER_TARGET"]
    if meter:
        LOGGER.trace("Initializing meter %s", meter)
        init_meter(request, meter, session_dir, appserve_artifacts, LOGGER, fw_ver)
        yield meter
        LOGGER.trace("Finalizing meter %s", meter)
    else:
        LOGGER.error('%s was not idenitfied by itron.plugin.parallel as a meter test, or no meter was specified on the command line.  Use --dut-db or --meters option to run this test',request)

@pytest.fixture(scope='session')
def multi_meter(request, session_dir, appserve_artifacts, fw_ver):
    assert "PYTEST_XDIST_MULTI_METER_TARGET" in os.environ, "Error, you must specify multi-meters for this test"
    multi_meter = os.environ["PYTEST_XDIST_MULTI_METER_TARGET"]
    if multi_meter:
        multi_meter = multi_meter.split(",")
        for meter in multi_meter:
            init_meter(request, meter, session_dir, appserve_artifacts, LOGGER, fw_ver)
        return multi_meter
    LOGGER.error('%s was not idenitfied by itron.plugin.parallel as a meter test, or no meter was specified on the command line.  Use --dut-db or --meters option to run this test',request)

@pytest.fixture(scope='session')
def di_package_sha(decrypted_di_package):
    with session_lock:
        di_manifest = os.path.join(decrypted_di_package, "appservicesLR.manifest")
        with open(di_manifest, "rb") as data:
            data = data.read()
            sha = hashlib.sha256(data)
        return sha.hexdigest()

@pytest.fixture(scope='session')
def di_package_files(decrypted_di_package, di_version, cache_dir):
    """! this fixture provides all the files that would be installed to the meter """
    basedir = os.path.join(cache_dir, f"di_package_files-{di_version}")
    with session_lock:
        if os.path.exists(basedir):
            return basedir

        di_tarball = os.path.join(decrypted_di_package, "DI-AppServices.tar.bz2")
        with tarfile.open(name=di_tarball, mode="r:gz") as tarball:
            tarball.extractall(basedir)

    return basedir

def cache_decrypt(basedir, di_package, logger):
    with session_lock:
        if os.path.exists(basedir):
            logger.trace("Using cached decrypted di package: %s to %s", di_package, basedir)
            return basedir

        try:
            logger.trace("Decrypting DI Package: %s to %s", di_package, basedir)
            encrypted_dir = os.path.join(basedir, "encrypted")
            os.makedirs(encrypted_dir, exist_ok=True)

            with zipfile.ZipFile(di_package) as z:
                z.extractall(encrypted_dir)

            files = glob.glob(os.path.join(encrypted_dir, "*"))
            found = None
            for file in files:
                if file.endswith(".tar.gz"):
                    found = file
            assert found != None

            decrypted_file = decrypt(found, os.path.join(basedir, "decrypted.tar.gz"))
            with tarfile.open(name=decrypted_file,mode="r:gz") as t:
                t.extractall(basedir)
            os.remove(decrypted_file)
        except:
            shutil.rmtree(basedir)
            raise

@pytest.fixture(scope='session')
def decrypted_di_package_2k(di_package_2k, di_version, cache_dir):
    """ Create decrypted package.  This is thread safe
        as many meter sessions will ask for it
        """
    basedir = os.path.join(cache_dir, f"di_decrypted_package_files_2k-{di_version}")
    cache_decrypt(basedir, di_package_2k, LOGGER)

    LOGGER.info("DI Package 2k: %s", basedir)
    return basedir


@pytest.fixture(scope='session')
def di_package_image_files_2k(decrypted_di_package_2k,di_version_2k):
    """! this fixture provides all the files that would be installed to the meter """
    di_tarball = os.path.join(decrypted_di_package_2k, f"encrypted/DI-AppServices-Package-{di_version_2k}.tar.gz")
    return di_tarball

@pytest.fixture(scope='session')
def decrypted_di_package(di_package, di_version, cache_dir):
    """ Create decrypted package.  This is thread safe
        as many meter sessions will ask for it
        """
    basedir = os.path.join(cache_dir, f"di_decrypted_package_files-{di_version}")

    cache_decrypt(basedir, di_package, LOGGER)
    return basedir

class MeterExitHandler:
    """ class to notify callers that the meter is going away

        this would probably be used to collect information that
        could be lost after the meter lock has been release, like
        code coverage data, etc.

    """
    def __init__(self,  meter):
        self.callbacks = {}
        self.meter = meter

    def get_handler_by_name(self, name):
        return self.callbacks.get(name, None)

    def register_exit_handler_by_name(self, name, fnc):
        oldone = None
        if name in self.callbacks:
            LOGGER.info("Registering multipe cleanup callbacks!!!! probably should not do this")
            oldone = self.callbacks[name]

        self.callbacks[name] = fnc
        LOGGER.info("Registered %s callbacks for meter %s", len(self.callbacks), self.meter)
        return oldone

    def shutdown(self):
        while len(self.callbacks) > 0:
            try:
                x = next(iter(self.callbacks))
                fnc = self.callbacks.pop(x)
                fnc(self.meter)
            except Exception as e:
                LOGGER.exception(e)

        #self.meter.unlock()
        self.callbacks = None

@pytest.fixture(scope='session')
def meter_exit_handler(request, meter):
    """ This fixture provides way to register a callback when all of the tests are complete
    The typical use would be to collect code coverage data or error logs for the session that
    would be too onerus to collect between each test.

    The parallel plugin will execute all tests the specific meter, then it will call all of the functions registered
    with the meter_exit_handler.register_exit_handler_by_name
    """
    meter_exit_handler = MeterExitHandler(meter)
    yield meter_exit_handler
    meter_exit_handler.shutdown()

@pytest.fixture(scope='session')
def multi_meter_exit_handler(request, multi_meter):
    """ This fixture provides way to register a callback when all of the tests are complete
    The typical use would be to collect code coverage data or error logs for the session that
    would be too onerus to collect between each test.

    The parallel plugin will execute all tests the specific meter, then it will call all of the functions registered
    with the meter_exit_handler.register_exit_handler_by_name
    """
    meter_exit_handlers = [MeterExitHandler(meter) for meter in multi_meter]
    yield meter_exit_handlers
    for handler in meter_exit_handlers:
        handler.shutdown()

class AppServeContext(object):
    def __init__(self, artifact_output_dir, di_package, di_version, di_artifacts,  session_dir, di_package_sha):
        self.artifact_output_dir = artifact_output_dir
        self.di_package = di_package
        self.di_version = di_version
        self.di_artifacts = di_artifacts
        self.session_dir = session_dir
        self.di_package_sha = di_package_sha

@pytest.fixture(scope='session')
def appserve_artifacts(artifact_output_dir, di_package, di_version, di_artifacts,  session_dir, di_package_sha):
    """ shorthand function for artifacts from build """
    return AppServeContext(artifact_output_dir, di_package, di_version, di_artifacts,  session_dir, di_package_sha)

