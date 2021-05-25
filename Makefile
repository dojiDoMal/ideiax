PROCS=4

test:
	py.test -n $(PROCS) --reuse-db ${ARGS}

test_newdb:
	py.test -n $(PROCS) --create-db ${ARGS}

test_snapshot:
	py.test -n $(PROCS) --reuse-db --snapshot-update ${ARGS}

test_coverage:
	py.test -n $(PROCS) --reuse-db --cov-report term-missing:skip-covered --cov=ideax ${ARGS}

test_watch:
	ptw -c -- -n $(PROCS) --reuse-db ${ARGS}

test_ci:
	py.test --create-db

pip_outdated:
	pip list --outdated --format=columns

lint:
	flake8 ideax

pylint:
	pylint --load-plugins pylint_django ideax

gettext: clean_empty_mo
	python manage.py compilemessages --locale pt_BR

ci: gettext lint test_ci
	@echo "done"

clean_pyc:
	find ideax -type f -name '*.pyc' -delete
	find ideax -type d -name __pycache__ -delete

clean_empty_mo:
	find . -iname '*.mo' -empty -delete

clean: clean_pyc clean_empty_mo
	@echo "done"
