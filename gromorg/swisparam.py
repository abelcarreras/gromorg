import requests as req
from lxml import html
import time
import io
from zipfile import ZipFile
import openbabel


class SwissParams:

    def __init__(self, structure):
        self._structure = structure
        self._filename = 'test'

        self._zip_data = None
        self._url_data = None

    def get_mol2(self):
        obConversion = openbabel.OBConversion()
        obConversion.SetInAndOutFormats("xyz", "mol2")

        mol = openbabel.OBMol()
        obConversion.ReadString(mol, self._structure.get_xyz())

        return obConversion.WriteString(mol)

    def get_zip_file(self, wait_time=10):

        if self._zip_data is not None:
            return self._zip_data

        url_data = self.submit_file()

        url_zip = url_data.replace('index.html', self._filename + '.zip')

        r_data = req.get(url_data, allow_redirects=True)

        print('connecting to SwissParam...')
        while 'Your job is currently being performed' in r_data.text:
            r_data = req.get(url_data, allow_redirects=True)
            print('waiting...')
            time.sleep(wait_time)

        r = req.get(url_zip, allow_redirects=True)

        if r.status_code == 404:
            print(r_data.text)
            print('Failed!')
            return None

        print('done!')
        self._zip_data = r.content

        r.close()
        r_data.close()

        return self._zip_data

    def store_param_zip(self, filename='params.zip'):
        with open(filename, 'wb') as f:
            f.write(self.get_zip_file())

    def submit_file(self):

        if self._url_data is not None:
            return self._url_data

        url = 'https://www.swissparam.ch/submit.php'

        files = {'MAX_FILE_SIZE': '30000000',
                 'mol2Files': (self._filename + '.mol2',
                               io.StringIO(self.get_mol2()),
                               'multipart/form-data')}

        r = req.post(url, files=files)

        tree = html.fromstring(r.content)

        self._url_data = tree.xpath('//a[@class="sib_link"]/text()')[0]

        r.close()

        return self._url_data

    def get_data_contents(self):
        input_zip = ZipFile(io.BytesIO(self.get_zip_file()))
        return {name: input_zip.read(name) for name in input_zip.namelist()}

    def get_itp_data(self):
        return self.get_data_contents()[self._filename + '.itp'].decode()

    def get_pdb_data(self):
        return self.get_data_contents()[self._filename + '.pdb'].decode()

