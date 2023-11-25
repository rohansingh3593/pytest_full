# !/bin/bash

set -o pipefail
set -e

# sudo apt update

sudo apt install -y git python3.8 python3.8-dev python3-pip curl
mkdir -p ~/VGS_TEST
cd ~/VGS_TEST 
wget https://github.com/GitCredentialManager/git-credential-manager/releases/download/v2.0.785/gcm-linux_amd64.2.0.785.deb 
sudo apt install ./gcm-linux_amd64.2.0.785.deb 

git-credential-manager-core configure 
git config --global credential.credentialStore plaintext 

echo your email is set to $USER@gmail.com
echo 'Enter your full name (for git commit user.name):  '
read NAME
echo git config --global user.name "$NAME"
git config --global user.name "$NAME"
echo git config --global user.email "$USER@gmail.com" 
git config --global user.email "$USER@gmail.com" 