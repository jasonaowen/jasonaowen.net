Title: Setting up PostgreSQL on Debian
Date: 2017-07-29
Tags: postgresql
Category: postgresql

From time to time I need to set up PostgreSQL on a Debian machine. It's fairly
straightforward, but I frequently need to look something up, so this time I am
writing down my notes.

[Debian packages PostgreSQL](https://packages.debian.org/stretch/postgresql),
and if you don't care about what version of PostgreSQL you use that's the
easiest way. If you do care about what version, [the PostgreSQL project
packages all the supported versions of
PostgreSQL](https://www.postgresql.org/download/linux/debian/) - this allows
you to install old (supported) versions, and will allow you to easily install
PostgreSQL 10 once it is released. The PostgreSQL Debian page includes
instructions on how to add their apt repository.

Whether you're installing the Debian-packaged or PostgreSQL-packaged server,
installation of the current version of the server is the same:

```ShellSession
$ sudo apt install postgresql-9.6
```

This will install the server and the client, and create and start a cluster.

The default, installer-created cluster does not have [data
checksums](http://paquier.xyz/postgresql-2/postgres-9-3-feature-highlight-data-checksums/)
enabled. Data checksums trade performance for safety; since I am not using
PostgreSQL in a particularly performance-sensitive environment, I would prefer
safety. To enable data checksums, we will need to recreate the cluster.

Additionally, I prefer to have PostgreSQL store its data files in
`/srv/postgresql` instead of `/var/lib/postgresql/`. Since we're recreating the
cluster anyway, we don't need to move any files, and can instead simply specify
the new location at creation time.

First, drop the old cluster:

```ShellSession
$ sudo -u postgres pg_dropcluster --stop 9.6 main
```

Then, create the new cluster:

```ShellSession
$ sudo -u postgres pg_createcluster \
    --datadir=/srv/postgresql/9.6/main \
    --start \
    9.6 \
    main \
    -- \
    --data-checksums
```

Note the version and cluster name in the data directory argument. Debian
contributors have created wrapper scripts (like `pg_createcluster`) to allow
multiple versions and multiple instances of PostgreSQL to run on the same
system side-by-side; including the version and cluster name in the path support
that.

You can check that data checksums are enabled by running this query in a psql
session:

```
$ sudo -u postgres psql
postgres=# show data_checksums;
 data_checksums
----------------
 on
(1 row)
```

Once you've created a cluster, you'll probably want a user and a database:

```ShellSession
$ sudo -u postgres createuser ${USER}
$ sudo -u postgres createdb --owner=${USER} ${USER}
```

Now you should be able to log in with `psql`!
