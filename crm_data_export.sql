--
-- PostgreSQL database dump
--

\restrict YvVCXehclLEpjq2YgCpeSSy5C58c67vYmckTaq9TSDrXhGg1xudCPXVMfbkU0zF

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

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

--
-- Data for Name: companies; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.companies (company_id, company_name, phone, website, status, address_line_1, address_line_2, city, state, postal_code, country, created_at, updated_at) FROM stdin;
1	Mashburn Data Systems	253-555-0100	mashburndatasystems.com	Active	3629 S L St	\N	Tacoma	WA	98418	USA	2026-09-09 10:06:21.296287	2026-09-09 10:06:21.296287
52	Cascade Harbor Supply	253-555-0142	cascadeharborsupply.example	Active	1840 Marine View Dr	\N	Tacoma	WA	98422	USA	2026-09-21 11:58:56.987128	2026-09-21 11:58:56.987128
53	Rainier Field Services	253-555-0187	rainierfieldservices.example	Active	7210 Canyon Rd E	Suite 210	Puyallup	WA	98371	USA	2026-09-21 11:58:56.987128	2026-09-21 11:58:56.987128
54	Soundview Packaging	206-555-0138	soundviewpackaging.example	Active	4600 East Marginal Way S	\N	Seattle	WA	98134	USA	2026-09-21 11:58:56.987128	2026-09-21 11:58:56.987128
55	Northline Equipment	425-555-0164	northlineequipment.example	Active	12820 Highway 99	\N	Everett	WA	98204	USA	2026-09-21 11:58:56.987128	2026-09-21 11:58:56.987128
56	Olympic Ridge Manufacturing	360-555-0126	olympicridgemfg.example	Active	915 Cooper Point Rd SW	\N	Olympia	WA	98502	USA	2026-09-21 11:58:56.987128	2026-09-21 11:58:56.987128
57	Cedar Peak Consulting	360-555-0191	cedarpeakconsulting.example	Active	1318 Broadway St	Suite 300	Vancouver	WA	98660	USA	2026-09-21 11:58:56.987128	2026-09-21 11:58:56.987128
58	Columbia Basin Logistics	509-555-0155	columbiabasinlogistics.example	Active	4205 W Clearwater Ave	\N	Kennewick	WA	99336	USA	2026-09-21 11:58:56.987128	2026-09-21 11:58:56.987128
59	Bluewater Marine Systems	360-555-0173	bluewatermarinesystems.example	Prospect	2601 Marine Dr	\N	Bellingham	WA	98225	USA	2026-09-21 11:58:56.987128	2026-09-21 11:58:56.987128
60	Summit Office Technologies	503-555-0119	summitofficetech.example	Prospect	1025 SE Grand Ave	Suite 140	Portland	OR	97214	USA	2026-09-21 11:58:56.987128	2026-09-21 11:58:56.987128
\.


