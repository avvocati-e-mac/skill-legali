#!/usr/bin/env python3
"""Inventory local package metadata without importing Docling or probing a server.

Run this script with the Python interpreter used to launch the Docling MCP.
Missing metadata describes this interpreter only. It does not establish that a
package is absent from another virtual environment or from a remote MCP host.
The inventory does not prove imports, model availability, conversion readiness,
or the MCP connection to the current chat. No configuration or secrets are read.
"""
from __future__ import annotations

import argparse
from importlib import metadata
import json
import os
import platform
import shutil
import sys


PACKAGES = ("docling", "docling-slim", "docling-core", "docling-mcp", "mcp", "pypdfium2")
COMMANDS = ("docling-mcp-server", "uv", "python3", "pdftotext", "pdftoppm")


def inspect_environment():
    """Return a read-only, interpreter-scoped inventory, not a readiness verdict."""
    packages = {}
    for name in PACKAGES:
        try:
            packages[name] = {"version": metadata.version(name), "status": "metadata_found"}
        except metadata.PackageNotFoundError:
            packages[name] = {"version": None, "status": "metadata_not_found_in_this_interpreter"}

    implementations = [name for name in ("docling", "docling-slim")
                       if packages[name]["status"] == "metadata_found"]
    return {
        "format_version": 1,
        "scope": "current_python_interpreter_and_command_search_path_only",
        "python": {"executable": sys.executable, "version": platform.python_version()},
        "system": {"name": platform.system(), "release": platform.release(),
                   "machine": platform.machine(), "os_name": os.name},
        "packages": packages,
        "commands": {name: shutil.which(name) for name in COMMANDS},
        "docling_implementation_candidates": implementations,
        "docling_implementation_note": (
            "docling-slim can supply the local Docling implementation even when the "
            "docling distribution is absent. Package metadata does not prove that "
            "document_converter imports or a conversion succeeds."
        ),
        "unverified": {
            "package_imports": "not_checked",
            "conversion_readiness": "not_checked",
            "models_available": "not_checked",
            "mcp_chat_connection": "not_checked",
            "mcp_tool_catalog": "not_checked",
            "mcp_execution_host": "not_checked",
            "server_local_or_remote_mode": "not_checked",
        },
        "limitations": [
            "Missing metadata here does not imply absence in another interpreter, virtual environment, or remote server.",
            "A command found on PATH may belong to a different environment from this Python interpreter.",
            "No configuration, credentials, or environment-variable values are inspected; no connection or conversion is attempted.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try:
        result = inspect_environment()
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except Exception as error:
        print(json.dumps({"status": "inventory_error", "error_type": type(error).__name__,
                          "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
