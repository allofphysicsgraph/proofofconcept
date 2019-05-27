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
  sudo apk add m4 && \
  
  git config --global user.email "docker@example.com" && \
  git config --global user.name "Docker CI" && \
  sudo -u opam sh -c "git clone -b master git://github.com/ocaml/opam-repository" && \
  sudo -u opam sh -c "git clone https://github.com/jrh13/hol-light.git /home/opam/hol-light"  && \
  sudo -u opam sh -c "opam update" && \
  sudo -u opam sh -c "opam switch 4.04.1" && \
  sudo -u opam sh -c "opam install -y depext travis-opam" && \
  sudo -u opam sh -c "opam install -y num" && \
  cd /home/opam/ && \
  wget https://github.com/camlp5/camlp5/archive/rel705.tar.gz && \
  tar -zxvf rel705.tar.gz && \
  cd camlp5-rel705 && \
  ./configure --strict && \
  make && \
  sudo make install && \
  cd .. && \
  cd /home/opam/hol-light && \
  make && \
  cd .. && \ 
ENTRYPOINT [ "opam", "config", "exec", "--" ]
CMD [ "bash" ]

