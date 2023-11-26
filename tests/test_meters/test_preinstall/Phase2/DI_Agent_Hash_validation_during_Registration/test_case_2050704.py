
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase2
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2050704
===================================================================================================
Test Case      : 2050704
Description    : Verify ApplicationServices(AgentAPI) calculates SHA256 hash value of the calling DI Agentapplication binary during its registration manual copy
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
install specific agent package with corresponding DI policy file

Step 2 - 
agent installed

Step 3 - 
ps | grep -i lxc

Step 4 - 
container Up

Step 5 - 
SwitchDIInits.sh -s

Step 6 - 
agent is Up and Database refreshes

Step 7 - 
ps | grep -i agent

Step 8 - 
specific agent should Up and Run in container

Step 9 - 
copy Policy File.xml  From Agent Package into /root

Step 10 - 
Policy File.xml copied into /root

Step 11 - 
Verify DI policy file  exists in database DI Policy File Table By Manual copyEx:sqlite3
/usr/share/itron/database/muse01.db \"insert into DIPolicyFile(AgentId,TimeStamp,PolicyFile)
VALUES(50528128,1603151455,readfile(\'PolicyFile.xml\'))\";

Step 12 - 
DI policy file copied in DI Policy File Table

Step 13 - 
Verify DI policy file exists in specified path by below commandEx:sqlite3
/mnt/common/database/muse01.db \"select PolicyFile from DIPolicyFile;\"

Step 14 - 
DI Policy file contents should display on terminal from DI Policy File table

Step 15 - 
kill -9 $(ps | grep DataServer | grep -v grep | awk \'{print $1}\')

Step 16 - 
Dataserver Killed

Step 17 - 
 ps | grep -i dataserver | grep -v grep

Step 18 - 
Dataserver restarts after few minutesEx:7055 dserver_ 14324 R    /usr/bin/DataServer
--username=dserver_u --groupname=dse 7057 root      1108 S    grep -i dataserver

Step 19 - 
dbus-send --type=signal --system --dest=com.itron.museplatform.ContainerManager
/com/itron/museplatform/ContainerManager com.itron.museplatform.ContainerManager.Refresh

Step 20 - 
container Refreshes :

Step 21 - 
Verify ApplicationServices(AgentAPI) calculates SHA256 hash value of the calling DI Agentapplication
binary during its registration by the executing the below command on terminal Ex:# sha256sum
/usr/bin/0302ff8a/HeartBeatAgent_Daemon | awk \'{print $1}\') 2> /dev/null

Step 22 - 
 hash value


===================================================================================================


"""

import pytest
import time
from tests.test_meters.utils import DI_TEST_AGENT,install_agent_and_activate,is_process_running,wait_for_agents,refresh_container,filter_ps,Active_Containers
from tests.test_meters.rohan_utils import agent_file,Container_stop,absolute_command

# AUTOGENERATED Test Case 2050704

# @pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
# @pytest.mark.regress_smoke
@pytest.mark.suite_id("2050697")
@pytest.mark.test_case("2050704")
def test_case(preinstalled_meter, logger, workdir):
    logger.trace("Executing Test Case 2050704 - Verify ApplicationServices(AgentAPI) calculates SHA256 hash value of the calling DI Agentapplication binary during its registration manual copy")

    logger.trace('Step 1')
    logger.trace('Step 2')
    logger.trace('Step 3')
    logger.trace('Step 4')
    install_agent_and_activate(preinstalled_meter,logger,DI_TEST_AGENT)

    query=f"select AgentUID from agentinformation where AgentName = \"{DI_TEST_AGENT.name}\""
    agent_id = preinstalled_meter.sql_query(query)[0]  

    assert DI_TEST_AGENT.container_id in Active_Containers(preinstalled_meter),f"Container {DI_TEST_AGENT.container_id} is not start after the Container Start command"
    assert is_process_running(preinstalled_meter,f'{DI_TEST_AGENT.name}_Daemon') ,f"{DI_TEST_AGENT.name} is not start"

    logger.trace('Step 5')

    logger.trace('Step 6')
    logger.trace('Step 7')
    logger.trace('Step 8')
    
    logger.trace('Step 9')
    agent_file(preinstalled_meter,DI_TEST_AGENT,"PolicyFile.xml",base_dir=workdir,meter_dir='/root')
    status  = "PolicyFile.xml" in preinstalled_meter.ls('/root')

    logger.trace('Step 10')
    assert status,'Policy File.xml not copied into /root'


    logger.trace('Step 11')
    query=f'insert or replace into DIPolicyFile(AgentId,TimeStamp,PolicyFile) VALUES({agent_id},0,readfile(\"PolicyFile.xml\"));'
    preinstalled_meter.sql_query(query) 
    absolute_command(preinstalled_meter,'rm /root/PolicyFile.xml')

    logger.trace('Step 12')
    logger.trace('Step 13')
    query=f"select PolicyFile from DIPolicyFile where agentid = {agent_id}"
    logger.info(query)
    content=preinstalled_meter.sql_query(query)

    logger.trace('Step 14')
    content = preinstalled_meter.sql_query(query) 
    assert len(content) >10



    logger.trace('Step 15')

    dataserver_pid = filter_ps(preinstalled_meter,f"DataServer_Daemon")[0][0]
    logger.trace('Step 16')

    absolute_command(preinstalled_meter,f'kill -9 {dataserver_pid}')

    logger.trace('Step 17')
    time0ut = time.time() + 7*60
    while time.time()<=time0ut:
        value = filter_ps(preinstalled_meter,f"DataServer_Daemon")
        if value:
            logger.info("DataServer is restart")
            break
        time.sleep(10)

    logger.trace('Step 18')

    assert value,"DataServer is not restart after the killing"


    logger.trace('Step 19')
    logger.trace('Step 20')

    # Stop the Container
    Container_stop(preinstalled_meter,DI_TEST_AGENT.container_id)
    # Start the container
    refresh_container(preinstalled_meter,logger,20*60)

    logger.trace('Step 21')
    logger.trace('Step 22')

    cmd = 'sha256sum /tmp/container/50593792/rootfs/usr/bin/0302ff80/DITestAgent_Daemon'
    Hash_Value1=absolute_command(preinstalled_meter,cmd)

    Hash_Value1=Hash_Value1[0].split()[0]

    query=f"select PolicyFile from DIPolicyFile where AgentId = {agent_id}"
    policy_file_content = " ".join(preinstalled_meter.sql_query(query))

    assert Hash_Value1 in policy_file_content