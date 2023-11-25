#!/usr/bin/env python3
# content of conftest.py

from utils import port_function,Lock_File,HOST_NAME,PORT,USERNAME,PASSWORD,system_load
import pytest
from datetime import datetime
from zeep import xsd
import os, json, subprocess, logging, pytz, time, psutil, shutil, platform
from requests import exceptions,request
from requests.auth import HTTPBasicAuth
from zeep import exceptions

LOGGER = logging.getLogger(__name__)

def pytest_addoption(parser):
    parser.addoption(
        "--artifact-output-dir", action="store", default=None, help="location to store artifacts"
    )
    parser.addoption(
        "--group_name", action="store", default="vgs_testing_1", help="Group name of Meters"
    )
    parser.addoption(
        "--macid", action="store", default=None, help="Macid of Meter"
    )
    parser.addoption("--all", action="store_true", help="run all combinations")


def pytest_generate_tests(metafunc):
    group_name = metafunc.config.getoption("--group_name")
    Mac_id = metafunc.config.getoption("--macid")
    if "vgs_meter" in metafunc.fixturenames:
        LOGGER.info(group_name)
        LOGGER.info(Mac_id)
        if Mac_id : Mac_ids = [Mac_id,]
        else : Mac_ids = Collect_Mac_id(group_name,LOGGER)
        metafunc.parametrize("meter", Mac_ids)

@pytest.fixture(autouse=True,scope='function')
def init_meter(vgs_meter,logger):
    if Meter_check(vgs_meter,logger):
        meter_lock = Lock_File(f"{vgs_meter}.lock", logger)
        logger.trace("Initializing meter %s", vgs_meter)
        with meter_lock:
            yield vgs_meter
        logger.trace("Finalizing meter %s", vgs_meter)
    else:
        logger.error('was not idenitfied by VGS as a meter test')



@pytest.fixture(scope='function')
def vgs_meter(meter,logger):

    function = port_function('DeviceManager','FindDevice',logger)
    Mac_data = {'SearchParameters': {'CommonAttributes': {'DeviceConfig' : {'MacID': meter}}},'NumberRows': '1',}
    response = function(**Mac_data)
    # logger.error('FindDevice : %s',response)

    assert  len(response['SearchResponse']) ,f'Meter : {meter} is not available in the AMM'

    meter_ip_address = response['SearchResponse'][0]['IPAddress']

    meter_info = False
    meter_twin_file = os.path.join('meter_twinw.json')

    logger.info(meter_twin_file)
    status = os.path.exists(meter_twin_file)

    assert status,'Meter twin file is not available in the directory'

    with open(meter_twin_file) as f:
        data = json.load(f)

    for mtr in data[meter_ip_address]:
        logger.info(f"{meter} full info in the VGS file ::  {mtr} ")
        meter_info = mtr
        break
    
    assert meter_info,f'Meter : {meter} is not available in the same ton with the VGS'
    logger.info("meter ::::  %s ",meter_info['sim'])

    '''
        {
            'sim': '2405:203:2a00:2bfd::10', 'port': '9083', 
            'auth_key': 'AE90F90883AC70AF5BCE9D8060EE22F0', 
            'encryp_key': '22C8DA0AA7BBE7918F57296C4BE9FA23'
        }
    '''
    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'
    # Building the command. Ex: "ping -c 1 google.com"
    # command = ['ping', param, '1', host]
    command = ['ping', param, '5', meter_info['sim']]
    assert subprocess.call(command) == 0,f'Meter : {meter} is not able to Ping'
    return meter


def pytest_sessionstart(session):
    [
        print(f'Environment Variable \'{vari}\' is not define') 
                for vari in ['AMMWSHOST','AMMWSHOSTPORT','AMMUSER','AMMPSWD'] if os.getenv(vari) is None
    ]

    if not all([HOST_NAME,PORT,USERNAME,PASSWORD]) :
        raise EnvironmentError(f"Your environment variable is not defined")
    
    # SOAP request URL
    base_url = f'https://{HOST_NAME}:{PORT}/amm/webservice/v2_7_1/SystemInfoPort'

    # headers
    headers = {'Content-Type': 'text/xml; charset=utf-8'}
    # headers = {'content-type': 'application/soap+xml'}
    print('Binding Address           : ',base_url)

    try:
        response = request("POST", base_url, headers=headers, data = system_load, auth=HTTPBasicAuth(USERNAME, PASSWORD))
    except exceptions.ConnectionError :
        raise ValueError(f"Could not connect to {base_url}.")
    assert response.status_code == 200,f"Login Credentials is invalid for ({USERNAME}, {PASSWORD})"
    print('request                   : ',response)

