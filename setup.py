from setuptools import setup, find_packages


def get_version_number():
    main_ns = {}
    for line in open('gromorg/__init__.py', 'r').readlines():
        if not(line.find('__version__')):
            exec(line, main_ns)
            return main_ns['__version__']


# Make python package
setup(name='gromorg',
      version=get_version_number(),
      description='Simple Gromacs python wrapper',
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      install_requires=['numpy', 'openbabel', 'gmxapi', 'mdtraj', 'lxml'],
      author='Abel Carreras',
      author_email='abelcarreras83@gmail.com',
      packages=find_packages(),
      url='https://github.com/abelcarreras/gromorg',
      classifiers=[
          "Programming Language :: Python",
          "License :: OSI Approved :: MIT License"]
      )
