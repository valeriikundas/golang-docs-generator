
# golang-docs-generator

The repository contains a documentation generator for Golang.\

The repository takes a code folder path as an input and generates an output folder which contains all the documentation.\

Currently implemented features include 
1. pages that contain all code objects
2. traversing between content pages and file pages
3. indexed page, which contains all objects from all files ordered alphabetically.


# usage

Usage: main.py [OPTIONS]

Options:

  --path TEXT code folder path

  --output TEXT output folder path

## examples:

```python3 main.py --path redis --output docs```

repository contains `redis` folder which can be used as an example
