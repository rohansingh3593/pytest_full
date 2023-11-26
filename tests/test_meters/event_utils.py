import time
import datetime
import re
import os
import logging

LOGGER = logging.getLogger(__name__)



def get_meter_date(meter, hw_time=False):
    fmt = "%Y.%m.%d-%H:%M:%S %z"
    if hw_time:
        hw_time = meter.command("/sbin/hwclock -r")[0]
        # remove "0.00000 seconds" and add utc offset
        hw_time = " ".join(hw_time.split()[:-2]) + " +0000"
        date = datetime.datetime.strptime(hw_time, "%a %b %d %H:%M:%S %Y %z")
    else:
        date = datetime.datetime.strptime(meter.command(f'date -u +"{fmt}"')[0], fmt)
    return date

def get_meter_system_time(meter):

    """
    Get the meter exact time from meter.
    It will send a random message to system files and fetch that time and start the testing
    """

    from tests.test_meters.utils import HAN_AGENT,install_agent_and_activate,Active_Containers
    import uuid


    agent = HAN_AGENT
    # For message send to meter at least it have a itron-container
    if agent.container_id not in Active_Containers(meter):
        install_agent_and_activate(meter,LOGGER,agent)

    file1 = '/tmp/logs/SYSLOG/INFORMATION/SYSLOG.txt'
    file2 = '/mnt/pouch/LifeBoatLogs/SYSLOG.txt'

    meter_time_stamp=int(meter.command(r"date +%s")[0])
    LOGGER.info('starting time timestamp of Meter : %s',meter_time_stamp)
    # find the the start time
    start_message = f'start {os.path.basename(__file__)} {meter_time_stamp}-{uuid.uuid1()}'
    LOGGER.info(start_message)
    found = False
    timeout = time.time() + 5*60
    while time.time() <= timeout and not found:
        
        code1,_=meter.command_with_code(f'lxc-attach -P /tmp/container -n {agent.container_id} -- logger -p INFO "{start_message}"')
        code2,_=meter.command_with_code(f'lxc-attach -P /tmp/container -n {agent.container_id} -- logger -p ERROR "{start_message}"')
        #---------------------------------------------------------------------------------------------#
        # need to check the message in the System Info  and system Error file 
        if code1 == code2 == 0:
            for _ in range(5):
                found_start_time_infolog = wait_for_eventlog_entry_with_rotator(meter, LOGGER, get_epoch(), 
                                            file1, start_message, timeout=10, do_assert=False)
                found_start_time_lifeboat = wait_for_eventlog_entry_with_rotator(meter, LOGGER, get_epoch(), 
                                                file2, start_message, timeout=10, do_assert=False) if found_start_time_infolog[0] else  False

                found = (found_start_time_infolog[0] and found_start_time_lifeboat[0]) if (found_start_time_infolog and found_start_time_infolog) else False
                if found:
                    LOGGER.info("The message is got from the Info and error in Event File")
                    break
                time.sleep(2)

        time.sleep(10)

    assert found,"we did not get the message "  

    if found_start_time_lifeboat[1]!=found_start_time_lifeboat[1]:
        LOGGER.warning(abs(found_start_time_lifeboat[1]-found_start_time_lifeboat[1]))
        LOGGER.warning("Logger are not in syn")


    fetch_time = min(found_start_time_lifeboat[1],found_start_time_lifeboat[1])
    LOGGER.info(fetch_time)

    meter_time = get_meter_date(meter)
    if fetch_time != meter_time:
        LOGGER.info(abs(fetch_time-meter_time))
        LOGGER.info("Logger and meter time is not in syn")

    return fetch_time

def get_epoch():
    """ an old time that can be used if nothing present """
    return datetime.datetime.strptime("1900/1/1 +0000", "%Y/%m/%d %z")

def scan_logfile(meter, logger, start_date, logfile, moniker, line_date=get_epoch()):

    if type(moniker) is str:
        moniker = re.compile(re.escape(moniker))

    code,container_manager = meter.command_with_code(f'cdsEventLogDecoderV2 -f1 -i {logfile}')
    found = False 
    if code ==0:
        for line in container_manager:
            # example log line:
            # "{2023/02/15 19:35:07 [50730025.964]}","None","TargetLxcContainerInterface.cpp at [195](pid:13789/thr:13789): StopContainer","INFORMATION","ContainerManager","","","10.5.770.1","MUSE","43","13789"

            # log lines that don't start with time are continuations of previous line, so same date
            if line.startswith('"{'):
                stamp = line.split("{")[1].split('[')[0] + "+0000"
                line_date = datetime.datetime.strptime(stamp, "%Y/%m/%d %H:%M:%S %z")
                logger.debug("Start: %s Diff: %s Entry: %s %s : %s", start_date, (line_date - start_date).total_seconds(), line_date, stamp,line)

            if line_date > start_date and moniker.search(line):
                logger.debug("found in %s Start: %s Diff: %s Entry: %s %s : %s", logfile, start_date, (line_date - start_date).total_seconds(), line_date, stamp,line)
                found = True
                break

    return found, line_date

def wait_for_eventlog_entry_with_rotator(meter, logger, start_date, logfile, moniker, timeout=120, do_assert=True):
    """ looks for log entry, also includes .gz files in log directory

    @param meter: meter connection object
    @param logger: were to output debug info
    @param start_date: meter time for log entries to look at (only later entries included)
                       caller should find log entry at the start of the test and
                       pass it here to exclude log entries from previous tests
    @param logfile: meter log file to scan (using cdsEventLogDecoderV2)
    @param moniker: what to look for.  can be a string or re
    @param timeout: how long to search for value
    @param do_asert: if true, assert if the match is not found (default), if false return True if found

    @returns  tuple(found, timestamp) return boolean found (True if found), and timestamp of line where found
    """
    stop = time.time() + timeout
    found = False

    line_date = get_epoch()
    while time.time() < stop and not found:
        files = meter.ls(logfile+"*")
        for file in files:
            found, line_date = scan_logfile(meter, logger, start_date, file, moniker, line_date)
            if found:
                break

        if not found:
            logger.trace("Waiting for event log")
            time.sleep(5)

    if do_assert:
        assert found, f"could not find {moniker} in file: {logfile}"

    return found, line_date

def wait_for_eventlog_entry(meter, logger, start_date, logfile, moniker, timeout=120, do_assert=True):
    """ Wait for log entry to show up on meter logs

    @param meter: meter connection object
    @param logger: were to output debug info
    @param start_date: meter time for log entries to look at (only later entries included)
                       caller should find log entry at the start of the test and
                       pass it here to exclude log entries from previous tests
    @param logfile: meter log file to scan (using cdsEventLogDecoderV2)
    @param moniker: what to look for.  can be a string or re
    @param timeout: how long to search for value
    @param do_asert: if true, assert if the match is not found (default), if false return True if found

    @returns  str: string if found, False if not found (or raises assert)
    """
    stop = time.time() + timeout
    found = False

    while time.time() < stop and not found:
        found,_ = scan_logfile(meter, logger, start_date, logfile, moniker)
        if not found:
            logger.trace("Waiting for event log")
            time.sleep(5)

    # time taken to get that log from the file 
    time_taken = time.time() - (stop - timeout)
    
    if found:
        logger.info("Took %s seconds to find %s", time_taken, moniker)
    else:
        logger.warning("%s not found in %s seconds", moniker, time_taken)

    if do_assert:
        assert found, f"could not find {moniker} in file: {logfile}"

    return found