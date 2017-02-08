Title: Variable names in PostgreSQL stored procedures
Date: 2017-02-08
Tags: coding, postgresql
Category: postgresql

I am building a web application that delegates authentication to a third party.
Once the third party authenticates the user, the app create a session for the
user - and maybe create the user, too, if they don't already exist!

My first draft of this had all the SQL queries in the code. The logic is
something like:

```
does user exist?
  yes: create session
  no: create user, then create session
```

I wasn't very happy with the code, for a couple of reasons. First, the SQL
queries were rather ugly string constants. Multi-line strings aren't really
great in any language, and embedding SQL in another language's source file
makes it harder for editors to do syntax highlighting. Second, handling errors
and encoding the (fairly simple) logic above was obscuring my intent.

[Stored procedures](https://en.wikipedia.org/wiki/Stored_procedure) are a way
to keep database logic in the database. Among other benefits, this can
dramatically simplify the calling code.

I ended up with a function like the following:

```PLpgSQL
CREATE FUNCTION create_session(
  external_user_id bigint,
  external_user_name text,
  OUT session_id uuid,
  OUT session_expiration TIMESTAMP WITH TIME ZONE
) AS $$
DECLARE
  existing_user_id INTEGER;
  new_user_id INTEGER;
BEGIN
  SELECT INTO existing_user_id user_id
    FROM users_external
    WHERE users_external.external_user_id = external_user_id;

  IF existing_user_id IS NULL THEN
    INSERT INTO users_external (external_user_id, external_user_name)
      VALUES (external_user_id, external_user_name)
      RETURNING user_id
      INTO new_user_id;
    INSERT INTO sessions (user_id)
      VALUES (new_user_id)
      RETURNING session_id, session_expiration
      INTO session_id, session_expiration;
  ELSE
    INSERT INTO sessions (user_id)
      VALUES (existing_user_id)
      RETURNING session_id, expires
      INTO session_id, session_expiration;
  END IF;
END;
$$ LANGUAGE plpgsql;
```

This is a syntactically correct function and will be accepted by PostgreSQL,
but fails at runtime:

```SQL
> select * from create_session(12345, 'example');
ERROR:  column reference "external_user_id" is ambiguous
LINE 3:     WHERE users_external.external_user_id = external_user_id
                                                    ^
DETAIL:  It could refer to either a PL/pgSQL variable or a table column.
QUERY:  SELECT                       user_id
    FROM users_external
    WHERE users_external.external_user_id = external_user_id
CONTEXT:  PL/pgSQL function create_session(bigint,text) line 6 at SQL statement
```

# How do you disambiguate a parameter from a column name?

There is some useful documentation about [how variable substitution works in
PL/pgSQL](https://www.postgresql.org/docs/current/static/plpgsql-implementation.html).
In particular, it mentions that you can disambiguate column names from variable
names by labelling the declaring block:

```SQL
<<block>>
DECLARE
    foo int;
BEGIN
    foo := ...;
    INSERT INTO dest (col) SELECT block.foo + bar FROM src;
```

This is tangentially related, but it does not cover the issue I was having.
However, it links to [Structure of
PL/pgSQL](https://www.postgresql.org/docs/current/static/plpgsql-structure.html),
which includes a note near the bottom:

> There is actually a hidden "outer block" surrounding the body of any PL/pgSQL
> function. This block provides the declarations of the function's parameters
> (if any), as well as some special variables such as FOUND (see Section
> 41.5.5). The outer block is labeled with the function's name, meaning that
> parameters and special variables can be qualified with the function's name.

That was the key piece I was missing! **You can disambiguate a parameter from a
column by prefixing the parameter with the function name.** Here's what we
needed to change to get the example to work:

```diff
@@ -13 +13 @@
-    WHERE users_external.external_user_id = external_user_id;
+    WHERE users_external.external_user_id = create_session.external_user_id;
@@ -17 +17,4 @@
-      VALUES (external_user_id, external_user_name)
+      VALUES (
+        create_session.external_user_id,
+        create_session.external_user_name
+      )
@@ -22,2 +25,4 @@
-      RETURNING session_id, session_expiration
-      INTO session_id, session_expiration;
+      RETURNING sessions.session_id,
+                sessions.session_expiration
+      INTO create_session.session_id,
+           create_session.session_expiration;
@@ -27,2 +32,4 @@
-      RETURNING session_id, expires
-      INTO session_id, session_expiration;
+      RETURNING sessions.session_id,
+                sessions.session_expiration
+      INTO create_session.session_id,
+           create_session.session_expiration;
```

This simplifies the calling code to a single query!

```SQL
> SELECT * FROM create_session(12345, 'example');
              session_id              |      session_expiration
--------------------------------------+-------------------------------
 7be20fa5-63ec-4937-8a02-3417df54571b | 2017-02-15 18:44:29.653136-05
(1 row)
```

- - -

Here's the schema I'm using for this example:

```SQL
CREATE TABLE users_external(
  user_id SERIAL PRIMARY KEY,
  external_user_id BIGINT NOT NULL,
  external_user_name TEXT NOT NULL
);
CREATE TABLE sessions(
  session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id INTEGER NOT NULL REFERENCES users_external (user_id),
  session_expiration TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW() + '1 week'
);
```

And the complete, rewritten, working stored procedure:

```PLpgSQL
CREATE FUNCTION create_session(
  external_user_id bigint,
  external_user_name text,
  OUT session_id uuid,
  OUT session_expiration TIMESTAMP WITH TIME ZONE
) AS $$
DECLARE
  existing_user_id INTEGER;
  new_user_id INTEGER;
BEGIN
  SELECT INTO existing_user_id user_id
    FROM users_external
    WHERE users_external.external_user_id = create_session.external_user_id;

  IF existing_user_id IS NULL THEN
    INSERT INTO users_external (external_user_id, external_user_name)
      VALUES (
        create_session.external_user_id,
        create_session.external_user_name
      )
      RETURNING user_id
      INTO new_user_id;
    INSERT INTO sessions (user_id)
      VALUES (new_user_id)
      RETURNING sessions.session_id,
                sessions.session_expiration
      INTO create_session.session_id,
           create_session.session_expiration;
  ELSE
    INSERT INTO sessions (user_id)
      VALUES (existing_user_id)
      RETURNING sessions.session_id,
                sessions.session_expiration
      INTO create_session.session_id,
           create_session.session_expiration;
  END IF;
END;
$$ LANGUAGE plpgsql;
```
