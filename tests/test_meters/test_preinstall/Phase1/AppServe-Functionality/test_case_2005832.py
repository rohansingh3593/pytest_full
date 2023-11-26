
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2005832
===================================================================================================
Test Case      : 2005832
Description    : Verify unInstalling Agents using GMR
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Trigger GMR using the below command/usr/share/itron/scripts/GlobalMeterReset.sh

Step 2 - 


Step 3 - 
Wait till the meter is back

Step 4 - 


Step 5 - 
Verify if the existing agents were uninstalled

Step 6 - 
ps | grep -i agent  -- should not show the Agents running\n

Step 7 - 
Verify no DB entries for Agents

Step 8 - 
sqlite3 --header /usr/share/itron/database/muse01.db \"select * from AgentInformation\"\n-- should
be empty


===================================================================================================


"""
import pytest
import time
from tests.test_meters.utils import Third_Party_PubSub_AGENT,install_agent_and_activate
# @pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2012056")
@pytest.mark.test_case("2005832")
@pytest.mark.gmr_meter
 
@pytest.mark.parametrize("agent_info", [Third_Party_PubSub_AGENT])
def test_case(preinstalled_meter, logger,agent_info):
    logger.trace("Executing Test Case 2005832 - Verify unInstalling Agents using GMR")
    logger.trace('Step 1')
    install_agent_and_activate(preinstalled_meter, logger, agent_info)
    agent_data=preinstalled_meter.sql_query('select AgentName from agentinformation;')
    assert 'ThirdPartyPubSubAgent' in agent_data
    preinstalled_meter.gmr()
    logger.trace('Step 2')
    logger.trace('Step 3')
    """Wait till the meter is back"""
    logger.trace('Step 4')
    logger.trace('Step 5')
    """Verify if the existing agents were uninstalled"""
    stdout = preinstalled_meter.command('ps | grep -i Agent')
    logger.trace('Step 6')
    output = [x for x in stdout if('/usr/bin/' in x.split()[4] and f'{agent_info.name}_Daemon' in x.split()[4])]
    assert len(output)==0
    logger.trace('Step 7')
    tables=preinstalled_meter.sql_query('.tables')  
    tables = [" ".join(t.split()) for t in tables]
    logger.trace('Step 8')
    assert 'AgentInformation' not in tables
