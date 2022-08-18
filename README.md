### Pradict repository active development time on GitHub

The target of this repository is to predict the active development time of a repository by analyzing the history of its development activities.

- First, it aggregates development activities such as commits, pull requests, issues, forks, and stars from GitHub.

- Second, the collected data is processed and converted into time series data

- Third, the data is trained on machine learning prediction models.

- Finally, based on the prediction, the development activity or maintenance status of the repository for a period of n is determined.

To set up the environment:

```git
 git clone
```

Then run the Makefile commands:

```makefile
make install    # to create virtual environment

make activiate  # Activating virtual environment

make setdds     # creates directories for data preprocessing
```

Then the retrieved raw repository data is stored in raw dir and the processed data is stored in processed dir. The final directory stores the prepared timesereis data.

Simply place the repository or list of repositories for which data is to be extracted from GitHub in the repos_name directory in the repos_csv file.

For retrieving the repository data:

```
pipenv run python src/fetch_repo_data.py
```

For preprocessing the data

```
pipenv run python src/preprocess_repo_data.py
```

The Machine Learing models are jupter notebooks.
