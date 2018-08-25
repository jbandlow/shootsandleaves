test:
	pipenv run py.test
	pipenv run py.test --cov-report term-missing --cov shootsandleaves

docs: **/*.py
	make -C docs/ clean
	make -C docs/ html
