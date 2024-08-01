check:
	echo "foo"
harvest:
	scripts/harvest.sh
make format:
	black python/*.py python/lib/*.py
make dev:
	pip install -r requirements-dev.txt