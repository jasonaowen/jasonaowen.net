Title: Benchmarking UUIDs, v2
Date: 2017-04-13T19:20-04:00
Modified: 2017-04-14T10:15-04:00
Tags: coding, postgresql
Category: postgresql

# Correction

Shortly after I published [Benchmarking
UUIDs](<{filename}/2017-04-13 Benchmarking UUIDs.md>), Per Wigren emailed me
with a correction. It turns out the approach Jonathan and I used to time how
long PostgreSQL takes to generate a million UUIDs is mostly timing how long it
takes to generate a million queries:

```postgresql
DO $$
BEGIN
  FOR i IN 0..1000000 LOOP
    PERFORM 1;
  END LOOP;
RETURN;
END;
$$;
```

They pointed out a better way to test:

```postgresql
SELECT COUNT(*)
FROM (
  SELECT 1 FROM generate_series(1, 1000000)
) AS x;
```

This results in a roughly order-of-magnitude difference in test times, just in
overhead.

When we take this insight and apply it to the two UUID generator functions,
we find that PostgreSQL is faster at this task than nodejs:

```postgresql
SELECT COUNT(*)
FROM (
  SELECT uuid_generate_v4() FROM generate_series(1, 1000000)
) AS x;
```
```postgresql
SELECT COUNT(*)
FROM (
  SELECT gen_random_uuid() FROM generate_series(1, 1000000)
) AS x;
```

On my machine, I see a big difference between the two functions, more than 5x:

| uuid_generate_v4 (uuid-ossp) | gen_random_uuid (pgcrypto) | nodejs      |
| ---------------------------- | -------------------------- | ------      |
| 6484.110 ms                  | 1166.969 ms                | 2886.117 ms |
| 6451.433 ms                  | 1169.010 ms                | 2822.078 ms |
| 6285.573 ms                  | 1161.001 ms                | 2829.395 ms |

Interestingly, on Per Wigren's machine, running macOS Sierra with PostgreSQL
9.6.2 installed from Homebrew, the two functions were approximately equally
fast, with `uuid_generate_v4` slightly edging out `gen_random_uuid`. Both were
faster than the nodejs version.

# Conclusion

- Writing benchmarks is tricky!
- Using this updated methodology, on my machine, PostgreSQL with pgcrypto is
  faster at generating UUIDs than nodejs, which in turn is faster than
  PostgreSQL with uuid-ossp.

Thankfully, I don't think the flaw in my original measurements undermines the
conclusion I drew: the difference between these methods is vanishingly small,
and the likelihood that generating UUIDs is the bottleneck in your system is
low. Better to focus your optimization efforts elsewhere!

---

*Many thanks to Per Wigren for the feedback!*

2017-04-14: Updated to credit Per Wigren and clarify the table of new
measurements by adding the extension to the title of the columns and including
the nodejs measurements from the previous post.
