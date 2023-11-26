""" utility functions used by multiple tests """
import sqlite3
import logging
import os
import json
from itron.meter.MeterInstance import MeterInstanceBase
import requests
from tempfile import TemporaryDirectory
import re
from itron.meter.AbstractMeter import AbstractMeter
from itron.meter.Gen5Meter import AdvancedMeter,SSHGen5Meter,FilterMatch
import time
from datetime import datetime as dt
from typing import List
from itron.meter.AgentMan import AgentInfo, ITRON_CONTAINER_ID, THIRD_PARTY_CONTAINER_ID
from itron.meter.MeterMan import DatabaseError
from itron.meter.Walker import OWI_URL


sql_tables_no_as = ["BINARYSTORE", "Blurt", "BlurtBackup", "CATEGORY_TO_EVENTS", "CATEGORY_TO_LIDS", "CONFIGURATIONXML",
    "CONTAINEROVERLAY", "CONTAINERSETUP", "CONTAINERSTATUS", "CORRECTOWNERSHIP", "ComponentGroups", "Configuration",
    "ConfigurationPackage", "CpcRecord", "DATABASEMAINTENANCE", "DBusToEvent", "DEVICE_TO_LIDS", "DISPLAYLINES",
    "DISPLAYSCREENS", "DLMSACCESSRIGHTS", "DLMSCLIENTS", "DLMSOBJECTSTRUCTURE", "DLMSSERVERS", "DSTPERIODS",
    "DemandCapture", "DemandCoincident", "DemandCoincidentConfig", "DemandConfiguration", "DemandCumulative",
    "DemandPeaks", "DemandPrevious", "DemandReset", "DemandSetConfiguration", "DemandSetEventTime", "DisconnectTable",
    "DlmsConnections", "DlmsCosemGen5Roles", "DlmsFrameCounter", "DlmsSecuritySetup", "DlmsServerAssociations",
    "DynamicConfiguration", "DynamicConfiguration2", "ENERGYCONFIGURATION", "ENERGYDATA", "ENERGYHISTORY", "ERRORS", "EVENT_ACTION_STATS",
    "EVENT_CATEGORIES", "EVENT_STATS", "EventAction", "EventDescription", "EventLogID", "EventSpecification",
    "FWINFORMATION", "GENERICLOOKUP", "GPRFILES", "HANACL", "HDLCCONNECTIONS", "HwControlTable", "IMAGETRANSFERBLOCK",
    "IMAGETRANSFERSTATUS", "ImageActivateInfo", "ImageProcessStatus", "ImageProcessTask", "LIDS", "LID_BEHAVIOR_TYPES",
    "LID_CATEGORIES", "LOG_EVENTRECORDS", "LOG_EVENTRULES", "LOG_EVENTRULES_TO_LISTENERSET_ASSOCIATIONS", "LOG_LISTENERSETS",
    "LOG_LISTENERS_TO_LISTENERSETS_ASSOCATIONS", "LidBehavior", "MESSAGESTORE", "OBIS", "OBISCLASSATTRIBUTES", "OBJECTSTORE",
    "OVERLAYCONFIGURATION", "OVERLAYSETUP", "PLUGINS", "PLUGINS_CATEGORY_TO_NAME", "PLUGINS_INTERFACE_TO_CATEGORY",
    "PREINSTALLPACKAGELIST", "PREINSTALLPACKAGEPREREQ", "PROFILEHISTORY", "ProfileFlag", "ProfileInterval",
    "ProfileIntervalMain", "ProfileSetSpec", "PulseWeightTable", "RAMTABLENAMES", "RESETREASONS", "REVERTREASONS",
    "ReactorPriorityTable", "ReactorSetTable", "SELFREADBILLINGDATA", "SELFREADQUANTITYCONFIGURATION", "SELFREADRECORDS",
    "STATISTICS", "STATISTICS2", "SelfReadHistory", "SelfReadSchedule", "TABLESTOUCHES", "TESTHISTORY", "TamperTable",
    "TimeProfile", "TouDayProfileTable", "TouEnergyTable", "TouRateLookupTable", "TouSeasonProfileTable", "TouSingleValuesTable",
    "TouSpecialDaysTable", "TouWeekProfileTable", "VersionHistory"]

LOGGER = logging.getLogger(__name__)

FW_1_7_PLUS_DIR = "/usr/share/itron/DI-AppServices-Package"
FW_PRE_1_7_DIR = "/mnt/common/DI-AppServices-Package"
deleted_list = [ '/usr/share/itron/improv/Diff.Install/AppServ',
                '/usr/share/itron/DI-AppServicesPackage.New',
                '/mnt/common/DI-AppServicesPackage.New',
                #'/mnt/common/D55-populateFWInformationForAppServices.sql'
                ]

default_new_tables = ["AgentData", "AgentEvents", "AgentFeatureDataCounter", "AgentInformation",
    "AgentMailbox", "AgentPolicy", "AgentRegistration", "DIDevice", "DIP2PGroupDbTable",
    "DIP2PKeyManagementDbTable", "DIP2PKeyValidationCounterDbTable", "DIP2PPublishedDataDbTable",
    "DIP2PReceivedNetworkMessagesDbTable", "DIP2PSentNetworkMessagesDbTable", "DIP2PStatSummaryTotalDbTable",
    "DIP2PStatsDatainCBORPerDay", "DIP2PSubscribedDataDbTable", "DIP2PSubscriptionDbTable", "DIPolicyFile",
    "DeviceArchive", "DeviceArchiveEntry", "FeatureConfiguration", "PolicyViolationStatistics"]

def numbered_file(workdir, file_name):
    name, ext = os.path.splitext(file_name)
    path = os.path.join(workdir, name + ext)
    i = 1
    while os.path.exists(path):
        path = os.path.join(workdir, f"name-{i}{ext}")
        i += 1
    return path

