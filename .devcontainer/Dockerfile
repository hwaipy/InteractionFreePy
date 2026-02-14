FROM mcr.microsoft.com/devcontainers/python:3.14

# enable git and git-lfs
RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
RUN sudo apt-get install git-lfs
RUN git lfs install
