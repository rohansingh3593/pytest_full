import pytest
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from threading import Event
from tests.test_meters.test_preinstall.conftest import install_appserve, verify_appserve
from tests.test_meters.utils import ParallelMeterWithDebug
from threading import current_thread

def check_meter_install(meter, logger, appserve_artifacts, meter_exit_handler):
    current_thread().setName(f"check_meter_install-{meter}")

    meter_context = ParallelMeterWithDebug(meter, logger)
    meter_context.connect()
    install_appserve(meter_context, logger, appserve_artifacts, meter_exit_handler)
    verify_appserve(meter_context, logger)

    return meter_context

@pytest.fixture(scope='function')
def preinstalled_multi_meter(multi_meter, logger, appserve_artifacts,  multi_meter_exit_handler):
    """! sets up multiple pre-installed meters for peer-to-peer communication tests

    This fixture will install the correct version if AppServices, then it will register with the meter_exit_handler to
    perform data harvesting after all tests have been run on the meter.  This includes extracting meter log files,
    harvesting gcov data and other important data.

    This will fixture will be called for each thread/meter pair
    """
    # spin up threads for each meter and setup installer
    results = []

    with ThreadPoolExecutor(len(multi_meter)) as executor:
        futures = {executor.submit(check_meter_install, multi_meter[i], logger, appserve_artifacts, multi_meter_exit_handler[i]) for i in range(len(multi_meter))}

        for fut in as_completed(futures):
            logger.info(f"The preinstall_mulit_meter outcome is {fut.result()}")
            results.append(fut.result())

    yield results
    logger.info("preinstalled_multi_meter generator done")
    for r in results:
        r.disconnect()
