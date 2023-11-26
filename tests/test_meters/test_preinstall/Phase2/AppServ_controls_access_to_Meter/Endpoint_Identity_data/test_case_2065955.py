"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase2
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2065955
===================================================================================================
Test Case      : 2065955
Description    : Verify requesting AgentID has no permission and log the violation in DI Policy file digest table
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 -
Verify Policy File permissions on Identity Data

Step 2 -
<Permission name="Data:Identity:Partial"/>

Step 3 -
Verify by removing manually  "<Permission name="Data:Identity:Partial"/>" from Policy File.xml
Step 4 -
copy Manually Policy File.xml into database by below command
Ex: sqlite3 /usr/share/itron/database/muse01.db "insert into DIPolicyFile(AgentId,TimeStamp,PolicyFile) VALUES(50528128,1603196818,readfile('PolicyFile.xml'))";


Step 5 - stop the conatiner refresh the conatiner

Step 6 -
Should have entry in AgentPolicyViolation Table

Step 7 -
Constraint ID : 4 should be logged in the table




===================================================================================================


"""
import pytest
from tests.test_meters.utils import DI_TEST_AGENT,install_agent_and_activate,refresh_container,Active_Containers
from tests.test_meters.rohan_utils import Config_push,agent_Config_collect,file_content_change,Container_stop,Dataserver_refresh,All_Agent_Table_Refresh,is_log_file_available,agent_policy_collect,policy_file_push,absolute_command
import re
import time

# AUTOGENERATED Test Case 2065955

# @pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
@pytest.mark.regress_smoke
@pytest.mark.suite_id("2063312")
@pytest.mark.test_case("2065955")
@pytest.mark.slow1020
def test_case(preinstalled_meter ,logger,di_package,di_version,workdir):
    logger.trace("Executing Test Case 2065955 - Verify requesting AgentID has no permission and log the violation in DI Policy file digest table")

    logger.trace('step 1')
    agent = DI_TEST_AGENT
    install_agent_and_activate(preinstalled_meter,logger,agent)

    # Getting the Agent ID form the Agent Information Table
    query=f'select AgentUID from agentinformation where AgentName = "{agent.name}"'
    agent_id=preinstalled_meter.sql_query(query)[0]

    Di_policy_file=preinstalled_meter.sql_query(f"select PolicyFile from DIPolicyFile where agentid ={agent_id}")
    logger.trace('step 2')
    lids='<Permission name="Data:Identity:Partial"/>'
    assert lids in Di_policy_file,f'{lids} are not available in the {agent} policy file '

    old_word='<Permission name="Data:Identity:Partial"/>'

    initial_max_timestamp = preinstalled_meter.sql_query("select max(timestamp) from PolicyViolationStatistics where AgentId=50528128;")
    logger.info('initial_max_timestamp %s',initial_max_timestamp)
    try:


       # Get the policy file
        file = agent_policy_collect(preinstalled_meter,agent,base_dir=workdir)

        # Remove the permission for the lids in the agent policy file table.
        file_content_change(preinstalled_meter,file,old_word)

       # Update the policy file
        policy_file_push(preinstalled_meter,agent)

        logger.trace('step 4')
        query = f"select ViolationParameter from PolicyViolationStatistics where agentid = {agent_id} and ConstraintID = 4 order by timestamp desc limit 1"
        time_out=time.time() + 5*60
        c = 0
        while time_out>time.time():
            ViolationParameter = preinstalled_meter.sql_query(query)
            logger.info('ViolationParameter : %s',ViolationParameter)
            value = ViolationParameter
            if value :
                break
            else:
                c+=1
            if c==5:
                # it will refresh all agent table 25 sec if not found
                All_Agent_Table_Refresh(preinstalled_meter,agent)
                c=0
            time.sleep(5)

        logger.trace('Step 2')
        assert value,"There is no violation register in policyviolationstatistics with constraint id 4"


    finally:

        # Update the policy file at the DIPolicyFile table at initial State
        agent_policy_collect(preinstalled_meter,agent,base_dir=workdir,force=True)
        policy_file_push(preinstalled_meter,agent)