# AWX CLI (Other commands)

This cheat sheet contains additional AWX CLI commands that did not make it into the main cheat sheet.

## Credentials

### Thycotic Secret Server

Creating Thycotic secret server credentials:

```bash
awx credential_types list -f human
awx credentials create --name "Thycotic secret server" --description "Credentials to connect to the thycotic secret server" --organization <id> --credential_type <id> --inputs '{ "username":"youruser", "password":"Password1!", "domain":"", server_url:"https://your.server.com/" }' -f human
```

### Source Control

Creating source control credentials with username and password or personal access token (PAT):

```bash
awx credential_types list -f human
awx credentials create --name "Git leak test" --description "Git leak test" --organization <id> --credential_type <id> --inputs '{ "username":"gituser", "password":"Password1!" }' -f human
```
