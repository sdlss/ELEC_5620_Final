--
-- PostgreSQL database dump
--

-- Dumped from database version 16.8
-- Dumped by pg_dump version 16.8

-- Started on 2025-10-31 18:17:03

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 232 (class 1255 OID 25108)
-- Name: trg_bump_case_updated_fn(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.trg_bump_case_updated_fn() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  NEW.updated_at := now();
  RETURN NEW;
END$$;


ALTER FUNCTION public.trg_bump_case_updated_fn() OWNER TO postgres;

--
-- TOC entry 233 (class 1255 OID 25175)
-- Name: trg_sync_case_status_fn(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.trg_sync_case_status_fn() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  UPDATE "case"
     SET status = CASE
                    WHEN NEW.status = 'eligible'      THEN 'eligible'
                    WHEN NEW.status = 'needs_review'  THEN 'in_review'
                    ELSE 'rejected'
                  END,
         needs_review = (NEW.status = 'needs_review')
   WHERE id = NEW.case_id;
  RETURN NEW;
END$$;


ALTER FUNCTION public.trg_sync_case_status_fn() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 216 (class 1259 OID 25076)
-- Name: app_user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.app_user (
    id bigint NOT NULL,
    email text NOT NULL,
    password_hash text NOT NULL,
    role text NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT app_user_role_check CHECK ((role = ANY (ARRAY['consumer'::text, 'logistics'::text, 'admin'::text])))
);


ALTER TABLE public.app_user OWNER TO postgres;

--
-- TOC entry 215 (class 1259 OID 25075)
-- Name: app_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.app_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.app_user_id_seq OWNER TO postgres;

--
-- TOC entry 5002 (class 0 OID 0)
-- Dependencies: 215
-- Name: app_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.app_user_id_seq OWNED BY public.app_user.id;


--
-- TOC entry 218 (class 1259 OID 25089)
-- Name: case; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."case" (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    status text NOT NULL,
    title text,
    latest_summary text,
    needs_review boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT case_status_check CHECK ((status = ANY (ARRAY['new'::text, 'in_review'::text, 'eligible'::text, 'rejected'::text, 'refunded'::text, 'shipped'::text, 'closed'::text, 'pending_verification'::text])))
);


ALTER TABLE public."case" OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 25088)
-- Name: case_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.case_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.case_id_seq OWNER TO postgres;

--
-- TOC entry 5003 (class 0 OID 0)
-- Dependencies: 217
-- Name: case_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.case_id_seq OWNED BY public."case".id;


--
-- TOC entry 226 (class 1259 OID 25153)
-- Name: eligibility_decision; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.eligibility_decision (
    id bigint NOT NULL,
    case_id bigint NOT NULL,
    policy_snapshot_id bigint,
    status text NOT NULL,
    rationale text NOT NULL,
    lenient_flag boolean DEFAULT false,
    decided_at timestamp with time zone DEFAULT now(),
    CONSTRAINT eligibility_decision_status_check CHECK ((status = ANY (ARRAY['eligible'::text, 'not_eligible'::text, 'needs_review'::text])))
);


ALTER TABLE public.eligibility_decision OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 25152)
-- Name: eligibility_decision_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.eligibility_decision_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.eligibility_decision_id_seq OWNER TO postgres;

--
-- TOC entry 5004 (class 0 OID 0)
-- Dependencies: 225
-- Name: eligibility_decision_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.eligibility_decision_id_seq OWNED BY public.eligibility_decision.id;


--
-- TOC entry 222 (class 1259 OID 25127)
-- Name: issue; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.issue (
    id bigint NOT NULL,
    case_id bigint NOT NULL,
    description text NOT NULL,
    classification text,
    clf_confidence numeric(5,2),
    ai_annotations jsonb,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.issue OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 25126)
-- Name: issue_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.issue_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.issue_id_seq OWNER TO postgres;

--
-- TOC entry 5005 (class 0 OID 0)
-- Dependencies: 221
-- Name: issue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.issue_id_seq OWNED BY public.issue.id;


--
-- TOC entry 224 (class 1259 OID 25143)
-- Name: policy_snapshot; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.policy_snapshot (
    id bigint NOT NULL,
    name text NOT NULL,
    source text NOT NULL,
    matched_rules jsonb NOT NULL,
    captured_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.policy_snapshot OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 25142)
-- Name: policy_snapshot_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.policy_snapshot_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.policy_snapshot_id_seq OWNER TO postgres;

--
-- TOC entry 5006 (class 0 OID 0)
-- Dependencies: 223
-- Name: policy_snapshot_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.policy_snapshot_id_seq OWNED BY public.policy_snapshot.id;


