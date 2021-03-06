ALTER TABLE billservice_ipinuse ADD COLUMN lost timestamp without time zone;

CREATE INDEX billservice_ipinuse_lost_idx
  ON billservice_ipinuse
  USING btree
  (lost) WHERE lost is not null;

CREATE OR REPLACE FUNCTION get_free_ip_from_pool(ag_pool_id_ integer, acct_interval integer)
  RETURNS inet AS

$BODY$
BEGIN

RETURN (SELECT free_ip.ipaddress FROM
(SELECT
(SELECT start_ip FROM billservice_ippool WHERE id=ag_pool_id_) + ip_series.ip_inc
FROM generate_series(0, (SELECT end_ip - start_ip FROM billservice_ippool WHERE id=ag_pool_id_))AS ip_series(ip_inc)) AS free_ip(ipaddress)
WHERE free_ip.ipaddress NOT IN (SELECT ip FROM billservice_ipinuse WHERE pool_id=ag_pool_id_ and ((ack=True and disabled is Null) or
(disabled is NULL and ack=False and datetime>now()-(acct_interval*3 || ' seconds')::INTERVAL) or (disabled is not null and disabled>now()-(acct_interval*3 || ' seconds')::INTERVAL) or (lost is not null and lost>now()-interval '30 minutes'))) ORDER BY RANDOM() LIMIT 1);

END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
