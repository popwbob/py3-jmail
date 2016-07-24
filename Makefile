default:
	@echo 'No default task'

clean:
	@find . -type d -name __pycache__ | xargs rm -vrf
	@rm -rf htmlcov

compile-all: clean lib-pyc lib-pyo

lib-pyc:
	@python3 -m compileall jmail/ | grep -Ev '^Listing ' || true

lib-pyo:
	@python3 -O -m compileall jmail/ | grep -Ev '^Listing '

django-runserver: lib-pyc
	@JMAIL_DEVMODE=1 python3 manage.py runserver localhost:6080

smtpd-debug-server:
	python3 -m smtpd -n -c DebuggingServer localhost:1025

test:
	@python3 manage.py test

test-coverage:
	@python3 -m coverage run manage.py test
	@python3 -m coverage report
	@python3 -m coverage html

.PHONY: default clean compile-all lib-pyc lib-pyo django-runserver smtpd-debug-server test test-coverage
