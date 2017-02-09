Title: AWS PostgreSQL RDS Passwords
Date: 2017-02-09
Tags: coding, postgresql
Category: postgresql

In order to set a strong password for the PostgreSQL database I provisioned on
Amazon RDS, I looked up the limits. In my case, there are two sources of
constraints:

1. [Amazon RDS
limits](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Limits.html)
    - Must contain 8 to 128 characters
    - The password for the master database user can be any printable ASCII
      character except `/`, `` ` ``, or `@`.
2. Characters allowed in Amazon Lambda environment variables
    - Member must satisfy regular expression pattern: `[^,]*` (I cannot find
      documentation for this, except the error message when you try to save a
      value that has a comma in it.)

We can generate a password that meets these restrictions with
[makepasswd(1)](https://tracker.debian.org/pkg/makepasswd):

```sh
$ makepasswd --chars=128 \ --string
  'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789`~!#$%^&*()-_=+[]{}\|;:<>.?'\'
```

Note the `'\'` at the end: that means "close the single-quoted string, and
append an escaped single-quote."

You can then save this to your
[`~/.pgpass`](https://www.postgresql.org/docs/current/static/libpq-pgpass.html)
file, being sure to escape `\` and `:` characters:

```sh
$ sed -e 's/\\/\\\\/g;s/:/\\:/g'
```
