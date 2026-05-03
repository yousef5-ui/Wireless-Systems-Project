# Wireless Systems Project Version Control Repository

This repository was created to manage version control for the Wireless Systems Project. It contains the original project code, controlled code improvements, and a change management log showing how updates were made, recorded and merged.

## Repository Purpose

The purpose of this repository is to demonstrate the use of GitHub for version control and change management. The original project files were first uploaded as a baseline version. Improvements were then made on separate branches, committed with clear messages, reviewed through pull requests, and merged back into the main branch.

This approach helped ensure that changes to the project code were traceable and that the original working version could be compared against later improvements.

## Repository Structure

- `code/`
  - `20260122_WirelessComms_CalibrateRx_v1.00.py`
  - `webserver.py`
  - `README.md`

- `change-management/`
  - `code_change_log.md`

- `README.md`

## QMS Traceability

The original filenames were kept unchanged to remain consistent with the project Quality Management System. This improves traceability between the GitHub repository, the project file naming convention, and the wider project documentation.

## Version Control Status

The original filenames were kept to maintain traceability with the project QMS. Instead of renaming the files after each update, GitHub commit history, pull requests and the change log were used to record version changes. This avoided duplicate filenames while still allowing each controlled update to be traced from the original baseline version to the final merged version.

| File | Baseline Version | Current Controlled Version | Change Summary |
|---|---|---|---|
| `20260122_WirelessComms_CalibrateRx_v1.00.py` | v1.00 | v1.02 | Documentation added and RSSI validation helper added |
| `webserver.py` | v1.00 | v1.02 | Documentation added and active transmitter status display added |

## Version Control Method

The following workflow was used:

1. The original code was uploaded to the `main` branch as the baseline version.
2. Controlled improvements were made separately from the stable version of the code.
3. Changes were committed with descriptive commit messages.
4. Pull requests were used to compare the improved code against `main`.
5. Approved changes were merged back into the `main` branch.

## Summary

GitHub was used to support structured change management during the Wireless Systems Project. The use of commits, pull requests and a change log made the development process more traceable and reduced the risk of losing or overwriting the original working code.
