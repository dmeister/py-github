#!/usr/bin/env python
#
# Copyright (c) 2005-2008  Dustin Sallings <dustin@spy.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# <http://www.opensource.org/licenses/mit-license.php>
"""
Defines and runs unittests.
"""

import unittest

import github

class BaseCase(unittest.TestCase):

    def _gh(self, expUrl, filename):

        def opener(url):
            self.assertEquals(expUrl, url)
            return open(filename)
        return github.GitHub(fetcher=opener)

    def _agh(self, expUrl, u, t, filename):

        def opener(url):
            self.assertEquals(expUrl, url + '?login=' + u + '&token=' + t)
            return open(filename)
        return github.GitHub(fetcher=opener)

class UserTest(BaseCase):

    def __loadUserSearch(self):
        return self._gh('http://github.com/api/v2/xml/user/search/dustin',
            'data/user.search.xml').users.search('dustin')

    def __loadUser(self, which, u=None, p=None):
        if u:
            return self._agh('http://github.com/api/v2/xml/user/show/dustin'
                              + '?login=' + u + '&token=' + p,
                              u, p, 'data/' + which).users.show('dustin')

        else:
            return self._gh('http://github.com/api/v2/xml/user/show/dustin',
                             'data/' + which).users.show('dustin')

    def testUserSearch(self):
        """Test the base properties of the user object."""
        u = self.__loadUserSearch()[0]
        self.assertEquals("Dustin Sallings", u.fullname)
        self.assertEquals("dustin", u.name)
        self.assertEquals("dustin@spy.net", u.email)
        self.assertEquals("Santa Clara, CA", u.location)
        self.assertEquals("Ruby", u.language)
        self.assertEquals(35, u.actions)
        self.assertEquals(77, u.repos)
        self.assertEquals(78, u.followers)
        self.assertEquals('user-1779', u.id)
        self.assertAlmostEquals(12.231684, u.score)
        self.assertEquals('user', u.type)
        self.assertEquals('2008-02-29T17:59:09Z', u.created)
        self.assertEquals('2009-03-19T09:15:24.663Z', u.pushed)
        self.assertEquals("<<User dustin>>", repr(u))

    def testUserPublic(self):
        """Test the user show API with no authentication."""
        u = self.__loadUser('user.public.xml')
        self.assertEquals("Dustin Sallings", u.name)
        # self.assertEquals(None, u.company)
        self.assertEquals(10, u.following_count)
        self.assertEquals(21, u.public_gist_count)
        self.assertEquals(81, u.public_repo_count)
        self.assertEquals('http://bleu.west.spy.net/~dustin/', u.blog)
        self.assertEquals(1779, u.id)
        self.assertEquals(82, u.followers_count)
        self.assertEquals('dustin', u.login)
        self.assertEquals('Santa Clara, CA', u.location)
        self.assertEquals('dustin@spy.net', u.email)
        self.assertEquals('2008-02-29T09:59:09-08:00', u.created_at)

    def testUserPrivate(self):
        """Test the user show API with extra info from auth."""
        u = self.__loadUser('user.private.xml', 'dustin', 'blahblah')
        self.assertEquals("Dustin Sallings", u.name)
        # self.assertEquals(None, u.company)
        self.assertEquals(10, u.following_count)
        self.assertEquals(21, u.public_gist_count)
        self.assertEquals(81, u.public_repo_count)
        self.assertEquals('http://bleu.west.spy.net/~dustin/', u.blog)
        self.assertEquals(1779, u.id)
        self.assertEquals(82, u.followers_count)
        self.assertEquals('dustin', u.login)
        self.assertEquals('Santa Clara, CA', u.location)
        self.assertEquals('dustin@spy.net', u.email)
        self.assertEquals('2008-02-29T09:59:09-08:00', u.created_at)

        # Begin private data

        self.assertEquals("micro", u.plan.name)
        self.assertEquals(1, u.plan.collaborators)
        self.assertEquals(614400, u.plan.space)
        self.assertEquals(5, u.plan.private_repos)
        self.assertEquals(155191, u.disk_usage)
        self.assertEquals(6, u.collaborators)
        self.assertEquals(4, u.owned_private_repo_count)
        self.assertEquals(5, u.total_private_repo_count)
        self.assertEquals(0, u.private_gist_count)

    def testKeysList(self):
        """Test key listing."""
        kl = self._agh('http://github.com/api/v2/xml/user/keys?login=dustin&token=blahblah',
                       'dustin', 'blahblah', 'data/keys.xml').users.keys()
        self.assertEquals(7, len(kl))
        k = kl[0]

        self.assertEquals('some key', k.title)
        self.assertEquals(2181, k.id)
        self.assertEquals(549, k.key.find('cdEXwCSjAIFp8iRqh3GOkxGyFSc25qv/MuOBg=='))

