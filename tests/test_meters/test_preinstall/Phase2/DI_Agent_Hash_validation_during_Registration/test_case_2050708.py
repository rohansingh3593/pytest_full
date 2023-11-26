"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase2
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2050708
===================================================================================================
Test Case      : 2050708
Description    : Verify ApplicationServices(AgentAPI) supplies the calculated SHA256 has value to theregistration request.
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Verify from Log  \"/tmp/logs/DataServer/INFORMATION/DataServer.txt\"
Step 2 - 
log messages
Step 3 - 
extract log file DataServer.txt by the command and verify the relevant log message as below  Ex:
cdsEventLogDecoderV2 -f1 -i /tmp/logs/DataServer_Daemon/INFORMATION/DataServer_Daemon.txt
Step 4 - 
 ]DITestAgentDaemon registered successfullyDITestAgentDaemon.Agent Registration success\"{2022/11/28
19:54:49 [66168799.380]}\",\"None\",\"Agent hash retrieved and matches policy.\",\"INFORMATION\",\"D
ataServer_Daemon\",\"\",\"\",\"10.5.735.1\",\"\",\"46\",\"4157\"\n\"{2022/11/28 19:54:49
[66168799.381]}\",\"None\",\"Hash key matches, Proceeding with Registration.\",\"INFORMATION\",\"Dat
aServer_Daemon\",\"\",\"\",\"10.5.735.1\",\"\",\"46\",\"4157\"\n\"{2022/11/28 19:54:49
[66168799.391]}\",\"None\",\"Registration successfully done
!!!\",\"INFORMATION\",\"DataServer_Daemon\",\"\",\"\",\"10.5.735.1\",\"\",\"46\",\"4157\"\n\n
Step 5 - 
Ensure Agent is functional.
Step 6 - 
Agent 1sec log should run.
===================================================================================================
"""

import pytest
import time
from tests.test_meters.utils import DI_TEST_AGENT,install_agent_and_activate,is_process_running,wait_for_agents
from tests.test_meters.rohan_utils import absolute_command,Dataserver_refresh,All_Agent_Table_Refresh,is_log_file_available
from tests.test_meters.event_utils import get_meter_system_time,wait_for_eventlog_entry
import re
#@pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2050697")
@pytest.mark.test_case("2050708")
@pytest.mark.parametrize("agent_info",[DI_TEST_AGENT])
#@pytest.mark.parametrize('execution_number', range(3))
def test_case(preinstalled_meter, logger,agent_info):
    logger.trace("Executing Test Case 2050708 - Verify ApplicationServices(AgentAPI) supplies the calculated SHA256 has value to theregistration request.")
    
    logger.trace('Step 1')
    install_agent_and_activate(preinstalled_meter,logger,agent_info)
    start_time = get_meter_system_time(preinstalled_meter)

    absolute_command(preinstalled_meter,"/usr/bin/SwitchDIInits.sh -s")
    agent_stop = time.time() + 5*60
    while time.time()<=agent_stop:
        value = not is_process_running(preinstalled_meter,f'{DI_TEST_AGENT.name}_Daemon')
        if value:
            logger.info("All agent is Stoped")
            break
        time.sleep(2)
    assert value,"All agent is not Stoped after SwitchDIInits.sh command "
    wait_for_agents(preinstalled_meter, logger, [DI_TEST_AGENT], 20*60)

    logger.trace('Step 2')
    
    logger.trace('Step 3')

    file_name = '/tmp/logs/DataServer_Daemon/INFORMATION/DataServer_Daemon.txt'
    found1 = wait_for_eventlog_entry(preinstalled_meter, logger, start_time,file_name,"Agent hash retrieved and matches policy",5*60)

    logger.trace('step 4')
    assert found1 , "Agent registration not notify in the log message"


    logger.trace('Step 5')
    assert is_process_running(preinstalled_meter,f'{agent_info.name}_Daemon'),"Agent not properly Functinoal"

    logger.trace('Step 6')

    stop = time.time() + (2*60)
    #prev_time = int(preinstalled_meter.command(r"date -u \+%s")[0])
    prev_time = int(absolute_command(preinstalled_meter, r"date -u \+%s")[0])
    logger.trace("Time before checking for 1sec log"+str(prev_time))

    # checking agent log file is available
    log_file=is_log_file_available(preinstalled_meter,DI_TEST_AGENT)
    DI_log_cmd=f'cat {log_file}'

    # # It will check the DI TEST AGENT lid have a access.
    stop=time.time() + 5*60
    c=0
    while stop>time.time():
        check = "\n".join(absolute_command(preinstalled_meter,DI_log_cmd)[-20:])
        value1 = 'Log:DBG:[TS,VA,VB,VC,IA,IB,IC,PA,PB,PC,QA,QB,QC,Temp,Freq]' in check
        compare_timestamp=re.findall(r"\n(\d+)\n",check)
        logger.info("Available Timestamp for the Message : %s",", ".join(compare_timestamp[-3:]))
        value3 = int(compare_timestamp[-1]) > prev_time if compare_timestamp else False
        status = value1 and value3
        if status:
            break
        else:
            c+=1
        if c%5==0:
            # it will refresh the dataserver after 25 sec if not found
            # Restart the DataServer
            Dataserver_refresh(preinstalled_meter)                
        if c==19:
            # it will refresh all agent table 95 min if not found
            All_Agent_Table_Refresh(preinstalled_meter,DI_TEST_AGENT)                
            c=0
        time.sleep(5)

    assert status ,"Agent not showing one sec logs"

   