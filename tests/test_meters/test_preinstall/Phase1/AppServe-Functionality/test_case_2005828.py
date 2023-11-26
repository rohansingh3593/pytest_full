"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2005828
===================================================================================================
Test Case      : 2005828
Description    : Verify Agent functionality
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Install Agent using FDM in Meter (previous testcase)

Step 2 - 
Agent should install

Step 3 - 
Activate the AgentSwitchDIInits.sh -s\n

Step 4 - 


Step 5 - 
Ensure the Agent is running (PID and Daemon should be available)

Step 6 - 
# ps | grep -i Agent\n 1905 containe  5956 S    /usr/bin/0302ff80/DITestAgent_Daemon\n 1965 root
1108 S    grep -i Agent

Step 7 - 
Agent Registration table should be having the Agent details

Step 8 - 
sqlite3 --header /usr/share/itron/database/muse01.db \"select * from AgentRegistration\"\n

Step 9 - 
Check if the Agent logs using below command.\ntail -f
/tmp/container/50593792/rootfs/tmp/agent/0302ff80/0302ff80_log\n

Step 10 - 
Agent should show one sec logs


===================================================================================================


"""
import pytest
import time
from tests.test_meters.utils import DI_TEST_AGENT, install_agent_and_activate,filter_ps

@pytest.mark.skip(reason="1sec log failing - add a check for log file available")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2012056")
@pytest.mark.test_case("2005828")
@pytest.mark.parametrize("agent_info", [DI_TEST_AGENT])
def test_case(preinstalled_meter, logger, agent_info):
    logger.trace("Executing Test Case 2005828 - Verify Agent functionality")
    logger.trace('Step 1')
    install_agent_and_activate(preinstalled_meter,logger,agent_info)
    logger.trace('Step 2')
    logger.trace('Step 3')
    logger.trace('Step 4')
    """ /usr/bin/SwitchDIInits.sh -s command run inside install_agent_and_activate function"""
    logger.trace('Step 5')
    logger.trace('Step 6')

    running_agent = filter_ps(preinstalled_meter,f'{agent_info.name}_Daemon')
    assert running_agent, f"{agent_info.name} is not Running"
    assert int(running_agent[0][0]) > 0, f"{agent_info.name} is not Running with pid"

    logger.trace('Step 7')
    stop = time.time() + (5*60)
    while time.time()<=stop:
        agent_reg_list = preinstalled_meter.sql_query('select Name from AgentRegistration')
        status = agent_info.name in agent_reg_list
        if status:
            break
        time.sleep(10)
    logger.trace('Step 8')
    assert status,f"{agent_info.name} is not register in the AgentRegistration table "
    logger.trace('Step 9')
    stop = time.time() + (5*60)
    count = 0

    time_out=time.time() + 60
    while time_out>time.time():    
        code,prev_time=preinstalled_meter.command_with_code(r"date +%s")
        if code == 0:
            prev_time=int(preinstalled_meter.command_with_code(r"date +%s")[0])
            logger.info('starting time timestamp of Meter : %s',prev_time)
            break
        time.sleep(10)

    assert code == 0 ,"Time command is not executed"


    logger.trace("Time before checking for 1sec log"+str(prev_time))
    cur_time = 0
    while time.time()<=stop:
        one_log = preinstalled_meter.command('tail -s 1 /tmp/container/50593792/rootfs/tmp/agent/0302ff80/0302ff80_log')
        logger.trace('Step 10')
        log_data = ''.join(one_log)
        logger.trace(one_log)
        if('Log:DBG:[TS,VA,VB,VC,IA,IB,IC,PA,PB,PC,QA,QB,QC,Temp,Freq]' in log_data):
            for val in one_log:
                try:
                    cur_time = (int(val))
                except ValueError:
                    pass
                if(cur_time > prev_time):
                    prev_time = cur_time
                    count = count + 1
                
        if(count>3):
            break
        else:
            time.sleep(10)  

    assert count > 3,"Agent not showing one sec logs"
