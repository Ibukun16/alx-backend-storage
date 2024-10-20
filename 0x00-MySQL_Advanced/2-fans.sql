-- A script that ranks country origins of bands,
-- ordered by the number of (non-unique) fans
-- Import this table dump: metal_bands.sql.zip
-- Column names must be: origin and nb_fans
SELECT DISTINCT origin, SUM(fans) as nb_fans FROM metal_bands
GROUP BY origin
ORDER BY nb_fans DESC;
