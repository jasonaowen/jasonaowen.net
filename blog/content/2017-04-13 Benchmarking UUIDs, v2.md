Title: Benchmarking UUIDs, v2
Date: 2017-04-13 19:20
Tags: coding, postgresql
Category: postgresql

# Correction

Shortly after I published [Benchmarking UUIDs](<{filename}/2017-04-13
Benchmarking UUIDs.md>), someone emailed me with a correction. It turns out the
approach Jonathan and I used to time how long PostgreSQL takes to generate a
million UUIDs is mostly timing how long it takes to generate a million queries:

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

When we take this insight and applying it to the two UUID generator functions,
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

On my machine, I see a big difference, more than 5x:

| uuid_generate_v4 | gen_random_uuid |
| ---------------- | --------------- |
| 6484.110 ms      | 1166.969 ms     |
| 6451.433 ms      | 1169.010 ms     |
| 6285.573 ms      | 1161.001 ms     |

Interestingly, on another machine, the two functions were approximately equally
fast, with `uuid_generate_v4` slightly edging out `gen_random_uuid`.

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

Many thanks to my anonymous contributor! I'll update this article to credit
them if they like.
