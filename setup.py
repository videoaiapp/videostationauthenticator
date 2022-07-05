from setuptools import setup, find_packages

setup(
    name='jupyterhub-videostationauthenticator',
    version='0.1',
    description='JupyterHub authenticator that hands out temporary accounts for everyone',
    url='https://github.com/videoaiapp/videostationauthenticator',
    author='VideoStation',
    author_email='tech@videostation.us',
    license='3 Clause BSD',
    packages=find_packages()
)