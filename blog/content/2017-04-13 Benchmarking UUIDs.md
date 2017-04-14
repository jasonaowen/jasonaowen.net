Title: Benchmarking UUIDs
Date: 2017-04-13 17:17
Modified: 2017-04-13 19:20
Tags: coding, postgresql
Category: postgresql

UPDATE: The test methodology is flawed! PostgreSQL can be faster than nodejs.
See the [follow-up article](<{filename}/2017-04-13 Benchmarking UUIDs, v2.md>).
---

Jonathan New wrote an interesting article on [UUID creation in Postgres vs
Node](http://blog.jonnew.com/posts/uuid-postgres-node). In it, he described the
performance tradeoff of generating a
[UUID](https://en.wikipedia.org/wiki/Universally_unique_identifier) in the
database vs in the application. It's not very long, go read it!

I've used PostgreSQL to generate UUIDs before, but I hadn't seen the function
`uuid_generate_v4()`. It turns out to come from the [uuid-ossp
extension](https://www.postgresql.org/docs/9.6/static/uuid-ossp.html), which
also supports other UUID generation methods. Previously, I've used the
[pgcrypto extension](https://www.postgresql.org/docs/9.6/static/pgcrypto.html),
which provides the `gen_random_uuid()` function.

How do they compare? On my machine, using the [PostgreSQL package for
Ubuntu](https://wiki.postgresql.org/wiki/Apt) (as opposed to the [Ubuntu
package for PostgreSQL](http://packages.ubuntu.com/xenial/postgresql)...), the
pgcrypto version is more than **twice as fast** than the uuid-ossp version.

How does this compare with nodejs? Using Jonathan's approach, nodejs is about
1.5 times as fast as PostgreSQL with pgcrypto!

| uuid-ossp    | pgcrypto    | nodejs      |
| ---------    | --------    | ------      |
| 10942.376 ms | 4173.924 ms | 2886.117 ms |
| 11235.807 ms | 4341.270 ms | 2822.078 ms |
| 10764.468 ms | 4265.632 ms | 2829.395 ms |

What does this mean? I argue: very little! The slowest method takes ~11 seconds
to generate one million UUIDs, and the fastest takes ~3 seconds. That's 3 - 11
microseconds per UUID! If this is the bottleneck in your application, I think
you've done a very good job of optimizing - and you might have a pretty unusual
use case.

PS: the [`RETURNING`
clause](https://www.postgresql.org/docs/9.6/static/sql-insert.html), not
mentioned in Jonathan's post, is really cool:

```postgresql-console
> CREATE TABLE example (
    example_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    number INTEGER NOT NULL
  );
CREATE TABLE
> INSERT INTO example (number)
    VALUES (1)
    RETURNING example_id;
              example_id
--------------------------------------
 045857b4-6125-4746-94b8-a2e58f342b86
(1 row)

INSERT 0 1
```

# Methodology

This was a very unscientific benchmark! I'm not controlling for other programs
running on my machine, and this is not a server, it's just a laptop.

<iframe width="560" height="315" src="https://www.youtube.com/embed/BSUMBBFjxrY" frameborder="0" allowfullscreen></iframe>

In the interest of writing things down, here's how I came up with the numbers
above.

## Environment

According to `/proc/cpuinfo`, I am running on a Intel(R) Core(TM) i7-3520M CPU
@ 2.90GHz. My operating system is Ubuntu 16.04.2.

```postgresql-console
> select version();
 PostgreSQL 9.6.2 on x86_64-pc-linux-gnu, compiled by gcc (Ubuntu 5.3.1-14ubuntu2) 5.3.1 20160413, 64-bit
```

```sh
$ nodejs --version
v6.10.2
```

## Tests

### nodejs

```sh
$ cd /tmp
$ npm install uuid
/tmp
└── uuid@3.0.1
$ nodejs
```

```js
const uuidV4 = require('uuid/v4');
test = function() {
  console.time("uuid");
  for (let i=0; i < 1000000; ++i) {
    uuidV4();
  }
  console.timeEnd("uuid");
}
test()
test()
test()
```

### pgcrypto

```postgresql
CREATE EXTENSION pgcrypto;
CREATE FUNCTION loop_gen_random_uuid() RETURNS void
  LANGUAGE plpgsql
  AS $$
BEGIN
  FOR i IN 0..1000000 LOOP
    PERFORM gen_random_uuid();
  END LOOP;
RETURN;
END;
$$;

\timing on
SELECT loop_gen_random_uuid();
SELECT loop_gen_random_uuid();
SELECT loop_gen_random_uuid();
```

### uuid-ossp

```postgresql
CREATE EXTENSION "uuid-ossp";
CREATE FUNCTION loop_uuid_generate_v4() RETURNS void
  LANGUAGE plpgsql
  AS $$
BEGIN
  FOR i IN 0..1000000 LOOP
    PERFORM uuid_generate_v4();
  END LOOP;
RETURN;
END;
$$;

\timing on
SELECT loop_uuid_generate_v4();
SELECT loop_uuid_generate_v4();
SELECT loop_uuid_generate_v4();
```

#### Background on `uuid-ossp`

The `uuid-ossp` extension
[builds](https://www.postgresql.org/docs/9.6/static/uuid-ossp.html#AEN184550)
upon some underlying library: `libc` on BSDs, `libuuid` from e2fs, or `ossp`,
the original library from which the extension takes its name. It appears that
[Postgres.app](https://postgresapp.com/) uses `libuuid`, according to [its
Makefile](https://github.com/PostgresApp/PostgresApp/blob/122a60e975368038d3fe003b09d3979888d66ea2/src/makefile#L81)
(note the `--with-uuid=e2fs`). The [PostgreSQL package for
Ubuntu](https://wiki.postgresql.org/wiki/Apt) (as opposed to the [Ubuntu
package for PostgreSQL](http://packages.ubuntu.com/xenial/postgresql)...) uses
the same library:

```sh
$ ldd /usr/lib/postgresql/9.6/lib/uuid-ossp.so | grep uuid
	libuuid.so.1 => /lib/x86_64-linux-gnu/libuuid.so.1 (0x00007fa4de773000)
```

So, I think Jonathan and I are using the same underlying library, and while we
have different machines, I think this is a reasonably apples-to-apples
comparison.
