
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase2
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2050757
===================================================================================================
Test Case      : 2050757
Description    : Verify ApplicationServices compares the two SHA256 hash values when mismatches with incorrect hash value from Agent AP - This is covered as part of 2060289
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Agent api caluculates  the wrong hash value by the below command sha256sum
/tmp/container/50593792/rootfs/usr/bin/0302ff80echo \'abc\' >>xxx_Daemonsha256sum xxx_DaemonNote:
xxx indicates the specific agent name

Step 2 - 
the hash value mismatches

Refer to: 2052927 - Agent registration mismatches

Step 1 - 
Verify when hash value mismatches

Step 2 - 
agent installation failure

Step 3 - 
cdsEventLogDecoderV2 -f1 -i /mnt/pouch/LifeBoatLogs/DataServer_Daemon.txt (if DataServer_Daemon.txt
has no information related to the registration, try previous gz files)# gunzip
DataServer_Daemon.txt.0065889332184.2022-11-25-0001669385823.902.gz\n# cdsEventLogDecoderV2 -f1 -i
DataServer_Daemon.txt.0065889332184.2022-11-25-0001669385823.902\n

Step 4 - 
\"{2022/11/25 14:16:53 [65889322.026]}\",\"None\",\"Agent hash retrieved but does not match policy
file (expected: 39bae641d2476866a1bc58bb889a8cfe810913101fc884bcebd0e4259ae07c34, actual 90c70c0a15a
26087877a74834f219508f14b6215b8f347f2ada988e258aae4d2).\",\"ERROR\",\"DataServer_Daemon\",\"\",\"\",
\"10.5.734.4 (Best Guess)\",\"\",\"46\",\"2214\"\n\"{2022/11/25 14:16:53
[65889322.034]}\",\"None\",\"HashKey generated by AgentAPI and from Policy file do not match,
Skipping Registration process for the
Agent.\",\"ERROR\",\"DataServer_Daemon\",\"\",\"\",\"10.5.734.4 (Best
Guess)\",\"\",\"46\",\"2214\"\n


===================================================================================================


"""
import pytest
from tests.test_meters.utils import  install_agent_and_activate, DI_TEST_AGENT,wait_for_agents,is_process_running,filter_ps,refresh_container,Active_Containers,refresh_container
import time
from tests.test_meters.rohan_utils import Container_stop,agent_policy_collect,policy_file_push,Dataserver_refresh,Container_stop, absolute_command
from tests.test_meters.event_utils import get_meter_system_time,wait_for_eventlog_entry

#@pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2050697")
@pytest.mark.test_case("2050757")
@pytest.mark.parametrize("agent_info", [DI_TEST_AGENT])
def test_case(preinstalled_meter, logger, agent_info,workdir):
    logger.trace("Executing Test Case 2050757 - Verify ApplicationServices compares the two SHA256 hash values when mismatches with incorrect hash value from Agent AP - This is covered as part of 2060289")

    logger.trace('Step 1')
    install_agent_and_activate(preinstalled_meter,logger,agent_info)
    path="/root"
    start_time = get_meter_system_time(preinstalled_meter)

    logger.trace('Step 2')
    query = "select AgentName from agentinformation"
    Agent_reg_list=preinstalled_meter.sql_query(query)
    assert agent_info.name in Agent_reg_list, "Agent is not successfully installed."

    #real_hash_value=preinstalled_meter.command(f'sha256sum /tmp/container/{agent_info.container_id}/rootfs/usr/bin/0302ff80/{agent_info.name}_Daemon')
    real_hash_value=absolute_command(preinstalled_meter,f'sha256sum /tmp/container/{agent_info.container_id}/rootfs/usr/bin/0302ff80/{agent_info.name}_Daemon')
    real_hash_value=real_hash_value[0].split()[0]
    logger.info(real_hash_value)

    # getting the right hash value T
    right_hash_value=f'Hash="{real_hash_value}'
    logger.info(right_hash_value)

    try:
        logger.trace('Step 3')

        #preinstalled_meter.command(f"echo 'b' >> /tmp/container/{agent_info.container_id}/rootfs/usr/bin/0302ff80/{agent_info.name}_Daemon")
        absolute_command(preinstalled_meter,f"echo 'b' >> /tmp/container/{agent_info.container_id}/rootfs/usr/bin/0302ff80/{agent_info.name}_Daemon")

        #modified_hash_value=preinstalled_meter.command(f'sha256sum /tmp/container/{agent_info.container_id}/rootfs/usr/bin/0302ff80/{agent_info.name}_Daemon')
        modified_hash_value=absolute_command(preinstalled_meter,f'sha256sum /tmp/container/{agent_info.container_id}/rootfs/usr/bin/0302ff80/{agent_info.name}_Daemon')
        modified_hash_value=modified_hash_value[0].split()[0]
        logger.info(modified_hash_value)


        logger.trace('Step 4')
        assert real_hash_value != modified_hash_value," agent hash value is not changed "

        logger.trace('Step 5')

        output=filter_ps(preinstalled_meter,f'{agent_info.name}_Daemon')
        logger.info(output)
        pid = output[0][0]
        logger.info(pid)
    
        #preinstalled_meter.command(f'kill -9 {pid}')
        absolute_command(preinstalled_meter,f'kill -9 {pid}')
        assert not is_process_running(preinstalled_meter,f'{agent_info.name}_Daemon'),'agent is still running'

        logger.trace('Step 7')
        file_name="/mnt/pouch/LifeBoatLogs/DataServer_Daemon.txt"
        logger.trace('Step 8')
        found1 = wait_for_eventlog_entry(preinstalled_meter, logger, start_time,file_name,"Agent hash retrieved but does not match policy file",5*60,do_assert=False)
        found2 = wait_for_eventlog_entry(preinstalled_meter, logger, start_time,file_name,"HashKey generated by AgentAPI and from Policy file do not match",5*60,do_assert=False)
        found3 = wait_for_eventlog_entry(preinstalled_meter, logger, start_time,file_name,'Skipping Registration process',5*60,do_assert=False)

        assert found1 and found2 and found3, "Agent registration not notify in the log message"

    finally:

        # Update the policy file at the DIPolicyFile table at initial State
        agent_policy_collect(preinstalled_meter,agent_info,base_dir=workdir,force=True)
        policy_file_push(preinstalled_meter,agent_info)


        # Restart the DataServer
        Dataserver_refresh(preinstalled_meter)

        # Container Stop 
        Container_stop(preinstalled_meter,agent_info.container_id)

        # Container Start
        refresh_container(preinstalled_meter,logger)
        assert is_process_running(preinstalled_meter,f'{agent_info.name}_Daemon') ,f"{agent_info.name} is not up and running"


        final_hash_value=absolute_command(preinstalled_meter,f'sha256sum /tmp/container/{agent_info.container_id}/rootfs/usr/bin/0302ff80/{agent_info.name}_Daemon')
        final_hash_value=final_hash_value[0].split()[0]
        logger.info(final_hash_value)
        assert final_hash_value == real_hash_value