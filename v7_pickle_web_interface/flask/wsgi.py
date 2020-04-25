#!/usr/bin/env python3

# this file is for gunicorn

from controller import app


print("hello from wsgi")

if __name__ == "__main__":
    app.run()

# EOF
