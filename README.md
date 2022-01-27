[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)

# Hydra Example Project for Python

> A small example project for efficiently configuring a Python application with YAMLs and the CLI.

## Why should I care?

A frequent requirement for productive Python application is that they are configurable via configuration files and/or
the command-line-interface (CLI). This allows you to change the behavior of your application without touching the source code, e.g. configuring
another database URL or the logging verbosity. For the CLI-part, [argparse] or [Click] is often used and with [PyYAML] configuration files
can be easily read, so where is the problem?

The CLI and configuration file of a Python application have many things in common, i.e., both

1. configure the runtime behaviour of your application,
2. need to implement validations, e.g. is the port an integer above 1024,
3. need to be consistent and mergeable, i.e. a CLI flag should be named like the YAML key and if both are passed the CLI
   overwrites the YAML configuration.

Thus implementing the CLI and configuration by a YAML file seperated from each other, leads often to code duplication
and inconsistent behavior, not to mention the enormous amount of work that must be done to get this right.

With this in mind, Facebook implemented the [Hydra] library, which allows you to do hierarchical configuration by
composition and override it through config files and the command-line. This repository serves as an example project set
up to demonstrate the most important features. We also show how [Hydra] can be used in conjunction with [pydantic],
which extends the validation capabilities of [OmegaConf] that is used internally by Hydra.

Read this [blog post] if you want to know more.

## Installation & Testing

If you want to play around with this project, just clone it and set up the necessary environment:

1. create an environment `hydra-example-project` with the help of [conda]:
   ```
   conda env create -f environment.yml
   ```
2. activate the new environment with:
   ```
   conda activate hydra-example-project
   ```

and you are all set to run `hydra-test`.

## By the way, how was this awesome example project set up?

Glad you asked. This project was set up using the miraculous [PyScaffold] with the [dsproject extension].
The setup was as simple as:
```shell
putup -f hydra-example-project --dsproject -p my_pkg
```

In order to have the CLI command `hydra-test`, we changed in `setup.cfg` the following lines:
```ini
# Add here console scripts like:
console_scripts =
     hydra-test = my_pkg.cli:main
```
Remember to run `pip install -e .` after any changes to `setup.cfg`.


## Project Organization

```
├── AUTHORS.md              <- List of developers and maintainers.
├── CHANGELOG.md            <- Changelog to keep track of new features and fixes.
├── CONTRIBUTING.md         <- Guidelines for contributing to this project.
├── Dockerfile              <- Build a docker container with `docker build .`.
├── LICENSE.txt             <- License as chosen on the command-line.
├── README.md               <- The top-level README for developers.
├── configs                 <- Directory for configurations of model & application.
├── data
│   ├── external            <- Data from third party sources.
│   ├── interim             <- Intermediate data that has been transformed.
│   ├── processed           <- The final, canonical data sets for modeling.
│   └── raw                 <- The original, immutable data dump.
├── docs                    <- Directory for Sphinx documentation in rst or md.
├── environment.yml         <- The conda environment file for reproducibility.
├── models                  <- Trained and serialized models, model predictions,
│                              or model summaries.
├── notebooks               <- Jupyter notebooks. Naming convention is a number (for
│                              ordering), the creator's initials and a description,
│                              e.g. `1.0-fw-initial-data-exploration`.
├── pyproject.toml          <- Build configuration. Don't change! Use `pip install -e .`
│                              to install for development or to build `tox -e build`.
├── references              <- Data dictionaries, manuals, and all other materials.
├── reports                 <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures             <- Generated plots and figures for reports.
├── scripts                 <- Analysis and production scripts which import the
│                              actual PYTHON_PKG, e.g. train_model.
├── setup.cfg               <- Declarative configuration of your project.
├── setup.py                <- [DEPRECATED] Use `python setup.py develop` to install for
│                              development or `python setup.py bdist_wheel` to build.
├── src
│   └── my_pkg              <- Actual Python package where the main functionality goes.
├── tests                   <- Unit tests which can be run with `pytest`.
├── .coveragerc             <- Configuration for coverage reports of unit tests.
├── .isort.cfg              <- Configuration for git hook that sorts imports.
└── .pre-commit-config.yaml <- Configuration of pre-commit git hooks.
```

<!-- pyscaffold-notes -->

## Note

This project has been set up using [PyScaffold] 4.1.4 and the [dsproject extension] 0.7.

[conda]: https://docs.conda.io/
[pre-commit]: https://pre-commit.com/
[Jupyter]: https://jupyter.org/
[nbstripout]: https://github.com/kynan/nbstripout
[Google style]: http://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
[PyScaffold]: https://pyscaffold.org/
[dsproject extension]: https://github.com/pyscaffold/pyscaffoldext-dsproject
[Hydra]: https://hydra.cc/
[pydantic]: https://pydantic-docs.helpmanual.io/
[OmegaConf]: https://omegaconf.readthedocs.io/
[Click]: https://click.palletsprojects.com/
[PyYAML]: https://pyyaml.org/
[blog post]: https://florianwilhelm.info/2022/01/configuration_and_cli_with_hydra/
