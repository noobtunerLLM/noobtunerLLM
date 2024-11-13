echo [$(date)]: "START" 
echo [$(date)]: "creating env with python 3.810version" 
conda create --prefix ./venv python=3.10 -y
echo [$(date)]: "activating the environment" 
source activate ./venv
echo [$(date)]: "installing the dev requirements" 
pip install -r requirements_dev.txt
echo [$(date)]: "END" 