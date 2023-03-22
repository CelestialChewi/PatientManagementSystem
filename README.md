<h1> Patient Management System </h1>
<h2> User requirement </h2>
This system is designed to help healthcare providers manage patient information, including allergy profile and prescription records. The following instructions will guide you through setting up the system's database.

<h3> Setting up database (PostgreSQL) </h3>

<p1> Medicine </p1>

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
<p2> PatientAllergies </p2>
```
CREATE TABLE IF NOT EXISTS public."PatientAllergies"
(
    "ID" bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    "patient_ID" bigint NOT NULL,
    "allergen_ID" bigint NOT NULL,
    CONSTRAINT "PatientAllergies_pkey" PRIMARY KEY ("ID"),
    CONSTRAINT "allergen_ID" FOREIGN KEY ("allergen_ID")
        REFERENCES public."Allergens" ("allergen_ID") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT "patient_ID" FOREIGN KEY ("patient_ID")
        REFERENCES public."Patient" ("patient_ID") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."PatientAllergies"
    OWNER to postgres;

COMMENT ON TABLE public."PatientAllergies"
    IS 'Patients with their allergies';

COMMENT ON CONSTRAINT "allergen_ID" ON public."PatientAllergies"
    IS 'Get allergen_ID from Allergens.table and insert into PatientAllergies.table';
COMMENT ON CONSTRAINT "patient_ID" ON public."PatientAllergies"
    IS 'Get patient_ID from Patient.table and insert into PatientAllergies.table';
```

<p3> Allergens </p3>
```
CREATE TABLE IF NOT EXISTS public."Allergens"
(
    "allergen_ID" bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    allergen_name character varying COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT "Allergens_pkey" PRIMARY KEY ("allergen_ID")
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."Allergens"
    OWNER to postgres;
    
# Medicine
CREATE TABLE IF NOT EXISTS public."Medicine"
(
    "medicine_ID" bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    medicine_name character varying COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT "Medicine_pkey" PRIMARY KEY ("medicine_ID")
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."Medicine"
    OWNER to postgres;
```

<p4> MedicineAllergens </p4>
```
CREATE TABLE IF NOT EXISTS public."MedicineAllergens"
(
    "ID" bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    "medicine_ID" bigint NOT NULL,
    "allergen_ID" bigint NOT NULL,
    CONSTRAINT "MedicineComponents_pkey" PRIMARY KEY ("ID"),
    CONSTRAINT "allergen_ID" FOREIGN KEY ("allergen_ID")
        REFERENCES public."Allergens" ("allergen_ID") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT "medicine_ID" FOREIGN KEY ("medicine_ID")
        REFERENCES public."Medicine" ("medicine_ID") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."MedicineAllergens"
    OWNER to postgres;

COMMENT ON TABLE public."MedicineAllergens"
    IS 'Medicine with allergies components';

COMMENT ON CONSTRAINT "allergen_ID" ON public."MedicineAllergens"
    IS 'Get allergen_ID from Allergens.table';
COMMENT ON CONSTRAINT "medicine_ID" ON public."MedicineAllergens"
    IS 'Get medicine_ID from Medicine.table';
```

<p5> TransactionHistory </p5>
```
CREATE TABLE public."TransactionHistory"
(
    "order_ID" bigint NOT NULL GENERATED ALWAYS AS IDENTITY,
    "patient_ID" bigint NOT NULL,
    "medicine_ID" bigint NOT NULL,
    quantity bigint NOT NULL,
    purchase_date date NOT NULL,
    PRIMARY KEY ("order_ID"),
    CONSTRAINT "medicine_ID" FOREIGN KEY ("medicine_ID")
        REFERENCES public."Medicine" ("medicine_ID") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT "patient_ID" FOREIGN KEY ("patient_ID")
        REFERENCES public."Patient" ("patient_ID") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
);

ALTER TABLE IF EXISTS public."TransactionHistory"
    OWNER to postgres;
```

<p6> ViewCart </p6>
```
CREATE TABLE public."ViewCart"
(
    "Cart_ID" bigint NOT NULL GENERATED ALWAYS AS IDENTITY,
    "patient_ID" bigint NOT NULL,
    "medicine_ID" bigint NOT NULL,
    quantity bigint NOT NULL,
    PRIMARY KEY ("Cart_ID"),
    CONSTRAINT "medicine_ID" FOREIGN KEY ("medicine_ID")
        REFERENCES public."Medicine" ("medicine_ID") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT "patient_ID" FOREIGN KEY ("patient_ID")
        REFERENCES public."Patient" ("patient_ID") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
);

ALTER TABLE IF EXISTS public."ViewCart"
    OWNER to postgres;
```