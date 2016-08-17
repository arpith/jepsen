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
