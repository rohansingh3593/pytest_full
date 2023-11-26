
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2004423
===================================================================================================
Test Case      : 2004423
Description    : Verify the Container Start Failure Cases
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Scenario 1: 

 Too Much Memory Requested.
a. Ensure Agent is installed and running 
b. Check the default memory LID- CONTAINER_MAX_MEMORY_LIMIT_KB and exceed the limit and verify the failure case.
c. update the LID to a smaller value
TransactionProcess --event="MUSE_V1;WriteLid;CONTAINER_MAX_MEMORY_LIMIT_KB ;1"
d. Stop and Restart the containers using dbus command.
#dbus-send --type=signal --system --dest=com.itron.museplatform.ContainerManager /com/itron/museplatform/ContainerManager com.itron.museplatform.ContainerManager.StopAllContainer
#dbus-send --type=signal --system --dest=com.itron.museplatform.ContainerManager /com/itron/museplatform/ContainerManager com.itron.museplatform.ContainerManager.Refresh
e.  DB should be logged with failure reason. 
Table : containerstatus 
f. Revert the CONTAINER_MAX_MEMORY_LIMIT_KB  back to 65000 to make the container functional.

Step 2 - 
a. ps | grep -i $Agent > should be returning the Agent Daemon and PID 
b. Default memory is:
ILID_CONTAINER_MAX_MEMORY_LIMIT_KB:U32=65000
c. Set Memory as:
ILID_CONTAINER_MAX_MEMORY_LIMIT_KB:U32=65
d. lxc should have new PID.
e. # sqlite3 --header /tmp/muse01.db "select GUID,state,LastStartFailureReason from containerstatus"
GUID|State|LastStartFailureReason
50593792|7|Memory limit exceeded

Step 3 - 
Scenario 2 :
Container Is Unable to Use Overlays. 
#sqlite3 /usr/share/itron/database/muse01.db "insert into OVERLAYSETUP (GroupId, UID, OverlayVersion, OverlayPath, IsDeletable, Source) values (1, 25,1, '/usr/share/itron/container-overlays/MockAgent.tar.bz2', 0, 0);"
#sqlite3 /usr/share/itron/database/muse01.db "insert into CONTAINEROVERLAY (GroupId, ContainerUID, OverlayUID, LoadIndex) values (1, 50593792,25, 15);"
# dbus-send --type=signal --system --dest=com.itron.museplatform.ContainerManager /com/itron/museplatform/ContainerManager com.itron.museplatform.ContainerManager.StopAllContainer
#dbus-send --type=signal --system --dest=com.itron.museplatform.ContainerManager /com/itron/museplatform/ContainerManager com.itron.museplatform.ContainerManager.Refresh



Step 4 - 
A container is not allowed to start if there are no overlays mapped to the container, 
or if it is mapped to an overlay that does not exist or cannot be untarred.


Step 5 - 
If the ContainerManager application is unable to start an enabled container,
 1.  the failure is indicated in CONTAINERSTATUS table. Check the State and LastStartFailureReason fields of the table
# sqlite3 --header /tmp/muse01.db "select GUID,state,LastStartFailureReason from containerstatus"

Step 6 - 
# sqlite3 --header /tmp/muse01.db "select GUID,state,LastStartFailureReason from containerstatus"
GUID|State|LastStartFailureReason
50593792|0|Overlay does not exist: /usr/share/itron/container-overlays/MockAgent.tar.bz2

Step 7 - 
Container Is Unable to Mount Flash

Step 8 - 
A container is not allowed to start if requested flash cannot be provided due to failures creating the backing store or mounting it within the container.
cat /mnt/pouch/LifeBoatLogs/ContainerManager.txt
"{2023/01/03 12:35:55 [66734196.354]}","None","Umounting failed /tmp/container/50593792/rootfs/: No such file or directory","ERROR","ContainerManager","","","10.7.27.1","MUSE","55","18377"
"{2023/01/03 12:35:56 [66734197.472]}","None","Unable to start container 50593792. Reason: Overlay does not exist: /usr/share/itron/container-overlays/MockAgent.tar.bz2","ERROR","ContainerManager","","","10.7.27.1","MUSE","55","18377"

Step 9 - 
LXC Container Fails to Start

Step 10 - 
Failures in LXC start are failures to start the container.
ps | grep -i lxc > should not return the container id.

Step 11 - 
To revert the containers back to running state :
sqlite3 /usr/share/itron/database/muse01.db "delete from OVERLAYSETUP where UID = 25"
sqlite3 /usr/share/itron/database/muse01.db "delete from CONTAINEROVERLAY where OverlayUID = 25"
dbus-send --type=signal --system --dest=com.itron.museplatform.ContainerManager /com/itron/museplatform/ContainerManager com.itron.museplatform.ContainerManager.Refresh

Step 12 - 



===================================================================================================


