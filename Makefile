default:
	@echo 'No default task'

clean:
	@find . -type d -name __pycache__ | xargs rm -vrf

compile-all: clean lib-pyc lib-pyo

lib-pyc:
	@python3 -m compileall jmail/ | grep -Ev '^Listing '

lib-pyo:
	@python3 -O -m compileall jmail/ | grep -Ev '^Listing '

django-runserver:
	@python3 manage.py runserver 127.10.10.10:8000

.PHONY: default clean compile-all lib-pyc lib-pyo django-runserver
