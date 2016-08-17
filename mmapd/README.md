# mmapd
Test mmapd with jepsen.

## Usage
### Start Jepsen
1. `$ git clone github.com/arpith/jepsen && cd jepsen/docker`
2. `$ sudo .up.sh`
3. `$ sudo docker exec -it jepsen-control bash`

### Run the test
`cd mmapd && lein test`

### Killing docker
If things don't work out, just kill your docker instances and try again :) You can do this with:

`$ sudo bash -c 'docker ps -a -q | xargs docker rm -f'`