"""
import pytest
import time
from tests.test_meters.utils import filter_ps,is_process_running,read_lid,write_lid,refresh_container,stop_container,Active_Containers,install_agent_and_activate,Third_Party_PubSub_AGENT
from tests.test_meters.event_utils import get_meter_system_time,wait_for_eventlog_entry,wait_for_eventlog_entry_with_rotator

# AUTOGENERATED Test Case 2004423

#@pytest.mark.skip(reason="get_meter_time shouldn't be used for getting the current time")
@pytest.mark.regress_nightly
@pytest.mark.regress_smoke
@pytest.mark.suite_id("2002265")
@pytest.mark.test_case("2004423")
def test_case(preinstalled_meter, logger):
    logger.trace("Executing Test Case 2004423 - Verify the Container Start Failure Cases")

    test_start = get_meter_system_time(preinstalled_meter)
    logger.info("Start: %s", test_start)


    lid="ILID_CONTAINER_MAX_MEMORY_LIMIT_KB"
    agent = Third_Party_PubSub_AGENT

    install_agent_and_activate(preinstalled_meter,logger,agent)

    Memory_limit = read_lid(preinstalled_meter,logger,lid)
    assert Memory_limit == 65000,"Default value of Container Max Memory Limit is not set"
    # before_active_container =  Active_Containers(preinstalled_meter)
    logger.trace('Step 1')
    assert is_process_running(preinstalled_meter,f'{agent.name}_Daemon') ,f"{agent.name} is not functional"

    try:

        value=1
        write_lid(preinstalled_meter,logger,lid,value)
        
        updated_memory_limit=read_lid(preinstalled_meter,logger,lid)
        assert updated_memory_limit==value,"Default value of Container Max Memory Limit is not set" 
        meter_time_stamp=int(preinstalled_meter.command(r"date +%s")[0]) 

        try:
            stop_container(preinstalled_meter)
        finally:
            preinstalled_meter.command("dbus-send --type=signal --system --dest=com.itron.museplatform.ContainerManager /com/itron/museplatform/ContainerManager com.itron.museplatform.ContainerManager.Refresh")
        
        logger.trace('Step 2')
        stop = time.time() + (5*60)
        cmd=f'sqlite3  /tmp/muse01.db "select LastStartFailureReason from containerstatus where EntryLastUpdatedRealtime > {meter_time_stamp}"'
        while time.time()<=stop:
            code,table_op = preinstalled_meter.command_with_code(cmd)
            table_op = " ".join(table_op)
            status = ('Memory limit exceeded' in table_op) and code == 0
            if status:
                break
            time.sleep(10) 
        assert status,'timeout for condition check'
    finally:
        lid="ILID_CONTAINER_MAX_MEMORY_LIMIT_KB"
        write_lid(preinstalled_meter,logger,lid,Memory_limit)
        stop_container(preinstalled_meter)
        refresh_container(preinstalled_meter,logger,20*60)
       

    meter_time_stamp=int(preinstalled_meter.command(r"date +%s")[0])   
    try:
        logger.trace('Step 3')
        preinstalled_meter.sql_query("insert into OVERLAYSETUP (GroupId, UID, OverlayVersion, OverlayPath, IsDeletable, Source) values (1, 25,1,\"/usr/share/itron/container-overlays/MockAgent.tar.bz2\", 0, 0)")
        preinstalled_meter.sql_query("insert into CONTAINEROVERLAY (GroupId, ContainerUID, OverlayUID, LoadIndex) values (1, 587464704,25, 15)")
        before_active_container =  Active_Containers(preinstalled_meter)

        try:
            stop_container(preinstalled_meter)
        finally:
            preinstalled_meter.command("dbus-send --type=signal --system --dest=com.itron.museplatform.ContainerManager /com/itron/museplatform/ContainerManager com.itron.museplatform.ContainerManager.Refresh")
        

        stop = time.time() + (5*60)
        while time.time()<=stop:
            output = agent.container_id not in  Active_Containers(preinstalled_meter)
            if output:
                break
            time.sleep(10)
        assert output, f"Container {agent.container_id} is still running"
        
        logger.trace('Step 4')
        cmd=f'sqlite3  /tmp/muse01.db "select LastStartFailureReason from containerstatus where EntryLastUpdatedRealtime > {meter_time_stamp}"'
        stop = time.time() + 5*60
        while time.time()<=stop:
            code,table_op = preinstalled_meter.command_with_code(cmd)
            table_op = " ".join(table_op)
            logger.info(table_op)
            status = ('Overlay does not exist: /usr/share/itron/container-overlays/MockAgent.tar.bz2' in table_op) and code == 0
            if status:
                break
            time.sleep(10)

        logger.trace('Step 5')
        logger.trace('Step 6')
        assert status ,"timeout error to check condition"

        logger.trace('Step 7')
        logger.trace('Step 8')
        moniker = 'Reason: Overlay does not exist:'
        found = wait_for_eventlog_entry_with_rotator(preinstalled_meter, logger, test_start,
            '/mnt/pouch/LifeBoatLogs/ContainerManager.txt',
            moniker, 5*60)

        logger.trace('Step 9')
        logger.trace('Step 10')
        stop = time.time() + (5*60)
        while time.time()<=stop:
            output = before_active_container != Active_Containers(preinstalled_meter)
            logger.info(filter_ps(preinstalled_meter,'lxc-start'))
            if output:
                break
            time.sleep(10)
        assert output, "Containers is still running"
        

    finally:
        logger.trace('Step 11')
        preinstalled_meter.sql_query("delete from OVERLAYSETUP where UID=25")
        preinstalled_meter.sql_query("delete from CONTAINEROVERLAY where OverlayUID=25")
        stop_container(preinstalled_meter)
        refresh_container(preinstalled_meter,logger,20*60)