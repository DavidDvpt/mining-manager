"""create finder table and seed finders

Revision ID: 003_create_finder
Revises: 002_create_economy
Create Date: 2026-10-22
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

import sqlalchemy as sa
from alembic import op

revision = "003_create_finder"
down_revision = "002_create_economy"
branch_labels = None
depends_on = None


def _timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


FINDERS = [
    ("709a2c30-9a0d-44df-94fd-3a930b724ac3", "Elder Seeker 10 (L)", None, "/finders/110", 8, 40, Decimal("701.5"), None, False, False, "2026-10-04T16:06:45.903Z", "2026-10-15T13:02:52.348Z", Decimal("0.3"), Decimal("10"), Decimal("0.001")),
    ("4f1cd0ba-f284-46c2-8207-fdbb8f5b7e32", "Mayhem Ziplex P50", None, "/finders/106", 8, 50, Decimal("701.5"), None, True, False, "2026-10-04T16:06:45.903Z", "2026-10-15T13:02:52.345Z", Decimal("0.3"), Decimal("100"), Decimal("0.00266")),
    ("7ff684ec-b6a7-404c-9e0b-a11787890858", "Mayhem Ziplex P400 (L)", None, "/finders/111", 8, 800, Decimal("701.5"), None, False, False, "2026-10-04T16:06:45.903Z", "2026-10-15T13:02:52.349Z", Decimal("0.3"), Decimal("10"), Decimal("0.0085")),
    ("206c6a67-6107-44be-81a2-e8a18c0c9f01", "Finder F-105, TEN Edition", 406, "/finders/15", 9, 10, Decimal("552.3"), None, True, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.368Z", Decimal("1.8"), Decimal("82"), Decimal("0.019")),
    ("ac435550-cc6d-4353-9797-923e1dcaf821", "Sabad Finder F-100 (L)", None, "/finders/112", 8, 2, Decimal("104.5"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.350Z", Decimal("1.5"), Decimal("0.1"), Decimal("0.00239")),
    ("63a6b43f-95be-4ac9-9195-a1e856cf0cf0", "Genesis Rookie Finder (L)", 1963, "/finders/25", 8, 1, Decimal("104.5"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.351Z", Decimal("1.5"), Decimal("0.06"), Decimal("0.00239")),
    ("35bc6026-30ed-42a7-abfa-47d1c0c472e7", "Finder F-210 (L)", 406, "/finders/17", 8, 10, Decimal("383.1"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.352Z", Decimal("0.7"), Decimal("105.2"), Decimal("0.01211")),
    ("db708f25-5865-46e4-8db4-2379b63e9329", "Lost Soul Seeker (L)", 5120, "/finders/31", 8, 32, Decimal("721"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.352Z", Decimal("1.5"), Decimal("48"), Decimal("0.037")),
    ("039cc3af-aa1d-4bed-97fd-69b347363dc7", "NI Finder New Settler Issue (L)", None, "/finders/32", 8, 1, Decimal("104.5"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.353Z", Decimal("1.5"), Decimal("1"), Decimal("0.002")),
    ("ab40bb12-b9d6-4648-8313-a1310607ec41", "Omegaton Detectonator MD-1 (L)", 7713, "/finders/33", 8, 1, Decimal("104.5"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.354Z", Decimal("1.5"), Decimal("0.1"), Decimal("0.00239")),
    ("deb42e52-9336-46a1-aed1-e5365ed23491", "CDF Finder z10 (L)", 406, "/finders/2", 8, 15, Decimal("223.9"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.355Z", Decimal("1.55"), Decimal("1"), Decimal("0.00323")),
    ("aa84aabd-d3a2-4063-b358-cba48f98b1c6", "CDF Finder z25 (L)", 406, "/finders/3", 8, 25, Decimal("422.9"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.357Z", Decimal("1.58"), Decimal("2"), Decimal("0.00554")),
    ("eecee910-71cd-442c-ac7c-89dbd0b813e3", "CDF Finder z40 (L)", 406, "/finders/4", 8, 40, Decimal("741.3"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.357Z", Decimal("1.62"), Decimal("4"), Decimal("0.00968")),
    ("e41b521d-64aa-488d-b09c-6281562bd726", "DSEC Seeker L12 (L)", 406, "/finders/7", 8, 12, Decimal("462.7"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.359Z", Decimal("1.92"), Decimal("49"), Decimal("0.0229")),
    ("ed7f21dd-6776-4c4b-ae3e-64c20c63a2a1", "A.R.C. Finder 0001 (L)", 5640, "/finders/1", 9, 10, Decimal("204"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.360Z", Decimal("1.6"), Decimal("0.1"), Decimal("0.0025")),
    ("1c95b5da-f8e2-4064-b7ed-d1ade9f0410c", "Demonic Detector MK-I (L)", 5120, "/finders/5", 8, 10, Decimal("204"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.361Z", Decimal("0.1"), Decimal("4.75"), Decimal("0.005")),
    ("65ae7794-b125-45fa-82e0-5e45a6e2b12a", "DSEC Seeker L30 (L)", 406, "/finders/8", 8, 20, Decimal("820.9"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.362Z", Decimal("1.97"), Decimal("136"), Decimal("0.0396")),
    ("4e2adca1-0101-4834-9112-508d9b5a71e7", "eMINE FS (L)", 3124, "/finders/9", 8, 10, Decimal("676.6"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.363Z", Decimal("2.1"), Decimal("122"), Decimal("0.01743")),
    ("1cf8ab72-a6e2-419f-a164-df1c455e0061", "Rookie TerraMaster", 5680, "/finders/44", 8, 1, Decimal("109.5"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.358Z", Decimal("2.1"), Decimal("1"), Decimal("0.00239")),
    ("e2eae43a-733d-4ce3-82a3-fd7f19fb1b1e", "Finder F-101", 406, "/finders/10", 8, 10, Decimal("263.7"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.364Z", Decimal("1"), Decimal("5.5"), Decimal("0.01")),
    ("dce739ec-7177-4f80-9651-2b38247a231a", "Finder F-212 (L)", 406, "/finders/19", 8, 10, Decimal("592"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.371Z", Decimal("0.7"), Decimal("155.2"), Decimal("0.01343")),
    ("bf24b220-214c-4452-a44a-d560bf863959", "Finder F-213 (L)", 406, "/finders/21", 8, 10, Decimal("631.8"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.373Z", Decimal("0.7"), Decimal("201.2"), Decimal("0.0166")),
    ("17c28378-c778-4ab8-83e8-88f5f899d3d2", "Finder F-213 (L) Adapted", 406, "/finders/22", 8, 10, Decimal("811"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.374Z", Decimal("0.7"), Decimal("678"), Decimal("0.0233")),
    ("3518e37a-b4c1-4dcf-b45f-1eeceec84a4a", "Finder F-213 (L) Customized", 406, "/finders/23", 8, 10, Decimal("850.8"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.374Z", Decimal("0.3"), Decimal("2678"), Decimal("0.0268")),
    ("66b144a6-256a-4e0b-99e3-775b908ec370", "Finder F-212, SGA Edition (L)", 406, "/finders/20", 8, 10, Decimal("612"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.376Z", Decimal("0.35"), Decimal("155.2"), Decimal("0.01343")),
    ("3efb7591-858d-4450-80e5-2d9c5580bdce", "ROCTEC S16 Finder (L)", 5120, "/finders/43", 8, 10, Decimal("253.8"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.381Z", Decimal("1.75"), Decimal("35"), Decimal("0.017")),
    ("9e14cd39-6784-452a-bb21-169889f9d441", "Finder F-102", 406, "/finders/11", 8, 10, Decimal("323.4"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.364Z", Decimal("1.1"), Decimal("30"), Decimal("0.0115")),
    ("c34edcf4-d46d-4b1d-aa7d-21685552c8a8", "Finder F-103", 406, "/finders/12", 8, 10, Decimal("363.2"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.365Z", Decimal("1.3"), Decimal("55"), Decimal("0.0145")),
    ("0f3f57ef-23b2-41d7-8ffa-78e2cebf0ac8", "Finder F-105", 406, "/finders/14", 8, 10, Decimal("522.4"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.367Z", Decimal("1.8"), Decimal("82"), Decimal("0.0205")),
    ("70e2bcbc-90d4-4ef1-b26b-33f3e50cd515", "Finder F-106", 406, "/finders/16", 8, 10, Decimal("582.1"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.369Z", Decimal("1.3"), Decimal("79.95"), Decimal("0.01799")),
    ("caea8d32-637c-49d3-8659-c3024908d605", "Finder F-104", 406, "/finders/13", 8, 10, Decimal("432.9"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.372Z", Decimal("1"), Decimal("66.6"), Decimal("0.01632")),
    ("ad5d765a-c495-4a0e-b049-088d50184346", "Island Ziplex Z1 Seeker", 406, "/finders/29", 8, 10, Decimal("204"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.377Z", Decimal("1.3"), Decimal("2.4"), Decimal("0.00751")),
    ("35a295f2-11ac-454f-90e8-0fb92eafc589", "Ziplex TK320 Seeker (L)", 1963, "/finders/92", 8, 10, Decimal("850.8"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.385Z", Decimal("1.1"), Decimal("311"), Decimal("0.02151")),
    ("07dadc27-6cbf-4670-b167-cbe2f3f3494e", "TerraMaster 1 (L)", 4701, "/finders/51", 8, 10, Decimal("206"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.386Z", Decimal("2.1"), Decimal("2.5"), Decimal("0.015")),
    ("8814cf64-31dd-4bf2-af40-e9acb74f49bc", "TerraMaster 2 (L)", 4701, "/finders/52", 8, 10, Decimal("408"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.387Z", Decimal("2.1"), Decimal("55"), Decimal("0.022")),
    ("93fc7089-7a40-446a-89ac-dba1ab97d442", "TerraMaster 3 (L)", 4701, "/finders/53", 8, 10, Decimal("631.8"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.388Z", Decimal("2.1"), Decimal("95"), Decimal("0.03225")),
    ("b2e473de-8214-4023-964f-c321ca8d26ae", "TerraMaster 4 (L)", 4701, "/finders/55", 8, 10, Decimal("741.3"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.389Z", Decimal("2.1"), Decimal("150"), Decimal("0.0372")),
    ("623cb1dd-aa61-4f7f-aede-7708fb3ce6fb", "TerraMaster 5 (L)", 4701, "/finders/56", 8, 10, Decimal("830.8"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.390Z", Decimal("2.1"), Decimal("205"), Decimal("0.04125")),
    ("e684e5cc-d05c-4ddd-a664-279d52731287", "TerraMaster 6 (L)", 4701, "/finders/57", 8, 10, Decimal("885.6"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.391Z", Decimal("2.1"), Decimal("260"), Decimal("0.04372")),
    ("7b65a3ed-09aa-4376-872b-69fcc768fc0b", "TerraMaster 7 (L)", 4701, "/finders/58", 8, 10, Decimal("925.4"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.392Z", Decimal("2.1"), Decimal("320"), Decimal("0.04552")),
    ("8ecfc2a0-44a0-4eca-8b63-9ff020f14224", "TerraMaster 8 (L)", 4701, "/finders/59", 8, 10, Decimal("1000"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.393Z", Decimal("2.1"), Decimal("390"), Decimal("0.0489")),
    ("912c03b7-82a1-41ce-8afa-bf6e8d35ac0c", "Ziplex TK320 Seeker, SGA Edition (L)", 1963, "/finders/93", 8, 10, Decimal("870.7"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.394Z", Decimal("0.55"), Decimal("233.25"), Decimal("0.02151")),
    ("f2910cea-d2de-4175-b759-ed346756932a", "Ziplex A10 (L)", 406, "/finders/63", 8, 10, Decimal("204"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.395Z", Decimal("1.5"), Decimal("50"), Decimal("0.015")),
    ("26fab5bc-8c62-4d2b-a8f3-a9f970475c17", "Ziplex VRX2000 Seeker (L)", 1963, "/finders/94", 8, 10, Decimal("925.4"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.395Z", Decimal("1.2"), Decimal("339"), Decimal("0.02323")),
    ("d8e1d355-b87a-4241-aeb0-db085f4bc3e3", "Ziplex VRX3000 Seeker (L)", 1963, "/finders/95", 8, 10, Decimal("1000"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.396Z", Decimal("1.1"), Decimal("387"), Decimal("0.02507")),
    ("e9e2f73a-cdc8-4047-9802-cbfd1a7f0f56", "Ziplex A19 (L)", 406, "/finders/66", 8, 10, Decimal("303.5"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.397Z", Decimal("1.5"), Decimal("53"), Decimal("0.018")),
    ("1a524d56-c43b-4cb5-8a88-4e28c0a6755d", "Omegaton Detectonator MD-10", 408, "/finders/34", 8, 10, Decimal("204"), None, True, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.377Z", Decimal("1"), Decimal("3"), Decimal("0.01")),
    ("d54d91e8-3c1e-4fff-9c3e-97cc4d5662ff", "Omegaton Detectonator MD-20", 408, "/finders/35", 8, 10, Decimal("223.9"), None, True, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.378Z", Decimal("2"), Decimal("26"), Decimal("0.009")),
    ("f63050b2-dd61-4c88-bfcd-570bf1f1c94c", "Omegaton Detectonator MD-30", 408, "/finders/36", 8, 10, Decimal("333.4"), None, True, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.379Z", Decimal("2"), Decimal("40"), Decimal("0.0086")),
    ("4f855541-2907-4ff6-ab5c-517d3cf098d7", "Omegaton Detectonator MD-40", 408, "/finders/37", 8, 10, Decimal("373.1"), None, True, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.380Z", Decimal("1"), Decimal("56"), Decimal("0.0083")),
    ("be9e7c5e-35fd-4168-8ff5-1fda79056362", "Omegaton Detectonator MD-50", 408, "/finders/38", 8, 10, Decimal("492.6"), None, True, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.380Z", Decimal("1"), Decimal("64"), Decimal("0.008")),
    ("c8ee671c-4859-48e4-8c7e-208887e4facc", "Ziplex Z5 Seeker (L)", 1963, "/finders/97", 8, 10, Decimal("303.5"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.398Z", Decimal("1.3"), Decimal("29.8"), Decimal("0.00927")),
    ("ca592e84-40a0-448e-9703-8b6503d347ec", "Ziplex Z10 Seeker (L)", 1963, "/finders/98", 8, 10, Decimal("403"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.398Z", Decimal("1.2"), Decimal("55"), Decimal("0.01105")),
    ("818c3505-bd4b-4189-a1f8-647454da8824", "Ziplex Z10 Seeker, SGA Edition (L)", 1963, "/finders/99", None, 10, Decimal("0"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.399Z", Decimal("0.6"), Decimal("55"), Decimal("0.01105")),
    ("24847fbf-2538-4de6-b8a3-3b72ae2776ca", "Ziplex Z15 Seeker (L)", 1963, "/finders/100", 8, 10, Decimal("477.6"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.400Z", Decimal("1.3"), Decimal("80"), Decimal("0.01279")),
    ("bef7b264-23d5-4348-b37b-40c575df6355", "Ziplex Z25 Seeker (L)", 1963, "/finders/102", 8, 10, Decimal("626.9"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.400Z", Decimal("1.4"), Decimal("172.4"), Decimal("0.01623")),
    ("7fa7bf15-6063-477b-a55f-ecd3a7838bca", "ROCTEC M1-LF Finder (L)", None, "/finders/42", 8, 15, Decimal("900.5"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.401Z", Decimal("1.75"), Decimal("45"), Decimal("0.024")),
    ("8d381606-7266-492e-b883-b1f21d0ed3fd", "Sabad Finder M5 (L)", None, "/finders/50", None, 10, Decimal("0"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.383Z", Decimal("2.1"), Decimal("118"), Decimal("0.0145")),
    ("4a49a919-e14a-4e22-b8c3-4bf723c11531", "Imperium Detectonator X2 (L)", None, "/finders/27", 8, 1, Decimal("626.9"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.404Z", Decimal("2.8"), Decimal("170"), Decimal("0.0325")),
    ("3c826f33-b690-4926-bd56-f48151f4eeb9", "Imperium Trainee Finder (L)", None, "/finders/28", 9, 1, Decimal("204"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.404Z", Decimal("1.6"), Decimal("0.1"), Decimal("0.0025")),
    ("7c3e50d2-ec76-4ac8-94d2-2e5840e17d6c", "Locator MK1 (L)", None, "/finders/30", 8, 1, Decimal("104.5"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.405Z", Decimal("1.5"), Decimal("0.1"), Decimal("0.00239")),
    ("a19ae2ac-4394-4f36-9fe4-2e1baf3655fc", "PaySafe Finder (L)", 1963, "/finders/39", 8, 1, Decimal("303.5"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.406Z", Decimal("2.5"), Decimal("6.2"), Decimal("0.01213")),
    ("371f270f-b23e-45a6-baae-d0df22ae7e8a", "Ziplex Z20 Seeker (L)", 1963, "/finders/101", 8, 10, Decimal("552.3"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.407Z", Decimal("1.4"), Decimal("126.2"), Decimal("0.01452")),
    ("3b8fb49c-9d21-4000-bbee-008dc079b44e", "Sabad Finder Beginner (L)", None, "/finders/45", 8, 1, Decimal("104.5"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.408Z", Decimal("1.6"), Decimal("0.08"), Decimal("0.00239")),
    ("f68972eb-c664-44d8-b317-29eb8f1eb9dd", "TerraMaster Trainer (L)", 4701, "/finders/61", 8, 1, Decimal("104.5"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.408Z", Decimal("2.1"), Decimal("0.4"), Decimal("0.0075")),
    ("01bd9bb7-41bc-4242-abc7-3bc3bf5ed183", "TerraMaster TT (L)", 4701, "/finders/62", 8, 1, Decimal("104.5"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.409Z", Decimal("1.5"), Decimal("0.1"), Decimal("0.00239")),
    ("1e3ceb51-aacf-47b3-9759-6a92b6420ff7", "Ziplex A22 (L)", 406, "/finders/67", 8, 15, Decimal("403"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.410Z", Decimal("1.5"), Decimal("54"), Decimal("0.019")),
    ("74cb100b-8976-4995-b6e2-ee28c1d80942", "Ziplex A25 (L)", 406, "/finders/68", 8, 15, Decimal("502.5"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.411Z", Decimal("1.5"), Decimal("55"), Decimal("0.02")),
    ("bb0a1028-b0c6-43e1-aca4-9b1db6c6e9e0", "Finder F-214 (L)", 406, "/finders/24", 8, 10, Decimal("651.8"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.412Z", Decimal("0.7"), Decimal("231.2"), Decimal("0.01759")),
    ("f573bebc-c731-4342-a384-c672ca5c9ec4", "Ziplex B35 (L)", 406, "/finders/73", 8, 20, Decimal("502.5"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.413Z", Decimal("1.5"), Decimal("50"), Decimal("0.03")),
    ("ca8c0a96-f4c2-47c9-bd16-8565c7406f79", "Ziplex B40 (L)", 406, "/finders/74", 8, 22, Decimal("522.4"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.414Z", Decimal("1.5"), Decimal("51"), Decimal("0.031")),
    ("3a6bf0db-bf29-4f1e-95e4-2935b0b2f9ab", "Ziplex B50 (L)", 406, "/finders/75", 8, 24, Decimal("542.3"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.415Z", Decimal("1.5"), Decimal("52"), Decimal("0.032")),
    ("4e05966a-ea27-4833-b2a5-6365c6ac14a8", "Sabad Finder M4 (L)", None, "/finders/49", 8, 10, Decimal("477.6"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.416Z", Decimal("1.9"), Decimal("78"), Decimal("0.01279")),
    ("fb027526-32c2-4b4f-9ff2-394e8490549e", "Ziplex C70 (L)", 406, "/finders/80", 8, 30, Decimal("363.2"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.419Z", Decimal("1.5"), Decimal("46"), Decimal("0.012")),
    ("b6b68ae5-19a2-4a40-8d94-b0e925f4a1e0", "Ziplex D44 (L)", 406, "/finders/82", 8, 20, Decimal("900.5"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.420Z", Decimal("1.5"), Decimal("46"), Decimal("0.032")),
    ("8ee1eeb8-f633-4886-a82f-b530e1dae9aa", "TerraMaster 8 Gold Rush", 6914, "/finders/60", 8, 10, Decimal("1000"), None, True, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.416Z", Decimal("2.1"), Decimal("390"), Decimal("0.0489")),
    ("45ab57a1-0620-4942-a5b7-3ce996abca7e", "Ziplex D52 (L)", 406, "/finders/83", 8, 25, Decimal("990"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.420Z", Decimal("1.5"), Decimal("55"), Decimal("0.03")),
    ("e3baf5c5-c579-4076-8e4e-de8cea0a9027", "Ziplex A16 (L)", 406, "/finders/65", 8, 10, Decimal("253.8"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.421Z", Decimal("1.5"), Decimal("52"), Decimal("0.017")),
    ("90b2afb1-06d9-4c85-82e9-5771ddb9456b", "Ziplex A33 (L)", 406, "/finders/71", 8, 10, Decimal("801"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.422Z", Decimal("1.5"), Decimal("58"), Decimal("0.023")),
    ("2f957df1-6599-436e-bda1-55164b89385c", "Ziplex P30 (L)", 406, "/finders/86", 8, 30, Decimal("701.5"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.423Z", Decimal("0.3"), Decimal("10"), Decimal("0.0016")),
    ("68698e2d-1eff-4742-a556-227dc9fdbca0", "Ziplex P50 (L)", 406, "/finders/87", 8, 50, Decimal("701.5"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.424Z", Decimal("0.3"), Decimal("10"), Decimal("0.00266")),
    ("5f70836d-da8a-4b79-ae3a-4a44f7171f24", "Ziplex A35 (L)", 406, "/finders/72", None, 10, Decimal("900.5"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.424Z", Decimal("1.5"), Decimal("59"), Decimal("0.024")),
    ("c583ff11-0442-426a-88f1-ef210532b3e6", "TerraMaster 3 Gold Rush", 6914, "/finders/54", 8, 10, Decimal("631.8"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.388Z", Decimal("2.1"), Decimal("95"), Decimal("0.03225")),
    ("119feb45-507c-41cf-89c2-c9f849741c38", "Qura Seeker(L)", None, "/finders/109", None, 0, Decimal("0"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.429Z", Decimal("0"), Decimal("0"), Decimal("0")),
    ("3ca3276b-5108-4703-8ead-d0b77aeceea1", "Adventurer's Finder (L)", None, "/finders/108", 8, 4, Decimal("303.5"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.430Z", Decimal("1.1"), Decimal("20"), Decimal("0.00239")),
    ("26f02b05-02a3-4385-908a-e9f79206de60", "Ziplex A28 (L)", 406, "/finders/69", 8, 15, Decimal("602"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.431Z", Decimal("1.5"), Decimal("56"), Decimal("0.021")),
    ("f44e2f31-180d-4140-9172-3f787964fd4c", "Ziplex P20, TWEN Edition", None, "/finders/85", 8, 20, Decimal("701.5"), None, True, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.436Z", Decimal("0.3"), Decimal("100"), Decimal("0.001")),
    ("a0429970-961f-4fa3-bb85-a81fc49b11a5", "Ziplex A31 (L)", 406, "/finders/70", 8, 15, Decimal("701.5"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.432Z", Decimal("1.5"), Decimal("57"), Decimal("0.022")),
    ("4f00d8ed-bc6d-4aeb-935a-f13047f86839", "Ziplex B70 (L)", 406, "/finders/77", 8, 28, Decimal("582.1"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.433Z", Decimal("1.5"), Decimal("54"), Decimal("0.034")),
    ("de55e085-ba55-494e-8165-b94fdac69ccb", "Ziplex P20 (L)", 406, "/finders/84", 8, 20, Decimal("701.5"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.435Z", Decimal("0.3"), Decimal("10"), Decimal("0.001")),
    ("c6b67a90-eadf-43bc-8549-e8c92c6ac097", "Ziplex B60 (L)", 406, "/finders/76", 8, 26, Decimal("562.2"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.433Z", Decimal("1.5"), Decimal("53"), Decimal("0.033")),
    ("6e261fa5-74e5-43b2-9f36-ebedee9333cd", "Ziplex C50 (L)", 406, "/finders/78", 8, 30, Decimal("283.6"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.434Z", Decimal("1.5"), Decimal("40"), Decimal("0.012")),
    ("3a3f2023-4cf4-499d-b7c4-9669f51c3c8f", "Ziplex P160 (L)", 406, "/finders/89", 8, 160, Decimal("701.5"), None, False, False, "2026-10-04T16:06:45.903Z", "2026-10-15T13:02:52.342Z", Decimal("0.3"), Decimal("10"), Decimal("0.0075")),
    ("43942a00-a361-4ed3-b8b3-4fb382b10e9e", "ROCTEC C0UGR Finder (L)", 5120, "/finders/41", 8, 26, Decimal("562.2"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.366Z", Decimal("1.75"), Decimal("50"), Decimal("0.033")),
    ("4e1b2953-24ba-42ad-a9d7-6fdb56188ee3", "DSEC Seeker L2 (L)", 406, "/finders/6", None, 10, Decimal("213.9"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.370Z", Decimal("1.85"), Decimal("18.6"), Decimal("0.01122")),
    ("8984ebad-6c4f-4c9f-acf3-8b330193eea8", "Finder F-211 (L)", 406, "/finders/18", 8, 10, Decimal("472.6"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.370Z", Decimal("0.7"), Decimal("121.2"), Decimal("0.01306")),
    ("47a0ff81-333d-4fbd-b5c4-5f8d06447dcc", "Sabad Finder M1 (L)", None, "/finders/46", 8, 10, Decimal("204"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.382Z", Decimal("1.5"), Decimal("2"), Decimal("0.00751")),
    ("efc41c04-b908-410a-9987-1d83bdafbad4", "Ziplex TK120 Seeker (L)", 1963, "/finders/90", 8, 10, Decimal("701.5"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.384Z", Decimal("1.2"), Decimal("218.6"), Decimal("0.01803")),
    ("e918328f-ea61-4ec4-9e95-69f15c6513b3", "Genesis Star Rookie Finder (L)", 7714, "/finders/26", 8, 1, Decimal("104.5"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.402Z", Decimal("1.5"), Decimal("0.1"), Decimal("0.002")),
    ("fc16e97a-6de5-4fe0-bf92-20cf3b0589ad", "Sabad Finder M2 (L)", None, "/finders/47", 8, 10, Decimal("303.5"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.412Z", Decimal("1.6"), Decimal("26"), Decimal("0.00927")),
    ("70f4e54f-5152-469e-853e-cacd779c9579", "Ziplex A13 (L)", 406, "/finders/64", 8, 10, Decimal("223.9"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.417Z", Decimal("1.5"), Decimal("51"), Decimal("0.016")),
    ("536f9892-204d-4344-858b-b1b974fe0b71", "Ziplex C65 (L)", 406, "/finders/79", 8, 30, Decimal("313.5"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.418Z", Decimal("1.5"), Decimal("44"), Decimal("0.012")),
    ("c9d749d6-ca3b-4e22-8b3a-91be48728898", "Ziplex D33 (L)", 406, "/finders/81", 8, 10, Decimal("801"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.425Z", Decimal("1.5"), Decimal("44"), Decimal("0.034")),
    ("94259f88-bfce-43a2-80d7-9e88972540d1", "Ziplex TK220 Seeker (L)", 1963, "/finders/91", 8, 10, Decimal("776.1"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.426Z", Decimal("1.2"), Decimal("264.8"), Decimal("0.0198")),
    ("b7a804e8-1ec5-4d92-8e4a-668743755c1a", "Initiate's Finder (L)", None, "/finders/104", 8, 1, Decimal("104.5"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.427Z", Decimal("1.5"), Decimal("0.1"), Decimal("0.00239")),
    ("ec071eb8-f03e-47ff-8de6-3c4e9e91e9e6", "Exceptional Ziplex P400 (L)", None, "/finders/107", 8, 400, Decimal("701.5"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.428Z", Decimal("0.3"), Decimal("10"), None),
    ("8a13e900-f642-490c-aaeb-51cb65e100ce", "Ziplex P85 (L)", 406, "/finders/88", 8, 85, Decimal("701.5"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.437Z", Decimal("0.3"), Decimal("10"), Decimal("0.004")),
    ("cb1409c8-7dca-4383-bd9a-6fab31c3c70e", "Mayhem Ziplex P30", None, "/finders/105", 8, 30, Decimal("701.5"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.437Z", Decimal("0.3"), Decimal("100"), Decimal("0.0016")),
    ("63aec3ab-d954-41ca-a648-166450936ce7", "Punk Metal Detector (L)", None, "/finders/40", 8, 1, Decimal("104.5"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.356Z", Decimal("1.5"), Decimal("0.1"), Decimal("0.00239")),
    ("289a1740-d16d-4a28-960f-1af85c6bbf33", "Sabad Finder M3 (L)", None, "/finders/48", None, 10, Decimal("0"), None, False, False, "2026-10-04T16:06:45.904Z", "2026-10-15T13:02:52.383Z", Decimal("1.7"), Decimal("55"), Decimal("0.01105")),
    ("5313a63b-bf5f-4e4c-aad2-5c3912ab2e60", "Ziplex Z1 Seeker", 1963, "/finders/96", 8, 10, Decimal("204"), None, False, False, "2026-10-04T16:06:45.905Z", "2026-10-15T13:02:52.403Z", Decimal("1.3"), Decimal("2.4"), Decimal("0.00751")),
]


def upgrade() -> None:
    op.create_table(
        "finder",
        sa.Column("item_id", sa.Uuid(), nullable=False),
        sa.Column("use_per_minute", sa.Integer(), nullable=True),
        sa.Column("depth", sa.Numeric(), nullable=True),
        sa.Column("range", sa.Numeric(), nullable=True),
        sa.Column("ammo_burn", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["item_id"], ["item.id"]),
        sa.PrimaryKeyConstraint("item_id"),
    )


    item_table = sa.table(
        "item",
        sa.column("id", sa.Uuid()),
        sa.column("name", sa.String()),
        sa.column("img_id", sa.Integer()),
        sa.column("weight", sa.Numeric()),
        sa.column("is_active", sa.Boolean()),
        sa.column("nexus_url", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("is_rare", sa.Boolean()),
        sa.column("is_untradeable", sa.Boolean()),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    finder_table = sa.table(
        "finder",
        sa.column("item_id", sa.Uuid()),
        sa.column("use_per_minute", sa.Integer()),
        sa.column("depth", sa.Numeric()),
        sa.column("ammo_burn", sa.Integer()),
    )
    economy_table = sa.table(
        "economy",
        sa.column("item_id", sa.Uuid()),
        sa.column("tt", sa.Numeric()),
        sa.column("decay", sa.Numeric()),
    )

    op.bulk_insert(
        item_table,
        [
            {
                "id": UUID(row[0]),
                "name": row[1],
                "img_id": row[2],
                "weight": row[12],
                "is_active": True,
                "nexus_url": row[3],
                "description": row[7],
                "is_rare": row[8],
                "is_untradeable": row[9],
                "created_at": _timestamp(row[10]),
                "updated_at": _timestamp(row[11]),
            }
            for row in FINDERS
        ],
    )
    op.bulk_insert(
        finder_table,
        [
            {
                "item_id": UUID(row[0]),
                "use_per_minute": row[4],
                "depth": row[6],
                "ammo_burn": row[5],
            }
            for row in FINDERS
        ],
    )
    op.bulk_insert(
        economy_table,
        [
            {
                "item_id": UUID(row[0]),
                "tt": row[13],
                "decay": row[14],
            }
            for row in FINDERS
        ],
    )


def downgrade() -> None:
    bind = op.get_bind()
    item_ids = [UUID(row[0]) for row in FINDERS]

    economy_table = sa.table("economy", sa.column("item_id", sa.Uuid()))
    finder_table = sa.table("finder", sa.column("item_id", sa.Uuid()))
    item_table = sa.table("item", sa.column("id", sa.Uuid()))
    bind.execute(economy_table.delete().where(economy_table.c.item_id.in_(item_ids)))
    bind.execute(finder_table.delete().where(finder_table.c.item_id.in_(item_ids)))
    bind.execute(item_table.delete().where(item_table.c.id.in_(item_ids)))
    op.drop_table("finder")
