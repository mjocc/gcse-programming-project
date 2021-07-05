# gcse-programming-project

## Generating API Docs

[Insomnia Documenter](https://github.com/jozsefsallai/insomnia-documenter#readme) offers a CLI tool to make it super easy to set up a documentation page. You can use it in two ways.

### Updating the API

Updating the API is super simple! Since Insomnia Documenter is a plug-and-play web app, you can just replace your `insomnia.json` with your new exported JSON file. Just make sure it's called `insomnia.json`.

The same actually applies to the logo as well (`logo.png`).


### To create (if static/api-docs is deleted)

**Using `npx`**

```sh
npx insomnia-documenter --config /path/to/insomnia/config.json
```

**By installing the package globally**

```sh
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
