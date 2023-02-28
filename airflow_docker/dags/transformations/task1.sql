create table if not exists Orders(
    timestamp timestamp,
    name character varying,
    payment_option character varying,
    amount money,
    primary key (timestamp)
) 