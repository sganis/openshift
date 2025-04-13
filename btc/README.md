# start all pods if scaled down to zero:
# cmd
for /f "delims=" %d in ('oc get deploy -o name') do oc scale %d --replicas=1

# bash
for d in $(oc get deploy -o name); do oc scale $d --replicas=1; done



docker run -d ^
  --name=bitcoind ^
  -v F:\btc-regtest:/home/bitcoin/.bitcoin ^
  -p 18444:18444 ^
  -p 18443:18443 ^
  -p 28332:28332 ^
  -p 28333:28333 ^
  bitcoin/bitcoin ^
  -regtest=1 ^
  -txindex=1 ^
  -server=1 ^
  -rpcpassword=Secret1! ^
  -rpcbind=0.0.0.0 ^
  -rpcallowip=0.0.0.0/0 ^
  -rpcuser=bitcoin ^
  -zmqpubrawblock=tcp://0.0.0.0:28332 ^
  -zmqpubrawtx=tcp://0.0.0.0:28333
  
# test:
alias bcli='bitcoin-cli -regtest -rpcuser=bitcoin -rpcpassword=Secret1! -rpcconnect=127.0.0.1 -rpcport=18443'
bcli getblockchaininfo
bcli createwallet "mywallet"
bcli -rpcwallet=mywallet getnewaddress
bcli -rpcwallet=mywallet generatetoaddress 110 bcrt1qjh227d9nkfwzyewgq69n5nmulegs8wduagnhcc
bcli -rpcwallet=mywallet getbalance
bcli -rpcwallet=mywallet listunspent
bcli -rpcwallet=mywallet getblockcount
bcli -rpcwallet=mywallet listreceivedbyaddress 0 true

docker run -d ^
  --name lnd ^
  -p 9735:9735 ^
  -p 10009:10009 ^
  -p 8080:8080 ^
  -v F:\lnd-simnet:/root/.lnd ^
  lightninglabs/lnd:v0.19.0-beta.rc2 ^
  lnd ^
  --bitcoin.regtest ^
  --bitcoin.node=bitcoind ^
  --bitcoind.rpchost=host.docker.internal:18443 ^
  --bitcoind.rpcuser=bitcoin ^
  --bitcoind.rpcpass=Secret1! ^
  --bitcoind.zmqpubrawblock=tcp://host.docker.internal:28332 ^
  --bitcoind.zmqpubrawtx=tcp://host.docker.internal:28333 ^
  --restlisten=0.0.0.0:8080 ^
  --rpclisten=0.0.0.0:10009 ^
  --listen=0.0.0.0:9735 

# test:
alias lncli='lncli --network=regtest --lnddir=/data/.lnd' 
lncli create
lncli getinfo
