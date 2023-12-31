"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/1992820
===================================================================================================
Test Case      : 1992820
Description    : Verify the Agent application which were running on the container should continue to work as before upon successful upgrade
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 -
After the upgradation of AppServices package into the meter.  Check the agents running on the
container is continue working as before.

Step 2 -
Sample agent exist outside container. real agent test required. Sample Agent can be created as a
package inside the container.


===================================================================================================


"""
import pytest
from tests.test_meters.utils import install_multiple_agents_and_activate,HAN_AGENT,P2P_AGENT,is_process_running,filter_ps,is_stand_alone_init, enter_standalone,wait_for_agents
import time

# AUTOGENERATED Test Case 1992820

# @pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
@pytest.mark.slow1020 # test takes 10 to 20 minutes
@pytest.mark.regress_smoke
@pytest.mark.suite_id("1990123")
@pytest.mark.test_case("1992820")
def test_case(preinstalled_meter, logger,di_package_2k,di_version_2k):
    logger.trace("Executing Test Case 1992820 - Verify the Agent application which were running on the container should continue to work as before upon successful upgrade")

    logger.trace('Step 1')
    agent_list=[HAN_AGENT,P2P_AGENT]
    install_multiple_agents_and_activate(preinstalled_meter, logger, agent_list)

    for agent in agent_list:
        assert is_process_running(preinstalled_meter,f'{agent.name}_Daemon') ,f"{agent.name} is not Running"

    preinstalled_meter.install(file=di_package_2k)
    fermver,appserver=preinstalled_meter.version_info()
    logger.trace('Step 2')
    assert appserver == di_version_2k,"Appserver is not successful upgrade"
    enter_standalone(preinstalled_meter, logger)
    wait_for_agents(preinstalled_meter, logger, agent_list, 20*60)

    logger.trace('Step 2')

    for agent in agent_list:
        assert is_process_running(preinstalled_meter,f'{agent.name}_Daemon') ,f"{agent.name} is not able to continue to work as before upon successful upgrade"
