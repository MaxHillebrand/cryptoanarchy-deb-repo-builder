name = "bitcoin-mainnet"
version = "0.18.1"
bin_package = "bitcoind"
binary = "/usr/bin/bitcoind"
conf_param = "-conf="
user = { group = true, create = { home = true } }
# dpkg | bitcoin-zmq-mainnet is a hack avoiding restarts of bitcoind
depends = ["bitcoin-pruned-mainnet (>= 0.20.0-1) | bitcoin-chain-mode-mainnet (>= 1.0)", "bitcoin-pruned-mainnet (>= 0.20.0-1) | bitcoin-chain-mode-mainnet (<< 2.0)", "dpkg | bitcoin-zmq-mainnet"]
summary = "Bitcoin fully validating node"
extra_service_config = """
# Stopping bitcoind can take a very long time
TimeoutStopSec=300
Restart=always
RuntimeDirectory=bitcoin-mainnet
RuntimeDirectoryMode=0750
"""

[config."bitcoin.conf"]
format = "plain"
cat_dir = "conf.d"
cat_files = ["chain_mode"]

[config."bitcoin.conf".ivars.datadir]
type = "path"
file_type = "dir"
create = { mode = 755, owner = "$service", group = "$service" }
default = "/var/lib/bitcoin-mainnet"
priority = { dynamic = { script = """
. /etc/bitcoin-mainnet/chain_mode
test "$prune" -eq 0 && expected_chain_size="`expr 350000000 + 30000000 '*' $txindex`" || expected_chain_size="`expr $prune '*' 1000 + 5000000`"
used_size="`du -s /var/lib/bitcoin-mainnet 2>/dev/null`"
test -n "$used_size" && used_size="`echo "$used_size" | cut -d $'\t' -f 1`" || used_size=0
expected_chain_size="`expr $expected_chain_size - $used_size`"
test "`df /var | tail -1 | awk '{ print $4; }'`" -lt "$expected_chain_size" && PRIORITY=high || PRIORITY=medium
""" } }
summary = "Directory containing the bitcoind data"
long_doc = """
The full path to the directory which will contain timechain data (blocks and chainstate).
Important: you need around 10-400GB of free space!
"""

[config."bitcoin.conf".ivars.p2p_bind_port]
type = "bind_port"
default = "8333"
priority = "low"
summary = "Bitcoin P2P port (mainnet)"
store = false

[config."bitcoin.conf".ivars.p2p_bind_host]
type = "bind_host"
default = "0.0.0.0"
priority = "low"
summary = "Bitcoin P2P port (mainnet)"
store = false

[config."bitcoin.conf".hvars.bind]
type = "string"
script = "echo \"${CONFIG[\"bitcoin-mainnet/p2p_bind_host\"]}:${CONFIG[\"bitcoin-mainnet/p2p_bind_port\"]}\""

[config."bitcoin.conf".ivars.rpcport]
type = "bind_port"
default = "8331"
priority = "low"
summary = "Bitcoin RPC port"

[config."bitcoin.conf".ivars.dbcache]
type = "uint"
default = "450"
priority = "medium"
summary = "Size of database cache in MB"

[config."bitcoin.conf".hvars.rpccookiefile]
type = "string"
constant = "/var/run/bitcoin-mainnet/cookie"