def verify_appserve(logger, meter, workdir, expected_version, sql_tables_no_as=None, expected_new_tables=None, check_hash=True):
    """ verify that the meter is working and that AppServe is running and active """
    failed = False
    info={}
    if expected_new_tables is None:
        expected_new_tables = default_new_tables

    meter.capture_logs(workdir)
    if sql_tables_no_as:
        info['sql_tables_with_as'] = meter.sql_query( '.tables', json_file=numbered_file(workdir, "sql_tables_with_as.json"))

        new_entries, deleted_entries = diff_and_save(numbered_file(workdir, "new_tables.json"),
            sql_tables_no_as,
            info['sql_tables_with_as'])
        info['new_entries'] = new_entries
        info['deleted_entries'] = deleted_entries

        if set(new_entries) != set(expected_new_tables):
            logging.warning("The expected table list does not match the new tables")
            missing = list(set(expected_new_tables) - set(new_entries))
            extra = list(set(new_entries) - set(expected_new_tables))
            if missing:
                logging.error("Missing tables: %s", missing)
            if extra:
                logging.warning("Extra tables: %s", extra)
            failed = True

    info['database'] = database = meter.download_db(workdir)
    # TODO: Verify database

    con = sqlite3.connect(database)
    cursor = con.cursor()
    res = cursor.execute("select id,path,version,unsignedhash,enabled  from fwinformation")

    for x in res:
        if x[1] == '/usr/share/itron/sha/appservicesLR.manifest':
            version = x[2]
            _id = x[0]
            _hash = x[3]
            enabled = x[4]

    assert version == expected_version
    assert int(enabled) == 1

    logger.trace1("AppServe Id: %s Hash:%s Version:%s", _id, _hash, version)
    if check_hash:
        verify_hashs(logger,meter, x[1])

    # Validate cleanup during install

    logger.trace1("Verify deleted files")
    for entry in deleted_list:
        lst = meter.ls(entry)
        logging.info("ls:%s\n%s",entry, lst)

        if lst:
            logging.error("Item should be deleted from meter: %s", entry)
            failed = True

    failed = failed | verify_uninstaller(logger, meter, workdir, _hash)

    failed = failed | verify_as_running(meter,logger)

    logger.trace1("Create meter report info.json")
    with open(numbered_file(workdir, "info.json"),"w") as f:
        json.dump(info, f)

    assert failed is False

    return info

def ASSERT(truth, logger, failed, string):
    if not truth:
        logger.error(string)
        return True
    return failed

def verify_cosem(logger, meter, workdir):
    failed=False
    meter.command("di-tool ")
    return failed

def verify_hashs(logger,meter,remote_lrfile):
    fail = False
    list = meter.command(f"cat {remote_lrfile}")
    for item in list:
        items = item.split()
        hash = items[0]
        file = items[1]
        rhash = meter.command(f"sha256sum {file}", timeout=60)
        rhash = rhash[0].split()[0]
        if hash != rhash:
            logger.error("Hash mismatch for %s %s != %s", file, hash, rhash)
            fail = True

    return fail

def verify_uninstaller(logger,meter,workdir,_hash):
    """ verify that the uninstaller directory matches
        the current installed version """
    un_dir = "/usr/share/itron/DI-AppServices-Package"
    if not meter.ls(un_dir):
        un_dir = "/mnt/common/DI-AppServices-Package"

    rhash_file = os.path.join(un_dir, 'appservicesLR.manifest')
    un_hash = meter.command(f"sha256sum {rhash_file}")
    logger.info(un_hash)
    failed = ASSERT(len(un_hash) == 1, logger, False,
        "hash not generated, File not found??")
    failed = ASSERT(un_hash[0].split()[0] == _hash, logger, failed,
        "hashes for leagally relevant didn't match hash from uninstall dir")
    failed = failed or verify_hashs(logger, meter, rhash_file)
    return failed

def verify_no_di(logger,meter,workdir):
    """ check to make sure app services is not installed """

    assert meter.ls(FW_1_7_PLUS_DIR) is None

def clean_as_and_gmr(logger, meter: AbstractMeter, workdir):
    """ remove as from the system on falure.  Will cause GMR """
    logger.info("gmr and clean AppServe")

    meter.gmr()

    # cleanup uninstaller entries
    meter.command(f"rm -rf {FW_1_7_PLUS_DIR}")
    meter.command(f"rm -rf {FW_1_7_PLUS_DIR}.New")
    meter.command(f"rm -rf {FW_PRE_1_7_DIR}")
    meter.command(f"rm -rf {FW_PRE_1_7_DIR}.New")

    # cleanup db entries
    meter.command("rm -rf /usr/share/itron/DI*")

    for entry in deleted_list:
        meter.command(f"rm -fr {entry}")


def verify_as_running(meter,logger):
    """ make sure app services is running and responding to DBUS messages
    """
    stat = meter.command("ps")
    r = re.compile(".*DataServer.*")
    di = list(filter(r.match, stat)) # Read Note below
    if not di:
        logger.error("DataServer is not running")
        return True
    else:
        logger.info("Dataserver running: %s", di)
    return False

