# Healthchecks.io Python Runner

Just a simple wrapper around the Start, Success, and Failure endpoints of the [Healthchecks.io ping api](https://healthchecks.io/docs/http_api/).

# Install
## Directly using pip
```
pip install git+https://github.com/brandonvu99/health-checks-io-python-runner.git
```

# Usage
```python
# Contents of minimal_working_example.py
from health_checks_io_runner import HealthChecksIoRunner, ScriptStatus


def my_work() -> ScriptStatus:
    # Do some work.

    if some_work_was_valid:
        return ScriptStatus(
            is_success=True, message="my cool, custom, optional success message"
        )

    return ScriptStatus(
        is_success=False, message="my cool, custom, optional failure message"
    )


def main():
    HealthChecksIoRunner.run(my_work)


if __name__ == "__main__":
    main()

```
