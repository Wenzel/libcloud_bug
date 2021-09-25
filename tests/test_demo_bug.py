"""demo the bug"""

def test_demo_ObjectHashMismatchError_with_pyfakefs(clean_minio_db, fs):
    # create test file
    test_file = "/file1.txt"
    test_file_data = b"hello"
    with open(test_file, "wb") as f:
        f.write(test_file_data)
    # create container
    driver = clean_minio_db
    container = driver.create_container('test')
    # test
    driver.upload_object(str(test_file), container, 'test_file')
    obj = driver.get_object(container, "test_file")
    # assert
    test_file_download = "/file2.txt"
    driver.download_object(obj, str(test_file_download))
    with open(test_file_download, "rb") as f:
        assert f.read() == test_file_data


def test_demo_InvalidCreds(clean_minio_db, tmp_path):
    # setup
    expected_data = b"data"
    with open(tmp_path / "file1.txt", "wb") as f:
        f.write(expected_data)
    adapter = clean_minio_db
    c = adapter.create_container("objects")
    # test
    ret = adapter.upload_object(tmp_path / "file1.txt", c, "file1")
    obj = adapter.get_object(c, "file1")
    # assert
    assert ret
    ret = adapter.download_object(obj, tmp_path / "file2.txt")
    assert ret
    with open(tmp_path / "file2.txt", "rb") as f:
        data = f.read()
        assert expected_data == data
