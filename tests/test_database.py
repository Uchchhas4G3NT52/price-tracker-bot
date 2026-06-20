"""
test_database.py - Tests for database.py using a temporary SQLite file
(pytest's tmp_path fixture) so tests never touch the real price_history.db.
"""
from tracker.database import get_history, get_latest_check, init_db, save_check


def test_init_db_creates_table(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    assert db_path.exists()


def test_save_and_get_latest_check(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    save_check("Test Book", 19.99, True, 5, db_path=db_path)
    latest = get_latest_check("Test Book", db_path=db_path)

    assert latest is not None
    assert latest.price == 19.99
    assert bool(latest.in_stock) is True
    assert latest.stock_count == 5


def test_get_latest_check_returns_none_when_no_data(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    assert get_latest_check("Nonexistent Book", db_path=db_path) is None


def test_get_latest_check_returns_most_recent_not_first(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    save_check("Test Book", 19.99, True, 5, db_path=db_path)
    save_check("Test Book", 17.99, True, 3, db_path=db_path)

    latest = get_latest_check("Test Book", db_path=db_path)
    assert latest.price == 17.99


def test_get_history_returns_all_checks_oldest_first(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    save_check("Test Book", 19.99, True, 5, db_path=db_path)
    save_check("Test Book", 17.99, True, 3, db_path=db_path)

    history = get_history("Test Book", db_path=db_path)
    assert len(history) == 2
    assert history[0].price == 19.99
    assert history[1].price == 17.99


def test_history_is_scoped_to_title(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    save_check("Book A", 10.00, True, 1, db_path=db_path)
    save_check("Book B", 20.00, True, 1, db_path=db_path)

    history_a = get_history("Book A", db_path=db_path)
    assert len(history_a) == 1
    assert history_a[0].title == "Book A"
