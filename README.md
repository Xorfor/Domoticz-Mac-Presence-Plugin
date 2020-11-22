# NOT MAINTAINED ANYMORE!!!
I am disappointed in the way Domoticz developes: 
* 1 stable version per year, I had to wait 4 months until a bug was fixed
* no reaction on reported bugs, also if you give a direction for solution
* lost data after upgrade to a new stable versions
* etc.

So I moved to Home Assistant, and have no time/environment to maintain this plugin

# Mac address presence
This Domoticz Python Plugin scan the Domoticz network for the existance of the specified mac addresses.
## Prerequisites
You need the latest beta version of Domoticz for the best support of Python plugins and `arp-scan` to use this plagin. This tool can be installed by:
```bash
sudo apt-get install -y arp-scan
```
## Parameters
| Parameter | Description |
| :--- | :--- |
| **MAC addresses** | MAC addresses in de format xx:xx:xx:xx:xx:xx,xx:xx:xx:xx:xx:xx,xx:xx:xx:xx:xx:xx |
| **Minutes between check** | Polling time in minutes to check for the presence of the specified mac addresses |
| **Minutes for timeout** | Switch off the device when after this specified number of minutes, none of the mac addresses is found |
## Devices
| Name | Description |
| :--- | :--- |
| **MAC Presence** | A switch indicating whether one of the specified mac adresses was seen on the Domoticz network |

## To do
- [ ] Replace '-' for ':' in the mac addresses
