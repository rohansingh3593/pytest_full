import logging
import os
import requests
import re
import time
from tests.test_meters.utils import AgentInfo,Active_Containers,filter_ps,is_process_running,refresh_container,wait_for_agents
from tests.test_meters.event_utils import get_meter_date
from itron.meter.Gen5Meter import SSHGen5Meter
import scp
import tempfile
import zipfile
import gzip
from datetime import datetime as dt
from datetime import timedelta as delta

LOGGER = logging.getLogger(__name__)

def agent_file(g5m: SSHGen5Meter, agent_info: AgentInfo,*files,base_dir,meter_dir=None) -> tuple:
    """

    file="PolicyFile.xml"
    file="PolicyFile.xml",'ReleaseManifest.xml'
    file="config/0302ff84.0303fffb.xml"

    """


    files=[file for file in files]
    url = agent_info.url
    r = requests.get(url, stream=True)
    r.raise_for_status()
    zipfile_name = os.path.join(base_dir, os.path.basename(url))
    # LOGGER.info('zipfile_name : %s',zipfile_name)
    with open(zipfile_name, 'wb') as file:
        for chunk in r.iter_content(chunk_size=8192):
            file.write(chunk)
            del chunk

    zipfile_name = os.path.abspath(zipfile_name)
    path = os.path.dirname(zipfile_name)
    file = os.path.basename(zipfile_name)
    LOGGER.debug("path: %s, file:%s", path, file)
    full = os.path.join(path,file)    
    # tmpdirpath = tempfile.mkdtemp()
    with tempfile.TemporaryDirectory() as tmpdirpath:
        with zipfile.ZipFile(full, 'r') as zip_ref:
            zip_ref.extractall(tmpdirpath)
        # dirs = os.listdir(tmpdirpath)
        path=[]
        # strdate = dt.now().strftime("%d-%m-%Y_%H_%M_%S")
        if meter_dir:
            target=meter_dir
        else:
            strdate=base_dir.split("/")[-1]
            target = f"/media/agent_info/{strdate}"
            cmd = f'mkdir -p {target}'
            absolute_command(g5m,cmd)
            # g5m.command(f'mkdir -p {target}')

        for file in files:
            serach_file = file
            _from = os.path.join(tmpdirpath, serach_file)
            if os.path.isfile(_from):
                _to =  os.path.join(target, os.path.basename(serach_file))
                LOGGER.info("scp %s %s", _from, _to)
                g5m.put_file(_from, _to)
                path.append(os.path.join(target, serach_file))
            else:
                LOGGER.error(f"{file} is not present in the package")
                assert False,f"{file} is not present in the package"
    LOGGER.info(f"{target}/{file}")
    return f"{target}/{file}"

def file_content_change(g5m: SSHGen5Meter,file,old_word,new_word=None,uncomment=False):

    temp_file=file
    file_base=temp_file.split("/")
    content_file = file_base.pop()
    path="/".join(file_base)
    dir= "Main" if path in [""," "] else path[1:]
    assert content_file in g5m.ls(path),f"{content_file} is not available in {dir} directory"
  
    cmd = f"cat {file}"


    data = absolute_command(g5m,cmd)

    file_content="\n".join(data)
    # LOGGER.info(file_content)
    assert old_word in file_content,f"{old_word} is not present in the {content_file}"

    if not new_word:
        if uncomment:
            # it will uncomment old_word.
            new_word=old_word
            old_word=f'<!--{old_word}-->'
        else:
            # it will comment it out the old_word.
            new_word=f'<!--{old_word}-->'

    cmd=f"sed -i 's+{old_word}+{new_word}+g' {file}"
    # g5m.command(cmd)
    absolute_command(g5m,cmd)
    cmd = f"cat {file}"
    file_content="\n".join(absolute_command(g5m,cmd))
    # LOGGER.info(file_content)
    assert new_word in file_content,f"{content_file} is not modified"

    

