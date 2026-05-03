# Wireless Systems Project Code Change Log

This change log records the version-controlled changes made to the Wireless Systems Project code. Each change was developed on a separate branch, committed with a descriptive message, reviewed through a pull request, and merged back into the main branch.

| Change ID | Branch | File(s) Changed | Change Made | Reason for Change | Version Control Evidence |
|---|---|---|---|---|---|
| C1 | feature/add-code-documentation | 20260122_WirelessComms_CalibrateRx_v1.00.py | Added a file header and function docstrings to explain the receiver calibration script, Kalman filter and RSSI sampling functions. | Improved readability and made the calibration code easier for team members to understand and maintain. | Commit and pull request recorded in GitHub. |
| C2 | feature/add-code-documentation | webserver.py | Added a file header and docstrings to explain the positioning dashboard, data logger, RSSI prediction, heatmap generation and main loop. | Improved understanding of the positioning script and made the code structure easier to follow before future edits. | Commit and pull request recorded in GitHub. |
| C3 | feature/add-rssi-validation | 20260122_WirelessComms_CalibrateRx_v1.00.py | Added named RSSI validation limits and an `is_valid_rssi()` helper function. | Reduced hard-coded values inside the calibration loop and made the RSSI validation range easier to update. | Commit and pull request recorded in GitHub. |
| C4 | feature/add-transmitter-status | webserver.py | Added active transmitter count, named signal status constants and a low signal confidence warning on the live dashboard. | Improved live testing feedback by showing when too few transmitter readings were available for reliable positioning. | Commit and pull request recorded in GitHub. |

## Summary

Version control was used to manage both documentation and functional improvements to the Wireless Systems Project code. The main branch was kept as the stable version, while separate feature branches were used to make and record specific changes. Pull requests were then used to compare each branch with main before merging, creating a clear audit trail of how the code developed.
