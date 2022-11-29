# pveTelnetCommand
PVE Telnet Remote Interface for Guacamole

With this simple Tool/Container you can expose some simple functions of the pve API via Telnet to your Guacamole Server.
! Handle with care, set Env vars for PVE Api only via Secrets !
! There is no encryption or authorization on place, everyone with access to the port can use this tool !

## Configuration
### Connection Details
PVE_TOKEN="user@provider!nameofapitoken"
PVE_SECRET="secretofthetokenprovidedabove"
PVE_NODE="pvenodename"
PVE_URL="https://pve.tld:8006"

### Provide VM Map:
PVE_MAP_VMNAME_VMID

Example:
PVE_MAP_Server1=123
PVE_MAP_Server2=111
