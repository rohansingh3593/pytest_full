"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2005831
===================================================================================================
Test Case      : 2005831
Description    : Verify Third party Agent functionality
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 -
Follow the previous testcase id : 2005828 for ThirdPartyPubSubAgent_0.4.24.377216952_TS.zip

Step 2 -

Step 3 -
Do SwitchDiinit.sh to start the Agent

Step 4-

Step 5-
Update the Agent config

Step 6 -

Step 7 -
Check if 10sec log is proper for this Agent

 tail -F /tmp/container/587464704/rootfs/tmp/agent/2302fff4/2302fff4_log

Step 8 -
The agent should show one sec logs  with Add and Publish every second


===================================================================================================


"""
import pytest
import time
from tests.test_meters.utils import Third_Party_PubSub_AGENT, install_agent_and_activate, refresh_container
from tests.test_meters.rohan_utils import file_content_change,agent_file

#@pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2012056")
@pytest.mark.test_case("2005831")
def test_case(preinstalled_meter, logger,workdir):
    logger.trace("Executing Test Case 2005831 - Verify Third party Agent functionality")
    logger.trace('Step 1')
    install_agent_and_activate(preinstalled_meter,logger,Third_Party_PubSub_AGENT)
    logger.trace('Step 2')
    logger.trace('Step 3')
    """This step is done in install_agent_and_activate function"""
    logger.trace('Step 4')
    logger.trace('Step 5')
    level5_file="config/2302fff4.2303fff4.xml"
    path='/root'
    agent_file(preinstalled_meter,Third_Party_PubSub_AGENT,level5_file,base_dir=workdir,meter_dir=path)
    level5_file=level5_file.split("/")[-1]
    Initial_file_gz_content=preinstalled_meter.command(f"cat {path}/{level5_file}")
    logger.trace(Initial_file_gz_content)
    query=f'select level from FeatureConfiguration where FeatureID = 587464692 and level = 5;'
    level=preinstalled_meter.sql_query(query)
    file=f"{path}/{level5_file}"
    old_lid = 'value="1#0#0#0#Itron#0#0#0#0#255#255#587464692#1#0"'
    new_lid = 'value="1#5#5#100#ThirdParty:Publish#1#0#0#0#255#255#587464692#1#0"'
    file_content_change(preinstalled_meter,file,old_lid,new_lid)
    Final_file_gz_content=preinstalled_meter.command(f"cat {path}/{level5_file}")
    logger.trace('*********************')
    logger.trace(Final_file_gz_content)

    cmd = 'gzip '+level5_file
    try:
        log_file_path = '/tmp/container/587464704/rootfs/tmp/agent/2302fff4/2302fff4_log'
        preinstalled_meter.command(cmd)
        if not level:
            query=f"INSERT INTO FeatureConfiguration(FeatureId,FeatureVersion,ConfigurationId,Level,Data,LastUpdateTime) VALUES(587464692,0,0,5,readfile(\"{level5_file}.gz\"),{int(time.time())});"
            preinstalled_meter.sql_query(query)
        else:
            cmd = f'update featureconfiguration set data=readfile("{level5_file}.gz") where FeatureID = 587464692 and Level=5;'
            preinstalled_meter.sql_query(cmd)
        sec_log = validate_config_push(preinstalled_meter, logger, Third_Party_PubSub_AGENT.name, log_file_path)
        logger.trace('Step 7')
        if('Success' in sec_log):
            count = 0
            sec_log_prev = ''
            for i in range(20):
                time.sleep(10)
                sec_log_cur = preinstalled_meter.command('tail -s 10 /tmp/container/587464704/rootfs/tmp/agent/2302fff4/2302fff4_log')
                logger.trace('Step 8')
                sec_log_cur = ('').join(sec_log_cur)
                logger.trace(sec_log_cur)
                if "Add" in sec_log_cur and "Pub" in sec_log_cur:
                    logger.trace("Add & pub found")
                    logger.trace(sec_log_prev)
                    logger.trace(sec_log_cur)
                    if sec_log_cur != sec_log_prev:
                        count = count+1
                        assert "Add" in sec_log_cur and "Pub" in sec_log_cur
                        sec_log_prev = sec_log_cur
                    else:
                        logger.info(f'For {i} iteration previous log & current log are same')
                else:
                    logger.info(f'For {i} iteration Add & and Pub messaged not found')
            logger.trace(f'Count for getting proper log is: {count}')
            assert count >= 3,"Not getting proper log"
        else:
            logger.trace('config not push successfully')
    finally:
        preinstalled_meter.command(f'rm -rf *')
        level5_file="config/2302fff4.2303fff4.xml"
        path='/root'
        agent_file(preinstalled_meter,Third_Party_PubSub_AGENT,level5_file,base_dir=workdir,meter_dir=path)
        level5_file=level5_file.split("/")[-1]
        cmd = 'gzip '+level5_file
        preinstalled_meter.command(cmd)
        cmd = f'update featureconfiguration set data=readfile("{level5_file}.gz") where FeatureID = 587464692 and Level=5;'
        preinstalled_meter.sql_query(cmd)
        validate_config_push(preinstalled_meter, logger, Third_Party_PubSub_AGENT.name, log_file_path)
        preinstalled_meter.command(f'rm -rf *')


def validate_config_push(meter, logger, agent_name, log_file_path):
    stop = time.time() + (2*60)
    while time.time()<=stop:
        stdout = meter.command('ps | grep Agent')
        output = [x.split()[0] for x in stdout if('/usr/bin/' in x.split()[4] and f'{agent_name}_Daemon' in x.split()[4] and 'Z' not in x.split()[4])]
        if(len(output)!=0):
            break
        else:
            time.sleep(10)
    assert len(output),'timeout for condition check'
    meter.command(f'kill -9 {output[0]}')
    refresh_container(meter, logger,20*60)
    logger.trace('Step 6')
    stop = time.time() + (2*60)
    while time.time()<=stop:
        sec_log = meter.command(f'cat {log_file_path}')
        sec_log = ('').join(sec_log)
        if('Success' in sec_log):
            break
        else:
            time.sleep(10)
    assert 'Success' in sec_log,'timeout for condition check'
    return sec_log