def Container_stop(meter: SSHGen5Meter,container_id :str):

    """ 
    Stop the particular Container which container id from the meter is Provided

    @param meter       : meter connection object
    @param container_id: Container Id

    """

    if container_id in Active_Containers(meter):
        cmd = f"dbus-send --print-reply --system --dest=com.itron.museplatform.ContainerManager /com/itron/museplatform/ContainerManager com.itron.museplatform.ContainerManager.StopOneContainer string:{container_id}"
        absolute_command(meter,cmd)


    stop = time.time() + (2*60)
    while time.time()<=stop:
        value = container_id in Active_Containers(meter)
        if not value:
            break
        time.sleep(10)

    assert not value,f"Container {container_id} did not stop"
    LOGGER.info("Container %s is stoped",container_id)

def agent_hex_code(meter: SSHGen5Meter, agent: AgentInfo):
    """ 
    From the meter It Provided hex code of the Agent 
    
    @param meter       : meter connection object
    @param agent       : Agent

    """
    # Getting the Agent ID form the Agent Information Table
    query=f'select AgentUID from agentinformation where AgentName = "{agent.name}";'
    assert meter.sql_query(query),f"{agent.name} is not installed in the meter"

    Agent_id=meter.sql_query(query)[0]
    return hex(int(Agent_id)).lstrip("0x")


def is_log_file_available(meter: SSHGen5Meter, agent: AgentInfo,stop=5*60):
        
    """ 
    From the meter It Provided Agent logging file is present in the folder and try to get the file after agent kill. 
    It will wait for some time (not less then 5 min) and keep checking that file present in the folder.
    
    @param meter       : meter connection object
    @param agent       : Agent
    @param stop        : time out

    """
    hex_code = agent_hex_code(meter, agent)

    # Checking --> Log File is available in the Agent Folder.
    path=f"/tmp/container/{agent.container_id}/rootfs/tmp/agent/0{hex_code}"
    file_name = f"0{hex_code}_log"

    log_time=time.time() + stop
    repeat=0
    while log_time > time.time():
        if file_name in meter.ls(path):
            break
        else:
            repeat+=1
        if repeat % 3 == 0:
            # After the 30 sec kill the again and wait for wake up if log file is not available.
            before_agent_pid = filter_ps(meter,f'{agent.name}_Daemon')
            assert before_agent_pid ,f"{agent.name} is not up and running"
            before_agent_pid = before_agent_pid[0][0]
            cmd = f"kill -9 {before_agent_pid}"
            absolute_command(meter,cmd)
            time_out=time.time() + 5*60
            while time_out>time.time():
                after_agent_pid = filter_ps(meter,f'{agent.name}_Daemon')
                value = before_agent_pid != after_agent_pid[0][0] if after_agent_pid else False
                if value:
                    break
                time.sleep(10)
            assert value ,f"{agent.name} is not up and running"
            
        elif repeat == 10:
            # After the 100 sec Dataserver will be refreshed if log file is not available.
            # Stop the DataServer
            Dataserver_refresh(meter,process="restart")
            repeat=0
        time.sleep(10)

    assert file_name in meter.ls(path),f'{file_name} is not available in {path}'
    LOGGER.info(f"{file_name} is available")
    return f'{path}/{file_name}'


def Dataserver_refresh(meter,process="restart"):

    """ 
    Stop/Start/Restart the Dataserver of meter

    @param meter       : meter connection object
    @param process     : process name --> "start","stop","restart"

    """

    def stop():
        # Stop the DataServer
        dataServerstop = time.time() + 5*60
        while time.time()<=dataServerstop:
            cmd = 'monit stop DataServer'
            absolute_command(meter,cmd)
            value = not filter_ps(meter,f"DataServer_Daemon")
            if value:
                LOGGER.info("DataServer is stop after the Stop command")
                break
            time.sleep(10)
        assert value,"DataServer is not stop after the Stop command"


    def start():
    # Start the DataServer
        dataServerstart = time.time() + 5*60
        while time.time()<=dataServerstart:
            cmd = 'monit start DataServer'
            absolute_command(meter,cmd)
            value = filter_ps(meter,f"DataServer_Daemon")
            if value:
                LOGGER.info("DataServer is start after the Start command")
                break
            time.sleep(10)
        assert value,"DataServer is not start after the Start command"

    
    def refresh():
        time_out=time.time()
        try:
            stop()
        finally:
            start()
        time_taken=int(time.time()-time_out)
        LOGGER.info(f"Dataserver is restared after a {time_taken}sec ")


    result={"start":start,"stop":stop,"restart":refresh}
    function=result.get(process,None)

    return function()