def install_all_from_preinstall(logger,meter,agent = True,force = False):
    """ 
        install the DI-AppServices-Package 
        If Appserv is already installed 
    
    """

    dir="/usr/share/itron/PreInstall"
    logger.info(f'found preinstall file : {", ".join(meter.ls(dir))}')

    files = meter.ls(f"{dir}/DI-AppServices-Package*.tar.gz")
    fwver, asver = meter.version_info()
    if len(files) > 1: 
        assert False, f"Dublicate DI-AppServices-Package is present in {dir}"

    code = 1
    retry = 3
    while retry !=0 :

        # DI-AppServices-Package is try to install 
        # if tar.gz is still available in the Directory and installalion is failed

        try:
            if files and (not asver or force):
                logger.info("found preinstall file, installing: DI-AppServices-Package")
                file = os.path.join(dir,files[0])
                code = meter.install(file=file,remote_file=True)
            else:
                logger.info(f"DI-AppServices-Package is not present in {dir}")

        except ValueError as e:
            # There is problem to install DI-AppServices-Package in meter so we just installed again 
            # if the file is still present DI-AppServices-Package tar.gz is still present.                
            logger.error("%s",e)
            logger.error('There is problem to install DI-AppServices-Package in meter so we just installed again')


        files = meter.ls(f"{dir}/DI-AppServices-Package*.tar.gz")
        fwver, asver = meter.version_info()

        if code!=0 and files :
            logger.info("'Installation is not successful',: DI-AppServices-Package")

        status = asver and (not files)

        if status :
            logger.info(f'Installation is succesfull after {4-retry} try')
            break
        time.sleep(60)
        retry -= 1

    assert not files,'DI-AppServices-Package tar file is not still available'
    assert asver,'Appserv version is not availbale'


    if agent:
        install_han_from_preinstall(logger,meter)


def install_han_from_preinstall(logger,meter: AbstractMeter):
    """ install the HAN agent """
    dir="/usr/share/itron/PreInstall"
    files = meter.ls(f"{dir}/HANAgent*.tar.gz")
    agent_list = [agent.name for agent in get_installed_agents(meter,logger)]
    HAN_agent_status = HAN_AGENT.name in agent_list
    if files and len(files) == 1 and not HAN_agent_status:
        logger.info("HAN agent found,  installing")
        exit_standalone(meter, logger)
        file = os.path.join(dir,files[0])
        logger.info("found preinstall file, installing: DI-AppServices-Package")
        file = os.path.join(dir,files[0])
        try:
            meter.install(file=file,remote_file=True)
        except ValueError as e:
            # There is problem to install HANAgent-Package in meter so we just installed again 
            # if the file is still present HANAgent-Package tar.gz is still present.                
            logger.error("%s",e)
            logger.error('There is problem to install HANAgents-Package in meter so we just installed again')

        agent_list = [agent.name for agent in get_installed_agents(meter,logger)]
        logger.info(agent_list)
        enter_standalone(meter, logger)

 



def diff_tables(sql_tables_no_as, sql_tables_with_as):
    unique = list(set(sql_tables_with_as) ^ set(sql_tables_no_as ))
    deleted = list(set(sql_tables_no_as ) & set(unique))
    return unique, deleted

def diff_and_save(file, a, b):
    new_tables, deleted = diff_tables(a,b)
    new_tables.sort()
    with open(file,"w") as f:
        json.dump(new_tables, f)
    return new_tables,deleted

def install_build(logger, workdir, m, di_package, di_version, expected_new_tables=None, sql_tables_no_as=None):
    """ install or upgrade DI package and verify correct installation """

    if not sql_tables_no_as:
        logger.info("DI Package: %s", di_package)
        fwver, asver = m.version_info()
        assert asver is None, "AS is installed so we can't get a list of non AS tables, this must be passed in"
        sql_tables_no_as = m.sql_query( '.tables', json_file=numbered_file(workdir, "sql_tables_no_as.json"))

    # now install AppServe
    code = m.install(file=di_package)
    #m.capture_logs()
    assert code == 0
    fwver, asver = m.version_info()
    assert asver == di_version
    sql_tables_with_as = m.sql_query( '.tables', json_file=numbered_file(workdir,f"sql_tables_with_{di_version}.json"))
    verify_appserve(logger, m, workdir, asver, sql_tables_no_as=sql_tables_no_as, expected_new_tables=expected_new_tables)

    new_tables,deleted = diff_and_save(numbered_file(workdir, "new_tables.json"),
        sql_tables_no_as,
        sql_tables_with_as)

    assert not deleted, "there should be no deleted tables"

    return new_tables

class AdvancedMeterWithDebug(AdvancedMeter):
    def __repr__(self):
        return f'AdvancedMeter({self.meter_db})'
class SSHGen5MeterWithDebug(SSHGen5Meter):
    def __repr__(self):
        return f'SSHGen5Meter({self.meter_name})'

class ParallelMeterWithDebug:
    """ This clas provides a factory for creating an avanced meter or a hard coded ip address meter
    """
    ADVANCED_METER = 1
    JUST_SSH_METER = 2

    def __new__(self, meter, logger, *args, timeout=10*60):
        if isinstance(meter, MeterInstanceBase):
            return AdvancedMeterWithDebug(meter, logger, *args, timeout=timeout)
        else:
            return SSHGen5MeterWithDebug(meter, logger, *args, timeout=timeout)

#Tensor Flow Agent
TENSOR_AGENT = AgentInfo('TensorFlowAgent', '0.0.6.1557546219', ITRON_CONTAINER_ID,
    f"{OWI_URL}DI_Agents/TensorFlowAgent/0.0.6/DevInternal/TensorFlowAgent_0.0.6.1557546219_TS.zip",has_daemon=False)

#EV Agent

EV_ML_AGENT = AgentInfo('EV_MLAgent', '0.0.5.3762474023', ITRON_CONTAINER_ID,
                        f"{OWI_URL}DI_Agents/EV_MLAgent/0.0.5/DevInternal/EV_MLAgent_0.0.5.3762474023_TS.zip", has_daemon=False)
EV_AGENT = AgentInfo('EVAgent', '0.4.15.1750449543', ITRON_CONTAINER_ID,
    f"{OWI_URL}DI_Agents/EVAgent/0.4.15/DevInternal/EVAgent_0.4.15.1750449543_TS.zip", depends_on=[TENSOR_AGENT, EV_ML_AGENT])

