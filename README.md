# url-snapshotter

[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md)


`url-snapshotter` is a powerful command-line tool built in Python for monitoring the health and content of web services over time. It works by creating "snapshots" that capture both the HTTP status codes and the content of specified URLs at particular moments. This tool allows you to create, view, and compare these snapshots to efficiently identify changes, regressions, or anomalies in your services.

With `url-snapshotter`, you can ensure the reliability of your web platforms by regularly auditing the status and content of your URLs. Whether you want to track updates, verify expected changes after deployments, or spot unexpected issues, `url-snapshotter` helps you gain a deeper understanding of how your services evolve and ensures they function as expected.

## Table of Contents

- [url-snapshotter](#url-snapshotter)
  - [Table of Contents](#table-of-contents)
  - [Key Use Cases](#key-use-cases)
  - [Core Features](#core-features)
  - [Quick Start with Docker](#quick-start-with-docker)
  - [General Usage](#general-usage)
  - [Command-Line Options](#command-line-options)
  - [Examples](#examples)
  - [Defining a URLs File](#defining-a-urls-file)
  - [Development Setup with Pyenv and Poetry](#development-setup-with-pyenv-and-poetry)
    - [Prerequisites](#prerequisites)
    - [Setting Up Your Development Environment](#setting-up-your-development-environment)
  - [Patterns and Custom Content Cleaning](#patterns-and-custom-content-cleaning)
    - [Adding or Modifying Patterns](#adding-or-modifying-patterns)
  - [FAQ](#faq)
    - [(Kubernetes) How do I quickly generate a urls.txt with all configured httpproxy crd and ingresses?](#kubernetes-how-do-i-quickly-generate-a-urlstxt-with-all-configured-httpproxy-crd-and-ingresses)
    - [(Kubernetes) How do I quickly generate a urls.txt for ingresses?](#kubernetes-how-do-i-quickly-generate-a-urlstxt-for-ingresses)
    - [(Kubernetes) How do I quickly generate a urls.txt for gateways and httproutes?](#kubernetes-how-do-i-quickly-generate-a-urlstxt-for-gateways-and-httproutes)
    - [(Network) My resources are behind a VPN or proxy](#network-my-resources-are-behind-a-vpn-or-proxy)
  - [License](#license)

## Key Use Cases

- **Pre-Maintenance Verification for Web Services**: Ensure smooth upgrades and maintenance by using `url-snapshotter` to validate your services before and after any infrastructure changes. Whether you're managing websites through Kubernetes (like with an Ingress Controller), or handling broader infrastructure updates such as cluster upgrades, `url-snapshotter` helps ensure your services remain consistent and reliable throughout the maintenance process.

  - Create a pre-upgrade snapshot to capture the baseline state of your services, including HTTP status codes and content.
  - After the upgrade, take another snapshot and use `url-snapshotter` to compare both snapshots side-by-side, allowing you to quickly identify any discrepancies.
  - Instantly detect potential issues to confirm successful maintenance, reducing the risk of unnoticed regressions or service outages.

- **Periodic Monitoring and Change Tracking**: Proactively monitor the state of your web services over time by using `url-snapshotter` to regularly capture snapshots of key URLs. This approach is invaluable for identifying unexpected issues, verifying deployments, and validating intended changes in your applications.

  - Schedule periodic snapshots to keep an evolving record of the content and status codes of your services.
  - Track unexpected changes, such as unauthorized modifications or emerging errors, and verify that new deployments function as intended.
  - Validate and document changes over time to ensure alignment with your development and deployment goals, ultimately maintaining service quality.

## Core Features

- **Efficient Asynchronous URL Fetching**: Speed up the process of monitoring large sets of URLs using asynchronous requests to fetch content concurrently. `url-snapshotter` makes use of async I/O to handle multiple URLs at once, resulting in significantly improved performance, especially when dealing with long URL lists.

- **Comprehensive Snapshot Comparison**: Easily compare two snapshots to identify any changes in HTTP status codes or page content. Detect regression, monitor modifications, or spot unexpected issues in your web services. By highlighting differences between snapshots, `url-snapshotter` helps you understand what has changed at a glance, empowering you to take corrective actions swiftly if necessary.

- **Customizable Content Cleaning with Patterns**: Automatically clean up dynamic elements that frequently change, such as CSRF tokens, script nonces, or session identifiers, using custom regex patterns. This ensures that the comparisons are focused only on meaningful content changes. You can add, modify, or remove cleaning patterns to suit the specific needs of your web applications.

- **Interactive Dynamic Snapshot Viewing**: View the details of any previously captured snapshot directly from the command line, including HTTP status codes and content hashes. The dynamic viewing capability helps you quickly verify the current state of URLs or investigate individual snapshots without having to dig through raw data.

- **Adjustable Concurrency Control**: Set the level of concurrency during URL fetching to suit your needs—whether you want rapid fetching for small lists or more controlled fetching to reduce the load on your servers.

- **Intuitive CLI Integration**: Execute all operations from a single command-line interface (`url-snapshotter`). Whether you're creating a new snapshot, comparing snapshots, or viewing snapshot details, the easy-to-use CLI streamlines these tasks. 

## Quick Start with Docker

The easiest way to run `url-snapshotter` is with [Docker](https://docs.docker.com/engine/install/). This avoids the need to set up Python or dependencies on your machine:

```bash
docker run -it --rm -v $(pwd):/app -w /app python:3.12-slim-bookworm sh -c "pip install --no-cache-dir -r requirements.txt && python -m url_snapshotter.cli"
```

This command:

- Uses a Python Docker image
- Mounts the current directory to the Docker container.
- Installs dependencies and starts the `url-snapshotter` CLI prompts.

## General Usage

The tool can be run using Poetry, which is used to manage dependencies and the virtual environment. Once installed, you can run `url-snapshotter` with:

```bash
url-snapshotter [OPTIONS]
```

Alternatively, via Python (requires dependencies installed and Python 3.12+):

```bash
python -m url_snapshotter.cli [OPTIONS]
```

## Command-Line Options

- **`create`**: Create a new snapshot of URLs from a file.
- **`view`**: View the details of an existing snapshot.
- **`compare`**: Compare two snapshots to see any differences.
- **`-f, --file [PATH]`**: Specify the file containing URLs (one URL per line).
- **`-c, --concurrent [NUM]`**: Number of concurrent requests for async fetching (default is 4).
- **`--debug`**: Enable debug logging for more details.

Note that if you don't give any options, by default the interactive CLI will start.

## Examples

The examples assume you have Poetry setup properly and added to your path.

1. **Create a Snapshot**

   ```bash
   url-snapshotter create -f urls.txt
   ```

2. **Compare Two Snapshots**

   ```bash
   url-snapshotter compare
   ```

3. **View a Snapshot**

   ```bash
   url-snapshotter view --snapshot-id 1
   ```

4. **Adjust Concurrent Requests**

   ```bash
   url-snapshotter create -f urls.txt -c 10
   ```

## Defining a URLs File

The `urls.txt` file (or any name you choose) is a simple text file containing the list of URLs you want to monitor. Each URL should be on a separate line without extra spaces or characters. Example:

```
https://example.com
https://another-example.com
https://api.example.com/subpage/endpoint
```

## Development Setup with Pyenv and Poetry

If you're planning to contribute or extend `url-snapshotter`, the best way to set up your environment is using **pyenv** and **Poetry**.

### Prerequisites

- **[Pyenv](https://github.com/pyenv/pyenv)**: For managing different Python versions.
- **[Poetry](https://python-poetry.org/)**: For dependency management and packaging.

### Setting Up Your Development Environment

1. **Install Pyenv**
   Follow the instructions in the [pyenv GitHub repository](https://github.com/pyenv/pyenv).

2. **Install the Correct Python Version**
   Use pyenv to install the version specified in the `pyproject.toml`:

   ```bash
   pyenv install 3.12.7
   ```

3. **Install Poetry**
   Install Poetry for dependency management:

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

4. **Create a Virtual Environment and Install Dependencies**

   ```bash
   pyenv virtualenv 3.12.7 url-snapshotter-env
   pyenv activate url-snapshotter-env
   poetry install
   ```

5. **Run the Application**
   To run the CLI directly after installing the dependencies:

   ```bash
   poetry run url-snapshotter
   ```

## Patterns and Custom Content Cleaning

The `patterns.py` file contains regex patterns that are used to clean up dynamic elements from the content of the fetched URLs. This is crucial for removing elements that may change frequently (e.g., CSRF tokens, timestamps, session identifiers), allowing you to focus only on meaningful content changes.

Each pattern in `patterns.py` consists of a regex pattern and an optional message to describe what is being cleaned up.

### Adding or Modifying Patterns

To add a new pattern, simply append it to the list in the `get_patterns` function in `url_snapshotter/patterns.py`. Each entry should be a dictionary containing a compiled regex pattern and an optional message for logging purposes.

For example, to add a new pattern to remove a dynamic authentication token, you can add:

```python
{
    "pattern": re.compile(r'auth_token="[^"]+"'),
    "message": "Authentication token detected and removed."
}
```

Make sure the regex patterns are well-tested to avoid removing unintended content.

## FAQ

### (Kubernetes) How do I quickly generate a urls.txt with all configured httpproxy crd and ingresses?

This assumes you use Contour with `httpproxy` crds and also the regular `ingress` objects. 

```bash
(
  # Get HTTPProxies URLs
  kubectl get httpproxies --all-namespaces -o jsonpath="{range .items[*]}https://{.spec.virtualhost.fqdn}{'\n'}{end}"
  
  # Get Ingresses URLs and ensure only the first URL (if multiple) is grabbed
  kubectl get ingresses --all-namespaces -o jsonpath="{range .items[*]}https://{.spec.rules[*].host}{'\n'}{end}" \
  | awk '{print $1}'  # This will grab only the first URL in case there are multiple
) | sort | uniq > urls.txt
```

This command is designed to list all fully qualified domain names (FQDNs) from both HTTPProxy and Ingress resources in a Kubernetes cluster, ensuring there are no duplicate URLs in the final output. 

**Note** It's common that multiple virtualhosts point to the same deployment; you might want to filter the `urls.txt` and adjust accordingly.

### (Kubernetes) How do I quickly generate a urls.txt for ingresses?

Just using `ingress` objects? Awesome, use this snippet.

```
(
  # Get Ingresses URLs and ensure only the first URL (if multiple) is grabbed
  kubectl get ingresses --all-namespaces -o jsonpath="{range .items[*]}https://{.spec.rules[*].host}{'\n'}{end}" \
  | awk '{print $1}'  # This will grab only the first URL in case there are multipe
) | sort | uniq > urls.txt
```

### (Kubernetes) How do I quickly generate a urls.txt for gateways and httproutes?

Using the somewhat new `gateway` object or `httproutes`? Got you covered.

```bash
(
  # Get Gateways hostnames
  kubectl get gateways --all-namespaces -o jsonpath="{range .items[*]}https://{.spec.listeners[*].hostname}{'\n'}{end}"
  
  # Get HTTPRoute hostnames
  kubectl get httproutes --all-namespaces -o jsonpath="{range .items[*]}https://{.spec.hostnames[*]}{'\n'}{end}" \
  | awk '{print $1}'  # Only take the first hostname if multiple
) | sort | uniq > urls.txt
``` 

### (Network) My resources are behind a VPN or proxy

Make sure you run `url-snapshotter` from a machine that has access to the URLs. If you can `curl` or `wget` a URL, then `url-snapshotter` should work fine.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