@pytest.fixture(autouse=True,scope='session')
def vgs_run(session_logger):

    '''
    Check if there is any running process that contains the given name processName.
    '''
    process_name = "my_program_automation"
    # listOfProcessObjects = []

    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if process_name.lower() in proc.name().lower():
                session_logger.info(f"The VGS script: {process_name} is running")
                #  'UID PID PPID C STIME TTY TIME CMD'
                pinfo = proc.as_dict(attrs=['pid', 'name', 'create_time'])
                # Check if process name contains the given name string.
                if process_name.lower() in pinfo['name'].lower() :
                    # listOfProcessObjects.append(pinfo)
                    return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    else:
        session_logger.info(f"The VGS script :{process_name} is not running")
        assert False, f"The VGS script : {process_name} is not running"


@pytest.fixture(autouse=True,scope='session')
def meter_twin(vgs_run,session_logger):
    user = vgs_run.username()
    source = f"/home/{user}/VGS_Automation/meter_twinw.json"
    # Destination path
    meter_twin_file = os.path.join('meter_twinw.json')

    session_logger.info(meter_twin_file)
    status = os.path.exists(meter_twin_file)

    if not status:
        shutil.copyfile(source, meter_twin_file)
        status = os.path.exists(meter_twin_file)

    assert status,'Meter twin file is not available in the directory'
    return meter_twin_file


def Meter_check(meter_MacID,logger):
    Macid = meter_MacID
    function = port_function('DeviceManager','FindDevice',logger)
    Mac_data = {'SearchParameters': {'CommonAttributes': {'DeviceConfig' : {'MacID': Macid}}},'NumberRows': '1',}
    response = function(**Mac_data)
    logger.info('FindDevice : %s',response)
    assert  len(response['SearchResponse']) ,'Meter is not available in the AMM'

    Device_State_connection_state = response['SearchResponse'][0]['UiqDeviceStateID']['LocalizedValue']
    logger.info('Uiq Device StateID : %s',Device_State_connection_state)
    # assert Device_State_connection_state !='Unreachable',f'DeviceId {UtilDeviceID} with Macid {meter_MacID} is unable to reached'
    
    meter_MacID = response['SearchResponse'][0]['MacID']
    meter_state = response['SearchResponse'][0]['UtilDeviceStateID']['LocalizedValue']
    logger.info('Device %s : State connection state : %s',meter_MacID,meter_state)

    meter_twin_file = os.path.join('meter_twinw.json')

    assert  meter_MacID ,'Meter is not available in the AMM'
    return meter_MacID

@pytest.fixture(scope='function')
def meter_time_stamp(init_meter,logger):

    ping_read_data =  {'AutoActivate': 'true',
                        'JobInfo': {'Description': 'This is a meter ping test job',
                                    'Name': 'Job_1'},
                        'PingJob': {'IsBackboneJob': 'false',
                                    'AppLevelPing': {'NumberPings': '5',
                                                    'DeviceMacID': init_meter},
                                    'NumberRetries': '0',
                                    'Priority': {'Name': 'JOB_PRIORITY_HIGH'},
                                    'PushResults': {'PushResultsToJMS': {'TimeoutThresholdInSeconds': '35'}}},
                        'Schedule': {'Immediate': xsd.Nil}}

    amm_time_zone = 'America/Los_Angeles'
    IST = pytz.timezone(amm_time_zone)

    ############################################################
    retry = 0
    time_out=time.time() + 10*60
    while time_out>time.time():

        if retry != 0:
            function = port_function('JobManager','getJobStatus',logger)
            response= function(**job_request_data)
            JobStatus = response['ExecutionStatus']['LocalizedValue']
            logger.info(f"Searching for the JobID --> {JobID} {JobStatus} {retry}")

        if retry==0 or JobStatus == 'Failure' or retry >= 20:
            function = port_function('JobManager','addPingJob',logger)
            datetime_ist = datetime.now(IST).strftime('%Y-%m-%dT%H:%M:%S')

            JobID = function(**ping_read_data)
            logger.info(f"My JobID = {JobID}")
            job_request_data =  {'JobID': JobID}
            retry = 0

        elif JobStatus == 'Completed':
            break

        elif JobStatus =='Not Started' :
            function = port_function('JobManager','activateJob',logger)
            response = function(**job_request_data)


        retry += 1
        time.sleep(1)


    # logger.info(response)
    ############################################################
    assert JobStatus == 'Completed',f'VGS to AMM connection is not achieved'

    request_data =  {'NumberRows':'100','SearchParameters': {'JobID': JobID}}
    function = port_function('DeviceResults','getPingResultsByJobID',logger)
    response= function(**request_data)
    logger.info(response)

    assert response['DevicePing'][0]['JobID'] == JobID
    data = response['DevicePing'][0]['Ping']
    # logger.info(data)
    GatewayTimestamp = [ member['GatewayTimestamp'] for id,member in enumerate(data)]
    logger.info(GatewayTimestamp)
    logger.info(datetime_ist)
    # assert any([datetime_ist in tm for tm in GatewayTimestamp]),''

    return GatewayTimestamp