HAN_AGENT = AgentInfo("HANAgent", "3.2.39.145550592", ITRON_CONTAINER_ID,
    f"{OWI_URL}DI_Agents/HANAgent/DI_HAN_AGENT_3_2_39_REL_03-11-22_1419242/Release/signed-HANAgent_3.2.39.145550592_TS.zip")

DI_TEST_AGENT = AgentInfo("DITestAgent", "0.4.21.1980208074", ITRON_CONTAINER_ID,
    f"{OWI_URL}DI_Agents/DITestAgent/0.4.21/DevInternal/DITestAgent_0.4.21.1980208074_TS.zip")

V7_AGENT = AgentInfo("V7Agent", "0.3.9.2609897068",  ITRON_CONTAINER_ID,
    f"{OWI_URL}DI_Agents/V7Agent/0.3.9/Release/V7Agent_0.3.9.2609897068_TS.zip")

V7_CLONE_AGENT = AgentInfo("GTO12Agent", "0.3.4.23841262",  ITRON_CONTAINER_ID,
    f"{OWI_URL}DI_Agents/V7CloneAgents/GTO12Agent/Release/GTO12Agent_0.3.4.23841262_TS.zip")

P2P_AGENT = AgentInfo("ItronPubSubAgent", "0.4.25.2006012783", ITRON_CONTAINER_ID,
    f"{OWI_URL}DI_Agents/PubSubAgentP2P/0.4.25/ItronPubSubAgent/DevInternal/ItronPubSubAgent_0.4.25.2006012783_TS.zip")

Third_Party_PubSub_AGENT = AgentInfo("ThirdPartyPubSubAgent","0.4.24.377216952", THIRD_PARTY_CONTAINER_ID,
    f"{OWI_URL}DI_Agents/PubSubAgentP2P/0.4.24/ThirdPartyPubSubAgent/DevInternal/ThirdPartyPubSubAgent_0.4.24.377216952_TS.zip")

METROLOGY_DATA_AGENT = AgentInfo("MetrologyDataAgent","1.1.5.4150202388", ITRON_CONTAINER_ID,
    f"{OWI_URL}DI_Agents/MeterologyDataAgent/1.1.5/DevInternal/MetrologyDataAgent_1.1.5.4150202388_TS.zip")

ITRONPUBSUBAGENT2 = AgentInfo("ItronPubSubAgent2", "0.4.25.2006012783", ITRON_CONTAINER_ID,
    f"{OWI_URL}DI_Agents/PubSubAgentP2P/0.4.25/ItronPubSubAgent2/DevInternal/ItronPubSubAgent2_0.4.25.2006012783_TS.zip")

HID_AGENT = AgentInfo('HidTheftAgent', '0.3.110.4170148481', ITRON_CONTAINER_ID,
    f"{OWI_URL}DI_Agents/HidTheft/0.3.110/DevInternal/HidTheftAgent_0.3.110.4170148481_TS.zip", depends_on=[TENSOR_AGENT],
    reg_name = 'HID_Agent')


#Data Collection Agent[5:23 PM] Manikanthan, Shiyam


DATA_COLLECT_AGENT_3_72 = AgentInfo('DataCollectionAgent', '0.3.72.2607496414', ITRON_CONTAINER_ID,
    f"{OWI_URL}DI_Agents/DataCollectionAgent/0.3.72/DevInternal/DataCollectionAgent_0.3.72.2607496414_TS.zip")

DATA_COLLECT_AGENT = AgentInfo('DataCollectionAgent', '0.3.73.3768118381', ITRON_CONTAINER_ID,
    f"{OWI_URL}DI_Agents/DataCollectionAgent/0.3.73/DevInternal/DataCollectionAgent_0.3.73.3768118381_TS.zip")


#Location Awareness V2
LOCATION_AGENT = AgentInfo('LocationAwarenessAgentV2', '0.4.47.3881262520', ITRON_CONTAINER_ID,
    f"{OWI_URL}DI_Agents/LocationAwarenessAgentV2/0.4.47/DevInternal/LocationAwarenessAgentV2_0.4.47.3881262520_TS.zip")

available_agents = [
    HAN_AGENT, DI_TEST_AGENT, V7_AGENT, V7_CLONE_AGENT, P2P_AGENT,
    Third_Party_PubSub_AGENT, METROLOGY_DATA_AGENT, ITRONPUBSUBAGENT2, TENSOR_AGENT,
    HID_AGENT, EV_AGENT, EV_ML_AGENT, DATA_COLLECT_AGENT, LOCATION_AGENT
    ]


def agent_installed(g5m: SSHGen5Meter, logger: logging.Logger, agent_info: AgentInfo) -> bool:
    """
    Check if agent is installed and correct version

    :param g5m: meter to install agent on
    :param logger: logging fixture
    :param agent_info: agent to install
    :return: bool - True if agent installed and correct version, False if it is not installed or different version
    """
    agents = g5m.get_table("agentinformation")
    logger.debug("Agents installed: %s", agents)
    found_wrong = False
    for agent in agents:
        if agent['AgentName'] == agent_info.name:
            if agent['AgentVersion'] == agent_info.version:
                return True
            else:
                found_wrong = True

    if found_wrong:
        logger.info("Agent installed, but wrong version %s should be %s",
                    agent['AgentVersion'], agent_info.version)
    return False

def download_file(url, tempdir):
    r = requests.get(url, stream=True)
    r.raise_for_status()

    zipfile_name = os.path.join(tempdir, os.path.basename(url))
    with open(zipfile_name, 'wb') as file:
        for chunk in r.iter_content(chunk_size=8192):
            file.write(chunk)
            del chunk

    return zipfile_name

