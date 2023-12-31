
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase2
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2060711
===================================================================================================
Test Case      : 2060711
Description    : Verify agent installed with DI policy file and when uninstalled it should remove agent and corresponding policy file
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
install specific agent package with corresponding DI policy file

Step 2 - 
agent installed on specified location

Step 3 - 
Verify DI Policy file installed in specified pathsqlite3 --header
/usr/share/itron/database/muse01.db \"select * from DIPolicyFile\"

Step 4 - 
DI policy file exists in specified path and in database

Step 5 - 
perform registration match testcases from testcase id :2050749

Step 6 - 
registration successful

Step 7 - 
uninstall agent Note : Agent uninstall is not applicable. Performing GMR Is the only way to properly
remove Agent from meter.

Step 8 - 
agent and DI policy file should removed and data resulting from the consumption of said policy shall
be removed

Step 9 - 



===================================================================================================


"""
import pytest
from tests.test_meters.utils import  install_agent_and_activate, DI_TEST_AGENT
from tests.test_meters.rohan_utils import absolute_command

# AUTOGENERATED Test Case 2060711

#pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
# @pytest.mark.regress_smoke
@pytest.mark.suite_id("2050697")
@pytest.mark.gmr_meter
@pytest.mark.slow1020
@pytest.mark.test_case("2060711")
@pytest.mark.parametrize("agent_info", [DI_TEST_AGENT])
def test_case(preinstalled_meter, logger, agent_info,di_package):
    logger.trace("Executing Test Case 2060711 - Verify agent installed with DI policy file and when uninstalled it should remove agent and corresponding policy file")
    
    logger.trace('Step 1')
    install_agent_and_activate(preinstalled_meter,logger,agent_info)

    logger.trace('Step 2')
    cmd = 'sha256sum /tmp/container/50593792/rootfs/usr/bin/0302ff80/DITestAgent_Daemon'
    Hash_Value1=absolute_command(preinstalled_meter,cmd)
    Hash_Value1=Hash_Value1[0].split()[0]

    logger.trace('Step 3')
    cmd=f'select AgentUID from agentinformation where AgentName = "{agent_info.name}"'
    agent_id = preinstalled_meter.sql_query(cmd)[0]
   
    cmd=f'select PolicyFile from DIPolicyFile where AgentId = "{agent_id}"'
    policy_file_content = preinstalled_meter.sql_query(cmd)
    logger.info("policy file data is : %s",policy_file_content)
    policy_file_content = ''.join(policy_file_content)

    logger.trace('Step 4')
    logger.trace('Step 5')
    logger.trace('Step 6')
    assert Hash_Value1 in policy_file_content, "registration match not successful"

    try:
        logger.trace('Step 7')
        preinstalled_meter.gmr()
        logger.trace('Step 8')
        tables=preinstalled_meter.sql_query('.tables')  
        logger.trace('Step 9')
        tables = " ".join(tables)
        logger.trace('Step 10')
        table_list = ['DIPolicyFile', 'AgentInformation']
        for table in table_list:
            assert table not in tables ,f'{table} is present after the GMR'

    finally:
        preinstalled_meter.install(file = di_package)