#https://github.com/allofphysicsgraph/proofofconcept/issues/37
#for required dependencies

curl -O https://raw.githubusercontent.com/pypa/virtualenv/master/virtualenv.py
python virtualenv.py myenv --no-pip --no-setuptools --no-wheel
. myenv/bin/activate
wget http://pyyaml.org/download/pyyaml/PyYAML-3.11.tar.gz
tar zxvf PyYAML-3.11.tar.gz 
cd PyYAML-3.11/
python setup.py install
