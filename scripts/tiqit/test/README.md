# Tiqit script tests

## Running these tests

Ensure the `scripts` directory is on the PYTHONPATH and run the tests with pytest.
E.g. from the root of the tiqit git repo:

```bash
$ PYTHONPATH=$(pwd)/scripts pytest
```

## Coverage reports

Use the `pytest-cov` plugin to produce a code coverage report for the tests:

```bash
$ PYTHONPATH=$(pwd)/scripts pytest --cov --cov-report=html:coverage_re
```

The generated HTML coverage report can then be viewed in a browser.

Tip: use `python3 -m http.server` to host a local HTTP server from which to view the coverage report easily.
