import sys, pickle, time, fcntl
import warnings


# Singleton class to handle cache
class SimpleCache:
    __instance__ = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance__ is not None:
            return cls.__instance__

        # Py2 compatibility
        if sys.version_info[0] < 3:
            BlockingIOError = IOError

        cls._calculation_data_filename = '.parameters.pkl'
        cls._pickle_protocol = pickle.HIGHEST_PROTOCOL

        cls.__instance__ = super(SimpleCache, cls, ).__new__(cls)
        return cls.__instance__

    def __init__(self, filename=None):
        """
        Constructor
        """

        if filename is not None:
            self._calculation_data_filename = filename

        # python 2 compatibility
        if not '_calculation_data_filename' in dir(self):
            self._calculation_data_filename = '.parameters.pkl'

        try:
            with open(self._calculation_data_filename, 'rb') as input:
                self._calculation_data = pickle.load(input)
                # print('Loaded data from {}'.format(self._calculation_data_filename))
        except (IOError, EOFError, BlockingIOError):
            # print('Creating new calculation data file {}'.format(self._calculation_data_filename))
            self._calculation_data = {}
        except (UnicodeDecodeError):
            warnings.warn('Warning: Calculation data file is corrupted and will be overwritten')
            self._calculation_data = {}

    def redefine_calculation_data_filename(self, filename):

        self._calculation_data_filename = filename
        # print('Set data file to {}'.format(self._calculation_data_filename))

        try:
            with open(self._calculation_data_filename, 'rb') as input:
                self._calculation_data = pickle.load(input)
                # print('Loaded data from {}'.format(self._calculation_data_filename))
        except (IOError, EOFError):
            # print('Creating new calculation data file {}'.format(self._calculation_data_filename))
            self._calculation_data = {}

    def store_calculation_data(self, structure, keyword, data, timeout=60):

        for iter in range(100):
            try:
                with open(self._calculation_data_filename, 'rb') as input:
                    self._calculation_data = pickle.load(input)
            except FileNotFoundError:
                self._calculation_data = {}
                continue
            except (UnicodeDecodeError):
                warnings.warn('Warning: {} file is corrupted and will be overwritten'.format(self._calculation_data_filename))
                self._calculation_data = {}
            except (BlockingIOError, IOError, EOFError):
                # print('read_try: {}'.format(iter))
                time.sleep(timeout/100)
                continue
            break

        self._calculation_data[(hash(structure), keyword)] = data

        for iter in range(100):
            try:
                with open(self._calculation_data_filename, 'wb') as f:
                    fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    pickle.dump(self._calculation_data, f, self._pickle_protocol)
            except BlockingIOError:
                # print('read_try: {}'.format(iter))
                time.sleep(timeout/100)
                continue
            break

    def retrieve_calculation_data(self, input_qchem, keyword):
        return self._calculation_data[(hash(input_qchem), keyword)] if (hash(input_qchem), keyword) in self._calculation_data else None

    @property
    def calculation_data(self):
        return self._calculation_data

    @calculation_data.setter
    def calculation_data(self, calculation_data):
        self._calculation_data = calculation_data