--
-- TOC entry 220 (class 1259 OID 25111)
-- Name: receipt; Type: TABLE; Schema: public; Owner: postgres
--


--
-- TOC entry 219 (class 1259 OID 25110)
-- Name: receipt_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--


--
-- TOC entry 5007 (class 0 OID 0)
-- Dependencies: 219
-- Name: receipt_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

-- Receipt table removed


--
-- TOC entry 230 (class 1259 OID 25196)
-- Name: reminder; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reminder (
    id bigint NOT NULL,
    case_id bigint NOT NULL,
    deadline_id bigint,
    scheduled_at timestamp with time zone NOT NULL,
    sent_at timestamp with time zone,
    status text NOT NULL,
    channel text NOT NULL,
    CONSTRAINT reminder_channel_check CHECK ((channel = ANY (ARRAY['email'::text, 'sms'::text, 'inapp'::text]))),
    CONSTRAINT reminder_status_check CHECK ((status = ANY (ARRAY['scheduled'::text, 'sent'::text, 'failed'::text])))
);


ALTER TABLE public.reminder OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 25195)
-- Name: reminder_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reminder_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reminder_id_seq OWNER TO postgres;

--
-- TOC entry 5008 (class 0 OID 0)
-- Dependencies: 229
-- Name: reminder_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reminder_id_seq OWNED BY public.reminder.id;


--
-- TOC entry 231 (class 1259 OID 25218)
-- Name: v_case_overview; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_case_overview AS
 SELECT c.id AS case_id,
    c.user_id,
    c.status AS case_status,
    c.needs_review,
    c.latest_summary,
    c.created_at,
    c.updated_at,
    ed.status AS eligibility_status,
    ed.lenient_flag,
    ed.decided_at
   FROM (public."case" c
     LEFT JOIN LATERAL ( SELECT e.id,
         e.case_id,
         e.policy_snapshot_id,
         e.status,
         e.rationale,
         e.lenient_flag,
         e.decided_at
        FROM public.eligibility_decision e
       WHERE (e.case_id = c.id)
       ORDER BY e.decided_at DESC
      LIMIT 1) ed ON (true));


ALTER VIEW public.v_case_overview OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 25178)
-- Name: warranty_deadline; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.warranty_deadline (
    id bigint NOT NULL,
    case_id bigint NOT NULL,
    deadline_date date NOT NULL,
    type text NOT NULL,
    source text,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT warranty_deadline_type_check CHECK ((type = ANY (ARRAY['return'::text, 'warranty'::text])))
);


ALTER TABLE public.warranty_deadline OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 25177)
-- Name: warranty_deadline_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.warranty_deadline_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.warranty_deadline_id_seq OWNER TO postgres;

--
-- TOC entry 5009 (class 0 OID 0)
-- Dependencies: 227
-- Name: warranty_deadline_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.warranty_deadline_id_seq OWNED BY public.warranty_deadline.id;


--
-- TOC entry 4776 (class 2604 OID 25079)
-- Name: app_user id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.app_user ALTER COLUMN id SET DEFAULT nextval('public.app_user_id_seq'::regclass);


--
-- TOC entry 4778 (class 2604 OID 25092)
-- Name: case id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."case" ALTER COLUMN id SET DEFAULT nextval('public.case_id_seq'::regclass);


--
-- TOC entry 4788 (class 2604 OID 25156)
-- Name: eligibility_decision id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eligibility_decision ALTER COLUMN id SET DEFAULT nextval('public.eligibility_decision_id_seq'::regclass);


--
-- TOC entry 4784 (class 2604 OID 25130)
-- Name: issue id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue ALTER COLUMN id SET DEFAULT nextval('public.issue_id_seq'::regclass);


--
-- TOC entry 4786 (class 2604 OID 25146)
-- Name: policy_snapshot id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.policy_snapshot ALTER COLUMN id SET DEFAULT nextval('public.policy_snapshot_id_seq'::regclass);


--
-- TOC entry 4782 (class 2604 OID 25114)
-- Name: receipt id; Type: DEFAULT; Schema: public; Owner: postgres
--

-- removed: receipt default id


--
-- TOC entry 4793 (class 2604 OID 25199)
-- Name: reminder id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reminder ALTER COLUMN id SET DEFAULT nextval('public.reminder_id_seq'::regclass);


--
-- TOC entry 4791 (class 2604 OID 25181)
-- Name: warranty_deadline id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warranty_deadline ALTER COLUMN id SET DEFAULT nextval('public.warranty_deadline_id_seq'::regclass);


