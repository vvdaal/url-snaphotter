# url-snapshotter

`url-snapshotter` is a command-line tool written in Python designed for monitoring and tracking the status and content of a set of URLs over time. It enables you to create "snapshots" that capture the HTTP status codes and content of your URLs at a given point in time. By viewing and comparing these snapshots, you can efficiently identify any changes or anomalies in your web services.

## Table of Contents
- [url-snapshotter](#url-snapshotter)
  - [Table of Contents](#table-of-contents)
  - [Key Use Cases](#key-use-cases)
  - [Core Features](#core-features)
  - [Quick Start with Docker](#quick-start-with-docker)
  - [General Usage](#general-usage)
    - [Command-line Options (flags)](#command-line-options-flags)
  - [Examples](#examples)
    - [Usage with Docker](#usage-with-docker)
  - [Defining a URLs file](#defining-a-urls-file)
  - [Development Setup with Pyenv](#development-setup-with-pyenv)
      - [Using Pyenv to Set Up a Virtual Environment](#using-pyenv-to-set-up-a-virtual-environment)
  - [License](#license)

## Key Use Cases

- **Pre-Maintenance Checks for Web Services**: Running `url-snapshotter` on a list of URLs (such as those defined in your Kubernetes `HTTPProxy` configurations) before performing maintenance or upgrades helps ensure that your services are behaving as expected.
    - Create a snapshot before the upgrade to capture the current state.
    - Create another snapshot after the upgrade, and use `url-snapshotter` to compare them.
    - Instantly identify any discrepancies in HTTP status codes or content, allowing you to quickly detect issues and confirm successful maintenance.

- **Tracking Changes Over Time**: Use `url-snapshotter` to periodically monitor a list of URLs and keep track of any content or status changes. This is helpful for identifying unexpected issues, verifying deployments, or validating expected changes in your web services.

## Core Features

- **Asynchronous URL Fetching**: Efficiently fetches content from multiple URLs concurrently using asynchronous requests, with configurable concurrency for improved performance.
- **Content Cleaning**: Automatically removes known dynamic elements from responses (like CSRF tokens or script nonces) to focus on meaningful content changes.
- **Customizable Patterns for Cleaning Content**: The `patterns.py` file contains regex patterns used to clean up dynamic elements from the content. You can easily add, modify, or remove patterns to fit your needs.
- **Detailed Logging**: Provides clear logging at different levels (INFO, DEBUG, WARNING) for easy monitoring and troubleshooting, with a `--debug` flag for deeper insights during execution.

## Quick Start with Docker

Running `url-snapshotter` is easiest with Docker ([Docker Overview](https://docs.docker.com/get-started/docker-overview/)). No manual setup is needed, just a single command:

```bash
docker run -it --rm -v $(pwd):/app -w /app python:3.12-slim-bookworm sh -c "pip install --no-cache-dir -r requirements.txt && python cli.py"
```

This command:
- Pulls a Python Docker image that matches the current `.python-version` of this repository.
- Mounts your current directory to the container.
- Installs all dependencies from `requirements.txt` and runs `cli.py` which will start the CLI prompts for `url-snapshotter`.

## General Usage

```bash
python cli.py [OPTIONS]
```

### Command-line Options (flags)

- `--create`: Create a new snapshot of URLs from a file.
- `--view`: View the details of a snapshot.
- `--compare`: Compare two snapshots to see changes.
- `--file`: Specify the file containing URLs (one URL per line).
- `--concurrent`: Number of concurrent requests for async fetching (default is 4).
- `--debug`: Enable debug logging.

## Examples

1. **Create a Snapshot**:
    ```bash
    python cli.py --create --file urls.txt
    ```

2. **Compare Two Snapshots**:
    ```bash
    python cli.py --compare
    ```

3. **View a Snapshot**:
    ```bash
    python cli.py --view
    ```

4. **Adjust Concurrent Requests**:
    ```bash
    python cli.py --create --file urls.txt --concurrent 10
    ```

### Usage with Docker

This command will open a bash shell inside a Python container, where you can execute url-snapshotter using any of the available options, such as python cli.py, along with other examples as needed.

```bash
docker run -it --rm -v $(pwd):/app -w /app python:3.12-slim-bookworm sh -c "pip install --no-cache-dir -r requirements.txt && bash"
```

## Defining a URLs file

The `urls.txt` file (or whatever you name it) is a simple text file that contains a list of URLs you want to create a snapshot of. Each URL should be on a separate line without any extra spaces or characters. Here's a brief example:

```
https://example.com
https://another-example.com
https://cool-api.example.com/subpage/awesome-article
```

When creating a snapshot with `url-snapshotter`, this file will be used to fetch the HTTP status and content of each listed URL.

To create a snapshot, run:
```bash
python cli.py --create --file urls.txt
```

Or, if you prefer entering the filename at a prompt:
```bash
python cli.py --create
```

This will prompt you for the file name.

## Development Setup with Pyenv

Before using `url-snapshotter`, ensure all dependencies are installed. My recommended way to handle Python environments is to use `pyenv`.

#### Using Pyenv to Set Up a Virtual Environment

1. **Install `pyenv`**: Follow the installation instructions in the [pyenv GitHub repository](https://github.com/pyenv/pyenv).

2. **Install Python Version**: Once `pyenv` is set up, install the required Python version as specified in the `.python-version` file:
   ```bash
   pyenv install 3.12.6
   ```

3. **Create a Virtual Environment**: Use `pyenv virtualenv` to create a new virtual environment for the project:
   ```bash
   pyenv virtualenv venv-url-snapshotter
   ```

4. **Activate the Virtual Environment**:
   ```bash
   pyenv activate venv-url-snapshotter
   ```

5. **Install Requirements**: With the virtual environment active, install the project dependencies:
   ```bash
   pip install -r requirements.txt
   ```

To deactivate the environment, simply run:
```bash
pyenv deactivate
```

By using `pyenv`, you can easily manage your Python versions and isolate dependencies for different projects. For more detailed instructions, refer to the official [pyenv documentation](https://github.com/pyenv/pyenv).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
