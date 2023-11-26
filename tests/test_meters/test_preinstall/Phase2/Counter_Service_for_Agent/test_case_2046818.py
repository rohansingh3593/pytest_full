"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase2
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2046818
===================================================================================================
Test Case      : 2046818
Description    : Verify if the Agent Alarm messages from DI-Agent application is stored in the DailyAlarmMessagesSent column of AgentFeatureDataCounter table
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Check if the agent is up and running using the command ps | grep Agent

Step 2 - 
Agent should be up with Agent name and Agent pid

Step 3 - 
Check the AgentFeatureDataCounter  using the command sqlite3 --header
/usr/share/itron/database/muse01.db \"select * from AgentFeatureDataCounter;\"

Step 4 - 
The column DailyAlarmMessagesSent should have integer (not null) values when an upstream data  is
stored.. # sqlite3 --header /usr/share/itron/database/muse01.db \"select * from AgentFeatureDataCoun
ter;\"\nAgentId|FeatureId|DailyUpstreamDataSent|P2PBroadcastDataSent|DailyP2PUnicastDataSent|DailyAl
armMessagesSent|TimeStamp\n50528128|50548608|1505|0|0|0|1602547200\n50528128|50593780|980|0|0|0|1602
547200\n50528128|50593776|48233|0|0|280|1602547200\n50528128|50536320|99|0|0|1|1602547200\n50528128|
50593777|1900|0|0|0|1602547200\n50528128|50593778|464|0|0|0|1602547200\n50528128|50528256|90|0|0|0|1
602547200\n50528128|50540416|94|0|0|0|1602547200


===================================================================================================


"""
import pytest
from tests.test_meters.utils import install_agent_and_activate,get_installed_agents,wait_for_agents,HAN_AGENT


# AUTOGENERATED Test Case 2046818

# @pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
@pytest.mark.regress_smoke
@pytest.mark.suite_id("2046635")
@pytest.mark.test_case("2046818")
def test_case(preinstalled_meter, logger):
        logger.trace("Executing Test Case 2046818 - Verify if the Agent Alarm messages from DI-Agent application is stored in the DailyAlarmMessagesSent column of AgentFeatureDataCounter table")
        logger.trace('Step 1')
        installed_agents = get_installed_agents(preinstalled_meter,logger)
        if(not installed_agents):
            install_agent_and_activate(preinstalled_meter, logger, HAN_AGENT)
        else:
            logger.trace('Step 2')
            wait_for_agents(preinstalled_meter, logger, installed_agents, 20*60)
        
        logger.trace('Step 3')
        stdout = preinstalled_meter.sql_query("select DailyAlarmMessagesSent from AgentFeatureDataCounter;")
        logger.trace('Step 4')
        for num in stdout:
            assert num is not None