--
-- TOC entry 4982 (class 0 OID 25076)
-- Dependencies: 216
-- Data for Name: app_user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.app_user (id, email, password_hash, role, created_at) FROM stdin;
\.


--
-- TOC entry 4984 (class 0 OID 25089)
-- Dependencies: 218
-- Data for Name: case; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."case" (id, user_id, status, title, latest_summary, needs_review, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4992 (class 0 OID 25153)
-- Dependencies: 226
-- Data for Name: eligibility_decision; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.eligibility_decision (id, case_id, policy_snapshot_id, status, rationale, lenient_flag, decided_at) FROM stdin;
\.


--
-- TOC entry 4988 (class 0 OID 25127)
-- Dependencies: 222
-- Data for Name: issue; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.issue (id, case_id, description, classification, clf_confidence, ai_annotations, created_at) FROM stdin;
\.


--
-- TOC entry 4990 (class 0 OID 25143)
-- Dependencies: 224
-- Data for Name: policy_snapshot; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.policy_snapshot (id, name, source, matched_rules, captured_at) FROM stdin;
\.


--
-- TOC entry 4986 (class 0 OID 25111)
-- Dependencies: 220
-- Data for Name: receipt; Type: TABLE DATA; Schema: public; Owner: postgres
--

-- removed: receipt data


--
-- TOC entry 4996 (class 0 OID 25196)
-- Dependencies: 230
-- Data for Name: reminder; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reminder (id, case_id, deadline_id, scheduled_at, sent_at, status, channel) FROM stdin;
\.


--
-- TOC entry 4994 (class 0 OID 25178)
-- Dependencies: 228
-- Data for Name: warranty_deadline; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.warranty_deadline (id, case_id, deadline_date, type, source, created_at) FROM stdin;
\.


--
-- TOC entry 5010 (class 0 OID 0)
-- Dependencies: 215
-- Name: app_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.app_user_id_seq', 1, false);


--
-- TOC entry 5011 (class 0 OID 0)
-- Dependencies: 217
-- Name: case_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.case_id_seq', 1, true);


--
-- TOC entry 5012 (class 0 OID 0)
-- Dependencies: 225
-- Name: eligibility_decision_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.eligibility_decision_id_seq', 1, false);


--
-- TOC entry 5013 (class 0 OID 0)
-- Dependencies: 221
-- Name: issue_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.issue_id_seq', 1, false);


--
-- TOC entry 5014 (class 0 OID 0)
-- Dependencies: 223
-- Name: policy_snapshot_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.policy_snapshot_id_seq', 1, false);


--
-- TOC entry 5015 (class 0 OID 0)
-- Dependencies: 219
-- Name: receipt_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

-- removed: receipt sequence setval


--
-- TOC entry 5016 (class 0 OID 0)
-- Dependencies: 229
-- Name: reminder_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reminder_id_seq', 1, false);


--
-- TOC entry 5017 (class 0 OID 0)
-- Dependencies: 227
-- Name: warranty_deadline_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.warranty_deadline_id_seq', 1, false);


--
-- TOC entry 4801 (class 2606 OID 25087)
-- Name: app_user app_user_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.app_user
    ADD CONSTRAINT app_user_email_key UNIQUE (email);


--
-- TOC entry 4803 (class 2606 OID 25085)
-- Name: app_user app_user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.app_user
    ADD CONSTRAINT app_user_pkey PRIMARY KEY (id);


--
-- TOC entry 4805 (class 2606 OID 25100)
-- Name: case case_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."case"
    ADD CONSTRAINT case_pkey PRIMARY KEY (id);


--
-- TOC entry 4817 (class 2606 OID 25163)
-- Name: eligibility_decision eligibility_decision_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eligibility_decision
    ADD CONSTRAINT eligibility_decision_pkey PRIMARY KEY (id);


--
-- TOC entry 4813 (class 2606 OID 25135)
-- Name: issue issue_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue
    ADD CONSTRAINT issue_pkey PRIMARY KEY (id);


--
-- TOC entry 4815 (class 2606 OID 25151)
-- Name: policy_snapshot policy_snapshot_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.policy_snapshot
    ADD CONSTRAINT policy_snapshot_pkey PRIMARY KEY (id);


--
-- TOC entry 4810 (class 2606 OID 25119)
-- Name: receipt receipt_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

-- removed: receipt primary key


--
-- TOC entry 4826 (class 2606 OID 25205)
-- Name: reminder reminder_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reminder
    ADD CONSTRAINT reminder_pkey PRIMARY KEY (id);


--
-- TOC entry 4822 (class 2606 OID 25187)
-- Name: warranty_deadline warranty_deadline_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warranty_deadline
    ADD CONSTRAINT warranty_deadline_pkey PRIMARY KEY (id);


--
-- TOC entry 4806 (class 1259 OID 25107)
-- Name: idx_case_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_case_status ON public."case" USING btree (status);


--
-- TOC entry 4807 (class 1259 OID 25106)
-- Name: idx_case_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_case_user ON public."case" USING btree (user_id);


--
-- TOC entry 4819 (class 1259 OID 25193)
-- Name: idx_deadline_case; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_deadline_case ON public.warranty_deadline USING btree (case_id);


--
-- TOC entry 4820 (class 1259 OID 25194)
-- Name: idx_deadline_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_deadline_date ON public.warranty_deadline USING btree (deadline_date);


--
-- TOC entry 4818 (class 1259 OID 25174)
-- Name: idx_elig_case; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_elig_case ON public.eligibility_decision USING btree (case_id);


--
-- TOC entry 4811 (class 1259 OID 25141)
-- Name: idx_issue_case; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_issue_case ON public.issue USING btree (case_id);


--
-- TOC entry 4808 (class 1259 OID 25125)
-- Name: idx_receipt_case; Type: INDEX; Schema: public; Owner: postgres
--

-- removed: idx_receipt_case


--
-- TOC entry 4823 (class 1259 OID 25216)
-- Name: idx_reminder_case; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_reminder_case ON public.reminder USING btree (case_id);


--
-- TOC entry 4824 (class 1259 OID 25217)
-- Name: idx_reminder_scheduled; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_reminder_scheduled ON public.reminder USING btree (scheduled_at);


--
-- TOC entry 4835 (class 2620 OID 25232)
-- Name: case trg_case_bump_updated; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_case_bump_updated BEFORE UPDATE ON public."case" FOR EACH ROW EXECUTE FUNCTION public.trg_bump_case_updated_fn();


--
-- TOC entry 4836 (class 2620 OID 25233)
-- Name: eligibility_decision trg_sync_case_status; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_sync_case_status AFTER INSERT ON public.eligibility_decision FOR EACH ROW EXECUTE FUNCTION public.trg_sync_case_status_fn();


--
-- TOC entry 4827 (class 2606 OID 25101)
-- Name: case case_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."case"
    ADD CONSTRAINT case_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.app_user(id) ON DELETE CASCADE;


--
-- TOC entry 4830 (class 2606 OID 25164)
-- Name: eligibility_decision eligibility_decision_case_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eligibility_decision
    ADD CONSTRAINT eligibility_decision_case_id_fkey FOREIGN KEY (case_id) REFERENCES public."case"(id) ON DELETE CASCADE;


--
-- TOC entry 4831 (class 2606 OID 25169)
-- Name: eligibility_decision eligibility_decision_policy_snapshot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eligibility_decision
    ADD CONSTRAINT eligibility_decision_policy_snapshot_id_fkey FOREIGN KEY (policy_snapshot_id) REFERENCES public.policy_snapshot(id);


--
-- TOC entry 4829 (class 2606 OID 25136)
-- Name: issue issue_case_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.issue
    ADD CONSTRAINT issue_case_id_fkey FOREIGN KEY (case_id) REFERENCES public."case"(id) ON DELETE CASCADE;


--
-- TOC entry 4828 (class 2606 OID 25120)
-- Name: receipt receipt_case_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

-- removed: receipt FK to case


--
-- TOC entry 4833 (class 2606 OID 25206)
-- Name: reminder reminder_case_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reminder
    ADD CONSTRAINT reminder_case_id_fkey FOREIGN KEY (case_id) REFERENCES public."case"(id) ON DELETE CASCADE;


--
-- TOC entry 4834 (class 2606 OID 25211)
-- Name: reminder reminder_deadline_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reminder
    ADD CONSTRAINT reminder_deadline_id_fkey FOREIGN KEY (deadline_id) REFERENCES public.warranty_deadline(id) ON DELETE SET NULL;


--
-- TOC entry 4832 (class 2606 OID 25188)
-- Name: warranty_deadline warranty_deadline_case_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warranty_deadline
    ADD CONSTRAINT warranty_deadline_case_id_fkey FOREIGN KEY (case_id) REFERENCES public."case"(id) ON DELETE CASCADE;


-- Completed on 2025-10-31 18:17:03

--
-- PostgreSQL database dump complete
--

