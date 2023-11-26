
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase2
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2064774
===================================================================================================
Test Case      : 2064774
Description    : Verify Agent Data requested feature subscription is requested but the access request does not appear in the feature list  and the Policy Violation is recorded in PolicyViolationStatistics 
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Verify Agent Data requested feature subscription is requested but the access request does not appear
in the feature list  and the Policy Violation is recorded in PolicyViolationStatistics

Step 2 - 
                          AgentId       FeatureID      ConstraintID 15     ViolationParameter
\"Unauthorized Feature Subscription Attempt: [%d]\"     ViolationCount


===================================================================================================


"""
import pytest
from tests.test_meters.utils import P2P_AGENT,install_agent_and_activate,refresh_container,Active_Containers,ITRONPUBSUBAGENT2,METROLOGY_DATA_AGENT
from tests.test_meters.rohan_utils import file_content_change,absolute_command,Container_stop,Dataserver_refresh,All_Agent_Table_Refresh,is_log_file_available,agent_policy_collect,policy_file_push,agent_Config_collect,Config_push
import time
import re

# AUTOGENERATED Test Case 2064774

# @pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
# @pytest.mark.regress_smoke
@pytest.mark.suite_id("2060761")
@pytest.mark.test_case("2064774")
def test_case(preinstalled_meter, logger, workdir):
    logger.trace("Executing Test Case 2064774 - Verify Agent Data requested feature subscription is requested but the access request does not appear in the feature list  and the Policy Violation is recorded in PolicyViolationStatistics ")

    test_case_start_time_stamp=int(absolute_command(preinstalled_meter,r"date +%s")[0])
    logger.info('starting time timestamp of Meter : %s',test_case_start_time_stamp)

    logger.trace('Step 1')
    agent=P2P_AGENT
    install_agent_and_activate(preinstalled_meter,logger,agent)
    
    # Getting the Agent ID form the Agent Information Table
    query=f'select AgentUID from agentinformation where AgentName = "{agent.name}";'
    agent_id=preinstalled_meter.sql_query(query)[0]


    # Getting the feature ID form the Dipolicy file table
    query=f'select PolicyFile from DIPolicyFile where AgentId = \"{agent_id}\";'
    check=fr'<Feature ID="(\d+)" description="PubSubFeature" subscribable="external" visibility="public">' # pubsub agent
    Policy_file_content="\n".join(preinstalled_meter.sql_query(query))
    Feature_id=re.findall(check,Policy_file_content)[0]
    logger.info(Feature_id)

    word1          = 'value="1#0#0#0#Itron#0#0#0#0#255#255#50593756#1#0"' # pubsub agent
    replaced_word1 = 'value="1#0#0#0#Itron#0#0#0#0#255#255#0#1#0"'        # pubsub agent

    word2          = 'value="0#0#50593756#1" ' # pubsub agent
    replaced_word2 = 'value="1#1#0#1" '        # pubsub agent


    try:
        # P2P agent config push
        file = agent_Config_collect(preinstalled_meter,agent,Feature_id,base_dir=workdir,force=True)

        file_content_change(preinstalled_meter,file,word1,replaced_word1)
        file_content_change(preinstalled_meter,file,word2,replaced_word2)

       
        Config_push(preinstalled_meter,Feature_id)


        # Restart the DataServer
        Dataserver_refresh(preinstalled_meter)

        # Stop the Container
        Container_stop(preinstalled_meter,agent.container_id)

        # Start the container
        refresh_container(preinstalled_meter,logger,20*60)
        assert agent.container_id in Active_Containers(preinstalled_meter),f"Container {agent.container_id} is not start after the Container Start command"

        is_log_file_available(preinstalled_meter,agent)
        
        query = f"select ViolationParameter from PolicyViolationStatistics where agentid = {agent_id} and ConstraintID = 15 and TimeStamp > {test_case_start_time_stamp} order by timestamp desc limit 1"
        time_out=time.time() + 2*60
        c = 0
        while time_out>time.time():
            ViolationParameter = preinstalled_meter.sql_query(query)
            logger.info('ViolationParameter : %s',ViolationParameter)
            value = ViolationParameter and ViolationParameter[0] == '0'
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
        assert value,"There is no violation register in policyviolationstatistics with constraint id 15"

    finally:
                  
        query=f'select TimeStamp from PolicyViolationStatistics'
        std_out=preinstalled_meter.sql_query(query)
        # Revert back the PolicyViolationStatistics table
        for tm in std_out:
            if int(tm)>test_case_start_time_stamp:
                query = f'delete from PolicyViolationStatistics where TimeStamp = "{tm}"'
                std_out=preinstalled_meter.sql_query(query)

        # Update the Config file at the FeatureConfiguration table at initial State
        file = agent_Config_collect(preinstalled_meter,agent,Feature_id,base_dir=workdir,force = True)
        Config_push(preinstalled_meter,Feature_id)


        # Restart the DataServer
        Dataserver_refresh(preinstalled_meter)

        # Stop the Container
        Container_stop(preinstalled_meter,agent.container_id)

        # Start the container
        refresh_container(preinstalled_meter,logger,20*60)
        assert agent.container_id in Active_Containers(preinstalled_meter),f"Container {agent.container_id} is not start after the Container Start command"


        # checking agent log file is available
        is_log_file_available(preinstalled_meter,agent)