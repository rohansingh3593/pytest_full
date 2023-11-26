"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1/AppServ-Installation
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/1993237
===================================================================================================
Test Case      : 1993237
Description    : Verify all the tables related to container with columns are present in the DB
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Check whether all the tables related to Container are present in the
/usr/share/itron/database/muse01.db The tables are containersetup, overlaysetup, containeroverlay,
overlayconfiguration. sqlite3 /mnt/common/database/muse01.db \"select * from CONTAINERSETUP\"sqlite3
/mnt/common/database/muse01.db \"select * from overlaysetup\"sqlite3 /mnt/common/database/muse01.db
\"select * from containeroverlay\" sqlite3 /mnt/common/database/muse01.db \"select * from
overlayconfiguration\"  and also verify containerstatus under /tmp/muse01.db  -   sqlite3 --header
/tmp/muse01.db \"select * from CONTAINERSTATUS;\"

Step 2 - 
All the tables related to container should be present inside the database.


===================================================================================================


"""
import pytest
from tests.test_meters.utils import install_agent_and_activate,HAN_AGENT

@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("1993280")
@pytest.mark.test_case("1993237")
def test_case(preinstalled_meter, logger):
    logger.trace("Executing Test Case 1993237 - Verify all the tables related to container with columns are present in the DB")
    logger.trace('Step 1')
    install_agent_and_activate(preinstalled_meter,logger,HAN_AGENT)
    containersep=preinstalled_meter.sql_query("select * from CONTAINERSETUP")
    overlaysetup=preinstalled_meter.sql_query("select * from overlaysetup")
    containeroverlay=preinstalled_meter.sql_query("select * from containeroverlay")
    overlayconfiguration=preinstalled_meter.sql_query("select * from overlayconfiguration")
    logger.trace('Step 2')
    assert len(containersep)>0,'CONTAINERSETUP table not exist'
    assert len(overlaysetup)>0,'overlaysetup table not exist'
    assert len(containeroverlay)>0,'containeroverlay table not exist'
    assert len(overlayconfiguration)>0,'overlayconfiguration table not exist'


