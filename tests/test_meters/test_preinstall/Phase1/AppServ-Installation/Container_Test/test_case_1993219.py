"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1/AppServ-Installation
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/1993219
===================================================================================================
Test Case      : 1993219
Description    : CMCreateContainers
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 -
Create container by using any agent package.ex: HID agent package creates single container on the
system. Once the container is created, in order to create multiple containers use the sqlite command
to update the tables of containersetup and overlaysetup. Execute the below sqlite3 statements by
changing the uid and containeruid in order to create multiple containers.#sqlite3
/mnt/common/database/muse01.db \"update containersetup set uid=50593793 where uid=50593792\"#
sqlite3 /mnt/common/database/muse01.db \"update containeroverlay setcontaineruid=50593793 where
containeruid=50593792\"

Step 2 -
ps output should show the created lxc containers - which is  50593793 on the system Check using : ps
| grep -i contain and ps | grep -i lxc


===================================================================================================


"""
import pytest
import time
from tests.test_meters.utils import install_agent_and_activate,stop_container,refresh_container,DI_TEST_AGENT

# AUTOGENERATED Test Case 1993219

#@pytest.mark.slow1020
@pytest.mark.regress_nightly
@pytest.mark.suite_id("1993280")
@pytest.mark.test_case("1993219")
def test_case(preinstalled_meter, logger):
    logger.trace("Executing Test Case 1993219 - CMCreateContainers")

    logger.trace('Step 1')

    install_agent_and_activate(preinstalled_meter,logger,DI_TEST_AGENT)
    try:
        preinstalled_meter.sql_query("update containersetup set uid=50593793 where uid=50593792")
        preinstalled_meter.sql_query("update containeroverlay set containeruid=50593793 where containeruid=50593792")
        stop_container(preinstalled_meter)
        preinstalled_meter.command('dbus-send --type=signal --system --dest=com.itron.museplatform.ContainerManager /com/itron/museplatform/ContainerManager com.itron.museplatform.ContainerManager.Refresh')
        logger.trace('Step 2')
        stop = time.time() + (2*60)
        while time.time()<=stop:
            stdout = preinstalled_meter.command('ps | grep -i contain')
            contain_data = [con for con in stdout if '50593793' in con]
            if(len(contain_data)!=0):
                break
            else:
                time.sleep(10)

        assert len(contain_data)!=0,"timeout for condition check"

        stdout = preinstalled_meter.command('ps | grep -i lxc')
        output = [con for con in stdout if '50593793' in con]
        assert len(output)!=0
    finally:
        """Following lines of code is for reseting the default container uid"""
        preinstalled_meter.gmr()

