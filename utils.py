
# content of utils.py

import os,time,logging,fcntl
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, xsd
from zeep.transports import Transport
import logging
from dotenv import load_dotenv
from zeep.plugins import HistoryPlugin
# history = HistoryPlugin()


# Environment Variable
load_dotenv()
HOST_NAME = os.getenv('AMMWSHOST')
PORT = os.getenv('AMMWSHOSTPORT')
USERNAME = os.getenv('AMMUSER')
PASSWORD = os.getenv('AMMPSWD')
# Authentication Session for the WSDL Access
session = Session()
session.auth = HTTPBasicAuth(USERNAME, PASSWORD)
session.trust_env = False
AUTHENTICATION = Transport(session=session)
logger = logging.getLogger(__name__)
                  



system_load = """
                <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:com:ssn:schema:service:v2.7.1:SystemInfo.xsd">
                    <soapenv:Header/>
                        <soapenv:Body>
                            <urn:GetCopyrightYear/>
                        </soapenv:Body>
                </soapenv:Envelope>
            """

class Lock_File:
    
    # LOCK_UN – unlock
    # LOCK_SH – acquire a shared lock
    # LOCK_EX – acquire an exclusive lock

    def __init__(self, name, logger):
        self.name = name
        self.fd = None
        self.logger = logger

    def __enter__(self):
        self.fd = open(self.name, 'w')
        fcntl.flock(self.fd, fcntl.LOCK_EX)
        self.logger.info('acquired lock on %s', self.name)

    def __exit__(self, type, value, traceback):
        self.logger.info('releasing lock on %s', self.name)
        fcntl.flock(self.fd, fcntl.LOCK_UN)



def port_function(wsdl_port,fun_name,logger):
    logger.info(f'Retrieve WSDL Function for Directory ({wsdl_port}::{fun_name})')
    port_name = wsdl_port + 'Port'
    
    wsdl_file = os.path.join('pytest-VGS-venv','AppSW.EsbWsdl','amm','2_7_1',f'{wsdl_port}.wsdl')
    logger.info("WSDL file location : %s",wsdl_file)
    assert os.path.exists(wsdl_file),f'{wsdl_port} is not available in the file'

    client = Client(wsdl_file, transport=AUTHENTICATION)
    base_url = f'https://{HOST_NAME}:{PORT}/amm/webservice/v2_7_1/{port_name}'
    logger.debug("Binding Address : %s",base_url)
    client.service._binding_options["address"] = base_url
    fun = getattr(client.service, fun_name)
    logger.info("Function Name : %s",fun_name)
    logger.debug("Function Name location : %s",fun)
    return fun


def device_state(vgs_meter,logger,do_assert = False):
    function = port_function('DeviceManager','FindDevice',logger)
    Mac_data = {'SearchParameters': {'CommonAttributes': {'DeviceConfig' : {'MacID': vgs_meter}}},'NumberRows': '1',}

    response = function(**Mac_data)
    logger.debug('FindDevice : %s',response)
    assert  len(response['SearchResponse']) ,f'Meter : {vgs_meter} is not available in the AMM'

    Device_State_connection_state = response['SearchResponse'][0]['UiqDeviceStateID']['LocalizedValue']

    if do_assert:
        assert Device_State_connection_state !='Unreachable',f'Meter : {vgs_meter} is unable to reached'

    meter_state = response['SearchResponse'][0]['UtilDeviceStateID']['LocalizedValue']
    logger.info('Meter State : %s',meter_state)
    return meter_state


