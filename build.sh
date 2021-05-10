pip install wheel

pip uninstall pandiocli -y

python setup.py bdist_wheel

pip install dist/pandiocli-1.0.6-py3-none-any.whl