def Refresh_AgentFeatureDataCounter(meter: SSHGen5Meter,agent: AgentInfo):
    """ 
    From the meter It refreshed AgentFeatureDataCounter table with updating the some coloums.

    @param meter       : meter connection object
    @param agent       : Agent

    """

    # Getting the Agent ID form the Agent Information Table
    query=f'select AgentUID from agentinformation where AgentName = "{agent.name}";'
    assert meter.sql_query(query),f"{agent.name} is not installed in the meter"
    query=f'select AgentUID from agentinformation where AgentName = "{agent.name}";'
    agent_id=meter.sql_query(query)[0]

    # refresh Agent counter table 
    query=f'update AgentFeatureDataCounter SET DailyUpstreamDataSent=0,\
        P2PBroadcastDataSentPlc=0,P2PBroadcastDataSentRf=0,P2PUnicastDataSentRf=0,\
            DailyAlarmMessagesSent=0,P2PBroadcastStaticDataSentPlc=0,P2PBroadcastStaticDataSentRf=0,\
                P2PUnicastStaticDataSentRf=0,P2PBroadcastIBDailyDataSentCounterPlc=0,\
                    P2PBroadcastIBDailyDataSentCounterRf=0,P2PUnicastDailyDataSentCounterRf=0,\
                        P2PBroadcastIB1hrDataSentCounterPlc=0,P2PBroadcastIB1hrDataSentCounterRf=0,\
                            P2PUnicast1hrDataSentCounterRf=0 where agentid = "{agent_id}"'
    meter.sql_query(query)
    LOGGER.info(f"AgentDataCounter table is refreshed the counters for {agent.name}")



def Refresh_Agentevent(meter: SSHGen5Meter,agent: AgentInfo):
    """ 
    From the meter It refreshed AgentEvent table with Deleting previous activate/success massage (98# and etc.).

    @param meter       : meter connection object
    @param agent       : Agent

    """

    # Getting the Agent ID form the Agent Information Table
    query=f'select AgentUID from agentinformation where AgentName = "{agent.name}";'
    assert meter.sql_query(query),f"{agent.name} is not installed in the meter"
    query=f'select AgentUID from agentinformation where AgentName = "{agent.name}";'
    agent_id=meter.sql_query(query)[0]

    query = f'select count(*) from AgentEvents where agentid = "{agent_id}"'
    count=meter.sql_query(query)
    if count:
        count=int(count[0])
        LOGGER.info("count : %s",count)
        if count>1:
            query = f'select Id from AgentEvents where agentid = "{agent_id}" order by Id desc limit {count-1}'
            ids=meter.sql_query(query)
            # LOGGER.info("Id : %s",ids)
            for id in ids:
                query = f'delete from AgentEvents where agentid = "{agent_id}" and Id = "{id}"'
                # LOGGER.info(query)
                meter.sql_query(query)
    
    LOGGER.info(f'AgentEvents table is refreshed for {agent.name}')

def Refresh_Agentdata(meter: SSHGen5Meter,agent: AgentInfo):

    """ 
    From the meter It refreshed AgentData table with Deleting previous Error massage (error and errcode etc.).

    @param meter       : meter connection object
    @param agent       : Agent

    """
    
    # Getting the Agent ID form the Agent Information Table
    query=f'select AgentUID from agentinformation where AgentName = "{agent.name}";'
    assert meter.sql_query(query),f"{agent.name} is not installed in the meter"
    agent_id=meter.sql_query(query)[0]

    query = f'select data from Agentdata WHERE agentid = "{agent_id}" and (data LIKE "%error%" or data LIKE "%errcode%")'
    LOGGER.info(query)

    data = meter.sql_query(query)

    if data:
        query = f'delete from Agentdata WHERE agentid = "{agent_id}" and (data LIKE "%error%" or data LIKE "%errcode%")'
        meter.sql_query(query)
        LOGGER.info(query)


        query = f'select count(*) from Agentdata WHERE agentid = "{agent_id}" and (data LIKE "%error%" or data LIKE "%errcode%")'
        count=meter.sql_query(query)

        if count:
            count=int(meter.sql_query(query)[0])
        LOGGER.info("count : %s",count)            
    LOGGER.info(f'Agentdata table is refreshed for {agent.name} ')


