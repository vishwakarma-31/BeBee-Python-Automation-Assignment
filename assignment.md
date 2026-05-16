BeBee Python Automation Assignment

Summary
Your assignment is to build a Python automation module for BeBee that supports:

account signup
account login
email verification
batch login from CSV
parallel batch execution
result logging
The goal is to create a clean, reliable, and maintainable automation system that can be used repeatedly and extended later.

Scope
Your work must cover these areas:

HTTP session setup
optional proxy support
signup workflow
login workflow
email verification handling
CSV-based batch processing
configurable parallel execution
structured logging
clear failure handling
Target URLs

Your documentation and implementation must clearly explain the purpose of each of these URLs.

Signup-related:
https://bebee.com/
https://bebee.com/br
https://bebee.com/api/auth/session
https://bebee.com/api/users
https://bebee.com/api/auth/verify-email
https://bebee.com/api/search/locations
https://bebee.com/api/upload/photo

Login-related:
https://bebee.com/auth/login
https://bebee.com/api/auth/session
https://bebee.com/api/auth/csrf
https://bebee.com/api/auth/callback/credentials
You must map each URL to the correct step in the workflow.

Task 1: Workflow Analysis
Before coding, write a short flow note that explains:

the full signup sequence
the full login sequence
which cookies are important
which tokens are important
where email verification happens
which step determines success
which URL is used at each stage
This should be written clearly enough that another engineer can understand the automation flow without reverse-engineering your code.

Task 2: Signup Automation
Implement a signup workflow that can:

start an HTTP session
optionally use proxies
prepare account details
send the required startup requests
fetch a valid location dynamically
create the BeBee user
wait for verification email
extract the verification token or verification link
complete email verification
upload a profile photo
determine whether the signup succeeded
store successful credentials in a CSV

Task 3: Login Automation
Implement a login workflow that can:

start an HTTP session
fetch auth/session prerequisites
fetch CSRF token if required
submit login credentials
confirm that the session is authenticated
determine whether login succeeded
Your implementation must not rely only on status codes. Use response contents and session state where necessary.

Task 4: Batch Login From CSV
Create batch login support using an input CSV with these columns:

email
password
For each row, run the login workflow and write a new output CSV containing:

email
password
success_status
Task 5: Parallel Batch Execution

Add support for configurable concurrency.

Requirements:

max_workers=1 must run sequentially
values like 3, 4, etc. must run that many jobs in parallel
completed rows must be written safely to the output CSV
output writing must not corrupt data
logs must clearly show when a job starts, finishes, succeeds, or fails
Task 6: Command-Line Usage

Your script must support command-line usage for:

single login
batch login
input CSV path
output CSV path
max worker count
optional proxy file
Task 7: Logging And Error Handling

Your implementation must clearly separate these failure types:

proxy failure
network/request failure
email verification failure
login failure
response parsing failure
Logs should make debugging easy and should show enough detail to identify the failed step quickly.

Task 8: Code Quality Expectations
Your implementation must be:

modular
readable
maintainable
easy to debug
suitable for repeated use in automation jobs
Avoid writing one long procedural script. Structure the code in a way that makes future extension practical.

Deliverables
Submit the following:
your Python implementation
a short architecture note
a workflow note describing signup and login
a short note listing:
assumptions
known risks
future improvements
Evaluation Criteria

Your work will be evaluated on:

correctness of signup flow
correctness of login flow
correctness of URL-to-step mapping
quality of batch processing
correctness of parallel execution
quality of logging
quality of error handling
code structure and readability
clarity of documentation
Submission Standard

Your final submission should be clear enough that:
another engineer can run it
another engineer can debug it
another engineer can extend it without guessing how the workflow works