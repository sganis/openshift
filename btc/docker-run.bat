docker run -d ^
  --name=bitcoind-testnet ^
  -v F:\btc-testnet:/home/bitcoin/.bitcoin ^
  -p 18333:18333 ^
  -p 18332:18332 ^
  bitcoin/bitcoin ^
  -testnet=1 ^
  -assumevalid=000000000f0ff6905c39ad4b7d26b36dd0d38d067002f4ff696b76d4c233c931 ^
  -prune=550 ^
  -txindex=0 ^
  -server=1 ^
  -rpcbind=0.0.0.0 ^
  -rpcallowip=0.0.0.0/0 ^
  -rpcuser=bitcoin ^
  -rpcpassword=secret

