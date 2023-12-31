"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2004429
===================================================================================================
Test Case      : 2004429
Description    : Verify the B2datavLibrary overlay changes to interact with any Bsquare d-bus connections outside the container
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Verify the B2datavLibrary overlay changes to interact with any Bsquare d-bus connections outside the
container.sqlite3 --header /usr/share/itron/database/muse01.db \"select * from
overlayconfiguration\"

Step 2 - 
Sending and/or receiving communication with
org.bsquare.datav.itrondi.signal.source,\norg.bsquare.datav.itrondi.method.caller, and
org.bsquare.datav.itrondi.method.server. \nWhen creating the overly for B2DatavLibrary, it an entry
should be added to the OVERLAYCONFIGURATION table for the d-bus data.
<?xmlversion=\"1.0\" encoding=\"UTF-8\"?><!DOCTYPE\nbusconfig PUBLIC\"-//freedesktop//DTD\nD-BUS Bus
Configuration
1.0//EN\"\"http://www.freedesktop.org/standards/dbus/1.0/busconfig.dtd\"><busconfig><!-- These need
to be available to the\nagents. --><policy\ngroup=\"container_dbus_g\"><allow\nsend_destination=\"or
g.bsquare.datav.itrondi.signal.source\" send_interface=\"org.bsquare.datav.itrondi.signal.source\" /
><allow\nsend_destination=\"org.bsquare.datav.itrondi.method.caller\"send_interface=\"org.bsquare.da
tav.itrondi.method.caller\"
/><allow\nreceive_sender=\"org.bsquare.datav.itrondi.method.server\"\nreceive_type=\"method_call\"
/>                                    <allowsend_destination=\"org.bsquare.datav.itrondi.method.serv
er\"send_interface=\"org.bsquare.datav.itrondi.method.server\" /></policy></busconfig>


===================================================================================================


"""
import pytest
from tests.test_meters.utils import DI_TEST_AGENT,install_agent_and_activate

# AUTOGENERATED Test Case 2004429
# @pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2002265")
@pytest.mark.test_case("2004429")
def test_case(preinstalled_meter, logger):
    logger.trace("Executing Test Case 2004429 - Verify the B2datavLibrary overlay changes to interact with any Bsquare d-bus connections outside the container")
    logger.trace('Step 1')
    install_agent_and_activate(preinstalled_meter,logger,DI_TEST_AGENT)
    OVERLAYCONFIGURATION_table=preinstalled_meter.sql_query('select configuration from overlayconfiguration')
    varifivation_code=["D-BUS Bus Configuration 1.0","container_dbus_g",'"org.bsquare.datav.itrondi.signal.source"','send_interface="org.bsquare.datav.itrondi.signal.source"',
                        'send_destination="org.bsquare.datav.itrondi.method.caller"','send_interface="org.bsquare.datav.itrondi.method.caller"',
                        'receive_sender="org.bsquare.datav.itrondi.method.server"', 'send_destination="org.bsquare.datav.itrondi.method.server"',
                        'send_interface="org.bsquare.datav.itrondi.method.server"']
    res = all([any(clr in sub for sub in OVERLAYCONFIGURATION_table) for clr in varifivation_code])
    logger.trace('Step 2')
    assert res,"B2 datav Library overlay is not changes to interact with any Bsquare d-bus connections outside the container"
