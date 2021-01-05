Title: Monitoring GPG Key Expiration
Date: 2021-01-04
Tags: coding, work
Category: coding

When I learned how to use the [GNU Privacy Guard](https://gnupg.org/),
I was taught to set an expiration date on my key.
The manual
[suggests this](https://www.gnupg.org/gph/en/manual/c481.html#AEN519):

> if you lose control of the key and do not have a revocation certificate with
> which to revoke the key, having an expiration date on the master key ensures
> that the key will eventually fall into disuse

There are no permanent consequences to letting a key expire;
if you still control the key,
you can change the expiration date and publish it as normal.
However, there is one rather direct consequences:
other users encrypting to you will get an error, as intended.
This includes any tools that depend on GPG, such as
[`pass(1)`](https://www.passwordstore.org/)
or
[`duplicity(1)`](http://duplicity.nongnu.org/).

It's better not to allow your key to expire.

There are a variety of scripts people have written in a variety of contexts
to solve this basic problem.
There are two requirements that I had, though, and my brief search didn't
turn up any that met both:

1. clearly licensed
2. easy to specify the expiration threshold

I would also prefer something I can read and understand;
many of the scripts I found use the machine-parsable output of the
`gpg(1)` command line tool, which leads to some impressive but impenetrable
shell pipes.

Instead, I made my own:
[gpg-expiration](https://github.com/jasonaowen/gpg-expiration).
It is licensed under the GPLv3, and is (I hope) fairly readable Python.
It is intended to be run as a cron job; it is silent on success,
and prints some useful information on failure:

```
$ ./gpg-expiration.py --days 100 jasonaowen
$ echo $?
0

$ ./gpg-expiration.py --days 1000 jasonaowen
Jason Owen <jason@jasonaowen.net> will expire before 2023-10-01 18:09:55.894062:
  2B38BD955557647E7C26B53C19E27469767CFC68 expires at 2022-01-04 13:23:32
  B41F874786836B92CCC30D1E87AF208B3BA28925 expires at 2022-01-04 13:24:07
  5A466EE6DA264910588578D2BB90600F9D11F1A4 expires at 2022-01-04 13:24:07
  BDD790654C9560DF26E18FFD903C59EC50568825 expires at 2022-01-04 13:24:07
$ echo $?
1
```

Set it up as a cron job and be reminded before your key expires!
