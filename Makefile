# Let's put often used management commands in this Makefile so we can use it as
# executable documentation
TEST_APPS=smeuhoverride microblogging threadedcomments friends messages \
	  avatar photos timeline blog profiles account artist
TEST_COMMAND=manage.py test $(TEST_APPS)
OMIT_COVERAGE=*_settings.py,fabfile.py,*/migrations/*.py


install:
	pip install -r requirements.txt
	python manage.py migrate

develop:
	pip install -r test-requirements.txt


test:
	python $(TEST_COMMAND)

coverage:
	coverage run --source=. --omit="$(OMIT_COVERAGE)" $(TEST_COMMAND)
	coverage report

fasttest:
	DJANGO_TEST_FAST=1 python manage.py test --failfast $(TEST_APPS)


.PHONY: deploy
deploy:
	fab -R smeuh deploy

serve:
	python manage.py runserver

.PHONY: backup
backup:
	fab backup