--
-- Data for Name: contacts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.contacts (contact_id, first_name, last_name, title, department, phone, mobile, email, status, source, owner, created_at, updated_at, company_id) FROM stdin;
92528	Davy	Jones	\N	\N	123-456-7890	\N	singer@monkey.com	\N	\N	\N	2026-10-13 16:30:59.15062	2026-10-13 16:30:59.15062	\N
1	Steve	Mashburn	Founder / CEO2	Development	253-732-0504	253-555-0198	stephen@mashburndatasystems.com	Active	Referral	Steve Mashburn	2026-09-05 13:47:08.757517	2026-09-09 23:06:42.701543	1
92529	cpanel	External Sender	\N	\N	\N	\N	cpanel@mashburndatasystems.com	\N	\N	\N	2026-10-13 18:20:31.055171	2026-10-13 18:20:31.055171	\N
92530	stephen	External Sender	\N	\N	\N	\N	stephen@tahomaspice.com	\N	\N	\N	2026-10-13 18:34:42.434942	2026-10-13 18:34:42.434942	\N
267	Laura	Bennett	Operations Manager	Operations	253-555-0143	253-555-0211	laura.bennett@cascadeharborsupply.example	Active	Customer Referral	Steve	2026-09-21 12:03:26.091244	2026-09-21 12:03:26.091244	52
268	Marcus	Chen	Purchasing Manager	Purchasing	253-555-0144	253-555-0212	marcus.chen@cascadeharborsupply.example	Active	Customer Referral	Steve	2026-09-21 12:03:26.091244	2026-09-21 12:03:26.091244	52
269	Elena	Torres	Office Administrator	Administration	253-555-0145	253-555-0213	elena.torres@cascadeharborsupply.example	Active	Customer Referral	Steve	2026-09-21 12:03:26.091244	2026-09-21 12:03:26.091244	52
270	Daniel	Mercer	General Manager	Management	253-555-0188	253-555-0221	daniel.mercer@rainierfieldservices.example	Active	Website	Steve	2026-09-21 12:03:26.091244	2026-09-21 12:03:26.091244	53
271	Rachel	Kim	Service Coordinator	Service	253-555-0189	253-555-0222	rachel.kim@rainierfieldservices.example	Active	Website	Steve	2026-09-21 12:03:26.091244	2026-09-21 12:03:26.091244	53
272	Andre	Collins	Field Operations Supervisor	Operations	253-555-0190	253-555-0223	andre.collins@rainierfieldservices.example	Active	Website	Steve	2026-09-21 12:03:26.091244	2026-09-21 12:03:26.091244	53
273	Natalie	Brooks	Director of Operations	Operations	206-555-0139	206-555-0231	natalie.brooks@soundviewpackaging.example	Active	Trade Show	Steve	2026-09-21 12:03:26.091244	2026-09-21 12:03:26.091244	54
274	Owen	Patel	IT Manager	Information Technology	206-555-0140	206-555-0232	owen.patel@soundviewpackaging.example	Active	Trade Show	Steve	2026-09-21 12:03:26.091244	2026-09-21 12:03:26.091244	54
275	Grace	Sullivan	Customer Service Manager	Customer Service	206-555-0141	206-555-0233	grace.sullivan@soundviewpackaging.example	Active	Trade Show	Steve	2026-09-21 12:03:26.091244	2026-09-21 12:03:26.091244	54
276	Michael	Reed	Sales Manager	Sales	425-555-0165	425-555-0241	michael.reed@northlineequipment.example	Active	Sales Outreach	Steve	2026-09-21 12:03:26.091244	2026-09-21 12:03:26.091244	55
277	Priya	Shah	Business Systems Analyst	Operations	425-555-0166	425-555-0242	priya.shah@northlineequipment.example	Active	Sales Outreach	Steve	2026-09-21 12:03:26.091244	2026-09-21 12:03:26.091244	55
278	Evan	Foster	Parts Coordinator	Parts	425-555-0167	\N	evan.foster@northlineequipment.example	Active	Sales Outreach	Steve	2026-09-21 12:03:26.091244	2026-09-21 12:03:26.091244	55
279	Karen	Mitchell	Plant Administrator	Administration	360-555-0127	360-555-0251	karen.mitchell@olympicridgemfg.example	Active	Customer Referral	Steve	2026-09-21 12:03:26.091244	2026-09-21 12:03:26.091244	56
280	Luis	Ramirez	Production Manager	Production	360-555-0128	360-555-0252	luis.ramirez@olympicridgemfg.example	Active	Customer Referral	Steve	2026-09-21 12:03:26.091244	2026-09-21 12:03:26.091244	56
281	Heather	Wallace	Accounting Manager	Accounting	360-555-0129	\N	heather.wallace@olympicridgemfg.example	Active	Customer Referral	Steve	2026-09-21 12:03:26.091244	2026-09-21 12:03:26.091244	56
282	Jordan	Ellis	Managing Partner	Management	360-555-0192	360-555-0261	jordan.ellis@cedarpeakconsulting.example	Active	Website	Steve	2026-09-21 12:03:26.091244	2026-09-21 12:03:26.091244	57
283	Maya	Thompson	Client Services Manager	Client Services	360-555-0193	360-555-0262	maya.thompson@cedarpeakconsulting.example	Active	Website	Steve	2026-09-21 12:03:26.091244	2026-09-21 12:03:26.091244	57
284	Aaron	Douglas	Operations Director	Operations	509-555-0156	509-555-0271	aaron.douglas@columbiabasinlogistics.example	Active	Industry Event	Steve	2026-09-21 12:03:26.091244	2026-09-21 12:03:26.091244	58
285	Samantha	Nguyen	Logistics Coordinator	Logistics	509-555-0157	509-555-0272	samantha.nguyen@columbiabasinlogistics.example	Active	Industry Event	Steve	2026-09-21 12:03:26.091244	2026-09-21 12:03:26.091244	58
286	Eric	Monroe	Systems Administrator	Information Technology	509-555-0158	\N	eric.monroe@columbiabasinlogistics.example	Active	Industry Event	Steve	2026-09-21 12:03:26.091244	2026-09-21 12:03:26.091244	58
287	Rebecca	Hayes	Operations Manager	Operations	360-555-0174	360-555-0281	rebecca.hayes@bluewatermarinesystems.example	Prospect	Website	Steve	2026-09-21 12:03:26.091244	2026-09-21 12:03:26.091244	59
288	Thomas	Walker	Service Manager	Service	360-555-0175	360-555-0282	thomas.walker@bluewatermarinesystems.example	Prospect	Website	Steve	2026-09-21 12:03:26.091244	2026-09-21 12:03:26.091244	59
289	Nicole	Grant	Account Manager	Sales	503-555-0120	503-555-0291	nicole.grant@summitofficetech.example	Prospect	Website	Steve	2026-09-21 12:03:26.091244	2026-09-21 12:03:26.091244	60
290	Jason	Park	Technical Services Manager	Technical Services	503-555-0121	503-555-0292	jason.park@summitofficetech.example	Prospect	Website	Steve	2026-09-21 12:03:26.091244	2026-09-21 12:03:26.091244	60
\.


--
-- Name: companies_company_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.companies_company_id_seq', 18690, true);


--
-- Name: contacts_contact_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.contacts_contact_id_seq', 92530, true);


--
-- PostgreSQL database dump complete
--

\unrestrict YvVCXehclLEpjq2YgCpeSSy5C58c67vYmckTaq9TSDrXhGg1xudCPXVMfbkU0zF