def All_Agent_Table_Refresh(meter: SSHGen5Meter,agent: AgentInfo):
    """ 
    From the meter It refreshed all table related to Agent and refresh the DateServer and refresh the Agent container.

    @param meter       : meter connection object
    @param agent       : Agent

    """

    Refresh_AgentFeatureDataCounter(meter,agent)
    Refresh_Agentevent(meter,agent)
    Refresh_Agentdata(meter,agent)

    # Restarting a Dataserver
    Dataserver_refresh(meter)

    # Stop the Container
    Container_stop(meter,agent.container_id)

    # Start the container
    refresh_container(meter,LOGGER,20*60)
    assert agent.container_id in Active_Containers(meter),f"Container {agent.container_id} is not start after the Container Start command"



def all_file_read(meter: SSHGen5Meter,path,file_name,include_gz=False,destination_path=None):


    """ 
    From the meter It Get all log and event file on the time basis related to Agent,Appser,Dataserver, Container after refresh the DateServer and refresh the Agent container.

    @param meter       : meter connection object
    @param agent       : Agent

    """

    # 2023-03-24 08:53:27 
    fmt = "%Y-%m-%d %H:%M:%S"
    search = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
    meter_time = absolute_command(meter,f'date -u +"{fmt}"')[0]
    time_reference = dt.strptime(meter_time, fmt) - delta(minutes=30)

    LOGGER.info(meter_time)
    LOGGER.info(time_reference)

    all_files=[]
    file_cmd = f'ls {path}/{file_name}* --full-time -ltr'
    simple_file=absolute_command(meter,file_cmd)

    simple_file={i.split()[-1]:re.findall(search,i)[0] for i in simple_file}
    simple_file = dict(sorted(simple_file.items(), key=lambda x: dt.strptime(x[1],fmt))) 

    # simple_file = {key:value for (key, value) in simple_file.items()}
    # filter on the time basis 15 minites
    simple_file = {key:value for (key, value) in simple_file.items() if dt.strptime(value,fmt) >= time_reference}

    [all_files.append(key) for key,value in simple_file.items()]

    if len(all_files) > 1:
        log_message = ""
        with tempfile.TemporaryDirectory() as tmpdirpath:
            for file in all_files:
                meter.get_file(file, tmpdirpath)
            
            dirs = os.listdir(tmpdirpath)
            LOGGER.info(dirs)
            stop = time.time() + 60
            while time.time()<=stop:
                value = all(file.split("/")[-1] in dirs for file in all_files)
                if value:
                    LOGGER.info("All file is successfully Grab from the meter")
                    break
                time.sleep(5)
                
            for file in all_files:
                file=file.split("/")[-1]
                if file.endswith(".gz"):
                    with gzip.open(f'{tmpdirpath}/{file}') as f:
                        log_message += f.read().decode()
                else:
                    with open(f'{tmpdirpath}/{file_name}', 'r') as f:
                        log_message+=f.read()


            full_log_file=f'{tmpdirpath}/full_{file_name}'
            with open(full_log_file, "w") as f:
                f.truncate(0)
                f.write(log_message)
            full_log_file=full_log_file.split("/")[-1]

            if destination_path:
                target=destination_path
            else:
                target = f"/media/{tmpdirpath}"
                absolute_command(meter,f'mkdir -p {target}')
                
            meter.put_file(f'{tmpdirpath}/{full_log_file}', target)
            LOGGER.info(meter.ls(target))

            time_out=time.time() + 60
            while time_out>time.time():
                file_updated_status = full_log_file in meter.ls(target)
                if file_updated_status:
                    break
                time.sleep(5)
            assert file_updated_status,f'{file_name} is not available in {target}'
        LOGGER.info('File is send to %s Directory',f'{target}/{full_log_file}')

        return f'{target}/{full_log_file}'



