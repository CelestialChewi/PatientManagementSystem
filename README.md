<h1> Patient Management System </h1>
This system is designed to help healthcare providers manage patient information, including medical history, appointments, and prescription records. The following instructions will guide you through setting up the system's database.

<h2> Setting up database </h2>

<h3> Medicine </h3>
````
```
CREATE TABLE IF NOT EXISTS public."Patient"
(
    "patient_ID" bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    patient_name character varying COLLATE pg_catalog."default" NOT NULL,
    "patient_DOB" date NOT NULL,
    "patient_IC" integer,
    patient_passport character varying COLLATE pg_catalog."default",
    CONSTRAINT "Patient_pkey" PRIMARY KEY ("patient_ID")
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."Patient"
    OWNER to postgres;
```
````