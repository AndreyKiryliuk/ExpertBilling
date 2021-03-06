DROP INDEX billservice_transaction_account_id;
DROP INDEX billservice_transaction_tarif_id;

CREATE OR REPLACE FUNCTION tsct_del_trg_fn() RETURNS trigger
    AS $$
    BEGIN
        INSERT INTO billservice_transaction (bill, account_id, type_id, approved, tarif_id, summ, description, created) VALUES( OLD.bill, OLD.account_id, OLD.type_id, OLD.approved, OLD.tarif_id, OLD.summ, OLD.description, OLD.created);
        RETURN OLD;
    END;
$$
    LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION tsct_crt_cur_ins(datetx date) RETURNS void
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION tsct_cur_ins (tsctr billservice_transaction) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO tsct';
                         
    fn_bd_tx2_ text := '(bill, account_id, type_id, approved, tarif_id, summ, description, created)
                          VALUES 
                         (tsctr.bill, tsctr.account_id, tsctr.type_id, tsctr.approved, tsctr.tarif_id, tsctr.summ, tsctr.description, tsctr.created); RETURN; END;';
                          
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';


    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION tsct_cur_datechk(tsct_date timestamp without time zone) RETURNS integer AS ';

    ch_fn_bd_tx1_ text := ' DECLARE d_s_ date := DATE ';
    ch_fn_bd_tx2_ text := '; d_e_ date := (DATE ';
    ch_fn_bd_tx3_ text := ')::date; BEGIN IF    tsct_date < d_s_ THEN RETURN -1; ELSIF tsct_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';



    dt_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION tsct_cur_dt() RETURNS date AS ';
    
    onemonth_ text := '1 month';
    query_ text;
    
    prevdate_ date;
    
BEGIN    


    
        query_ :=  fn_tx1_  || quote_literal(fn_bd_tx1_ || datetx_ || fn_bd_tx2_) || fn_tx2_;

        EXECUTE query_;


        query_ :=  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '+ interval ' || quote_literal(onemonth_) ||  ch_fn_bd_tx3_) || fn_tx2_;

        EXECUTE query_;
        
        prevdate_ := tsct_cur_dt();
        
        PERFORM tsct_crt_prev_ins(prevdate_);
        
        query_ := dt_fn_tx1_ || quote_literal(' BEGIN RETURN  DATE ' || quote_literal(datetx_) || '; END; ') || fn_tx2_;
        
        EXECUTE query_;

        
    RETURN;

END;
$$
    LANGUAGE plpgsql;




CREATE OR REPLACE FUNCTION tsct_crt_pdb(datetx date) RETURNS integer
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');
    datetx_e_ text := to_char((datetx + interval '1 month')::date, 'YYYYMM01');

    qt_dtx_ text;
    qt_dtx_e_ text;
    seq_tx1_ text := 'CREATE SEQUENCE tsct#rpdate#_id_seq
                      INCREMENT 1
                      MINVALUE 1
                      MAXVALUE 9223372036854775807
                      START 1
                      CACHE 1;';
    seqname_tx1_ text := 'tsct#rpdate#_id_seq';

    chk_tx1_ text := 'CHECK ( created >= DATE #stdtx# AND created < DATE #eddtx# )';
    ct_tx1_ text := 'CREATE TABLE tsct#rpdate# (
                     #chk#,
                     CONSTRAINT tsct#rpdate#_id_pkey PRIMARY KEY (id) ) 
                     INHERITS (billservice_transaction) 
                     WITH (OIDS=FALSE);                     
                     CREATE INDEX tsct#rpdate#_created_id ON tsct#rpdate# USING btree (created);
                     CREATE INDEX tsct#rpdate#_account_id ON tsct#rpdate# USING btree (account_id);
                     CREATE INDEX tsct#rpdate#_tarif_id ON tsct#rpdate# USING btree (tarif_id);
                     ';
                     
    at_tx1_ text := 'ALTER TABLE tsct#rpdate# ALTER COLUMN id SET DEFAULT nextval(#qseqname#::regclass);';

    chk_       text;
    seq_query_ text;
    ct_query_  text;
    seqn_      text;
    at_query_  text;


BEGIN    
    seq_query_ := replace(seq_tx1_, '#rpdate#', datetx_);
    EXECUTE seq_query_;
    qt_dtx_    := quote_literal(datetx_);
    qt_dtx_e_  := quote_literal(datetx_e_);
    chk_       := replace(chk_tx1_, '#stdtx#', qt_dtx_ );
    chk_       := replace(chk_, '#eddtx#', qt_dtx_e_ );
    ct_query_  := replace(ct_tx1_, '#rpdate#', datetx_);
    ct_query_  := replace(ct_query_, '#chk#', chk_);
    EXECUTE ct_query_;
    seqn_        := replace(seqname_tx1_, '#rpdate#', datetx_);
    at_query_    := replace(at_tx1_, '#rpdate#', datetx_);
    at_query_    := replace(at_query_, '#qseqname#', quote_literal(seqn_));
    EXECUTE at_query_;
    RETURN 0;

END;
$$
    LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION tsct_crt_prev_ins(datetx date) RETURNS void
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION tsct_prev_ins (tsctr billservice_transaction) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO tsct';
                         
    fn_bd_tx2_ text := '(bill, account_id, type_id, approved, tarif_id, summ, description, created)
                          VALUES 
                         (tsctr.bill, tsctr.account_id, tsctr.type_id, tsctr.approved, tsctr.tarif_id, tsctr.summ, tsctr.description, tsctr.created); RETURN; END;';
                          
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';


    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION tsct_prev_datechk(tsct_date timestamp without time zone) RETURNS integer AS ';

    ch_fn_bd_tx1_ text := ' DECLARE d_s_ date := DATE ';
    ch_fn_bd_tx2_ text := '; d_e_ date := (DATE ';
    ch_fn_bd_tx3_ text := ')::date; BEGIN IF    tsct_date < d_s_ THEN RETURN -1; ELSIF tsct_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';

    ch_fn_tx2_ text := ' LANGUAGE plpgsql VOLATILE COST 100;';

    qts_ text := 'CHK % % %';
    
    onemonth_ text := '1 month';
    query_ text;
    
