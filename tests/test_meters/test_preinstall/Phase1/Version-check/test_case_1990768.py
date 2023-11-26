"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/1990768
===================================================================================================
Test Case      : 1990768
Description    : Verify if we are able to retrieve the ApplicationService component version from DI agent applications.
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 -
Install any agent after the installation of Appserv.  ex: DItest Agent

Step 2 -


Step 3 -
Start the agent with: #SwitchDIInits.sh -s

Step 4 -
ps | grep Agent should show agent running

Step 5 -
Check the agentevents table#sqlite3 --header /usr/share/itron/database/muse01.db \"select * from
AgentEvents\"

Step 6 -
Chech for the AppService version installed in the startup message with 98#
data.2|50528128|12|50536320|1663360976|98#0302ff80#0.4.23#10.5.743.1#1.7.400.0#3031f80 303fff0
303fff1 303fff2 303fff3 3032f80 3034f80 3033f80##2560#4#1024#2|0

Step 7 -
Check the Appserv version installed matches with the agentevents table output

Step 8 -
Both the versions should match


===================================================================================================


"""
import pytest
from tests.test_meters.utils import install_agent_and_activate,is_process_running,DI_TEST_AGENT
import time

# AUTOGENERATED Test Case 1990768

# @pytest.mark.xfail(reason="if agent already installed by previous version, check fails")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("1990124")
@pytest.mark.test_case("1990768")
def test_case(preinstalled_meter, logger):
    logger.trace("Executing Test Case 1990768 - Verify if we are able to retrieve the ApplicationService component version from DI agent applications.")

    logger.trace('Step 1')
    agent = DI_TEST_AGENT
    install_agent_and_activate(preinstalled_meter,logger,agent)

    # Getting the Agent ID form the Agent Information Table
    query=f'select AgentUID from agentinformation where AgentName = "{agent.name}";'
    assert preinstalled_meter.sql_query(query),f"{agent.name} is not installed in the meter"
    Agent_id=preinstalled_meter.sql_query(query)[0]
        
    logger.trace('Step 2')
    logger.trace('Step 3')
    """SwitchDIInits.sh -s run in function wait_until_agent_up"""
    logger.trace('Step 4')
    assert is_process_running(preinstalled_meter,f'{agent.name}_Daemon'),f'{agent.name} is not running'
    logger.trace('Step 5')
    logger.trace('Step 6')

    time_out=time.time() + 5*60
    while time_out>time.time():
        agent_data=preinstalled_meter.sql_query(f"select Data from AgentEvents where agentid = {Agent_id} and data LIKE \"98#%\" order by timestamp desc")
        if agent_data:
            logger.info('Agent is successfully running')
            break
        time.sleep(10)
    assert agent_data,'Agent is not running'
    data=agent_data[0].split("#")

    """stdout has this data like:98#0302ff77#0.4.25#10.5.765.1#3.1.134.0#0303ffdc 03031f77 03032f77 03033f77 03034f77 ##800#4#1024#2|1671632008
       so need to split with # to fetch version which will get at 4th index after split"""
    version_from_table = data[4]
    logger.trace('Step 7')
    stdout = preinstalled_meter.command('TransactionProcess --event="MUSE_V1;ReadLid;ILID_DATASERVER_APPSERV_FW_VERSION;"')
    version = stdout[0].split('=')
    version_installed = version[1]
    logger.trace('Step 8')
    assert version_from_table == version_installed,'Both the versions is not match'