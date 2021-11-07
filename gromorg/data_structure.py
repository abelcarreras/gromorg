

class DataStructure:
    def __init__(self, itp_data):

        if isinstance(itp_data, str):
            self._data = {}
            label = ''
            self._data[label] = []
            for lines in itp_data.split('\n'):
                if len(lines.strip()) > 0: # and ';' not in lines:
                    if '[' in lines and ']' in lines:
                        label = lines.split('[')[1].split(']')[0].strip()
                        self._data[label] = []
                        continue

                    self._data[label].append(lines)
        elif isinstance(itp_data, dict):
            self._data = itp_data

        else:
            raise TypeError('itp_data must be str or dict')

    def get_txt(self):
        itp_txt = ''
        for label in self._data:
            if len(label) > 0:
                itp_txt += '\n[ {} ]\n'.format(label)
            for line in self._data[label]:
                itp_txt += line + '\n'

        return itp_txt

    def append_line(self, label, line):
        self._data[label].append(line)

    def append_data(self, label, data):
        self._data[label] += list(data)

    def get_data(self, label):
        return self._data[label]

    def remove_data(self, label):
        del self._data[label]


if __name__ == "__main__":
    topology = DataStructure(open("../gromorg_50962/test.itp", 'r').read())
    topology.append_line('atomtypes', 'CO  1  fr')
    print(topology.get_txt())
    print(topology.get_data('atomtypes'))
