# GPU_MANAGER_PACKAGE
GPU_MANAGER_PACKAGE: Developed a Python package to automate GPU usage, including allocation and release of memory specifically for Machine Learning tasks. Implemented for use on a DGX A100 server with 4 GPUs, each with 40GB memory, within a JupyterHub server environment. It can be installed on your ubuntu systems using pip.

GPU_MANAGER PACKAGE

Steps to setup the package and install:
Download the gpu_manager folder and setup.py file.
Run the below command in the terminal with the gpu_manager folder and setup.py file path.
 python setup.py sdist
After running the above command gpu_manager.egg-info and dist folders are created automatically in the same path.
In the dist folder, the gpu_manager-1.0.0.tar.gz file will be there, using this file we can install the package with the following terminal command. 
Sudo pip3 install gpu_manager-1.0.0.tar.gz

