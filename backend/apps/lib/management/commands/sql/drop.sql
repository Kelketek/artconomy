-- Copyright © 2019, 2020
--      mirabilos <t.glaser@tarent.de>
--
-- Provided that these terms and disclaimer and all copyright notices
-- are retained or reproduced in an accompanying document, permission
-- is granted to deal in this work without restriction, including un‐
-- limited rights to use, publicly perform, distribute, sell, modify,
-- merge, give away, or sublicence.
--
-- This work is provided “AS IS” and WITHOUT WARRANTY of any kind, to
-- the utmost extent permitted by applicable law, neither express nor
-- implied; without malicious intent or gross negligence. In no event
-- may a licensor, author or contributor be held liable for indirect,
-- direct, other damage, loss, or other issues arising in any way out
-- of dealing in the work, even if advised of the possibility of such
-- damage or existence of a defect, except proven that it results out
-- of said person’s immediate fault when using the work as intended.
-- -
-- Drop everything from the PostgreSQL database.

DO $$
    DECLARE
        q TEXT;
        r RECORD;
    BEGIN
        -- triggers
        FOR r IN (SELECT pns.nspname, pc.relname, pt.tgname
                  FROM pg_catalog.pg_trigger pt, pg_catalog.pg_class pc, pg_catalog.pg_namespace pns
                  WHERE pns.oid=pc.relnamespace AND pc.oid=pt.tgrelid
                    AND pns.nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                    AND pt.tgisinternal=false
        ) LOOP
                EXECUTE format('DROP TRIGGER %I ON %I.%I;',
                               r.tgname, r.nspname, r.relname);
            END LOOP;
        -- constraints #1: foreign key
        FOR r IN (SELECT pns.nspname, pc.relname, pcon.conname
                  FROM pg_catalog.pg_constraint pcon, pg_catalog.pg_class pc, pg_catalog.pg_namespace pns
                  WHERE pns.oid=pc.relnamespace AND pc.oid=pcon.conrelid
                    AND pns.nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                    AND pcon.contype='f'
        ) LOOP
                EXECUTE format('ALTER TABLE ONLY %I.%I DROP CONSTRAINT %I;',
                               r.nspname, r.relname, r.conname);
            END LOOP;
        -- constraints #2: the rest
        FOR r IN (SELECT pns.nspname, pc.relname, pcon.conname
                  FROM pg_catalog.pg_constraint pcon, pg_catalog.pg_class pc, pg_catalog.pg_namespace pns
                  WHERE pns.oid=pc.relnamespace AND pc.oid=pcon.conrelid
                    AND pns.nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                    AND pcon.contype<>'f'
        ) LOOP
                EXECUTE format('ALTER TABLE ONLY %I.%I DROP CONSTRAINT %I;',
                               r.nspname, r.relname, r.conname);
            END LOOP;
        -- indicēs
        FOR r IN (SELECT pns.nspname, pc.relname
                  FROM pg_catalog.pg_class pc, pg_catalog.pg_namespace pns
                  WHERE pns.oid=pc.relnamespace
                    AND pns.nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                    AND pc.relkind='i'
        ) LOOP
                EXECUTE format('DROP INDEX %I.%I;',
                               r.nspname, r.relname);
            END LOOP;
        -- normal and materialised views
        FOR r IN (SELECT pns.nspname, pc.relname
                  FROM pg_catalog.pg_class pc, pg_catalog.pg_namespace pns
                  WHERE pns.oid=pc.relnamespace
                    AND pns.nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                    AND pc.relkind IN ('v', 'm')
        ) LOOP
                EXECUTE format('DROP VIEW %I.%I;',
                               r.nspname, r.relname);
            END LOOP;
        -- tables
        FOR r IN (SELECT pns.nspname, pc.relname
                  FROM pg_catalog.pg_class pc, pg_catalog.pg_namespace pns
                  WHERE pns.oid=pc.relnamespace
                    AND pns.nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                    AND pc.relkind='r'
        ) LOOP
                EXECUTE format('DROP TABLE %I.%I;',
                               r.nspname, r.relname);
            END LOOP;
        -- sequences
        FOR r IN (SELECT pns.nspname, pc.relname
                  FROM pg_catalog.pg_class pc, pg_catalog.pg_namespace pns
                  WHERE pns.oid=pc.relnamespace
                    AND pns.nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                    AND pc.relkind='S'
        ) LOOP
                EXECUTE format('DROP SEQUENCE %I.%I;',
                               r.nspname, r.relname);
            END LOOP;
        -- extensions (only if necessary; keep them normally)
        FOR r IN (SELECT pns.nspname, pe.extname
                  FROM pg_catalog.pg_extension pe, pg_catalog.pg_namespace pns
                  WHERE pns.oid=pe.extnamespace
                    AND pns.nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
        ) LOOP
                EXECUTE format('DROP EXTENSION %I;', r.extname);
            END LOOP;
        -- aggregate functions first (because they depend on other functions)
        FOR r IN (SELECT pns.nspname, pp.proname, pp.oid
                  FROM pg_catalog.pg_proc pp, pg_catalog.pg_namespace pns, pg_catalog.pg_aggregate pagg
                  WHERE pns.oid=pp.pronamespace
                    AND pns.nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                    AND pagg.aggfnoid=pp.oid
        ) LOOP
                EXECUTE format('DROP AGGREGATE %I.%I(%s);',
                               r.nspname, r.proname,
                               pg_get_function_identity_arguments(r.oid));
            END LOOP;
        -- routines (functions, aggregate functions, procedures, window functions)
        IF EXISTS (SELECT * FROM pg_catalog.pg_attribute
                   WHERE attrelid='pg_catalog.pg_proc'::regclass
                     AND attname='prokind' -- PostgreSQL 11+
            ) THEN
            q := 'CASE pp.prokind
                        WHEN ''p'' THEN ''PROCEDURE''
                        WHEN ''a'' THEN ''AGGREGATE''
                        ELSE ''FUNCTION''
                    END';
        ELSIF EXISTS (SELECT * FROM pg_catalog.pg_attribute
                      WHERE attrelid='pg_catalog.pg_proc'::regclass
                        AND attname='proisagg' -- PostgreSQL ≤10
            ) THEN
            q := 'CASE pp.proisagg
                        WHEN true THEN ''AGGREGATE''
                        ELSE ''FUNCTION''
                    END';
        ELSE
            q := '''FUNCTION''';
        END IF;
        FOR r IN EXECUTE 'SELECT pns.nspname, pp.proname, pp.oid, ' || q || ' AS pt
                FROM pg_catalog.pg_proc pp, pg_catalog.pg_namespace pns
                WHERE pns.oid=pp.pronamespace
                    AND pns.nspname NOT IN (''information_schema'', ''pg_catalog'', ''pg_toast'')
            ' LOOP
                EXECUTE format('DROP %s %I.%I(%s);', r.pt,
                               r.nspname, r.proname,
                               pg_get_function_identity_arguments(r.oid));
            END LOOP;
        -- nōn-default schemata we own; assume to be run by a not-superuser
        FOR r IN (SELECT pns.nspname
                  FROM pg_catalog.pg_namespace pns, pg_catalog.pg_roles pr
                  WHERE pr.oid=pns.nspowner
                    AND pns.nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast', 'public')
                    AND pr.rolname=current_user
        ) LOOP
                EXECUTE format('DROP SCHEMA %I;', r.nspname);
            END LOOP;
        -- voilà
        RAISE NOTICE 'Database cleared!';
    END; $$;
