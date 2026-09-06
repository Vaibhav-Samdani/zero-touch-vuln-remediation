
# Zero Touch Vulnerability Remediation

## STAR Method Pitch

### S - Situation

#### Overview of the Project

-> During my internship in HPE under CPP Program, I worked on the Project called **Zero Touch Vulnerability Remediation.**

-> About the current Remediation flow.

-> Problems with current remediation flow

-> Objective - Multi Agent AI-Based Remediation System.

### T - Task

### A - Action

### R - Result

## Overview of the whole project 

“This is the overall workflow of our Automated Vulnerability Management System.
We start by running multiple security scanners such as Trivy, Snyk, Grype, ZAP, Nmap,
and Lynis. Their outputs can be in different formats, so our system first automatically
parses them and converts them into CSV, followed by normalization into a common
schema.
After normalization, we prioritize the vulnerabilities using factors like CVSS, EPSS, CISA
KEV, and asset criticality. The high-priority vulnerabilities are then added to the
remediation queue.
For a selected vulnerability, we clone the target VM so that we can safely test the
remediation without directly affecting production. At the same time, we create a Jira
ticket and a GitHub branch.
Then our remediation agent generates a remediate.sh script and pushes it to GitHub.
This triggers GitHub Actions, which executes the script on the cloned VM.
If the execution fails, we capture the error logs and send them to the self-correction
agent. The agent analyzes the failure, modifies the remediation script, and the process
is retried automatically.

If the remediation succeeds, we validate the fix by running the scanners again on the
cloned VM. We then generate before-and-after evidence and update the Jira ticket. A
Pull Request is created for human review.
This is the only human approval point in our workflow.If the reviewer rejects the PR,
the feedback goes back to the remediation process and the script is regenerated. If the
reviewer approves it, the PR is merged, the fix is applied to the actual production VM,
and a final compliance scan is performed.
Finally, the cloned VM is cleaned up and the Jira ticket is resolved.
So, the key idea is that everything from vulnerability detection to remediation and
validation is automated, while human intervention is retained only at the final
production approval stage.”


## Questions

* **Why did you choose this tech stack?**
* **What are the trade-offs?**
* **Why not alternative technologies?**
* **What are the current bottlenecks?**
* **How would you scale it from a prototype to enterprise scale?**
