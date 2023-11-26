
def read_lid(g5m, lid):
    lines = g5m.command(f'TransactionProcess --event="MUSE_V1;ReadLid;{lid}"')
    data = lines[0].split(':')
    assert len(data) == 4
    assert data[1] == 'SUCCESS'
    assert data[0] == 'RESULT'
    assert data[2] == lid
    val = data[3].split('=')
    data_type = val[0]
    value = val[1]
    if data_type == 'U32':
        value = int(value)

    return value

def write_lid(g5m, lid, value):
    lines = g5m.command(f'ImProvHelper.sh --WriteLid {lid} {value}')