def collect_file(meter,file,extension,time_ref=10):

    """ 
    Collect all file from the meter which is recently update according to time

    @param meter: meter connection object
    @param file: file full location
    @param extension: type of file like .txt, .gz, .xml
    @param time_ref: time refrence in minutes

    """

    search = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
    fmt = "%Y-%m-%d %H:%M:%S"
    meter_time = absolute_command(meter,f'date -u +"{fmt}"')[0]
    time_reference = dt.strptime(meter_time, fmt) - delta(minutes=time_ref)
    file = meter.ls(file + '* --full-time -ltr')

    simple_file={(i.split()[-1]):(re.findall(search,i)[0]) for i in file}
    simple_file = dict(sorted(simple_file.items(), key=lambda x: dt.strptime(x[1],fmt))) 

    # filter on the time basis reference time
    simple_file = {key:value for (key, value) in simple_file.items() if dt.strptime(value,fmt) > time_reference}

    filter_file=[]
    [filter_file.append(key) for key,value in simple_file.items() if key.endswith(extension)]

    return filter_file



def unzip_file(meter,file,time_ref):


    """ 
    Unzip all file from the meter which is recently update according to time

    @param meter: meter connection object
    @param file: file full location
    @param time_ref: time refrence in minutes

    """

    zip_file = collect_file(meter,file,".gz",time_ref)
    # LOGGER.info("Available GZ file is %s",zip_file)
    for i in zip_file:
        absolute_command(meter,f"gunzip {i}",)

    unzip_file = [file.replace(".gz","") for file in zip_file]
    return unzip_file



def agent_Config_collect(meter: SSHGen5Meter,agent: AgentInfo,feature_id : str,base_dir: str,force = False):


    """ 
        Collect the Config file from the meter according to Feature iD provided.

    @param meter       : meter connection object
    @param agent       : Agent
    @param feature_id  : Feature id
    @param base_dir    : base Directory
    @param force       : if True It will collect the fresh config file from the Agent Package

    """
    # Getting the Level --> 5 form the FeatureConfiguration Table for Agent
    query=f'select level from FeatureConfiguration where FeatureID = \"{feature_id}\" and level = 5'
    level=meter.sql_query(query)

    meter_dir='/root'

    agent_gz_file=f"{feature_id}.xml.gz"
    agent_xml_file=f"{feature_id}.xml"
    if agent_gz_file in meter.ls(meter_dir):
        absolute_command(meter,f"rm {meter_dir}/{agent_gz_file}")
    if agent_xml_file in meter.ls(meter_dir):
        absolute_command(meter,f"rm {meter_dir}/{agent_xml_file}")

    if (not level) or force:
        # Geting the Gz File from the Agent Package
        agentid_hexcode = agent_hex_code(meter, agent)
        featureid_hexcode = hex(int(feature_id)).lstrip("0x")
        # LOGGER.info(featureid_hexcode)
        # level5_file="config/0302ff84.0303fffb.xml"
        level5_push_file = f"config/0{agentid_hexcode}.0{featureid_hexcode}.xml"
        if str(feature_id).startswith("58"):
            level5_push_file = f"config/{agentid_hexcode}.{featureid_hexcode}.xml"
        # LOGGER.info(level5_push_file)
        agent_file(meter,agent,level5_push_file,base_dir=base_dir,meter_dir = meter_dir)
        xml_file = level5_push_file.split("/")[-1]
        absolute_command(meter,f"mv {meter_dir}/{xml_file} {meter_dir}/{agent_xml_file}")



    else:

        # Geting the Gz File from the FeatureConfiguration table
        time_out=time.time() + 60
        while time_out>time.time():
            query = f'select writefile(\"{agent_gz_file}\",Data) from FeatureConfiguration where FeatureID = \"{feature_id}\" and Level = 5;'
            meter.sql_query(query)
            status = agent_gz_file in meter.ls(meter_dir)
            if status:
                LOGGER.info("Gz File got from the FeatureConfiguration table")
                break
            time.sleep(5)

        assert status ,f"{agent_gz_file} is not present in {meter_dir[1:]}"    
        absolute_command(meter,f"gunzip {meter_dir}/{agent_gz_file}")

        if agent_gz_file in meter.ls(meter_dir):
            absolute_command(meter,f"rm {meter_dir}/{agent_gz_file}")


        assert not agent_gz_file in meter.ls(meter_dir),f"{agent_gz_file} is still present in the in {meter_dir[1:]} directory"

    assert agent_xml_file in meter.ls(meter_dir),f"{agent_xml_file} is not available in {meter_dir[1:]} directory"
    return f"{meter_dir}/{agent_xml_file}"

