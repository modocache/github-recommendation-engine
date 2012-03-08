#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import print_function
from collections import defaultdict
from contextlib import contextmanager
import operator
import time

import github2
from github2.client import Github
from subprocess import Popen, PIPE


API_RATE_OVER_MSG = 'API Rate Limit Exceeded'
SLEEP_INTERVAL = 65


@contextmanager
def api_limiter(func, *args, **kwargs):
    """
    Pace requests to Github API.
    If request exceeds API limit, wait a brief period of time.

    :param function func: Function to perform
    :param list args: Positional arguments for function
    :param dict kwargs: Keyword arguments for function
    """
    attempts = 3
    for attempt_count in range(attempts):
        try:
            yield func(*args, **kwargs)
            break
        except github2.request.HttpError as e:
            if attempt_count == attempts-1:
                raise
            if e.code == 403 and API_RATE_OVER_MSG in str(e.content):
                print('{0}: Too many API calls, '
                      'taking a break...'.format(api_limiter.__name__))
                time.sleep(SLEEP_INTERVAL)
                print('{0}: Phew! Back to work.'.format(api_limiter.__name__))


def sort_dict(d):
    """
    Sort a dictionary of ints and return keys
    in descending order of magnitude.

    :param dict d: The dictionary to sort
    """
    sorted_dict = sorted(d.iteritems(), key=operator.itemgetter(1))
    sorted_dict.reverse()
    return [k for (k, v) in sorted_dict]


class RecommendationEngine(object):
    # Cache API calls
    _my_watched = None
    _watching_my_watched = None
    _similar_users = None
    _recommended_repos = None

    def __init__(self, username=None, api_user=None, api_token=None):
        """
        A recommendation engine which polls the Github API
        to find users with similar interests in repositories.
        """
        self.api_user = api_user or \
            self.git_config_get('github.user') or \
            self.git_config_get('user.name')
        self.api_token = api_token or self.git_config_get('github.token')
        self.username = username or self.api_user
        self.client = Github(self.api_user, self.api_token)
        self.sleep_interval = 65

    def __repr__(self):
        return "<{0}:{1}>".format(self.__class__, id(self))
    __str__ = __repr__

    def git_config_get(self, key):
        """
        Return a value for the corresponding key in the
        user's git config.

        :param str key: The git config value key
        """
        pipe = Popen(['git', 'config', '--get', key], stdout=PIPE)
        return pipe.communicate()[0].strip()

    @property
    def my_watched(self):
        """
        Return a list of repositories watched by current user.
        """
        if self._my_watched is None:
            with api_limiter(self.client.repos.watching, self.api_user) \
              as watched:
                self._my_watched = watched
        return self._my_watched

    def get_watching_my_watched(self):
        """
        Return a list of users also watching repositories
        watched by current user.
        """
        if self._watching_my_watched is None:
            ret = []
            for repo in self.my_watched:
                with api_limiter(self.client.repos.watchers,
                  '{0}/{1}'.format(repo.owner, repo.name)) as watchers:
                    ret.extend(watchers)
            ret = set(ret)
            ret.remove(self.api_user)
            self._watching_my_watched = ret
        return list(self._watching_my_watched)

    def get_similar_users(self, limit_api_calls=200, limit_top_users=10):
        """
        Return a sorted list of users whose followed repositories
        overlap with current user.

        :param int limit_api_calls: Maximum number of API calls to make
        :param int limit_users: Number of users to return
        """
        if self._similar_users is None:
            u = defaultdict(int)
            api_calls = 0
            for user in self.get_watching_my_watched():
                with api_limiter(self.client.repos.watching, user) as watched:
                    u[user] += sum(
                        [repo for repo in watched if repo in self.my_watched]
                    )
                    api_calls += 1
                    if api_calls >= limit_api_calls:
                        break
            self._similar_users = sort_dict(u)
        return self._similar_users[:limit_top_users]

    def get_recommended_repos(self, limit=10):
        """
        Return a list of repositories followed by related users,
        sorted by their popularity within the group.
        """
        if self._recommended_repos is None:
            r = defaultdict(int)
            for user in self.get_similar_users():
                with api_limiter(self.client.repos.watching, user) as watched:
                    for repo in watched:
                        r[repo] += 1
            self._recommended_repos = sort_dict(r)
        return self._recommended_repos[:limit]


def main():
    r = RecommendationEngine()
    print(r.get_recommended_repos())


if __name__ == '__main__':
    main()
