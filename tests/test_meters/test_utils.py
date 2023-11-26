import pytest


@pytest.mark.regress_nightly
def test_2k_version(logger, di_package, di_version, di_package_2k, di_version_2k):
    logger.info("DI package   : %s, version: %s",di_package,di_version)
    logger.info("DI 2K package: %s, version: %s",di_package_2k,di_version_2k)
    assert(di_version != di_version_2k)

