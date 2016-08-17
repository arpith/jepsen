# mmapd
Test mmapd with jepsen.

## Usage
### Start Jepsen
1. `$ git clone github.com/arpith/jepsen && cd jepsen/docker`
2. `$ .up.sh`
3. `$ docker exec -it jepsen-control bash`

### Run the test
1. `cd ../mmapd`
2. `lein test`

### Killing docker
If things don't work out, just kill your docker instances and try again :) You can do this with:

`$ sudo bash -c 'docker ps -a -q | xargs docker rm -f'`
