"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1/AppServ-Installation
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/1993242
===================================================================================================
Test Case      : 1993242
Description    : Verify there is directory with GUID name to manage each active container
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Verify that there is directory with container GUID name under /tmp/container # cd /tmp/container/\n#
ls\n50593792  ( itron container GUID)587464704  (thirdparty container GUID)

Step 2 - 
Each created container should have the respective GUID name under /tmp/container

Step 3 - 



===================================================================================================


"""
import pytest
import time
from tests.test_meters.utils import HAN_AGENT,Third_Party_PubSub_AGENT,install_agent_and_activate

# @pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("1993280")
@pytest.mark.test_case("1993242")
def test_case(preinstalled_meter, logger):
    logger.trace("Executing Test Case 1993242 - Verify there is directory with GUID name to manage each active container")
    logger.trace('Step 1')
    for agent in [HAN_AGENT,Third_Party_PubSub_AGENT]:
        install_agent_and_activate(preinstalled_meter, logger, agent)
    container_data=preinstalled_meter.ls('/tmp/container/')
    assert '50593792' in container_data 
    assert '587464704' in container_data

