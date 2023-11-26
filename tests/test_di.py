import pytest
import subprocess
import xml.etree.ElementTree as ET
import os

@pytest.mark.regress_nightly
def test_2k_version(logger, di_package, di_version, di_package_2k, di_version_2k):
    logger.info("DI package   : %s, version: %s",di_package,di_version)
    logger.info("DI 2K package: %s, version: %s",di_package_2k,di_version_2k)
    assert(di_version != di_version_2k)

@pytest.mark.regress_nightly
def test_di_package(logger, decrypted_di_package):

    output = subprocess.check_output(f"ls -lR {decrypted_di_package}".split())
    logger.trace("files: %s", output.decode('utf-8'))
    with open(os.path.join(decrypted_di_package, "ReleaseManifest.xml"),'r') as fh:
        mfst = fh.read()

    logger.trace("ReleaseManifest.xml contains: %s", mfst)
    
    tree = ET.parse(os.path.join(decrypted_di_package, "ReleaseManifest.xml"))

    root = tree.getroot()
    fw = root.find('.//*firmwareConstraints')
    minmax = list(fw.iter())
    logger.trace("minmax: %s", minmax)
    min = minmax[1].attrib['version']
    max = minmax[2].attrib['version']

    logger.trace("min fw version: %s, max fw version: %s", min, max)