def install_agent(g5m: SSHGen5Meter, logger: logging.Logger, agent_info: AgentInfo, force=False) -> int:
    """
    Install agent and wait for installation to finish.  This function DOES NOT wait for the
    container system or agent to start

    :param g5m: meter to install agent on
    :param logger: logging fixture
    :param agent_info: agent to install
    :return int error code from improv. 0 = Success
    """
    for x in agent_info.depends_on:
        install_agent(g5m, logger, x, force)

    if not force and agent_installed(g5m, logger, agent_info):
        return 0

    exit_standalone(g5m, logger)

    with TemporaryDirectory() as tempdir:
        url = agent_info.url
        if url.startswith("http://") or url.startswith("https://"):
            zipfile_name = download_file(url, tempdir)
        else:
            zipfile_name = url

        ret = g5m.install(file=zipfile_name)

        # for pipeline execution, pull the install logs
        path = os.getenv("BUILD_ARTIFACTSTAGINGDIRECTORY", None)
        if path:
            try:
                _to = os.path.join(os.path.realpath(path), g5m.meter_name + "-install_logs")
                os.makedirs(_to,exist_ok=True)
                files = g5m.ls("/mnt/common/*.txt")

                for file in files:
                    name = os.path.basename(file)
                    logger.info(f"scp {file}, {os.path.join(_to, name)}")
                    g5m.get_file(file, os.path.join(_to, name))
                    g5m.command(f"rm {file}")

            except Exception as ex:
                logger.exception("Error downloading install logs")
                pass

        assert ret == 0, "Agent failed to install correctly"


    if ret == 0:
        assert agent_installed(g5m, logger, agent_info), "Agent failed to install"

    wait_for_cm_up(g5m, logger)

    return ret

DIINITOverlayUID = 50659329
StandAloneOverlayUID = 50659333
DbusContainer = 50593792


def any_in_stand_alone_init(g5m):

    table = g5m.sql_query_as_dict(
        f'select * from ContainerOverlay where OverlayUID = {StandAloneOverlayUID} or OverlayUID = {DIINITOverlayUID} ')

    stand_alone = False
    for x in table:
        if int(x['OverlayUID']) == StandAloneOverlayUID:
            stand_alone = True
    return stand_alone


def is_stand_alone_init(g5m, container=None):

    # overlays = g5m.sql_query_as_dict('SELECT DISTINCT ContainerUID FROM ContainerOverlay')

    table = g5m.sql_query_as_dict(
        f'select * from ContainerOverlay where OverlayUID = {StandAloneOverlayUID} or OverlayUID = {DIINITOverlayUID} ')
    state = 0
    STANDALONE = 1
    DIINIT = 2
    dups = []
    for x in table:
        assert x['ContainerUID'] not in dups, "Error, Container Overlay Table has duplicates"
        dups.append(x['ContainerUID'])

        if container and x['ContainerUID'] != container:
            continue

        if int(x['OverlayUID']) == StandAloneOverlayUID:
            state |= STANDALONE
        else:
            state |= DIINIT

    return state == STANDALONE

def get_installed_agents(meter, logger):
    installed_agents = []
    try:
        agents = meter.get_table("agentinformation")
        containers = meter.get_table("containeroverlay")
        for agent in agents:
            container_id = None
            for cont in containers:
                if cont['OverlayUID'] == agent['OverlayUID']:
                    container_id = cont['ContainerUID']
                    break
            assert container_id, "agent has no overlay, this is bad"

            # try to find a matching available agent
            found = None
            for avail in available_agents:
                if avail.name == agent['AgentName'] and avail.version == agent['AgentVersion']:
                    found = avail

            if found:
                installed_agents.append(found)
            else:
                # we don't have one, so make one, however we can't get the URL for re-installation in this case
                installed_agents.append(AgentInfo(agent['AgentName'], agent['AgentVersion'],container_id,None))

        logger.debug("Agents installed %s", [agent.name for agent in installed_agents])
    except DatabaseError:
        return installed_agents
    return installed_agents

def exit_standalone(meter: SSHGen5Meter, logger: logging.Logger, timeout: int = 9*60):
    if any_in_stand_alone_init(meter):
        cmd = "/usr/bin/SwitchDIInits.sh -d"
        logger.debug(cmd)
        meter.command_with_code(cmd)
        logger.info("standalone deactivated")


def enter_standalone(meter: SSHGen5Meter, logger: logging.Logger, timeout: int = 9*60):
    """ Enter standalone mode,  find the active agents and wait for the all to start """
    # make sure we are not in stand-alone mode (currently DI-tool requires no-hash mode)

    # make sure we are in stand-alone mode
    if not is_stand_alone_init(meter):
        cmd = "/usr/bin/SwitchDIInits.sh -s"
        logger.debug(cmd)
        meter.command_with_code(cmd)
        logger.info("standalone activated")

    else:
        logger.debug("already in standalone")

    wait_for_cm_up(meter, logger, timeout)

def install_agent_for_p2p(meter, logger, timeout=9*60):
    """ install the agent, disable agents with switchdiinits and
        restart dataserver in no-hash mode
    """

    install_agent(meter, logger, P2P_AGENT)

    # make sure we are not in stand-alone mode (currently DI-tool requires no-hash mode)
    exit_standalone(meter, logger)

    timeout = time.time() + timeout
    while time.time() < timeout:

        # now, copy over di-tool and get the version number
        meter.command("cp /usr/bin/di-tool /tmp/container/50593792/rootfs/usr/bin/")
        meter.command("cp /usr/lib/libditool.so.0 /tmp/container/50593792/rootfs/usr/lib/")
        version = meter.command("lxc-attach -P /tmp/container -n 50593792 -- /usr/bin/di-tool --version")
        if len(version) > 1:
            break
        time.sleep(10)

    assert 'Version' in version[0]
    no_hash = re.compile(re.escape("--no-hash"))

    ds = filter_ps(meter, "DataServer_Daemon")

    # fourth column of ps is dataserver and args, check for no-hash option
    if not ds or not no_hash.search(ds[0][4]):
        # now stop dataserver and re-start it in no-hash mode
        meter.command_with_code("/etc/init.d/DataServer stop")
        out = meter.command("/etc/init.d/DataServer no-hash")
        if list(filter(no_hash.search, out)):
            logger.info("DataServer restarted in no hash mode")

    return version[0]

