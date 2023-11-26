"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase2
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2282676
===================================================================================================
Test Case      : 2282676
Description    : Verify if requestingAgentID has permission then application services check the access to the list of feature ID's for ThirdParty Agent
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Install ThirdParty agent1 on to the meter

Step 2 - 
Agent successfully installed

Step 3 - 
Check if the permissions are available in the agent policy file for all the features

Step 4 - 
Permissions should be available for all under <Permissions> and <FeatureData> tag

Step 5 - 
Subscribe to the featureId listed in the policy file in the agent config.Check the agent log :#
tail -F /tmp/container/50593792/rootfs/tmp/agent/2302fff4/2302fff4_log
#tail -F /tmp/container/587464704/rootfs/tmp/agent/2302fff4/2302fff4_log

Step 6 - 
Subscription should be successful


===================================================================================================


"""
import pytest,time
from tests.test_meters.utils import install_agent_and_activate, refresh_container, Third_Party_PubSub_AGENT, Active_Containers
from tests.test_meters.rohan_utils import absolute_command, Config_push,agent_Config_collect,file_content_change,Container_stop,Dataserver_refresh
# AUTOGENERATED Test Case 2282676

# @pytest.mark.skip(reason="TODO: config file dont have line ")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2063316")
@pytest.mark.test_case("2282676")
@pytest.mark.parametrize("agent_info", [Third_Party_PubSub_AGENT])
def test_case(preinstalled_meter, logger, agent_info, workdir):
    logger.trace("Executing Test Case 2282676 - Verify if requestingAgentID has permission then application services check the access to the list of feature ID\'s for ThirdParty Agent")
    logger.trace('Step 1')
    install_agent_and_activate(preinstalled_meter,logger,agent_info)
    dipolicy_file=preinstalled_meter.sql_query("select PolicyFile from DIPolicyFile where agentid = 587399156")
    policy_count=0
    for i in dipolicy_file :
        if '<Permission name="Data:Subscription:Agent"/>' in i:
            policy_count=policy_count+1
        if '<FeatureData>' in i:
            policy_count+=1
    logger.info('count is %s',policy_count)
    logger.trace('Step 2')
    assert policy_count ==2,'ThirdPartyPubSubAgent have not permission'
    Feature_id = "587464692"

    logger.trace('step 2')
    try:       
        # Get configuration file from the featureConfiguration table
        file = agent_Config_collect(preinstalled_meter,Third_Party_PubSub_AGENT,Feature_id,base_dir=workdir,force=True)

        # Update the configuration file
        file_content_change(preinstalled_meter,file,'value="1#0#0#0#Itron#0#0#0#0#255#255#587464692#1#0"','value="1#5#5#100#ThirdParty:Publish#1#0#0#0#255#255#587464692#1#0"')
        file_content_change(preinstalled_meter,file,'value="0#0#587464692#1"','value="1#0#587464692#1"')

        # Push configuration file to the featureConfiguration table
        Config_push(preinstalled_meter,Feature_id)

        # Restart the DataServer
        Dataserver_refresh(preinstalled_meter)

        # Stop the Container
        Container_stop(preinstalled_meter,Third_Party_PubSub_AGENT.container_id)

        # Start the container
        refresh_container(preinstalled_meter,logger,20*60)
        assert Third_Party_PubSub_AGENT.container_id in Active_Containers(preinstalled_meter),f"Container {Third_Party_PubSub_AGENT.container_id} is not start after the Container Start command"
        
        logger.trace('Step 4')
        stop = time.time() + (5*60)
        while time.time()<=stop:
            logs = absolute_command(preinstalled_meter,'cat /tmp/container/587464704/rootfs/tmp/agent/2302fff4/2302fff4_log')
            logs = ('').join(logs)
            logger.trace(logs)
            if "Add" in logs and "Pub" in logs and "Got" in logs:
                break
            time.sleep(10)
        assert "Add" in logs and "Pub" in logs and "Got" in logs

    finally:

        # Update the Data file at the FeatureConfiguration table at Initial State
        agent_Config_collect(preinstalled_meter,Third_Party_PubSub_AGENT,Feature_id,base_dir=workdir,force=True)
        Config_push(preinstalled_meter,Feature_id)        

        # Restart the DataServer
        Dataserver_refresh(preinstalled_meter)

        # Stop the Container
        Container_stop(preinstalled_meter,Third_Party_PubSub_AGENT.container_id)
        # Start the container
        refresh_container(preinstalled_meter,logger,20*60)
        assert Third_Party_PubSub_AGENT.container_id in Active_Containers(preinstalled_meter),f"Container {Third_Party_PubSub_AGENT.container_id} is not start after the Container Start command"
        
        absolute_command(preinstalled_meter,'rm -rf *')