class RepoTest(BaseCase):

    def __loadUserRepos(self):
        return self._gh('http://github.com/api/v2/xml/repos/show/verbal',
            'data/repos.xml').repos.forUser('verbal')

    def testUserRepoList(self):
        """Get a list of repos for a user."""
        rs = self.__loadUserRepos()
        self.assertEquals(10, len(rs))
        r = rs[0]
        self.assertEquals('A beanstalk client for the twisted network framework.',
                          r.description)
        self.assertEquals(2, r.watchers)
        self.assertEquals(0, r.forks)
        self.assertEquals('beanstalk-client-twisted', r.name)
        self.assertEquals(False, r.private)
        self.assertEquals('http://github.com/verbal/beanstalk-client-twisted',
                          r.url)
        self.assertEquals(True, r.fork)
        self.assertEquals('verbal', r.owner)
        # XXX:  Can't parse empty elements.  :(
        # self.assertEquals('', r.homepage)

    def testBranchList(self):
        """Test branch listing for a repo."""
        bl = self._gh('http://github.com/api/v2/xml/repos/show/schacon/ruby-git/branches',
                      'data/repos.branches.xml').repos.branches('schacon', 'ruby-git')
        self.assertEquals(4, len(bl))
        self.assertEquals('ee90922f3da3f67ef19853a0759c1d09860fe3b3', bl['master'])

class CommitTest(BaseCase):

    def testCommitList(self):
        """Test commit list."""
        cl = self._gh('http://github.com/api/v2/xml/commits/list/mojombo/grit/master',
                      'data/commits.xml').commits.forBranch('mojombo', 'grit')
        self.assertEquals(30, len(cl))

        c = cl[0]
        self.assertEquals("Regenerated gemspec for version 1.1.1", c.message)
        self.assertEquals('4ac4acab7fd9c7fd4c0e0f4ff5794b0347baecde', c.id)
        self.assertEquals('94490563ebaf733cbb3de4ad659eb58178c2e574', c.tree)
        self.assertEquals('2009-03-31T09:54:51-07:00', c.committed_date)
        self.assertEquals('2009-03-31T09:54:51-07:00', c.authored_date)
        self.assertEquals('http://github.com/mojombo/grit/commit/4ac4acab7fd9c7fd4c0e0f4ff5794b0347baecde',
                          c.url)
        self.assertEquals(1, len(c.parents))
        self.assertEquals('5071bf9fbfb81778c456d62e111440fdc776f76c', c.parents[0].id)
        self.assertEquals('Tom Preston-Werner', c.author.name)
        self.assertEquals('tom@mojombo.com', c.author.email)
        self.assertEquals('Tom Preston-Werner', c.committer.name)
        self.assertEquals('tom@mojombo.com', c.committer.email)

    def testCommitListForFile(self):
        """Test commit list for a file."""
        cl = self._gh('http://github.com/api/v2/xml/commits/list/mojombo/grit/master/grit.gemspec',
                      'data/commits.xml').commits.forFile('mojombo', 'grit', 'grit.gemspec')
        self.assertEquals(30, len(cl))

        c = cl[0]
        self.assertEquals("Regenerated gemspec for version 1.1.1", c.message)
        self.assertEquals('4ac4acab7fd9c7fd4c0e0f4ff5794b0347baecde', c.id)
        self.assertEquals('94490563ebaf733cbb3de4ad659eb58178c2e574', c.tree)
        self.assertEquals('2009-03-31T09:54:51-07:00', c.committed_date)
        self.assertEquals('2009-03-31T09:54:51-07:00', c.authored_date)
        self.assertEquals('http://github.com/mojombo/grit/commit/4ac4acab7fd9c7fd4c0e0f4ff5794b0347baecde',
                          c.url)
        self.assertEquals(1, len(c.parents))
        self.assertEquals('5071bf9fbfb81778c456d62e111440fdc776f76c', c.parents[0].id)
        self.assertEquals('Tom Preston-Werner', c.author.name)
        self.assertEquals('tom@mojombo.com', c.author.email)
        self.assertEquals('Tom Preston-Werner', c.committer.name)
        self.assertEquals('tom@mojombo.com', c.committer.email)

class IssueTest(BaseCase):

    def testListIssues(self):
        """Test listing issues."""
        il = self._gh('http://github.com/api/v2/xml/issues/list/schacon/simplegit/open',
                      'data/issues.list.xml').issues.list('schacon', 'simplegit')
        self.assertEquals(1, len(il))
        i = il[0]

        self.assertEquals('schacon', i.user)
        self.assertEquals('2009-04-17T16:19:02-07:00', i.updated_at)
        self.assertEquals('something', i.body)
        self.assertEquals('new', i.title)
        self.assertEquals(2, i.number)
        self.assertEquals(0, i.votes)
        self.assertEquals(1.0, i.position)
        self.assertEquals('2009-04-17T16:18:50-07:00', i.created_at)
        self.assertEquals('open', i.state)


if __name__ == '__main__':
    unittest.main()
