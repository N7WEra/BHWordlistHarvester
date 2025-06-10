# BHWordlistHarvester - Bloodhound Wordlist Generator

A Python script to parse Bloodhound JSON data and generate a comprehensive wordlist for security assessments. It extracts a wide variety of attributes from users, computers, groups, GPOs, and other Active Directory objects to create a targeted list for use in enumeration and password-based attacks.

## Inspiration

This project is a standalone, file-based parser inspired by the methodologies of other great tools. The goal was to create a script that works directly on JSON exports without needing a database connection.
**This script was 99% generated using Gemini.**

This work is inspired by:
* [MickeyDB/Neo4jWordlistHarvester](https://github.com/MickeyDB/Neo4jWordlistHarvester)
* [p0dalirius/pyLDAPWordlistHarvester](https://github.com/p0dalirius/pyLDAPWordlistHarvester)

## Features

* **Comprehensive Extraction**: Pulls SamAccountNames, user and group names, computer names, OU names, Service Principal Names (SPNs), GPO display names, domain trusts, and certificate template names.
* **Handles All Bloodhound JSON**: Parses all common Bloodhound file types (`users`, `computers`, `groups`, `domains`, `ous`, `gpos`, etc.) including ADCS-related objects (`cas`, `templates`).
* **Memory-Efficient**: Uses streaming JSON parsing (`ijson`) to handle very large multi-gigabyte files without consuming significant memory.
* **Robust File Handling**: Automatically detects the data type from file metadata, so you don't need to worry about specific filenames.
* **Clean Output**: The final wordlist is automatically de-duplicated, sorted, and filtered to remove empty or null values.
* **Easy to Use**: Simple command-line interface for pointing to your data folder and specifying an output file.

## Prerequisites

* Python 3.6+
* Bloodhound JSON data files (e.g., from SharpHound, the official Bloodhound collector, or other compatible tools).

## Installation

1.  Clone this repository or download the `bh2wordlist.py` script and `requirements.txt` file.

    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```

2.  Install the required Python package using the `requirements.txt` file:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Place all your Bloodhound `*.json` files into a single folder.

2.  Run the script, providing the path to the folder containing your JSON files.

    **Basic Example:**
    ```bash
    python3 bh2wordlist.py /path/to/your/bloodhound_json_exports/
    ```

    **Example with a Custom Output File:**
    ```bash
    python3 bh2wordlist.py /path/to/your/bloodhound_json_exports/ -o custom_wordlist.txt
    ```

### Command-Line Arguments
* `folder_path` (Required): The path to the folder containing the Bloodhound JSON files.
* `-o, --output` (Optional): The name of the output wordlist file. Defaults to `bloodhound_wordlist.txt`.

## Example
```
$ python3 bh2wordlist.py adex/                                                                   
Starting extraction...
Processing kingslanding.sevenkingdoms.local_1749478994_cert_bh.json...
  -> Detected type: gpos
Processing kingslanding.sevenkingdoms.local_1749478994_cert_ly4k_cas.json...
  -> Detected type: cas
Processing kingslanding.sevenkingdoms.local_1749478994_cert_ly4k_tpls.json...
  -> Detected type: templates
Processing kingslanding.sevenkingdoms.local_1749478994_computers.json...
  -> Detected type: computers
Processing kingslanding.sevenkingdoms.local_1749478994_domains.json...
  -> Detected type: domains
Processing kingslanding.sevenkingdoms.local_1749478994_groups.json...
  -> Detected type: groups
Processing kingslanding.sevenkingdoms.local_1749478994_users.json...
  -> Detected type: users

Extraction complete. 149 unique items saved to 'bloodhound_wordlist.txt'

```

## Output

The script will generate a text file (e.g., `bloodhound_wordlist.txt`) in the directory you run it from. This file contains a sorted list of unique names, with one entry per line, ready for use in other security tools for tasks such as:
* Password spraying
* Dictionary attacks
* Further enumeration
