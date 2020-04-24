# docker build -t mathjax .; docker run -it --rm -p5009:5009 mathjax:latest
# then open a browser and access
# http://0.0.0.0:5009/

# https://github.com/phusion/baseimage-docker
# http://phusion.github.io/baseimage-docker/
# https://github.com/phusion/baseimage-docker/releases
FROM phusion/baseimage:0.11

# npm, the Node.js package manager
RUN apt-get update && \
    apt-get install -y npm \ 
                       python3

# https://www.npmjs.com/package/mathjax
RUN npm install mathjax@3

# mv node_modules/mathjax/es5 <path-to-server-location>/mathjax

EXPOSE 5009

CMD cd node_modules/mathjax/es5 && \
# https://docs.python.org/3/library/http.server.html
#    python3 -m http.server 5009 --bind localhost
    python -m SimpleHTTPServer 5009
