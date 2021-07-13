# gcse-programming-project

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

## To Run

### For Development

After cloning, use poetry to install required packages into a virtual environment:

```shell
poetry install
```

This will be done automatically on replit.

Open the poetry virtual shell:

```shell
poetry shell
```

To run a local development server that automatically restarts when there are changes:

```shell
FLASK_APP=profit_calculator FLASK_ENV=development flask run
```

This will run on [localhost:5000](localhost:5000).

### In Production

After cloning, use poetry to install the required production packages into a virtual environment:

```shell
poetry install --no-dev
```

This will be done automatically on replit.

Open the poetry virtual shell:

```shell
poetry shell
```

**On Windows:**  

Run a waitress server on [localhost:8080](localhost:8080):

```shell
python -m wsgi
```

**On Linux:**  

Run a gunicorn server on [localhost:8080](localhost:8080):

```shell
gunicorn "wsgi:app"
```

## Generating API Docs

[Insomnia Documenter](https://github.com/jozsefsallai/insomnia-documenter#readme) offers a CLI tool to make it super easy to set up a documentation page. You can use it in two ways.

### Updating the API

Updating the API is super simple! Since Insomnia Documenter is a plug-and-play web app, you can just replace your `insomnia.json` with your new exported JSON file. Just make sure it's called `insomnia.json`.

The same actually applies to the logo as well (`logo.png`).


### To create (if static/api-docs is deleted)

**Using `npx`**

```shell
npx insomnia-documenter --config /path/to/insomnia/config.json
```

**By installing the package globally**

```shell
npm i -g insomnia-documenter
insomnia-documenter --config /path/to/insomnia/config.json
```

**Options**

```
Options:
  -c, --config <location>  Location of the exported Insomnia JSON config.
  -l, --logo <location>    Project logo location (48x48px PNG).
  -o, --output <location>  Where to save the file (defaults to current working directory).
  -h, --help               output usage information
```
