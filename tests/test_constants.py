from vsa.shared.constants import MasterLeadsColumns

def test_all_columns():
    columns = MasterLeadsColumns.all_columns()
    assert isinstance(columns, list)
    assert len(columns) > 0

def test_no_duplicates():
    columns = MasterLeadsColumns.all_columns()
    assert len(columns) == len(set(columns))
