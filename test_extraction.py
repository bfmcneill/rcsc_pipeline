import pathlib
import main

def test_initialize_db():
    db_path = pathlib.Path(__file__).parent / 'test-db.json'
    db_path.unlink(missing_ok=True)

    main.init_db('test-db.json')
    assert db_path.exists()


def test_destroy_db():
    db_path = pathlib.Path(__file__).parent / 'test-db.json'
    db_path.unlink(missing_ok=True)
    main.init_db('test-db.json')
    main.destroy_db(db_path)