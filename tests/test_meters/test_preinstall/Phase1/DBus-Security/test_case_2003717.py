
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2003717
===================================================================================================
Test Case      : 2003717
Description    : Verify that interaction between agents which has same user/group permissions but in different containers
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 -
Check if the DbusConnectionType is 1 - \"percontainer\".

Step 2 -
Check how the agent is running across containers.ps | grep -i agent

Step 3 -
The DI agents should continue to run as the container_dbus_u user and the container_dbus_g group. #
ps | grep -i agent\n 3206 containe  5444 R    /usr/bin/0302ff77/ItronPubSubAgent_Daemon\n 3252
containe  5956 R    /usr/bin/2302fff4/ThirdPartyPubSubAgent_Daemon# ls -lrt
ls -lrt /tmp/container/50593792/rootfs/usr/bin/0302ff77/ItronPubSubAgent_Daemon\n-rwxrwxrwx    1 containe
containe    130484 Mar  8 00:00
/tmp/container/50593792/rootfs/usr/bin/0302ff77/ItronPubSubAgent_Daemon\n# \n# ls -lrt
/tmp/container/587464704/rootfs/usr/bin/2302fff4/ThirdPartyPubSubAgent_Daemon \n-rwxrwxrwx    1
containe containe    133664 Mar  8 00:00
/tmp/container/587464704/rootfs/usr/bin/2302fff4/ThirdPartyPubSubAgent_Daemon


===================================================================================================
"""
import pytest
from tests.test_meters.utils import install_multiple_agents_and_activate,is_process_running,P2P_AGENT,Third_Party_PubSub_AGENT

#@pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2002265")
@pytest.mark.test_case("2003717")
def test_case(preinstalled_meter, logger):
    logger.trace("Executing Test Case 2003717 - Verify that interaction between agents which has same user/group permissions but in different containers")

    agent_list=[P2P_AGENT,Third_Party_PubSub_AGENT]
    install_multiple_agents_and_activate(preinstalled_meter,logger,agent_list)
    logger.trace('Step 1')
    std_out=preinstalled_meter.sql_query("select DbusConnectionType from containersetup")
    assert all([i=="1" for i in std_out])," DbusConnectionType is not 1"

    logger.trace('Step 2')
    for agent in agent_list:
        assert is_process_running(preinstalled_meter,f"{agent.name}_Daemon"),f"{agent.name} is not Up"

    logger.trace('Step 3')
    agent_name=P2P_AGENT.name
    std_out = preinstalled_meter.command(f'ls -lrt /tmp/container/50593792/rootfs/usr/bin/0302ff77/{agent_name}_Daemon')[0]
    ls_out = std_out.split()
    logger.trace(ls_out)
    assert 'containe' in ls_out[2] and ls_out[3] and 'ItronPubSubAgent_Daemon' in ls_out[-1]

    agent_name=Third_Party_PubSub_AGENT.name
    std_out = preinstalled_meter.command(f'ls -lrt /tmp/container/587464704/rootfs/usr/bin/2302fff4/{agent_name}_Daemon')[0]
    ls_out = std_out.split()
    logger.trace(ls_out)
    assert 'containe' in ls_out[2] and ls_out[3] and 'ThirdPartyPubSubAgent_Daemon' in ls_out[-1]

