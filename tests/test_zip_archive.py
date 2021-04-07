import pytest
from gyomu.archive.zip import ZipArchive
from gyomu.file_model import FileTransportInfo
import os
import shutil
import io
from gyomu.status_code import StatusCode
from gyomu.configurator import Configurator

@pytest.fixture(autouse=True, scope='class')
def setup_test_files(tmpdir_factory):
    compress_dir = tmpdir_factory.getbasetemp()
    source_directgory = os.path.dirname(__file__)
    source_directory = os.path.join(source_directgory, 'resources')
    destination_directory = os.path.join(compress_dir, 'compress')
    shutil.copytree(source_directory, os.path.join(compress_dir, 'compress'))
    yield destination_directory
    shutil.rmtree(destination_directory)


def compare_stream(src: io.BufferedIOBase, dest: io.BufferedIOBase) -> bool:
    with src:
        with dest:
            src_data = src.read()
            dest_data = dest.read()
            return src_data == dest_data


class TestZipArchive:
    def test_create(self, status_handler_setup, setup_test_files):
        config: Configurator = status_handler_setup
        extract_dir = os.path.join(setup_test_files, 'extracted')
        source_dir = os.path.join(setup_test_files, 'source')
        zip_filename = os.path.join(setup_test_files, 'test_zip_create.zip')
        transfer_info = FileTransportInfo(base_path=source_dir)
        transfer_info_list = [transfer_info]

        ZipArchive.create(zip_filename, transfer_info_list, config=config, encoding='cp437')

        with ZipArchive(zip_filename) as archive:
            with open(os.path.join(source_dir, 'README.md'), 'rb') as source_file:
                assert compare_stream(archive.get_entry_from_name('README.md'), source_file)

    def test_unzip(self, status_handler_setup, setup_test_files):
        config: Configurator = status_handler_setup
        extract_dir = os.path.join(setup_test_files, 'extracted')
        compress_dir = os.path.join(setup_test_files, 'compress')
        zip_filename = os.path.join(compress_dir, 'temp.zip')
        source_dir = os.path.join(setup_test_files, 'source')
        transfer_info = FileTransportInfo(source_filename= zip_filename, destination_foldername=extract_dir)
        ZipArchive.unzip(transfer_info, config, encoding='cp437')
        with open(os.path.join(extract_dir,'folder1\\folder 2\\フォルダ噂～３\\parameter_access.py')) as dest_file:
            with open(os.path.join(source_dir,'folder1\\folder 2\\フォルダ噂～３\\parameter_access.py')) as source_file:
                assert compare_stream(source_file,dest_file)

    def test_get_entry_from_transfer_information(self):
        assert False

    def test_get_entry_file_list_from_directory(self):
        assert False

    def test_file_exists(self, setup_test_files):
        zip_filename = os.path.join(setup_test_files, 'compress\\temp.zip')
        with ZipArchive(zip_filename, encoding='cp437') as archive:
            assert archive.file_exists('folder1/folder 2/フォルダ噂～３/parameter_access.py')

    def test_directory_exists(self, setup_test_files):
        zip_filename = os.path.join(setup_test_files, 'compress\\temp.zip')
        with ZipArchive(zip_filename, encoding='cp437') as archive:
            assert archive.directory_exists('folder1/folder 2/フォルダ噂～３/')

    def test_password_zip(self, setup_test_files):
        zip_filename = os.path.join(setup_test_files, 'compress\\README_password.zip')
        src_filename = os.path.join(setup_test_files, 'README.md')

        with ZipArchive(zip_filename, encoding='cp437', password="password", is_aes_encrypted=False) as archive:
            with open(src_filename, 'rb') as source_file:
                assert compare_stream(archive.get_entry_from_name('README.md'), source_file)

    def test_aes_password_zip(self, setup_test_files):
        zip_filename = os.path.join(setup_test_files, 'compress\\README_aes_password.zip')
        src_filename = os.path.join(setup_test_files, 'README.md')

        with ZipArchive(zip_filename, encoding='cp437', password="password", is_aes_encrypted=True) as archive:
            with open(src_filename, 'rb') as source_file:
                assert compare_stream(archive.get_entry_from_name('source\\README.md'), source_file)
