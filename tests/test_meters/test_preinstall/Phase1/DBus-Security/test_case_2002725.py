"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2002725
===================================================================================================
Test Case      : 2002725
Description    : Verify if the DI install script is populating/updating the new field "DbusConnectionType" in "containersetup" table.
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Verify that the DbusConnectionType field is 1 for Dbus (and 3 in case of systembus- old)sqlite3
--header /usr/share/itron/database/muse01.db \"select * from containersetup\"

Step 2 - 
# sqlite3 --header /usr/share/itron/database/muse01.db \"select * from containersetup\"\nGroupId|UID
|DesiredState|ContainerStartDelayMS|TempFilesystemSizeBytes|PriorityLevel|IgnoreResourceUsage|Friend
lyName|DbusConnectionType\n1|50593792|1|0|8000000|20|0|Itron|1\n1|587464704|1|0|8000000|20|0|3rdPart
y|1\n


===================================================================================================
"""
import pytest
#@pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2002265")
@pytest.mark.test_case("2002725")
def test_case(preinstalled_meter, logger, di_version):
    logger.trace("Executing Test Case 2002725 - Verify if the DI install script is populating/updating the new field \"DbusConnectionType\" in \"containersetup\" table.")
    logger.trace('Step 1')
    std_out=preinstalled_meter.sql_query("select DbusConnectionType from containersetup")
    logger.trace('Step 2')
    assert all([i=="1" for i in std_out])
