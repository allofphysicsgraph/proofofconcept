# What is not in this repo
 * certs/dhparam.pem
 * certs/fullchain.pem
 * certs/privkey.pem
 * .env

The certs/*.pem are generated by Let's Encrypt

The .env contains three lines,

    GOOGLE_CLIENT_ID=
    GOOGLE_CLIENT_SECRET=
    SECRET_KEY=



# quickstart
docker-compose up --build --remove-orphans

as a two step process:
docker-compose build --progress tty
docker-compose up

On DigitalOcean server:
docker-compose up --build --remove-orphans --detach



docker-compose instructions are from from
https://github.com/ChloeCodesThings/chloe_flask_docker_demo
and
https://codefresh.io/docker-tutorial/hello-whale-getting-started-docker-flask/

combining flask, gunicorn, nginx is from
https://testdriven.io/blog/dockerizing-flask-with-postgres-gunicorn-and-nginx/

nginx timeout
https://wiki.ssdt-ohio.org/display/rtd/Adjusting+nginx-proxy+Timeout+Configuration