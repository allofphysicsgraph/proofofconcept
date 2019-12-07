#https://github.com/jgm/texmath

installed="$(which curl)"
if [[ $installed -eq 0 ]];
then
  install='Y'
  echo "Curl is required, Install? [Y/n]"
  read install
  if [[ $install='Y' ]];
  then
    sudo apt install curl;
  fi
fi

git clone https://github.com/jgm/texmath.git
curl -sSL https://get.haskellstack.org/ | sh
cd texmath
stack setup
stack install --flag texmath:executable