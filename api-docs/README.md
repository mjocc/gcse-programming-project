# Generating API Docs

Insomnia Documenter offers a CLI tool to make it super easy to set up a documentation page. You can use it in two ways.

## Specific to this project
```sh
npx insomnia-documenter -c api-docs/insomnia-config.json -l api-docs/plane.png -o profit_calculator/static/api-docs
```

## General Instructions

### Using `npx`

```sh
npx insomnia-documenter --config /path/to/insomnia/config.json
```

### By installing the package globally

```sh
npm i -g insomnia-documenter
insomnia-documenter --config /path/to/insomnia/config.json
```

### Options

```
Options:
  -c, --config <location>  Location of the exported Insomnia JSON config.
  -l, --logo <location>    Project logo location (48x48px PNG).
  -o, --output <location>  Where to save the file (defaults to current working directory).
  -h, --help               output usage information
```