def Config_push(meter: SSHGen5Meter,feature_id:str):
        
    """ 
    Push the Config file to the meter according to Feature iD provided.

    @param meter       : meter connection object
    @param feature_id  : Feature id
    """

    meter_dir='/root'

    agent_gz_file=f"{feature_id}.xml.gz"
    agent_xml_file=f"{feature_id}.xml"
    TIMESTAMP = int(absolute_command(meter,'date +%s')[0])
    itroncontainerid= '50593792'
    thirdpartycontainerid="587464704"
    containertouse=itroncontainerid
    if str(feature_id).startswith("58"):
        containertouse=thirdpartycontainerid
    metertype = int(absolute_command(meter,"cat /etc/Version.txt | grep Major | cut -d':' -f2 | xargs")[0])
    CONFIGDATA = absolute_command(meter,"hexdump -v -e"+" '/1"+' "%d"","'+"'"+' '+agent_xml_file)[0]
    absolute_command(meter,f"dbus-send --bus=unix:path=/tmp/container/{int(containertouse)}/container_bus_socket /com/itron/owi/platform/dataserver com.itron.owi.platform.dataserver.FeatureUpdate uint64:{int(feature_id)} uint32:{TIMESTAMP} uint32:0 array:byte:{CONFIGDATA}")
    #pdb.set_trace()
    absolute_command(meter,f"gzip {agent_xml_file}")

    CONFIGDATAGZ = absolute_command(meter,f"""hexdump -v -e '/1 "%02x"' {agent_gz_file}""")[0]
    Data = f"X'{CONFIGDATAGZ}'"
    
    absolute_command(meter,f'''sqlite3 -bail -batch /usr/share/itron/database/muse01.db "update  featureconfiguration set lastupdatetime={TIMESTAMP},Data={Data} where featureid={feature_id};"''')
    absolute_command(meter,"rm -rf *.xml")
    absolute_command(meter,"rm -rf *.gz")



def agent_policy_collect(meter: SSHGen5Meter,agent: AgentInfo,base_dir:str,force = False):

    """ 
    Collect the Policy file from the meter according to Agent.

    @param meter       : meter connection object
    @param agent       : Agent
    @param base_dir    : base Directory
    @param force       : if True It will collect the fresh Policy file from the Agent Package

    """

    meter_dir='/root'

    if f"{agent.name}_PolicyFile.xml" in meter.ls(meter_dir):
        absolute_command(meter,f"rm {meter_dir}/{agent.name}_PolicyFile.xml")

    # Getting the Agent ID form the Agent Information Table
    query=f'select AgentUID from agentinformation where AgentName = "{agent.name}";'
    assert meter.sql_query(query),f"{agent.name} is not installed in the meter"
    Agent_id=meter.sql_query(query)[0]

    if force:
        # Update the policy file at the DIPolicyFile table at initial State
        agent_file(meter,agent,"PolicyFile.xml",base_dir=base_dir,meter_dir=meter_dir)
        assert "PolicyFile.xml" in meter.ls(meter_dir),f"PolicyFile.xml is not available in {meter_dir[1:]} directory"
        absolute_command(meter,f"mv {meter_dir}/PolicyFile.xml {meter_dir}/{agent.name}_PolicyFile.xml")
    else:
        # Geting the PolicyFile from the Di policy file table.
        time_out=time.time() + 5*60
        while time_out>time.time():
            query = f'select writefile(\"{agent.name}_PolicyFile.xml\",Policyfile) from DIPolicyFile where AgentId = \"{Agent_id}\";'
            meter.sql_query(query)
            value = f"{agent.name}_PolicyFile.xml" in meter.ls(meter_dir)
            if value:
                LOGGER.info(f"{agent.name}_PolicyFile.xml is Updated at the DIPolicyFile table")
                break
            time.sleep(10)
        assert value,"PolicyFile is not got from the DiPolicyFile table"

    assert f"{agent.name}_PolicyFile.xml" in meter.ls(meter_dir),f"{agent.name}_PolicyFile.xml is not available in {meter_dir[1:]} directory"
    return f"{meter_dir}/{agent.name}_PolicyFile.xml"


