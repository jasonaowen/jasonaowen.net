# Building the Blog

This blog is built with [Pelican](https://docs.getpelican.com/en/3.7.1/).

Set up a virtual environment:

```sh
$ virtualenv --python=python3 venv
```

Then, activate it:

```sh
$ . venv/bin/activate
```

Install the dependencies:

```sh
$ pip install -r requirements.txt
```

Get help with `make` or `make help`,
build with `make html` (for dev)
or `make publish` (for prod),
and deploy with `make rsync_upload`.
