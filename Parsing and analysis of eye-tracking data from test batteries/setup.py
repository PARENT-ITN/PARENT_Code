from setuptools import find_packages, setup

setup(
    name='lib_neus_et',
    packages=find_packages(),
    version='1.0.0b',
    description='Analysis and visualisation of eye-tracking data (public version).',
    author='Andrea De Gobbis',
    install_requires=[
        'numpy',
        'pandas',
        'scipy'
    ],
    license='MIT',    
    include_package_data=True,
)