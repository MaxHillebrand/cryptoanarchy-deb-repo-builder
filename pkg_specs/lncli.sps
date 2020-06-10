name = "lncli"
architecture = "any"
summary = "Lightnning Network Daemon CLI"
depends = ["${shlibs:Depends} ${misc:Depends}"]
recommends = ["lnd-system-mainnet | lnd-system-regtest"]
long_doc = """lncli is a tool used for managing lnd from the command line. This package
also contains a wrapper used to connect to the system-wide LND by default.
You can still use --macaroonpath --rpcserver and --tlscertpath to access a
different lnd."""