BEGIN    

        EXECUTE  fn_tx1_  || quote_literal(fn_bd_tx1_ || datetx_ || fn_bd_tx2_) || fn_tx2_;


        query_ :=  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '+ interval ' || quote_literal(onemonth_) ||  ch_fn_bd_tx3_) || fn_tx2_;
        
        EXECUTE query_;
        
    RETURN;

END;
$$
    LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION tsct_cur_datechk(tsct_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700201'; d_e_ date := (DATE '19700201'+ interval '1 month')::date; BEGIN IF    tsct_date < d_s_ THEN RETURN -1; ELSIF tsct_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION tsct_cur_dt() RETURNS date
    AS $$ BEGIN RETURN  DATE '19700201'; END; $$
    LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION tsct_cur_ins(tsctr billservice_transaction) RETURNS void
    AS $$BEGIN 
                         RETURN; END;$$
    LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION tsct_ins_trg_fn() RETURNS trigger
    AS $$
DECLARE
    cur_chk int;
    prev_chk int;
BEGIN
    cur_chk := tsct_cur_datechk(NEW.created);

    IF cur_chk = 0 THEN
        PERFORM tsct_cur_ins(NEW);
    ELSIF cur_chk = 1 THEN
        BEGIN
            PERFORM tsct_crt_pdb(NEW.created::date);
            PERFORM tsct_crt_cur_ins(NEW.created::date);
            EXECUTE tsct_cur_ins(NEW);
        EXCEPTION 
          WHEN duplicate_table THEN
             PERFORM tsct_crt_cur_ins(NEW.created::date);
             EXECUTE tsct_cur_ins(NEW);
        END;
        
        
    ELSE 
        prev_chk := tsct_prev_datechk(NEW.created);
        IF prev_chk = 0 THEN
            PERFORM tsct_prev_ins(NEW);
        ELSE
            BEGIN 
                PERFORM tsct_inserter(NEW);
            EXCEPTION 
              WHEN undefined_table THEN
                PERFORM tsct_crt_pdb(NEW.created::date);
                PERFORM tsct_inserter(NEW);
            END;
        END IF;      
    END IF;
    RETURN NULL;
END;
$$
    LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION tsct_inserter(tsctr billservice_transaction) RETURNS void
    AS $$
DECLARE
    datetx_ text := to_char(tsctr.created::date, 'YYYYMM01');
    insq_   text;

    ttrn_bill_ text; 
    ttrn_type_id_ text; 
    ttrn_approved_ boolean; 
    ttrn_tarif_id_ int; 
    ttrn_summ_ double precision; 
    ttrn_description_ text; 
    ttrn_created_ text;    
BEGIN
    
    IF tsctr.bill IS NULL THEN
       ttrn_bill_ := 'NULL';
    ELSE
       ttrn_bill_ := quote_literal(tsctr.bill);
    END IF;
    IF tsctr.type_id IS NULL THEN
       ttrn_type_id_ := 'NULL';
    ELSE
       ttrn_type_id_ := quote_literal(tsctr.type_id);
    END IF;
    IF tsctr.approved IS NULL THEN
       ttrn_approved_ := 'NULL';
    ELSE
       ttrn_approved_ := tsctr.approved;
    END IF;
    IF tsctr.tarif_id IS NULL THEN
       ttrn_tarif_id_ := 'NULL';
    ELSE
       ttrn_tarif_id_ := tsctr.tarif_id;
    END IF;
    IF tsctr.summ IS NULL THEN
       ttrn_summ_ := 'NULL';
    ELSE
       ttrn_summ_ := tsctr.summ;
    END IF;
    IF tsctr.description IS NULL THEN
       ttrn_description_ := 'NULL';
    ELSE
       ttrn_description_ := quote_literal(tsctr.description);
    END IF;
    IF tsctr.created IS NULL THEN
       ttrn_created_ := 'NULL';
    ELSE
       ttrn_created_ := quote_literal(tsctr.created);
    END IF;
    --check quote literal
    
    insq_ := 'INSERT INTO tsct' || datetx_ || ' (bill, account_id, type_id, approved, tarif_id, summ, description, created) VALUES (' 
    || ttrn_bill_ || ',' || tsctr.account_id || ','  || ttrn_type_id_ || ',' || ttrn_approved_ || ',' ||ttrn_tarif_id_ || ',' || ttrn_summ_ || ',' ||  ttrn_description_ || ','  || ttrn_created_ || ');';
    EXECUTE insq_;
    RETURN;
END;
$$
    LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION tsct_prev_datechk(tsct_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700101'; d_e_ date := (DATE '19700101'+ interval '1 month')::date; BEGIN IF    tsct_date < d_s_ THEN RETURN -1; ELSIF tsct_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION tsct_prev_ins(tsctr billservice_transaction) RETURNS void
    AS $$BEGIN 
                          RETURN; END;$$
    LANGUAGE plpgsql;
    
    
CREATE TRIGGER tsct_del_trg
    AFTER DELETE ON billservice_transaction
    FOR EACH ROW
    EXECUTE PROCEDURE tsct_del_trg_fn();


CREATE TRIGGER tsct_ins_trg
    BEFORE INSERT ON billservice_transaction
    FOR EACH ROW
    EXECUTE PROCEDURE tsct_ins_trg_fn();