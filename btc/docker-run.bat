docker run -d ^
  --name=bitcoind-testnet ^
  -v F:\btc-testnet:/home/bitcoin/.bitcoin ^
  -p 18333:18333 ^
  -p 18332:18332 ^
  bitcoin/bitcoin ^
  -testnet=1 ^
  -prune=550 ^
  -txindex=0 ^
  -server=1 ^
  -rpcbind=0.0.0.0 ^
  -rpcallowip=0.0.0.0/0 ^
  -rpcuser=bitcoin ^
  -rpcpassword=secret

