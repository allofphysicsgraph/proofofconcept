FROM ocaml/opam:alpine

MAINTAINER Ben <ben.is.located@gmail.com>

LABEL distro_style="apk" distro="alpine" arch="x86_64" operatingsystem="linux"

USER opam
ENV HOME /home/opam
WORKDIR /home/opam

#  

RUN rmdir .ssh && \
  rm -rf opam-repository && \
  mkdir .ssh && \
  chmod 700 .ssh && \
  git config --global user.email "docker@example.com" && \
  git config --global user.name "Docker CI" && \
  sudo -u opam sh -c "git clone -b master git://github.com/ocaml/opam-repository" && \
  sudo -u opam sh -c "opam init -a -y --comp 4.04.2+flambda /home/opam/opam-repository" && \
  sudo -u opam sh -c "opam install -y depext travis-opam" && \
  sudo -u opam install num
  sudo -u opam sh -c "git clone https://github.com/jrh13/hol-light.git"
ENTRYPOINT [ "opam", "config", "exec", "--" ]
CMD [ "bash" ]

