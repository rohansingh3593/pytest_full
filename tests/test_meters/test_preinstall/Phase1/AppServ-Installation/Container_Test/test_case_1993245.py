"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1/AppServ-Installation
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/1993245
===================================================================================================
Test Case      : 1993245
Description    : Verify that an event is logged when the container stop fails 
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
update the table - OVERLAYSETUP  with an invalid Agent

 "insert into OVERLAYSETUP (GroupId, UID, OverlayVersion, OverlayPath, IsDeletable, Source) values (1, 25,1, '/usr/share/itron/container-overlays/MockAgent.tar.bz2', 0, 0);" 2>&1

Step 2 -
Make appropriate entry in CONTAINEROVERLAY as well

 "insert into CONTAINEROVERLAY (GroupId, ContainerUID, OverlayUID, LoadIndex) values (1, 50593792,25, 15);" 2>&1

Step 3-
Stop the container and Refresh it.



dbus-send --type=signal --system --dest=com.itron.museplatform.ContainerManager /com/itron/museplatform/ContainerManager com.itron.museplatform.ContainerManager.StopAllContainer

dbus-send --type=signal --system --dest=com.itron.museplatform.ContainerManager /com/itron/museplatform/ContainerManager com.itron.museplatform.ContainerManager.Refresh

wait for 3 min 
Step 4-
Note :  Delete the entries from containeroverlay, overlaysetup and Refresh the container to make the container active

# "delete from containeroverlay where OverlayUID=25" 2>&1

# "delete from overlaysetup where UID=25" 2>&1

#dbus-send --type=signal --system --dest=com.itron.museplatform.ContainerManager /com/itron/museplatform/ContainerManager com.itron.museplatform.ContainerManager.Refresh

===================================================================================================


===================================================================================================


"""
import pytest
import time
from tests.test_meters.utils import HAN_AGENT,install_agent_and_activate,stop_container,refresh_container
from tests.test_meters.rohan_utils import Dataserver_refresh,absolute_command

# AUTOGENERATED Test Case 1993245

# @pytest.mark.skip(reason="TODO: unimplemented test case")
# @pytest.mark.xfail(reason="test is broke")
@pytest.mark.regress_nightly
# @pytest.mark.regress_smoke
@pytest.mark.suite_id("1993280")
@pytest.mark.test_case("1993245")
@pytest.mark.parametrize("agent_info", [HAN_AGENT])
def test_case(preinstalled_meter, logger,agent_info):
     logger.trace("Executing Test Case 1993245 - Verify that an event is logged when overlay mounting fails ")

     last_TimeStampInMs = preinstalled_meter.sql_query( "select max(TimeStampInMs) from log_eventrecords")[0]


     logger.trace('Step 1')
     try:
          install_agent_and_activate(preinstalled_meter, logger, agent_info)

          overlaysetup_before_insert=len(preinstalled_meter.sql_query('select * from OVERLAYSETUP'))
          preinstalled_meter.sql_query("insert into OVERLAYSETUP (GroupId, UID, OverlayVersion, OverlayPath, IsDeletable, Source) values (1, 25,1, \"/usr/share/itron/container-overlays/MockAgent.tar.bz2\", 0, 0)")
          stop = time.time() + (90)
          while time.time()<=stop:
            overlaysetup_after_insert=len(preinstalled_meter.sql_query('select * from OVERLAYSETUP'))
            if(overlaysetup_after_insert > overlaysetup_before_insert):
               break
            time.sleep(5)
          assert overlaysetup_after_insert > overlaysetup_before_insert,'timeout for condition check'
          logger.trace('Step 2')
          CONTAINEROVERLAY_before_insert=len(preinstalled_meter.sql_query('select * from CONTAINEROVERLAY'))
          preinstalled_meter.sql_query('insert into CONTAINEROVERLAY (GroupId, ContainerUID, OverlayUID, LoadIndex) values (1, 50593792,25, 15)')
          stop = time.time() + (90)
          while time.time()<=stop:
            CONTAINEROVERLAY_after_insert=len(preinstalled_meter.sql_query('select * from CONTAINEROVERLAY'))
            if(CONTAINEROVERLAY_after_insert > CONTAINEROVERLAY_before_insert):
               break
            time.sleep(5)
          assert CONTAINEROVERLAY_after_insert > CONTAINEROVERLAY_before_insert,'timeout for condition check'
          logger.trace('Step 3')
          stop_container(preinstalled_meter)  
          preinstalled_meter.command('dbus-send --type=signal --system --dest=com.itron.museplatform.ContainerManager /com/itron/museplatform/ContainerManager com.itron.museplatform.ContainerManager.Refresh')
          stop = time.time() + 5*60
          while time.time()<=stop:
               stdout= preinstalled_meter.command( 'ps | grep -i lxc')
               output=[x for x in stdout if("lxc-start -d -P /tmp/container -n  " in x)]
               if(len(output)!=0):
                    break
               time.sleep(10)

          LOG_EVENTRECORDS=preinstalled_meter.sql_query(f"select DataFieldItron from LOG_EVENTRECORDS where TimeStampInMs > {last_TimeStampInMs} ")
          log = " ".join(LOG_EVENTRECORDS)
          assert  "Overlay does not exist: /usr/share/itron/container-overlays/MockAgent.tar.bz2" in log

          logger.trace("step 4")
          
     finally:
          preinstalled_meter.sql_query("delete from overlaysetup where UID=25")
          preinstalled_meter.sql_query("delete from containeroverlay where OverlayUID=25")
          stop_container(preinstalled_meter)
          refresh_container(preinstalled_meter,logger,20*60) 