def policy_file_push(meter: SSHGen5Meter,agent: AgentInfo):

    """ 
    Push the Policy file from the meter according to Agent.

    @param meter       : meter connection object
    @param agent       : Agent

    """

    meter_dir='/root'
    
    # Getting the Agent ID form the Agent Information Table
    query=f'select AgentUID from agentinformation where AgentName = "{agent.name}";'
    assert meter.sql_query(query),f"{agent.name} is not installed in the meter"
    Agent_id=meter.sql_query(query)[0]
    

    test_xml_file=f"test_{agent.name}_PolicyFile.xml"

    if test_xml_file in meter.ls(meter_dir):
        absolute_command(meter,f"rm {meter_dir}/{test_xml_file}")


    assert f"{agent.name}_PolicyFile.xml" in meter.ls(meter_dir),f"{agent.name}_PolicyFile.xml is not available in {meter_dir[1:]} directory"
    policy_file_content=absolute_command(meter,f"cat {meter_dir}/{agent.name}_PolicyFile.xml")

    # Update the policy file
    time_out=time.time() + 5*60
    while time_out>time.time():
        query=f'replace into DIPolicyFile(AgentId,TimeStamp,PolicyFile) VALUES({Agent_id},0,readfile(\"{agent.name}_PolicyFile.xml\"));'
        meter.sql_query(query) 

        # collecting Test xml File from the DIPolicyFile table
        stop=time.time() + 30
        while stop>time.time():
            query = f'select writefile(\"{test_xml_file}\",Policyfile) from DIPolicyFile where AgentId = \"{Agent_id}\";'
            meter.sql_query(query)
            status = test_xml_file in meter.ls(meter_dir)
            if status:
                LOGGER.info("Test xml File is got from the DIPolicyFile  table")
                break
            time.sleep(5)

        assert status ,f"{test_xml_file} is not present in {meter_dir[1:]}"

        test_xml_file_content=absolute_command(meter,f'cat {meter_dir}/{test_xml_file}')

        if test_xml_file in meter.ls(meter_dir):
            absolute_command(meter,f"rm {meter_dir}/{test_xml_file}")

        assert not test_xml_file in meter.ls(meter_dir),f"{test_xml_file} is still available in {meter_dir[1:]} directory"

        if test_xml_file_content==policy_file_content:
            LOGGER.info(f"policy File is Updated at the DIPolicyFile table")
            absolute_command(meter,"SwitchDIInits.sh -s")
            time.sleep(2)           
            wait_for_agents(meter,LOGGER,[agent],20*60)
            break
        time.sleep(5)


    if f'{agent.name}_PolicyFile.xml' in meter.ls(meter_dir):
        absolute_command(meter,f"rm {meter_dir}/{agent.name}_PolicyFile.xml")

    assert test_xml_file_content==policy_file_content ,"Policy File Not Update in the DiPolicyFile table"



def absolute_command(meter: SSHGen5Meter,command:str,timeout = 10):

    """ 
    This function is keep executing the command until we did not get any error .

    @param meter       : meter connection object
    @param command     : Execiting command
    @param timeout     : time of execution

    """

    cmd_out=time.time() + timeout
    while cmd_out>time.time():    
        code,data=meter.command_with_code(command)
        if code == 0:
            # LOGGER.info('command is executed Succesfully')
            break
        time.sleep(2)

    assert code == 0 ,"Command is not executed"
    return data



def to2k(version): 
    ver = version.split('.') 
    ver2k = int(ver[2]) + 2000 
    ver[2] = str(ver2k) 
    ver2k = '.'.join(ver) 
    return ver2k