def RSM_intial_state(vgs_meter,logger,required_intial_state = 'Active'):

    """
    if meter_state == 'Active':
        RSM_Action_perform =  'JOB_OP_PROVISION_DISCONNECT'
        rsm_meter_check = 'Disconnected'

    elif meter_state == 'Disconnected':
        RSM_Action_perform =  'JOB_OP_PROVISION_CONNECT'
        rsm_meter_check = 'Active'
    else:
        RSM_Action_perform =  'JOB_OP_PROVISION_GET_STATUS'
    
    """

    from datetime import datetime
    import pytz

    '2023-07-09T01:22:39.510-07:00'

    state = device_state(vgs_meter,logger,do_assert = True)
    RSM_Action_perform =  'JOB_OP_PROVISION_GET_STATUS'

    if state == required_intial_state:
        logger.info(f" Meter : {vgs_meter} is already in {required_intial_state}")
        return required_intial_state


    if required_intial_state == 'Active':
        RSM_Action_perform =  'JOB_OP_PROVISION_CONNECT'

    elif required_intial_state == 'Disconnected':
        RSM_Action_perform =  'JOB_OP_PROVISION_DISCONNECT'


    logger.info('RSM Action Perform : %s',RSM_Action_perform)


    state_check_data = {'JobInfo': {'Name': 'Remote Provisioning Example'},
                                'AutoActivate': 'false',
                                'RemoteProvisioningJob': {'DeviceMacID': vgs_meter,
                                                            'NumberRetries': '0',
                                                            'Priority': {'Name': 'JOB_PRIORITY_HIGH'},
                                                            'ProvisioningAction': {'Name': RSM_Action_perform}},
                                'Schedule': {'Immediate': xsd.Nil}}

    retry = 0
    time_out=time.time() + 10*60



    amm_time_zone = 'America/Los_Angeles'
    IST = pytz.timezone(amm_time_zone)
    fromtime = datetime.now(IST).isoformat()

    # fromtime = datetime.now(IST).strftime('%Y-%m-%dT%H:%M:%S %Z %z')
    # fromtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # totime = datetime.now(IST).strftime('%Y-%m-%dT%H:%M:%S')
    # 'FromTime': '2023-07-09T01:22:39.510-07:00'
    # 'ToTime': '2024-10-29T13:22:39.510-07:00'



    while time_out>time.time():

        if retry != 0:
            function = port_function('JobManager','getJobStatus',logger)
            response= function(**job_request_data)
            JobStatus = response['ExecutionStatus']['LocalizedValue']
            logger.info(JobStatus)
            logger.info(f"Searching for the JobID --> {JobID} {JobStatus} {retry}")

        if retry==0 or JobStatus == 'Failure' or retry >= 20:
            time1 = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            function = port_function('JobManager','addRemoteProvisioningJob',logger)
            JobID = function(**state_check_data)
            logger.info(f"My JobID = {JobID}")
            job_request_data =  {'JobID': JobID}
            retry = 0

        elif JobStatus == 'Completed':
            request_data =  {'NumberRows':'10','SearchParameters': {'JobID': JobID}}
            function = port_function('DeviceResults','getRemoteProvisioningResultsByJobID',logger)
            response= function(**request_data)
            break

        elif JobStatus =='Not Started' :
            function = port_function('JobManager','activateJob',logger)
            response = function(**job_request_data)

        retry += 1
        time.sleep(10)
        time2 = datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z %z')

    ############################################################
    logger.info('Jobid status : %s',response)
    logger.info('::'*30)


    ############################################################
    totime = datetime.now(IST).isoformat()
    request_data={
        'SearchParameters':{
            'DeviceMacID':vgs_meter,
            'FromTime':fromtime,
            'ToTime':totime,
            'MeterDataType':'METER_DATA_TYPE_REGISTER',
            'LPSetId':'1L',
        },
        'NumberRows':'100',
    }
    function = port_function('DeviceResults','getMeterReadResultsByDeviceID',logger)
    response= function(**request_data)
    logger.info('Device status : %s',response)
    logger.info('::'*30)
    ############################################################

    assert JobStatus == 'Completed',f"Jobid : {JobID} is not Sussessful. \n There is lots of request in the Meter : {vgs_meter} from {time1} to {time2}"

    time_out=time.time() + 5*60
    while time_out>time.time():
        state = device_state(vgs_meter,logger)
        if state == required_intial_state:
            break
        time.sleep(10)

    ##########################################################################
    assert state == required_intial_state,f"AMM is not able to change Meter : {vgs_meter} state from {state} to {required_intial_state}"
