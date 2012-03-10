# Github Recommendation Engine

A single Python script which queries the Github API
to return a list of repositories you might be interested
in following.

## Usage

First, make sure you've entered your Github API token in
your global git config. Then:

    $ pip install git+https://modocache@github.com/modocache/github-recommendation-engine.git
    $ github-recommendation-engine
    ... Wait a long time ...
    ['<Repository: modocache/github-recommendation-engine>', ...]

## Limitations

Github limits calls to the API to 60 per minute. In order to
attain relevant data on users and repositories you might be
interested in, this program queries the API quite a lot, taking
a breather whenever Github returns an API Rate Exceeded error.
If you follow a lot of repos, the program might take a considerable
amount of time to produce a result.

You might be wondering whether Github would appreciate so many
requests being thrown at it--I wonder as well, and I plan on
getting some feedback from an admin once I get a chance.

## Requirements

- [github2](https://github.com/ask/python-github2), a Python wrapper for the Github API
