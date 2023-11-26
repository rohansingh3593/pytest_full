"""

Sample implementation of peer to peer test using the guide here:
  https://itron.sharepoint.com/:o:/s/appServices/EmyCxLJEhk1GlymVrtdKV8oBYV0pCw_iVgVaW43wb0oSJQ?e=lJLdrW


1) install appserve and p2p agent on meters
2) send PLC packet on meter 1
3) receive PLC packet on meter 2
4) validate that the packet was received

"""
import pytest
from tests.test_meters.utils import install_agent_for_p2p
import time
import uuid
from itron.meter.expect import Timeout
import logging
from tests.test_meters.lids import read_lid


@pytest.mark.disable_changed
@pytest.mark.parallel(p2p_meters=2) # test needs two meters
@pytest.mark.slow1020
@pytest.mark.parametrize("message", ("hi", "there"))
def test_no_threading(preinstalled_multi_meter,logger,message):
    """
    meter = meter connection
    logger = logger for the meter
    meter_group = the MeterThreadGroup that owns this thread
    """
    assert len(preinstalled_multi_meter) > 1, "we need more than one meter"
    master_meter = preinstalled_multi_meter[0]
    slave_meter = preinstalled_multi_meter[1]

    # inefficient, but setup both meters
    install_agent_for_p2p(master_meter, logger)
    install_agent_for_p2p(slave_meter, logger)

    message_to_send = f"{message} id:" + str(uuid.uuid4())[:5]

    found = False
    with slave_meter.expect_shell(output_level=logging.INFO) as exp:
        # for grins, have the GCOV data, if available,  put in the capture directory
        exp.command("export GCOV_PREFIX=/mnt/common/DI-AppServices-gcov")
        # startup reciever
        exp.send_line("ps | grep DataServer")
        exp.send_line("/usr/bin/di-tool --receive-plc")
        exp.expect("Waiting to receive", timeout=60)
        time.sleep(30)

        # now that the meter is availble, and we have what we are looking for,
        # monitor output with expect, and if we don't see the message, ask the
        # master to send again

        max_rate = read_lid(master_meter, "ILID_DATASERVER_P2P_PLC_BCAST_MAX_RATE_S")
        logger.trace("Maximum bcast rate = %s", max_rate)

        count = 0
        logger.trace("Sending '%s' to other meter", message_to_send)
        result = master_meter.command(f"/usr/bin/di-tool --send-plc --data '{message_to_send}-{count}'")
        count += 1
        assert "AgentSending Data" in '\n'.join(result)

        # should not take more than 5 transmit cycles, add some extra time for meter comms
        timeout = time.time() + (5*max_rate) + 120

        while time.time() < timeout:

            try:
                # on the slave meter, wait for the message to be displayed by di-tool
                found = exp.expect(message_to_send, timeout=max_rate)
                logger.trace("Found! %s", found)
                found = True
                break
            except Timeout as e:
                logger.warning("timeout,  ask to re-send")
                logger.trace("Sending '%s' to other meter", message_to_send)
                result = master_meter.command(f"/usr/bin/di-tool --send-plc --data '{message_to_send}-{count}'")
                count += 1
                assert "AgentSending Data" in '\n'.join(result)

        # stop the recieve and wait for prompt, then exit command processor
        exp.send_ctrl_c()
        exp.expect_prompt()
        exp.send_line("exit")
        exp.expect(execption_on_timeout=False)

    assert found, "Error, receiver did not get the message"
