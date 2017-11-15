from setuptools import setup, find_packages

setup(name='fess',
      version='0.0.1',
      description='Fast Easy SDR Sensors',
      url='',
      author='AJ Keller',
      author_email='pushtheworldllc@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=['numpy', 'pyzmq'])
