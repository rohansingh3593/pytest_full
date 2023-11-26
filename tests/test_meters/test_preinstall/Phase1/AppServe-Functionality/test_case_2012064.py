"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2012064
===================================================================================================
Test Case      : 2012064
Description    : Verify AgentEvents in Meter database
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Install given AppServe Software

Step 2 - 
Meter should update with new software

Step 3 - 
Install any agent in Meter and check AgentEvents in databasesqlite3 --header
/usr/share/itron/database/muse01.db \"select * from AgentEvents\"\n

Step 4 - 
Data should be available in data base with no errors and all the events should update.Eg :  #
sqlite3 --header /usr/share/itron/database/muse01.db \"select * from AgentEvents\"\nId|AgentId|Event
Id|FeatureId|TimeStamp|Data|isUnsentAlarm\n1|33685505|1|33759233|1655790264|93#140737488355328#0|0\n
2|50528119|12|50536311|1655790465|98#0302ff77#0.4.24#10.5.543.1#1.7.314.0#0303ffdc 03031f77 03032f77
03033f77 03034f77 ##800#4#1024#2|0\n


===================================================================================================


"""

import pytest
import time
from tests.test_meters.utils import DI_TEST_AGENT,install_agent_and_activate
@pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2012056")
@pytest.mark.test_case("2012064")
@pytest.mark.parametrize("agent_info", [DI_TEST_AGENT])
def test_case(preinstalled_meter, logger,agent_info):
    logger.trace("Executing Test Case 2012064 - Verify AgentEvents in Meter database")
    logger.trace('Step 1')
    """AppServe is installed with preinstalled_meter fixture"""
    logger.trace('Step 2')
    prev_agentevents_data=preinstalled_meter.sql_query("select data from agentevents where agentid=50528128;")
    install_agent_and_activate(preinstalled_meter, logger, agent_info)
    logger.trace('Step 3')
    logger.trace('Step 4')
    stop = time.time() + (2*60)
    while time.time()<=stop:
        cur_agentevents_data=preinstalled_meter.sql_query("select data from agentevents where agentid=50528128;")
        if(len(prev_agentevents_data)<len(cur_agentevents_data)):
            break
        else:
            time.sleep(10)
    data=preinstalled_meter.sql_query("select data from agentevents where agentid=50528128 and data LIKE \"98#%\" order by timestamp desc limit 1;")[0]
    assert "98#" in data,"Data is not available in data base with success message"
        
    