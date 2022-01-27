[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)

# Hydra Example Project for Python

> A small example project for efficiently configuring a Python application with YAMLs and the CLI.

### Why should I care?

A frequent requirement for productive Python application is that they are configurable via configuration files and/or
the command-line-interface (CLI). This allows you to change the behavior without touching the source code by e.g. configuring
another database URL or the logging verbosity. For the CLI-part, [Click] is often used and with [PyYAML] configuration files
can be easily read, so where is the problem?

The CLI and configuration file of a Python application have many things in commmon, i.e., both

1. configure the runtime behaviour of your application,
2. need to implement validations, e.g. is the port an integer above 1024,
3. need to be consistent and mergeable, i.e. a CLI flag should be named like the YAML key and if both are passed the CLI
   overwrites the YAML configuration.

Thus implementing the CLI and configuration by a YAML file seperated from each other, leads to often to code duplication
and inconsistent behavior, not to mention the enormous amount of work that must be done to get this right.

With this in mind, Facebook implemented the [Hydra] library, which allows you to do hierarchical configuration by
composition and override it through config files and the command-line. This repository serves as an example project set
up to demonstrate the most important features. We also show how [Hydra] can be used in conjunction with [pydantic],
which extends the validation capabilities of [OmegaConf] that is used internally by Hydra.


### Ok, so give me the gist of it!

Sure, just take a look into `src/my_pkg/cli.py` and `src/my_pkg/config.py` first as these are the only files we added,
roughly 70 lines of code. The hierarchical configuration can be found in `configs`.
```
├── configs
│   ├── main.yaml             <- entry point for configuration
│   ├── db                    <- database configuration group
│   │   ├── mysql.yaml        <- configuration of MySQL
│   │   └── postgresql.yaml   <- configuration for PostgreSQL
│   └── experiment            <- experiment configuration group
│       ├── exp1.yaml         <- configuration for experiment 1
│       ├── exp2.yaml         <- configuration for experiment 2
│       ├── missing_key.yaml  <- wrong configuration with missing key
│       └── wrong_type.yaml   <- wrong configuration with wrong type
```
Basically, this structure allows you to mix and match your configuration by choosing for instance the MySQL database
with the setup of experiment 2. Each group then corresponds to an attribute in the configuration object, which
includes other attributes, just think of a dictionary where some keys are again dictionaries.

We can invoke our application with the console command `hydra-test` and this will execute the `main` function in `cli.py`:
```python
@hydra.main(config_path=None, config_name="main")
def main(cfg: Config) -> None:
    # this line actually runs the checks of pydantic
    OmegaConf.to_object(cfg)
    print(OmegaConf.to_yaml(cfg)) # we just print the config and wait a few secs
    # note that IDEs allow auto-complete for accessing the attributes!
    time.sleep(cfg.main.sleep)
```

So executing just `hydra-test` results in:
```shell
Cannot find primary config 'main'. Check that it's in your config search path.

Config search path:
	provider=hydra, path=pkg://hydra.conf
	provider=main, path=pkg://my_pkg
	provider=schema, path=structured://

Set the environment variable HYDRA_FULL_ERROR=1 for a complete stack trace.
```
This is due to the fact that we set `config_path=None`, which is desirable for productive application. The application
itself doesn't know where it is gonna be installed and thus defining a path to the configuration files doesn't make sense.
For this reason we pass the configuration at execution with `-cd`, short for `--config-dir`:
```shell
hydra-test -cd configs
```
This results in the error:
```shell
Error executing job with overrides: []
Traceback (most recent call last):
  File ".../hydra-example-project/src/my_pkg/cli.py", line 11, in main
    OmegaConf.to_object(cfg)
omegaconf.errors.MissingMandatoryValue: Structured config of type `Config` has missing mandatory value: experiment
    full_key: experiment
    object_type=Config

Set the environment variable HYDRA_FULL_ERROR=1 for a complete stack trace.
```
This is exactly as we want it, since by taking a look into `config.py`, we see that the schema of the main configuration is:
```python
@dataclass
class Config:
    main: Main
    db: DataBase
    neptune: Neptune
    experiment: Experiment = MISSING
```
So experiment is a mandatory parameter that the CLI user needs to provide. Thus, we add `+experiment=exp1` to select the
configuration from `exp1.yaml` and finally get what we expect:
```shell
❯ hydra-test -cd configs +experiment=exp1
[2022-01-27 08:14:34,257][my_pkg.cli][INFO] -
main:
  sleep: 3
neptune:
  project: florian.wilhelm/my_expriments
  api_token: ~/.neptune_api_token
  tags:
  - run-1
  description: Experiment run on GCP
  mode: async
db:
  driver: mysql
  host: server_string
  port: 1028
  username: myself
  password: secret
experiment:
  model: XGBoost
  l2: 0.01
  n_steps: 1000
```
Note that we had to use a plus sign in the flag `+experiment` as we *added* the mandatory experiment parameter. Note
that Hydra has also set up the logging for us and besides the terminal all output will also be collected in an `./outputs`
folder.