def check_cm_ready(meter: SSHGen5Meter, logger, all_agents: List[AgentInfo], monitor: set):

    containers = [agent.container_id for agent in all_agents]

    # remove duplicates by converting to set
    containers = set(containers)

    # classify each agent by container
    ac = {container: [] for container in containers}
    for x in all_agents:
        if x.has_daemon:
            ac[x.container_id].append(x)

    # only wait for agents if we are in standalone
    matches_required = len(containers)*2

    # for each container, count agents only
    # if they are in standalone
    agent_match = set()
    will_register = set()
    found = set()
    for container in containers:
        if is_stand_alone_init(meter, container):
            agent_match |= set([agent.name + "_Daemon" for agent in ac[container]])
            will_register = will_register | set([agent.reg_name for agent in ac[container]])

    matches_required += len(agent_match)

    # get only container processes
    ps_stat = meter.get_process(FilterMatch("containe", column=FilterMatch.USER_COLUMN))
    container_manager_running = False

    daemons_up = 0
    if ps_stat:
        for line in ps_stat:
            logger.debug(line)
            if len(line) > 5:
                process = line[FilterMatch.PROCESS_COLUMN]
                if process.startswith('ContainerManager'):
                    container_manager_running = True
                if "/usr/bin/dbus-daemon" in process:
                    for cid in containers:
                        if cid in line[FilterMatch.ARGS_COLUMN]:
                            daemons_up += 1
                for match in agent_match:
                    if match in process:
                        daemons_up += 1
                        monitor |= set([match])
                        found |= set([match])

                if "{dvMonTC" in process:
                    daemons_up += 1

    # check the registration table for all agents expected to register (allow no Agents)
    try:
        table = meter.get_table("AgentRegistration")
        agents_registered = set([item['Name'] for item in table])
        missing = will_register - agents_registered
    except DatabaseError:
        missing = set()

    # if there are items in monitor that are not in found, then they were seen before and died
    if monitor - found:
        logging.error("Missing items have been found in the past, task died: %s", monitor-found)

    containers_up = False
    if not container_manager_running:
        logging.warning("Container manager is not running")
    else:
        containers_up = False
        active = Active_Containers(meter)
        if set(active) == set(containers):
            containers_up = True
            logging.info("Containers up")

    up = container_manager_running and containers_up and matches_required == daemons_up and not missing

    return up, (daemons_up, matches_required, missing, container_manager_running, found)

def wait_for_agents(meter: SSHGen5Meter, logger, agents:AgentInfo or list(AgentInfo), timeout: int, have_all=False):
    """ Wait for the container
    :param agents: a list of agents that we need to check that they are started
    :param logger: logging object
    :param timeout: how long to wait for everything to be up

    :return: None - Asserts when timeout occurs

    """
    
    start_time = time.time()
    end = start_time + timeout  # should not take more than 5 minutes
    refresh_container_time = start_time + 30
    thrice_time = start_time + (timeout/4)

    assert timeout/4 >= 120
    assert type(agents) is list
    if not have_all:
        all_agents = get_installed_agents(meter, logger)
        names_all = [agent.name for agent in all_agents]
        names_needed = [agent.name for agent in agents]
        assert set(names_needed) - set(names_all) == set(), "user asked to wait for an agent that is not present"
    else:
        all_agents = agents

    # now,  wait for the daemon to start
    monitor = set()
    while True:
        up, state = check_cm_ready(meter, logger, all_agents, monitor)
        daemons_up, matches_required, missing, cm_running, found = state
        if not up:

            """ TODO: get agent logs
            agent_info_all = meter.get_table("agentinformation")

            for agent in all_agents:
                for agent_info in agent_info_all:
                    if agent_info['AgentName'] == agent.name:
                        agent_id = agent_info['AgentUID']
                        agent_hex = hex(int(agent_id)).lstrip("0x")
                        start_dir = f'/tmp/container/{agent.container_id}/rootfs/tmp/agent/{agent_hex}'
            """

            if time.time() >= end:
                break

            # if there is no lxc-start within the refresh period, then someone probably left the meter
            # in a stopped state,  so send the refresh
            if cm_running:
                stdout = meter.command('ps -w | grep -i container')
                lxc_running = [x for x in stdout if ('lxc-start' in x.split()[4] and 'Z' not in x.split()[3])]

                if ((time.time() > refresh_container_time and not lxc_running) or
                        (time.time() > thrice_time)):

                    # agents have not come up.  Try one more time
                    thrice_time = refresh_container_time = time.time() + (timeout/4)
                    logging.warning("Containers have not started correctly,  Refressing container manager")
                    try:
                        stop_container(meter,2*60)
                    finally:
                        # NOTE: can't call refresh_container, as this would cause recursion
                        meter.command("dbus-send --type=signal --system --dest=com.itron.museplatform.ContainerManager"
                                    " /com/itron/museplatform/ContainerManager com.itron.museplatform.ContainerManager.Refresh")
            else:
                # if cm is not running, then it cant possbily be stopped, so disable refresh
                refresh_container_time = time.time() + timeout*2

            logger.info("waiting for agents to start: %s of %s running, found: %s not_registered: %s monitor: %s",
                        daemons_up, matches_required, found, missing, monitor)

            # avoid using lots of cpu, wait a few seconds and try again
            time.sleep(5)
        else:
            break

    assert up, "timeout error waiting for agents to start: %s of %s running, found: %s not_registered: %s monitor: %s" % (
                        daemons_up, matches_required, found, missing, monitor)

    logger.info("Agents up after %5.1f seconds", time.time() - start_time)

