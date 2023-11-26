"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase2
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2060591
===================================================================================================
Test Case      : 2060591
Description    : Verify if the AgentFeatureDataCounter table exists after reboot
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Use the command reboot and wait for the agent to come up
Step 2 - 
Check the AgentFeatureDataCounter
Step 3 - 
The table should be present as is
===================================================================================================
"""
import pytest,time
from tests.test_meters.utils import install_agent_and_activate ,DI_TEST_AGENT ,is_process_running,wait_for_agents

# @pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2050497")
@pytest.mark.test_case("2060591")
def test_case(preinstalled_meter, logger):
    logger.trace("Executing Test Case 2060591 - Verify if the AgentFeatureDataCounter table exists after reboot")
    logger.trace('Step 1')
    install_agent_and_activate(preinstalled_meter, logger, DI_TEST_AGENT)
    previous_feature_data=preinstalled_meter.sql_query("select count(AgentId),count(FeatureId),sum(DailyUpstreamDataSent) from AgentFeatureDataCounter;")
    data=previous_feature_data[0].split('|')
    previous_agent_value=data[0]
    previous_feature_value=data[1]
    previous_dailyupsteamdatasent_value=data[2]
    logger.info('previous value is agentid %s, featuteID %s,Sum of %s',previous_agent_value,previous_feature_value,previous_dailyupsteamdatasent_value)
    preinstalled_meter.reboot_meter()
    wait_for_agents(preinstalled_meter, logger, [DI_TEST_AGENT], 20*60)
    curret_feature_data=preinstalled_meter.sql_query("select count(AgentId),count(FeatureId),sum(DailyUpstreamDataSent) from AgentFeatureDataCounter;")
    current_data=curret_feature_data[0].split('|')
    current_agent_value=current_data[0]
    current_feature_value=current_data[1]
    current_dailyupsteamdatasent_value=current_data[2]
    assert previous_agent_value<=current_agent_value and previous_feature_value<=current_feature_value and previous_dailyupsteamdatasent_value<= current_dailyupsteamdatasent_value
   