# Technical-Operations-Support-System
IT Support • Request Tracking • Records Management • Troubleshooting

Python • SQLite • Ubuntu • Windows 11

Overview

Technical Operations Support System (TOSS) is a Python-based application for handling IT support requests, managing records, and keeping track of day-to-day technical and administrative tasks.

The project brings common support tasks into one place instead of relying on separate spreadsheets, notes, or manually updated files. It is designed to make it easier to report an issue, find information, track what has been done, and keep a clear record of how problems were handled.

TOSS focuses on the work that happens behind the scenes in IT support and office operations, from receiving a request to checking the details, fixing the issue, or passing it along to the right person.

What TOSS Does

▸ Support Requests & Triage
Log incoming requests, set priorities, assign tasks, update their status, and flag issues that need further attention.

▸ Records Management
Store and search support records, update information, and keep track of changes using SQLite.

▸ Troubleshooting & Issue Resolution
Track common problems involving software, network connections, system access, and other technical issues. Record what was checked, what was fixed, and whether the issue was resolved.

▸ Record Checks & Auditing
Check for missing details, duplicate entries, incorrect information, and records that need to be reviewed or updated.

▸ Reports & Follow-Ups
View open requests, pending tasks, completed work, and issues that still need follow-up.

How Requests Are Handled

     New Request
          │
          ▼
    Review Details
          │
          ▼
   Set Priority / Assign
          │
          ▼
   Troubleshoot or Review
          │
          ▼
    Resolve / Escalate
          │
          ▼
    Update Records
          │
          ▼
     Close Request

Each request is designed to have its own ID, description, priority, assigned person, status, and history of updates so that work can be followed from start to finish.

Tools & Environment

Tool

How It's Used

Python 3

Main application and task handling

SQLite

Saving, updating, and searching records

Ubuntu Linux

Running and testing the application

Windows 11

Host computer and troubleshooting tests

Oracle VirtualBox

Testing in a separate virtual machine

Current Progress

Status: In Development

The first version is focused on building a working request tracking system with Python and SQLite.

Planned work includes:

Create and manage support requests

Save and retrieve records from SQLite

Update request priorities and statuses

Track changes and completed actions

Check records for missing or incorrect information

Add basic troubleshooting tools

Generate reports for open and resolved requests

Features will be marked complete as they are built and tested.

Notes

TOSS is being developed and tested locally using fictional support requests and records. It does not use real employee information or connect to company or government systems.