def is_process_running(meter, match,include_zombies=False):
    return True if filter_ps(meter,match,include_zombies=include_zombies) else False

def filter_ps(meter: SSHGen5Meter, match, column=FilterMatch.PROCESS_COLUMN, is_re=False, include_zombies=False):
    return meter.get_process(FilterMatch(match,column,is_re), include_zombies)

def add_agents_to_table(agents):
    for agent in agents:
        if agent not in available_agents:
            available_agents.append(agent)

def install_agent_and_activate(meter: SSHGen5Meter, logger: logging.Logger, agent: AgentInfo, timeout=9*60, force=False):
    install_multiple_agents_and_activate(meter, logger, [agent], timeout, force)

def wait_for_cm_up(meter: SSHGen5Meter, logger: logging.Logger, timeout: int = 9*60):
    """ wait for container manager to come up """
    all_agents = get_installed_agents(meter, logger)
    wait_for_agents(meter, logger, all_agents, timeout,have_all=True)

def delete_agent(meter: SSHGen5Meter, logger, name, agent_id):
    logger.trace("Deleteing agent %s using removeAgent script", name)
    stop_container(meter)
    meter.put_file('tests/test_meters/removeAgent.sh', '/mnt/common/removeAgent.sh')
    code, stdout, stderr = meter.command_all(f'chmod +x /mnt/common/removeAgent.sh; /mnt/common/removeAgent.sh {agent_id}')
    assert code == 0, "error while trying to delete agent:\nstdout: %s\nstderr: %s" % (stdout, stderr)
    wait_for_cm_up(meter, logger)

def remove_other_agents(meter, logger, needed_agents):
    """ if other agents are installed, trim them back to a reasonable set  """
    agents = meter.get_table("agentinformation")
    to_delete = []
    for agent in agents:

        skip = False
        for needed in needed_agents:
            if agent['AgentName'] == needed.name:
                skip = True
                break

        if not skip:
            to_delete.append(agent)

    # always delete these agents
    always_delete = ['MetrologyDataAgent', 'V7Agent']
    left = []
    for agent in to_delete:
        if agent['AgentName'] in always_delete:
            delete_agent(meter, logger, agent['AgentName'], agent['AgentUID'])
        else:
            left.append(agent)

    if len(needed_agents) + len(left) > 3 and left:
        for agent in left:
            delete_agent(meter, logger, agent['AgentName'], agent['AgentUID'])

def install_multiple_agents_and_activate(meter: SSHGen5Meter, logger: logging.Logger, agents: List[AgentInfo], timeout=9*60, force=False, remove_other=False):
    """ install agent and make sure it is running, then insert di-tool and
        return it's version number
    """

    if remove_other:
        remove_other_agents(meter, logger, agents)

    for agent in agents:
        wait_for_cm_up(meter, logger)
        install_agent(meter, logger, agent, force=force)


    # make sure we are in stand-alone mode
    enter_standalone(meter, logger)

def install_agent_and_di_tool(meter, logger, agent, timeout=9*60, force=False):
    """ install agent, then install di-tool into the agent container
        this allows the lxc-attach {container} di-tool to funtion

    :return: version of di-tool running in the container (verifies it functions)
    """
    install_agent_and_activate(meter, logger, agent, timeout=timeout, force=force)

    # di-tool not supported in third-party container
    if agent.container_id != ITRON_CONTAINER_ID:
        return

    timeout = time.time() + 120
    while time.time() < timeout:

        container = agent.container_id

        # now, copy over di-tool and get the version number
        meter.command("cp /usr/bin/di-tool /tmp/container/{agent.container_id}/rootfs/usr/bin/")
        meter.command("cp /usr/lib/libditool.so.0 /tmp/container/{agent.container_id}/rootfs/usr/lib/")
        ls = meter.command("lxc-attach -P /tmp/container -n {agent.container_id} -- ls -l /usr/bin/di-tool")
        ls1 = meter.command("ls -l /tmp/container/{agent.container_id}/rootfs/usr/bin/di-tool")
        ls2 = meter.command("ls -l /usr/bin/di-tool")
        version = meter.command("lxc-attach -P /tmp/container -n {agent.container_id} -- /usr/bin/di-tool --version")
        if len(version) > 1:
            break
        time.sleep(10)

    assert 'Version' in version[0]

    return version[0]

def get_policy_file(m,agent_name):
    stdout = m.command(f'sqlite3 --header /usr/share/itron/database/muse01.db "select id from AgentRegistration where name ={agent_name}"')
    if len(stdout)>0:
        agent_UID = int(stdout[1])
    file_name = "'PolicyFile.xml'"
    stdout = m.command(f'sqlite3 --header /usr/share/itron/database/muse01.db "select writefile({file_name},PolicyFile) from DIPolicyFile where AgentId={agent_UID}";')
    dir_path = os.path.dirname(os.path.abspath(__file__))
    file_path = dir_path+'/'
    m.get_file('/root/PolicyFile.xml',file_path)
    return agent_UID



