import pytest
from gyomu.file_model import FileTransportInfo
from collections import namedtuple

TransportResult = namedtuple('TransportResult', ['input_base', 'input_sdir', 'input_sname', 'input_ddir', 'input_dname',
                                                 'source_full_base', 'source_full', 'source_dir', 'source_name',
                                                 'destination_full', 'destination_dir', 'destination_name'])


class TestFileTransportInfo:

    @pytest.mark.parametrize('input_data',
                             [
                                 TransportResult(input_base='base', input_sdir='SDir', input_sname='Sname',
                                                 input_ddir='Ddir', input_dname='Dname',
                                                 source_full_base='base\\SDir\\Sname', source_full='SDir\\Sname',
                                                 source_dir='SDir', source_name='Sname', destination_full='Ddir\\Dname',
                                                 destination_dir='Ddir', destination_name='Dname'),
                                 TransportResult(input_base='base', input_sdir='SDir', input_sname='Sname',
                                                 input_ddir='Ddir', input_dname='',
                                                 source_full_base='base\\SDir\\Sname', source_full='SDir\\Sname',
                                                 source_dir='SDir', source_name='Sname', destination_full='Ddir\\Sname',
                                                 destination_dir='Ddir', destination_name='Sname'),
                                 TransportResult(input_base='base', input_sdir='SDir', input_sname='Sname',
                                                 input_ddir='', input_dname='Dname',
                                                 source_full_base='base\\SDir\\Sname', source_full='SDir\\Sname',
                                                 source_dir='SDir', source_name='Sname', destination_full='SDir\\Dname',
                                                 destination_dir='SDir', destination_name='Dname'),
                                 TransportResult(input_base='base', input_sdir='SDir', input_sname='Sname',
                                                 input_ddir='', input_dname='', source_full_base='base\\SDir\\Sname',
                                                 source_full='SDir\\Sname', source_dir='SDir', source_name='Sname',
                                                 destination_full='SDir\\Sname', destination_dir='SDir',
                                                 destination_name='Sname'),
                                 TransportResult(input_base='base', input_sdir='SDir', input_sname='',
                                                 input_ddir='Ddir', input_dname='', source_full_base='base\\SDir',
                                                 source_full='SDir', source_dir='SDir', source_name='',
                                                 destination_full='Ddir', destination_dir='Ddir', destination_name=''),
                                 TransportResult(input_base='base', input_sdir='SDir', input_sname='', input_ddir='',
                                                 input_dname='', source_full_base='base\\SDir', source_full='SDir',
                                                 source_dir='SDir', source_name='', destination_full='SDir',
                                                 destination_dir='SDir', destination_name=''),
                                 TransportResult(input_base='base', input_sdir='', input_sname='', input_ddir='',
                                                 input_dname='', source_full_base='base', source_full='', source_dir='',
                                                 source_name='', destination_full='', destination_dir='',
                                                 destination_name=''),
                                 TransportResult(input_base='base', input_sdir='', input_sname='', input_ddir='Ddir',
                                                 input_dname='', source_full_base='base', source_full='', source_dir='',
                                                 source_name='', destination_full='Ddir', destination_dir='Ddir',
                                                 destination_name=''),
                                 TransportResult(input_base='base', input_sdir='', input_sname='Sname',
                                                 input_ddir='Ddir', input_dname='Dname', source_full_base='base\\Sname',
                                                 source_full='Sname', source_dir='', source_name='Sname',
                                                 destination_full='Ddir\\Dname', destination_dir='Ddir',
                                                 destination_name='Dname'),
                                 TransportResult(input_base='base', input_sdir='', input_sname='Sname',
                                                 input_ddir='Ddir', input_dname='', source_full_base='base\\Sname',
                                                 source_full='Sname', source_dir='', source_name='Sname',
                                                 destination_full='Ddir\\Sname', destination_dir='Ddir',
                                                 destination_name='Sname'),
                                 TransportResult(input_base='base', input_sdir='', input_sname='Sname', input_ddir='',
                                                 input_dname='Dname', source_full_base='base\\Sname',
                                                 source_full='Sname', source_dir='', source_name='Sname',
                                                 destination_full='Dname', destination_dir='',
                                                 destination_name='Dname'),
                                 TransportResult(input_base='base', input_sdir='', input_sname='Sname', input_ddir='',
                                                 input_dname='', source_full_base='base\\Sname', source_full='Sname',
                                                 source_dir='', source_name='Sname', destination_full='Sname',
                                                 destination_dir='', destination_name='Sname'),
                                 TransportResult(input_base='', input_sdir='SDir', input_sname='Sname',
                                                 input_ddir='Ddir', input_dname='Dname', source_full_base='SDir\\Sname',
                                                 source_full='SDir\\Sname', source_dir='SDir', source_name='Sname',
                                                 destination_full='Ddir\\Dname', destination_dir='Ddir',
                                                 destination_name='Dname'),
                                 TransportResult(input_base='', input_sdir='SDir', input_sname='Sname',
                                                 input_ddir='Ddir', input_dname='', source_full_base='SDir\\Sname',
                                                 source_full='SDir\\Sname', source_dir='SDir', source_name='Sname',
                                                 destination_full='Ddir\\Sname', destination_dir='Ddir',
                                                 destination_name='Sname'),
                                 TransportResult(input_base='', input_sdir='SDir', input_sname='Sname', input_ddir='',
                                                 input_dname='Dname', source_full_base='SDir\\Sname',
                                                 source_full='SDir\\Sname', source_dir='SDir', source_name='Sname',
                                                 destination_full='SDir\\Dname', destination_dir='SDir',
                                                 destination_name='Dname'),
                                 TransportResult(input_base='', input_sdir='SDir', input_sname='Sname', input_ddir='',
                                                 input_dname='', source_full_base='SDir\\Sname',
                                                 source_full='SDir\\Sname', source_dir='SDir', source_name='Sname',
                                                 destination_full='SDir\\Sname', destination_dir='SDir',
                                                 destination_name='Sname'),
                                 TransportResult(input_base='', input_sdir='SDir', input_sname='', input_ddir='Ddir',
                                                 input_dname='', source_full_base='SDir', source_full='SDir',
                                                 source_dir='SDir', source_name='', destination_full='Ddir',
                                                 destination_dir='Ddir', destination_name=''),
                                 TransportResult(input_base='', input_sdir='SDir', input_sname='', input_ddir='',
                                                 input_dname='', source_full_base='SDir', source_full='SDir',
                                                 source_dir='SDir', source_name='', destination_full='SDir',
                                                 destination_dir='SDir', destination_name=''),
                                 TransportResult(input_base='', input_sdir='', input_sname='Sname', input_ddir='Ddir',
                                                 input_dname='Dname', source_full_base='Sname', source_full='Sname',
                                                 source_dir='', source_name='Sname', destination_full='Ddir\\Dname',
                                                 destination_dir='Ddir', destination_name='Dname'),
                                 TransportResult(input_base='', input_sdir='', input_sname='Sname', input_ddir='Ddir',
                                                 input_dname='', source_full_base='Sname', source_full='Sname',
                                                 source_dir='', source_name='Sname', destination_full='Ddir\\Sname',
                                                 destination_dir='Ddir', destination_name='Sname'),
                                 TransportResult(input_base='', input_sdir='', input_sname='Sname', input_ddir='',
                                                 input_dname='Dname', source_full_base='Sname', source_full='Sname',
                                                 source_dir='', source_name='Sname', destination_full='Dname',
                                                 destination_dir='', destination_name='Dname'),
                                 TransportResult(input_base='', input_sdir='', input_sname='Sname', input_ddir='',
                                                 input_dname='', source_full_base='Sname', source_full='Sname',
                                                 source_dir='', source_name='Sname', destination_full='Sname',
                                                 destination_dir='', destination_name='Sname'),

                             ])
    def test_valid_transport_information(self, input_data):
        info: FileTransportInfo = TestFileTransportInfo.create_transport_information(input_data)
        TestFileTransportInfo.compare(input_data, info)

    @pytest.mark.parametrize('input_data',
                             [
                                 TransportResult(input_base='base', input_sdir='SDir', input_sname='',
                                                 input_ddir='Ddir',
                                                 input_dname='Dname', source_full_base='', source_full='',
                                                 source_dir='', source_name='',
                                                 destination_full='', destination_dir='', destination_name=''),
                                 TransportResult(input_base='base', input_sdir='SDir', input_sname='', input_ddir='',
                                                 input_dname='Dname',
                                                 source_full_base='', source_full='', source_dir='', source_name='',
                                                 destination_full='',
                                                 destination_dir='', destination_name=''),
                                 TransportResult(input_base='base', input_sdir='', input_sname='', input_ddir='Ddir',
                                                 input_dname='Dname',
                                                 source_full_base='', source_full='', source_dir='', source_name='',
                                                 destination_full='',
                                                 destination_dir='', destination_name=''),
                                 TransportResult(input_base='base', input_sdir='', input_sname='', input_ddir='',
                                                 input_dname='Dname',
                                                 source_full_base='', source_full='', source_dir='', source_name='',
                                                 destination_full='',
                                                 destination_dir='', destination_name=''),
                                 TransportResult(input_base='', input_sdir='SDir', input_sname='', input_ddir='Ddir',
                                                 input_dname='Dname',
                                                 source_full_base='', source_full='', source_dir='', source_name='',
                                                 destination_full='',
                                                 destination_dir='', destination_name=''),
                                 TransportResult(input_base='', input_sdir='SDir', input_sname='', input_ddir='',
                                                 input_dname='Dname',
                                                 source_full_base='', source_full='', source_dir='', source_name='',
                                                 destination_full='',
                                                 destination_dir='', destination_name=''),
                                 TransportResult(input_base='', input_sdir='', input_sname='', input_ddir='Ddir',
                                                 input_dname='Dname',
                                                 source_full_base='', source_full='', source_dir='', source_name='',
                                                 destination_full='',
                                                 destination_dir='', destination_name=''),
                                 TransportResult(input_base='', input_sdir='', input_sname='', input_ddir='Ddir',
                                                 input_dname='',
                                                 source_full_base='', source_full='', source_dir='', source_name='',
                                                 destination_full='',
                                                 destination_dir='', destination_name=''),
                                 TransportResult(input_base='', input_sdir='', input_sname='', input_ddir='',
                                                 input_dname='Dname',
                                                 source_full_base='', source_full='', source_dir='', source_name='',
                                                 destination_full='',
                                                 destination_dir='', destination_name=''),

                             ])
    def test_invalid_transport_information(self, input_data: TransportResult):
        with pytest.raises(ValueError):
            TestFileTransportInfo.create_transport_information(input_data)

    @staticmethod
    def compare(expected: TransportResult, source: FileTransportInfo):
        assert expected.source_full_base == source.source_fullname_with_basepath
        assert expected.source_full == source.source_fullname
        assert expected.source_dir == source.source_path
        assert expected.source_name == source.source_filename
        assert expected.destination_full == source.destination_fullname
        assert expected.destination_dir == source.destination_path
        assert expected.destination_name == source.destination_filename

    @staticmethod
    def create_transport_information(result: TransportResult) -> FileTransportInfo:
        return FileTransportInfo(base_path=result.input_base,
                                 source_filename=result.input_sname, source_folder_name=result.input_sdir,
                                 destination_filename=result.input_dname, destination_foldername=result.input_ddir)