def Collect_Mac_id(GroupName,logger):
	logger.info('Retrieve Group ID (GroupManager::FindGroup)')
	GroupName = 'vgs_testing_1'
	logger.info(GroupName)

	function = port_function('GroupManager','FindGroup',logger)
	Group_data = {'SearchParameters': {'GroupName': GroupName}}
	response = function(**Group_data)
	logger.info(response)
	GroupID = False

	for id,member in enumerate(response):
		if member['GroupName'] == GroupName :
			GroupID = member['GroupID']
			break

	assert GroupID,f'{GroupName} is not available in the AMM'

	logger.info('Retrieve Group ID Count (GroupManager::GetGroupMemberCount)')
	function = port_function('GroupManager','GetGroupMemberCount',logger)
	Group_data ={'GroupID': GroupID}
	Group_data_count = function(**Group_data)
	# logger.info(Group_data_count)

	logger.info('Retrieve Group ID Member (GroupManager::GetGroupMembers)')
	function = port_function('GroupManager','GetGroupMembers',logger)
	Group_data = {'SearchParameters': {'GroupID': GroupID},'NumberRows': Group_data_count}
	response = function(**Group_data)
	# logger.info(response)
	data = response['DeviceGroup']['MemberDevice']

	assert Group_data_count == len(data),f'some member is missed from the Groupid : {GroupID}'
	Mac_ids = [member['MacAddress'] for id,member in enumerate(data)]
	logger.info(Mac_ids)
	assert Group_data_count == len(Mac_ids),f'some member is missed from the Groupid : {GroupID}'
	return Mac_ids

@pytest.fixture(scope='session')
def session_name(worker_id):
    if ('VGS_METER_TARGET' in os.environ):
        name = os.environ["VGS_METER_TARGET"]
    else:
        name = worker_id
    return name



@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    if call.when == 'call':
        if call.excinfo is not None:
            # if excinfor is not None, indicate that this test item is failed test case
            logging.error("Test Case: {}.{} Failed.".format(item.location[0], item.location[2]))
            logging.error("Error: \n{}".format(call.excinfo))

    return outcome

# start time of session

# need to allocate this before pytest parallel plugin starts up and forks processes, so here goes
session_lock = Lock_File("pytest_session.lock", LOGGER)

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
def global_session_data(tmp_path_factory):
    """ this fixture provides a global session file that can share information
        betweeen workers.  Must be accessed with a session_lock. """

    # put stuff here that can be shared between every worker
    shared_singleton_data = {
        "session_date": time.time()
    }
    root_tmp_dir = tmp_path_factory.getbasetemp().parent
    fn = root_tmp_dir / "session_share.json"
    # if fn:
    #     json.dump(shared_singleton_data, fn)
    # else:
    with session_lock:
        # if file already created, we are done
        # if not fn.is_file():
        with open(fn,'w') as fp:
            json.dump(shared_singleton_data, fp)
    return fn

@pytest.fixture(scope='session')
def session_date(global_session_data):
    with session_lock:
        with open(global_session_data, "r") as fp:
            shared = json.load(fp)
        session_start = datetime.fromtimestamp(shared['session_date'])

    strdate = session_start.strftime("%Y-%m-%d_%H_%M_%S")
    return strdate

@pytest.fixture(scope='session')
def session_dir(session_date,request):
    log_dir = request.config.getoption("--artifact-output-dir")
    if not log_dir:
        log_dir = os.path.join(request.session.fspath, f"session-{session_date}")
    os.makedirs(log_dir,exist_ok = True)
    return log_dir

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