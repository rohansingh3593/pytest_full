
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase2
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2050727
===================================================================================================
Test Case      : 2050727
Description    : Verify if the DI-Agent Application is able to send DI outcome/upstream data to the headend.
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 -
Make sure the agent is running

Step 2 -
Agent should be up and running with its PID and agent name

Step 3 -
In the agent data table or agent events table, you should be able to see data being send to the
headend. #sqlite3 --header /usr/share/itron/database/muse01.db \"select * from AgentEvents;\"

Step 4 -
# sqlite3 --header /usr/share/itron/database/muse01.db \"select * from Agentevents;\"\nId|AgentId|Ev
entId|FeatureId|TimeStamp|Data|isUnsentAlarm\n1|50528128|12|50536320|1604138889|98#0302ff80#0.2.2#10
.0.621.1#1.3.227.0#3031f80 303fff0 303fff1 303fff2 303fff3 303fff4 3032f80 3034f80 3033f80##2048#2|0
\n2|50528128|1|50593776|1604139000|92#Event#Passed#20201031101000,TestEvent1,1|0\n3|50528128|1|50593
776|1604139000|92#Event#Passed#20201031101000,TestEvent2,2|0\n4|50528128|1|50593776|1604139000|92#Al
arm#Passed#20201031101000,TestAlarm1,1|0\n5|50528128|1|50593776|1604139000|92#Alarm#Passed#202010311
01000,TestAlarm2,2|0\n6|50528128|1|50593776|1604139300|92#Event#Passed#20201031101500,TestEvent1,3|0
\n7|50528128|1|50593776|1604139300|92#Event#Passed#20201031101500,TestEvent2,4|0\n8|50528128|1|50593
776|1604139300|92#Alarm#Passed#20201031101500,TestAlarm1,3|0\n9|50528128|1|50593776|1604139300|92#Al
arm#Passed#20201031101500,TestAlarm2,4|0\n10|50528128|12|50536320|1604139395|98#0302ff80#0.2.2#10.0.
621.1#1.3.227.0#3031f80 303fff0 303fff1 303fff2 303fff3 303fff4 3032f80 3034f80 3033f80##2048#2|0\n


===================================================================================================


"""
import pytest
import time
from tests.test_meters.rohan_utils import Config_push,agent_Config_collect,file_content_change,Container_stop,Dataserver_refresh,All_Agent_Table_Refresh
from tests.test_meters.utils import DI_TEST_AGENT, Active_Containers, get_installed_agents, install_agent_and_activate, refresh_container
# AUTOGENERATED Test Case 2050727

@pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2050497")
@pytest.mark.test_case("2050727")
def test_case(preinstalled_meter, logger, workdir):
    logger.trace("Executing Test Case 2050727 - Verify if the DI-Agent Application is able to send DI outcome/upstream data to the headend.")

    logger.trace('Step 1')
    agent = DI_TEST_AGENT
    featureId = '50593776'
    install_agent_and_activate(preinstalled_meter,logger,agent)


    # Getting the Agent ID form the Agent Information Table
    query=f'select AgentUID from agentinformation where AgentName = "{agent.name}";'
    agent_id=preinstalled_meter.sql_query(query)[0]

    logger.trace('Step 2')
    logger.trace('Step 3')

    try:
        # Get configuration file from the featureConfiguration table
        file = agent_Config_collect(preinstalled_meter,agent,featureId,base_dir=workdir)

        # Update the configuration file
        file_content_change(preinstalled_meter,file,'<parameter name="EventActive" value="0"/>','<parameter name="EventActive" value="1"/>')
        file_content_change(preinstalled_meter,file,'<parameter name="EventFrequency" value="00:05:00"/>','<parameter name="EventFrequency" value="00:00:15"/>')

        # Push configuration file to the featureConfiguration table
        Config_push(preinstalled_meter,featureId)

        logger.trace('Step 4')
        c = 0
        stop = time.time() + (5*60)
        while time.time()<=stop:
            query = f"select data from AgentEvents where agentid ={agent_id} and featureid = {featureId}"
            AgentEvents_data = preinstalled_meter.sql_query(query)

            value1 = '92#Event#' in AgentEvents_data[-1] if AgentEvents_data else False
            if value1 :
                break
            # if c%5==0:
            #     # it will refresh all agent table 25 sec if not found
            #     All_Agent_Table_Refresh(preinstalled_meter,agent)
            #     c=0
            # time.sleep(5)

        assert value1 , 'Agent event is not present in the AgentEvents table '

    finally:
        # Update the Data file at the FeatureConfiguration table at Initial State
        agent_Config_collect(preinstalled_meter,agent,featureId,base_dir=workdir,force=True)
        Config_push(preinstalled_meter,featureId)