def put_policy_file(m,agent_name,agent_info):
    dir_path = os.path.dirname(os.path.abspath(__file__))
    file_path = dir_path+'/PolicyFile.xml'
    m.put_file(file_path,'/root')
    stdout = m.command(f'sqlite3 --header /usr/share/itron/database/muse01.db "select id from AgentRegistration where name ={agent_name}"')
    if len(stdout)>0:
        agent_UID = int(stdout[1])
    file_name = "'PolicyFile.xml'"
    cmd = f'sqlite3 /usr/share/itron/database/muse01.db "replace into DIPolicyFile(AgentId,TimeStamp,PolicyFile) VALUES({agent_UID},0,readfile({file_name}))";'
    stdout = m.command(cmd)

    m.command('monit restart DataServer')
    cmd = 'ps | grep -i DataServer'
    output = wait_until_agent_up(m,agent_info,cmd)
    assert output!=0,"DataServer is not up"

    cmd = 'ps | grep Agent'
    output = wait_until_agent_up(m,agent_info,cmd)
    assert output!=0,"Agent is not installed"

def wait_until_agent_up(g5m,agent_info,cmd):
    stop = time.time() + (20*60)
    if not is_stand_alone_init(g5m):
        g5m.command('/usr/bin/SwitchDIInits.sh -s')
    while time.time()<=stop:
        output = []
        stdout = g5m.command(cmd)
        if(cmd == 'ps | grep Agent'):
            output = [x for x in stdout if('/usr/bin/' in x.split()[4] and f'{agent_info.name}_Daemon' in x.split()[4])]
        elif(cmd == 'ps | grep -i DataServer'):
            output = [x for x in stdout if('/usr/bin/' in  x.split()[4] and 'DataServer_Daemon'  in x.split()[4])]
        elif('pgrep ContainerManager'):
            output=stdout
        else:
            pass
        if(len(output)!=0):
                break
        time.sleep(10)
    return len(output)


def stat_check(g5m,dir,list_check):
    """
    dir="/mnt/common/lxc"
    list_check=["0755","containerd_u","containerd_g"] # list of list
    # value check list

    """
    cmd=f"stat {dir}"
    stat_out=g5m.command(cmd)
    stat_out=" ".join(stat_out)
    return all([(i in stat_out) for i in list_check])

def read_lid(g5m,logger,lid):
    code,result,error=g5m.command_all(f'TransactionProcess --event="MUSE_V1;ReadLid;{lid};"')
    result=" ".join(result)
    check = { "True": True,"False": False,"None":None}
    if code==0:
        result=result.split("=")[-1].lower().capitalize()
        result=check.get(result,int(result) if result.isnumeric() else result)
    else:
        logger.error("Error while trying to read : %s",lid)
        if error:
            logger.info("Error while trying to read:\nData: %s\nError: %s" % (result, error))
        else:
            logger.info("Error Data while trying to read:\nData: %s" % (result))

    return result

def write_lid(g5m,logger,lid,value):
    if not read_lid(g5m,logger,lid)==value:
        cmd=f'TransactionProcess --event="MUSE_V1;WriteLid;{lid};{value}"'
        g5m.command(cmd)
        logger.info("%s is set %s",lid,value)
        assert read_lid(g5m,logger,lid)==value,f"{lid} value is not set"


def log_table(g5m,file_name,log=True,start=None):
    """
    file_name= "/tmp/logs/ContainerManager/INFORMATION/ContainerManager.txt"
    start=time.time()
    """
    entries = []
    check = {"True": True,"False": False,"None":None}
    if log:
        log_data=g5m.command(f"/usr/bin/cdsEventLogDecoderV2 -f1 -i {file_name}")
    else:
        log_data=g5m.command(f"cat {file_name}")

    while len(log_data) > 0:
        headers= [i for i in log_data.pop(0).replace('"','').split(',')]
        if len(headers) > 2:
            break

    while len(log_data):
        values = [check.get(i,int(i) if i.isnumeric() else i) for i in log_data.pop(0).replace('"','').split(',')]
        data=dict(zip(headers,values))
        entries.append(data)

    if start:
        start= dt.fromtimestamp(start).strftime('%Y/%m/%d %H:%M:%S')
        a = dt.strptime(start, "%Y/%m/%d %H:%M:%S")
        log_change=[]
        for i in entries:
                date=re.findall(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}',i["Time"])[0]
                b = dt.strptime(date, "%Y/%m/%d %H:%M:%S")
                if b>=a:
                    log_change.append(i)
        entries=log_change
    return entries

def Active_Containers(meter_context,value="list"):
    cmd="dbus-send --system --dest=com.itron.museplatform.ContainerManager --print-reply --type=method_call /com/itron/museplatform/ContainerManager com.itron.museplatform.ContainerManager.GetContainerList"
    code, stdout, stderr = meter_context.command_all(cmd, splitlines=False)
    if code == 0:
        Container=re.findall(r"uint32 (\d+)", stdout)
        Container.sort()
        Container_path=re.findall(r"unix:path=(/tmp/container/\d+/container_bus_socket)",stdout)
        Container_path.sort()
        req={"list":Container,"path":Container_path}
        return req.get(value,None)
    else:
        # immediately after an install, the container manager may take some time to start.  Therefore
        # the system may encounter dbus errors
        LOGGER.error("Container manager returned error %s.  Contaner manager probably not running. stderr: %s", code, stderr)
    return []

def refresh_container(meter,logger,timeout=9*60):
    meter.command_with_code("dbus-send --type=signal --system --dest=com.itron.museplatform.ContainerManager /com/itron/museplatform/ContainerManager com.itron.museplatform.ContainerManager.Refresh")
    wait_for_cm_up(meter, logger, timeout)

def stop_container(meter,timeout = 10*60):
    stop = time.time() + timeout
    while time.time()<=stop:
        meter.command_with_code('dbus-send --type=signal --system --dest=com.itron.museplatform.ContainerManager /com/itron/museplatform/ContainerManager com.itron.museplatform.ContainerManager.StopAllContainer')
        output= not Active_Containers(meter)
        if output :
            break
        time.sleep(10)
    assert output , "All container is not stoped"
