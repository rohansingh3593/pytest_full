
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/R3.1
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2672851
===================================================================================================
Test Case      : 2672851
Description    : Verify the new Obis code present in AppServicesCosem.xml
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Check for the new OBIS code - 0-128:96.20.19.255 in AppServicesCosem.xml.  #cat
/usr/share/itron/DI.AppServices/AppServicesCosem.xml

Step 2 - 
<obisCode code=\"0-128:96.20.19.255\" name=\"DI ApplicationServices Installation Package Expected
Hash\" class=\"1\">\n      <properties>\n        <property type=\"attribute\" index=\"[1,2]\">\n
<clients>\n            <client name=\"[CollectionEngine,Tools]\">\n              <access
get=\"true\" set=\"false\" action=\"false\" />\n            </client>\n          </clients>\n
<roles>\n            <role name=\"[meter,meter_cfg,rd]\"  >\n              <access get=\"true\"
set=\"false\" action=\"false\" />\n            </role>\n          </roles>\n        </property>\n
</properties>\n    </obisCode>\n


===================================================================================================


"""
import pytest


#@pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2672846")
@pytest.mark.test_case("2672851")
def test_case(preinstalled_meter, logger, di_version):
    logger.trace("Executing Test Case 2672851 - Verify the new Obis code present in AppServicesCosem.xml")
    logger.trace('Step 1')
    std_out= preinstalled_meter.command('cat /usr/share/itron/DI.AppServices/AppServicesCosem.xml')
    logger.trace('Step 2')
    std_out= preinstalled_meter.command('grep -c "0-128:96.15.22.255" /usr/share/itron/DI.AppServices/AppServicesCosem.xml')
    std_out=int(std_out[0])
    assert std_out>0



