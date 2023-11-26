#!/usr/bin/env python3
# content of conftest.py

import pytest
import os
import logging
import re
import tempfile
import itron.meter.FwMan as FwMan
import subprocess
from tests.utils import LockFile

LOGGER = logging.getLogger(__name__)
repack_lock = LockFile('repack.lock', LOGGER)
repack_list = {}
templist = {}

legacy_upgrade = {
'10.2.536.1':'pytest/tests/test_install/diff-packages/signed-Test_FWDL_KETUMAd_SecureBoot_FW10.2.536.1-10.5.611.1.AsicTestSecure_Gen5RivaAsic.sp_ASDIFF_Revert_Workarounds_Dev.tar.gz_2022_06_09T08_11_30_0400_ps.zip',
'10.3.955.1':'pytest/tests/test_install/diff-packages/signed-Test_FWDL_KETUMAd_SecureBoot_FW10.3.955.1-10.5.611.1.AsicTestSecure_Gen5RivaAsic.sp_ASDIFF_Revert_Workarounds_Dev.tar.gz_2022_06_09T07_59_21_04_00_ps.zip',
'10.4.559.1':'pytest/tests/test_install/diff-packages/signed-Test_FWDL_KETUMAd_SecureBoot_FW10.4.559.1-10.5.611.1.AsicTestSecure_Gen5RivaAsic.sp_ASDIFF_Revert_Workarounds_Dev.tar.gz_2022_06_09T07_33_22_0400_ps.zip',
'10.5.542.1':'pytest/tests/test_install/diff-packages/signed-Test_FWDL_ETMAd_SecureBoot_FW10.5.542.1-10.5.611.1.AsicTestSecure_Gen5RivaAsic.sp_ASDIFF_Revert_Workarounds_Dev.tar.gz_2022_06_09T08_20_17_04_00_ps.zip',
}


@pytest.fixture(scope='session')
def current_fw(gittop, fw_ver):
    """ returns the full path to the coldstart image for the firmware """
    coldpath,coldfile,_,_ = FwMan.get_build(version=fw_ver)
    return os.path.join(coldpath, coldfile)

@pytest.fixture(scope='session')
def current_fw_ver(current_fw):
    """ returns the current firmware version """
    prev=re.search("FW(10[0123456789.]+)",current_fw)[1]
    return prev[:-1]

@pytest.fixture(scope='session')
def prev_fw_ver(diff_fw):
    """ return the version number of the UpgradeFromPrevious firmware """
    return re.search("FW(10[0123456789.]+)",diff_fw)[1][:-1]

@pytest.fixture(scope='session')
def diff_fw(current_fw_ver):
    """ return coldstart package for a diff upgrad (from package, to current version) """
    coldpath,coldfile,dp,df = FwMan.get_build(version=current_fw_ver,diff_upgrade=True)
    return os.path.join(coldpath, coldfile)

@pytest.fixture(scope='function')
def repacked_diff(gittop, request):
    """
    This fixture creates repackaged diff files
    """
    #dir = bt.repack_diff(diff_package, di_package)
    meter = request.node.funcargs['meter']
    diff_file = request.param
    if os.path.exists(diff_file):
        diff_pack = diff_file
    else:
        info = FwMan.get_build(version=diff_file, diff_upgrade=True)
        diff_pack = os.path.join(info[2], info[3])

    tmp = None
    with repack_lock:
        if diff_pack not in repack_list:
            tmp = tempfile.TemporaryDirectory()
            #TODO: repackage di_package into the diff_package.  For now this is done externally
            LOGGER.info("Generating repacked_diff on meter %s Temp dir: %s", meter, tmp.name)
            env = os.environ.copy()
            env['TARGET'] = meter
            repack = subprocess.check_output(["repack", "-o", tmp.name, diff_pack], cwd=gittop, env=env)
            lines = repack.decode('utf-8').splitlines()
            result = lines[-1]
            repack_list[diff_pack] = result
            templist[diff_pack] = [tmp]
            LOGGER.info("Repacked output: %s", result)
        else:
            LOGGER.info("Already repacked: %s", diff_pack)
            templist[diff_pack].append(None)
    yield repack_list[diff_pack]
    LOGGER.info("Cleanup repacked: %s", diff_pack)
    # remove reference to tmp...  when the list is empty the item will be cleaned up
    tmp = templist[diff_pack].pop()
    if tmp:
        tmp.cleanup()
