"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2003671
===================================================================================================
Test Case      : 2003671
Description    : Verify the Container manager functionalities when container starts with DbusConnectionType is “percontainer”
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 -
Verify the Dbus configuration generated under /tmp/container

Step 2 -
Check if the following folder is created:
/tmp/container/[ContainerUID]/dbuscontainer.d       - Dbus configuration gets generated into this
folder /tmp/container/[ContainerUID]/dbuscontainer.d  instead of /etc/dbus-1/system.d/.

Step 3 -
Check if overlay configurations( originally from B2DatavLibrary overlay)  are present in
dbuscontainer.d ls /tmp/container/50593792/dbuscontainer.dList the contents to check for the overlay
conf files

Step 4 -
#cd /tmp/container/50593792/dbuscontainer.d\n# ls\n50593792-33882114.conf  50593792-33882116.conf
50593792-50659330.conf  50593792-50659333.conf  50593792-50724727.conf\n\n

Step 5 -
Verify  session.confcat /tmp/container/50593792/session.conf  --> for Itron containercat
/tmp/container/587464704/session.conf  --> for ThirdParty container

Step 6 -
A container specific version of dbus configuration gets generated into
/tmp/container/[ContainerUID]/session.conf by replacing correct container id. Check for the below
entry in session.conf :  #cat /tmp/container/50593792/session.conf ..
<listen>unix:path=/tmp/container/50593792/container_bus_socket</listen>\n     # cat /tmp/container/5
87464704/session.conf..<listen>unix:path=/tmp/container/587464704/container_bus_socket</listen>

Step 7 -
Verify lxc mount entry in lxc.confcat /tmp/container/50593792/lxc.conf cat
/tmp/container/587464704/lxc.conf

Step 8 -
 In the generation of the LXC configuration file, an entry will be generated with the respective
container id   # cat /tmp/container/50593792/lxc.conf Check for the below entry : lxc.mount.entry  =
/tmp/container/50593792/container_bus_socket var/run/dbus/system_bus_socket none ro,bind,optional 0
0 # cat /tmp/container/587464704/lxc.conf ...lxc.mount.entry =
/tmp/container/587464704/container_bus_socket var/run/dbus/system_bus_socket none ro,bind,optional 0
0


===================================================================================================


"""
import pytest
from tests.test_meters.utils import HAN_AGENT,Third_Party_PubSub_AGENT,install_multiple_agents_and_activate
# AUTOGENERATED Test Case 2003671

#@pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2002265")
@pytest.mark.test_case("2003671")
def test_case(preinstalled_meter, logger):
    logger.trace("Executing Test Case 2003671 - Verify the Container manager functionalities when container starts with DbusConnectionType is  percontainer ")
    agent_list = [HAN_AGENT,Third_Party_PubSub_AGENT]
    install_multiple_agents_and_activate(preinstalled_meter, logger, agent_list)
    preinstalled_meter.command('ps | grep -i lxc')
    logger.trace('Step 1')
    container_id=preinstalled_meter.ls("/tmp/container")
    container_data=' '.join([str(x) for x in container_id])
    assert '587464704' in container_data and '50593792' in container_data
    logger.trace('Step 2')
    """Check if the following folder is created:"""
    logger.trace('Step 3')
    """Check if overlay configurations"""
    logger.trace('Step 4')
    dbuscontain=preinstalled_meter.command('ls /tmp/container/50593792/dbuscontainer.d')
    dbuscontain_data=" ".join([x for x in dbuscontain])
    assert '50593792-33882114.conf' in dbuscontain_data
    logger.trace('Step 5')
    session_data=preinstalled_meter.command('cat /tmp/container/50593792/session.conf')
    third_party_session_data=preinstalled_meter.command('cat /tmp/container/587464704/session.conf')
    logger.trace('Step 6')
    assert '<listen>unix:path=/tmp/container/50593792/container_bus_socket</listen>' in str(session_data)
    assert '<listen>unix:path=/tmp/container/587464704/container_bus_socket</listen>' in str(third_party_session_data)
    logger.trace('Step 7')
    itron_container=preinstalled_meter.command('cat /tmp/container/50593792/lxc.conf')
    third_party_container=preinstalled_meter.command('cat /tmp/container/587464704/lxc.conf')
    logger.trace('Step 8')
    itron_container_variable='lxc.mount.entry = /tmp/container/50593792/container_bus_socket var/run/dbus/system_bus_socket none ro,bind,optional 0 0'
    itron_container_string=' '.join([str(x) for x in itron_container])
    assert itron_container_variable in itron_container_string
    third_party_container_string_variable='lxc.mount.entry = /tmp/container/587464704/container_bus_socket var/run/dbus/system_bus_socket none ro,bind,optional 0 0'
    third_party_container_string=' '.join([str(x) for x in third_party_container])
    assert third_party_container_string_variable in third_party_container_string