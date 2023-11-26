"""

Sample implementation of peer to peer test using the guide here:
  https://itron.sharepoint.com/:o:/s/appServices/EmyCxLJEhk1GlymVrtdKV8oBYV0pCw_iVgVaW43wb0oSJQ?e=lJLdrW


1) install appserve and p2p agent on meters
2) send PLC packet on meter 1
3) receive PLC packet on meter 2
4) validate that the packet was received

"""
import pytest
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Barrier
from queue import Queue, Empty
from tests.test_meters.utils import install_agent_for_p2p
import time
from threading import current_thread, get_ident
from tests.test_meters.utils import ParallelMeterWithDebug
from itron.meter.expect import Timeout

@pytest.mark.parallel(p2p_meters=2) # test needs two meters (currently only 2 supported)
@pytest.mark.regress_weekly
@pytest.mark.slow1020
@pytest.mark.disable_changed
def test_expect(preinstalled_multi_meter, logger):
    m = preinstalled_multi_meter[0]
    with m.expect_shell() as exp:
        exp.send_line('ps | grep DataServer')
        exp.expect('DataServer_Daemon', timeout=4)
        exp.expect_prompt()
        exp.command("ENV_VAR=123")
        exp.send_line("echo $ENV_VAR")
        exp.expect("123")
        exp.expect_prompt()
        exp.send_ctrl_c()

@pytest.mark.regress_weekly
@pytest.mark.disable_changed
@pytest.mark.slow1020
@pytest.mark.parallel(p2p_meters=2) # test needs two meters (currently only 2 supported)
def test_multi_0(multi_meter, logger):
    logger.trace("Multimeters: %s", multi_meter)

@pytest.mark.regress_weekly
@pytest.mark.disable_changed
@pytest.mark.slow1020
@pytest.mark.parallel(p2p_meters=2) # test needs two meters (currently only 2 supported)
def test_multi_1(preinstalled_multi_meter, logger):
    logger.trace("Multimeters: %s", preinstalled_multi_meter)

#@pytest.mark.skip("meter pool does not have stable set of peers")
#@pytest.mark.regress_weekly
@pytest.mark.disable_changed
@pytest.mark.slow1020
@pytest.mark.parallel(p2p_meters=2) # test needs two meters (currently only 2 supported)
def test_multi_1(preinstalled_multi_meter,logger):

    # for this test case, we need one barrior to syncronize the send/receive
    BARRIERS_NEEDED=1

    num_meters = len(preinstalled_multi_meter) # maximum we can use
    assert num_meters > 1
    num_meters = 2 # we only need 2

    # we will use master (sending meter) and slave (reciever)
    master_meter = preinstalled_multi_meter[0]
    slave_meter = preinstalled_multi_meter[1]

    # setup 2 barriers to syncronize test cases at specific points
    barriers = [Barrier(num_meters) for i in range(BARRIERS_NEEDED)]

    queue_to_master = Queue()
    queue_to_slave = Queue()

    results = []

    logger.trace("Starting send loop")
    # start the master and slave meter tests
    with ThreadPoolExecutor(num_meters) as executor:
        slave = executor.submit(slave_meter_thread, slave_meter, logger, barriers, queue_to_master, queue_to_slave)

        logger.trace("Master Step 1")
        install_agent_for_p2p(master_meter, logger)

        # wait for other meter(s) to finish installing the agent
        barriers[0].wait()

        # at this point, both meters should be ready to communicate

        logger.trace("Master Step 2")
        logger.info("Send message to other meter")
        message_to_send = "Hi from master_meter id:" + str(get_ident())


        # send message to other thread
        queue_to_slave.put(message_to_send)

        logger.trace("Sending '%s' to other meter", message_to_send)
        result = master_meter.command(f"/usr/bin/di-tool --send-plc --data '{message_to_send}'")
        logger.info("Send result: %s", result)

        # slave should tell us if it didn't find the message
        while slave.running():
            try:
                while queue_to_master.get(block=True, timeout=30) == "Send again" and slave.running():
                    logger.trace("Sending '%s' to other meter", message_to_send)
                    result = master_meter.command(f"/usr/bin/di-tool --send-plc --data '{message_to_send}'")
                break
            except Empty:
                logger.info("Empty queue exception")
                pass

        logger.trace("Master complete, waiting for thread")
        slave_result = slave.result()
        logger.trace("Thread returned %s", slave_result)

    assert slave_result == True, "slave says it didn't recieve the test packet"
    logger.trace("Test complete: passed")


def slave_meter_thread(meter, logger, barriers, queue_to_master, queue_to_slave):
    """
    meter = meter connection
    logger = logger for the meter
    meter_group = the MeterThreadGroup that owns this thread
    """
    current_thread().setName(f"Slave Meter-{meter}")
    logger.trace("Slave Thread Started")

    logger.trace("Slave Thread Step 1")
    install_agent_for_p2p(meter, logger)

    send_address = None
    ret = False # default to failure
    timeout = time.time() + (1*60) # should not take more than 5 minutes

    logger.trace("Slave Thread Step 2")
    logger.info("receive message from other meter")
    with meter.expect_shell() as exp:
        exp.command("export GCOV_PREFIX=/mnt/common/DI-AppServices-gcov")
        exp.send_line("/usr/bin/di-tool --receive-plc")
        exp.expect("Waiting to receive", timeout=60)
        logger.info("Got waiting to recieve message")

        # wait for other meter(s) to finish installing the agent and ready to send
        barriers[0].wait()
        logger.trace("Slave Thread Ready for recieve")
        looking_for = queue_to_slave.get()

        # now that the meter is availble, and we have what we are looking for,
        # monitor output with expect, and if we don't see the message, ask the
        # master to send again
        while time.time() < timeout:
            try:
                logger.trace("Waiting for message: %s from master meter", looking_for)
                match = exp.expect(looking_for, timeout=20)
                queue_to_master.put("Found!")
                logger.info("Found! %s", match)
                ret = True
                break
            except Timeout as e:
                logger.warning("timeout,  ask to re-send")
                queue_to_master.put("Send again")
            except Exception as e:
                logger.exception("Unknown exception")
                break

        # stop the recieve and wait for prompt, then exit command processor
        exp.send_ctrl_c()
        exp.expect_prompt()

    if not ret:
        logger.error("Failed to receive")

    queue_to_master.put("Done")
    logger.trace("Slave Thread Complete (%s)", ret)

    return ret
