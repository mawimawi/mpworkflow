nosetests test.py --with-coverage -x -s && coverage html --omit='*site-packages*','*distutils*','hmac','multiprocessing*' && open htmlcov/index.html
