--
-- PostgreSQL database dump
--

\restrict ikvldyDjPQSSJsXCUgtpQNfMWjaFSkCa7xDer9fvcHKtzVoVyf1t7q8Mz74Vgud

-- Dumped from database version 18.4 (Homebrew)
-- Dumped by pg_dump version 18.4 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: admins; Type: TABLE; Schema: public; Owner: yogendraadiyarapu
--

CREATE TABLE public.admins (
    id integer NOT NULL,
    username character varying(80) NOT NULL,
    password_hash character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.admins OWNER TO yogendraadiyarapu;

--
-- Name: admins_id_seq; Type: SEQUENCE; Schema: public; Owner: yogendraadiyarapu
--

CREATE SEQUENCE public.admins_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.admins_id_seq OWNER TO yogendraadiyarapu;

--
-- Name: admins_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yogendraadiyarapu
--

ALTER SEQUENCE public.admins_id_seq OWNED BY public.admins.id;


--
-- Name: participants; Type: TABLE; Schema: public; Owner: yogendraadiyarapu
--

CREATE TABLE public.participants (
    id uuid NOT NULL,
    reg_id character varying(20) NOT NULL,
    name character varying(120) NOT NULL,
    age integer NOT NULL,
    weight double precision NOT NULL,
    city character varying(100) NOT NULL,
    phone character varying(20) NOT NULL,
    email character varying(150) NOT NULL,
    qr_path character varying(255),
    checked_in boolean NOT NULL,
    check_in_time timestamp with time zone,
    is_winner boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.participants OWNER TO yogendraadiyarapu;

--
-- Name: reg_id_seq; Type: SEQUENCE; Schema: public; Owner: yogendraadiyarapu
--

CREATE SEQUENCE public.reg_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reg_id_seq OWNER TO yogendraadiyarapu;

--
-- Name: admins id; Type: DEFAULT; Schema: public; Owner: yogendraadiyarapu
--

ALTER TABLE ONLY public.admins ALTER COLUMN id SET DEFAULT nextval('public.admins_id_seq'::regclass);


--
-- Data for Name: admins; Type: TABLE DATA; Schema: public; Owner: yogendraadiyarapu
--

COPY public.admins (id, username, password_hash, created_at) FROM stdin;
1	admin	$2b$12$qN1Sih1Bi.mK5g4qxYlmVerQeyniSDjngYnCcBtdLYFhZ3nDpH4DS	2026-06-17 12:13:09.776249+05:30
\.


--
-- Data for Name: participants; Type: TABLE DATA; Schema: public; Owner: yogendraadiyarapu
--

COPY public.participants (id, reg_id, name, age, weight, city, phone, email, qr_path, checked_in, check_in_time, is_winner, created_at) FROM stdin;
ed8e6788-794e-44df-a1a6-7a62f1198b43	KNM-00006	Yogi	21	70	Gajuwaka	9393876663	sharmilaadari18@gmail.com	/static/qrcodes/KNM-00006.png	f	\N	f	2026-06-17 21:48:01.453978+05:30
\.


--
-- Name: admins_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yogendraadiyarapu
--

SELECT pg_catalog.setval('public.admins_id_seq', 1, true);


--
-- Name: reg_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yogendraadiyarapu
--

SELECT pg_catalog.setval('public.reg_id_seq', 6, true);


--
-- Name: admins admins_pkey; Type: CONSTRAINT; Schema: public; Owner: yogendraadiyarapu
--

ALTER TABLE ONLY public.admins
    ADD CONSTRAINT admins_pkey PRIMARY KEY (id);


--
-- Name: participants participants_pkey; Type: CONSTRAINT; Schema: public; Owner: yogendraadiyarapu
--

ALTER TABLE ONLY public.participants
    ADD CONSTRAINT participants_pkey PRIMARY KEY (id);


--
-- Name: ix_admins_username; Type: INDEX; Schema: public; Owner: yogendraadiyarapu
--

CREATE UNIQUE INDEX ix_admins_username ON public.admins USING btree (username);


--
-- Name: ix_participants_email; Type: INDEX; Schema: public; Owner: yogendraadiyarapu
--

CREATE UNIQUE INDEX ix_participants_email ON public.participants USING btree (email);


--
-- Name: ix_participants_phone; Type: INDEX; Schema: public; Owner: yogendraadiyarapu
--

CREATE UNIQUE INDEX ix_participants_phone ON public.participants USING btree (phone);


--
-- Name: ix_participants_reg_id; Type: INDEX; Schema: public; Owner: yogendraadiyarapu
--

CREATE UNIQUE INDEX ix_participants_reg_id ON public.participants USING btree (reg_id);


--
-- PostgreSQL database dump complete
--

\unrestrict ikvldyDjPQSSJsXCUgtpQNfMWjaFSkCa7xDer9fvcHKtzVoVyf1t7q8Mz74Vgud

