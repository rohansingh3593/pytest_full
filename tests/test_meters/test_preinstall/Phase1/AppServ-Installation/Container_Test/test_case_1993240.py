"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1/AppServ-Installation
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/1993240
===================================================================================================
Test Case      : 1993240
Description    : Verify no action is taken on containers/overlays which are already in correct state when we run Refresh 
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Verify Dbus Refresh command on the unchanged database

Step 2 - 
When there is no change in the database for container/overlays. Dbus refresh should not make any
difference on the running container\'s

===================================================================================================


"""
import pytest
from tests.test_meters.utils import DI_TEST_AGENT,install_agent_and_activate

# @pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
@pytest.mark.regress_smoke
@pytest.mark.suite_id("1993280")
@pytest.mark.test_case("1993240")
@pytest.mark.parametrize("agent_info", [DI_TEST_AGENT])
def test_case(preinstalled_meter, logger,agent_info):
    logger.trace("Executing Test Case 1993240 - Verify no action is taken on containers/overlays which are already in correct state when we run Refresh ")
    logger.trace('Step 1')
    install_agent_and_activate(preinstalled_meter, logger, agent_info,force=True)
    ps_out1=preinstalled_meter.command("ps | grep lxc")
    lxc_prev_PID = [x.split()[0] for x in ps_out1 if('lxc-start' in x.split()[4] and 'Z' not in x.split()[3])]
    logger.trace(lxc_prev_PID[0])
    logger.trace('Step 2')
    preinstalled_meter.command("dbus-send --type=signal --system --dest=com.itron.museplatform.ContainerManager /com/itron/museplatform/ContainerManager com.itron.museplatform.ContainerManager.Refresh")
    ps_out2=preinstalled_meter.command("ps | grep lxc")
    lxc_cur_PID = [x.split()[0] for x in ps_out2 if('lxc-start' in x.split()[4] and 'Z' not in x.split()[3])]
    logger.trace(lxc_prev_PID[0])
    assert lxc_prev_PID==lxc_cur_PID