So the section `main` and `neptune` are directly defined in `main.yaml` but why did Hydra now choose the MySQL database?
This is due to fact that in `main.yaml`, we defined some defaults:
```yaml
# hydra section to build up the config hierarchy with defaults
defaults:
  - _self_
  - base_config
  - db: mysql.yaml
  # experiment: is not mentioned here but in config.py to have a mandatory setting
```
We can override this default behavior by adding `db=postgresql` and this time without `+` as we override a default:
```shell
❯ hydra-test -cd configs +experiment=exp1 db=postgresql
Error executing job with overrides: ['+experiment=exp1', 'db=postgresql']
Traceback (most recent call last):
  File ".../hydra-example-project/src/my_pkg/cli.py", line 11, in main
    OmegaConf.to_object(cfg)
pydantic.error_wrappers.ValidationError: 1 validation error for DataBase
port
  Choose a non-privileged port! (type=value_error)

Set the environment variable HYDRA_FULL_ERROR=1 for a complete stack trace.
```
Nice this worked as expected by telling us that our port configuration is actually wrong as we chose a privileged port!
This is the magic of [pydantic] doing its validation work. Taking a look into `config.py`, we see the check that assures
a port greater than 1023.
```python
@dataclass
class DataBase:
    driver: str
    host: str

    @validator("port")
    def validate_some_var(cls, port: int) -> int:
        if port < 1024:
            raise ValueError(f"Choose a non-privileged port!")
        return port

    port: int
    username: str
    password: str
```
Good, so we could fix our configuration file or pass an extra parameter if we are in a hurry, i.e.:
```shell
❯ hydra-test -cd configs +experiment=exp1 db=postgresql db.port=1832
[2022-01-27 08:13:52,148][my_pkg.cli][INFO] -
main:
  sleep: 3
neptune:
  project: florian.wilhelm/my_expriments
  api_token: ~/.neptune_api_token
  tags:
  - run-1
  description: Experiment run on GCP
  mode: async
db:
  driver: postgreqsql
  host: server_string
  port: 1832
  username: me
  password: birthday
experiment:
  model: XGBoost
  l2: 0.01
  n_steps: 1000
```
And this works! So much flexibility and robustness in just 70 lines of code, awesome! While you are at it, you can also
run `hydra-test -cd configs +experiment=missing_key` and `hydra-test -cd configs +experiment=wrong_type` to see some
nice errors from pydantic telling you about a missing key and wrong type of the configuration value, respectively.
[Hydra] and [pydantic] work nicely together. Just remember to use the `dataclass` from [pydantic], not the standard library
and call `OmegaConf.to_object(cfg)` at the start of your application to fail as early as possible.

Hydra has many more, really nice features. Imagine you want to run now the experiments `exp1` and `exp2` consecutively,
you can just use the `--multirun` feature, or `-m` for short:
```shell
hydra-test -m -cd configs "+experiment=glob(exp*)"
```
There's much more to Hydra and several plugins even for hyperparameter optimization exist. Also note that with the
flag `--hydra-help`, you can see the hydra-specific parameters of your application. So now go and check it out!


### BTW, how was this example project set up?

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
