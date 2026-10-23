"""add excavators and efficiency details

Revision ID: 005_create_excavator
Revises: 004_create_finder
Create Date: 2026-10-22
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

import sqlalchemy as sa
from alembic import op

revision = "005_create_excavator"
down_revision = "004_create_finder"
branch_labels = None
depends_on = None

EXCAVATOR_TYPE_ID = UUID("a81ff2c2-6d26-49bd-9dd7-73c38c64773d")


def _timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


EXCAVATORS = [
    ("2e4c84fb-8bb2-485d-bc51-1cd9f02ed245", "ARD Excavator M1 (L)", None, "/excavators/3", 19, Decimal("6.79999999999999982236431605997495353221893310546875"), None, False, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.633Z"), Decimal("1.8000000000000000444089209850062616169452667236328125"), Decimal("2.399999999999999911182158029987476766109466552734375"), Decimal("0.003000000000000000062450045135165055398829281330108642578125")),
    ("6ce91e62-5e18-4927-8846-c5024e85a075", "ARD Excavator M2 (L)", None, "/excavators/4", 24, Decimal("9.199999999999999289457264239899814128875732421875"), None, False, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.636Z"), Decimal("1.600000000000000088817841970012523233890533447265625"), Decimal("54"), Decimal("0.0126299999999999988664622918577151722274720668792724609375")),
    ("b9d9ee71-731e-4e37-ab7b-554f7c45eb60", "ARD Excavator M5 (L)", None, "/excavators/7", 26, Decimal("12.800000000000000710542735760100185871124267578125"), None, False, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.637Z"), Decimal("1.899999999999999911182158029987476766109466552734375"), Decimal("132"), Decimal("0.023359999999999998820943147848083754070103168487548828125")),
    ("1f767f45-e1e3-429d-a5f5-f59c125e9d6f", "Demonic Excavator MK-I (L)", None, "/excavators/8", 17, Decimal("0.59999999999999997779553950749686919152736663818359375"), None, False, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.638Z"), Decimal("1"), Decimal("5"), Decimal("0.001000000000000000020816681711721685132943093776702880859375")),
    ("8f759bb7-af68-4847-9067-aef630d8c52f", "Earth Excavator ME/01", 409, "/excavators/9", 19, Decimal("6.79999999999999982236431605997495353221893310546875"), None, False, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.639Z"), Decimal("2"), Decimal("2.399999999999999911182158029987476766109466552734375"), Decimal("0.003000000000000000062450045135165055398829281330108642578125")),
    ("87451fcf-e4a1-4ccb-94af-8c74f8235f02", "eMINE E (L)", 3043, "/excavators/10", 27, Decimal("12"), None, False, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.640Z"), Decimal("1.5"), Decimal("85"), Decimal("0.0210100000000000008970602038971264846622943878173828125")),
    ("39398bcd-e28c-4356-9de5-152e61ad3381", "Genesis Star Basic Excavator (L)", 409, "/excavators/13", 19, Decimal("6.79999999999999982236431605997495353221893310546875"), None, False, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.641Z"), Decimal("2"), Decimal("3"), Decimal("0.003000000000000000062450045135165055398829281330108642578125")),
    ("9e3ac37b-cd8b-402e-bff1-bb082d72adaf", "Genesis Star Earth Excavator ME/02", 409, "/excavators/14", 22, Decimal("7.20000000000000017763568394002504646778106689453125"), None, False, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.642Z"), Decimal("2"), Decimal("8"), Decimal("0.005000000000000000104083408558608425664715468883514404296875")),
    ("e2aaad40-1322-428c-9c4b-edde7872b861", "Genesis Star Earth Excavator ME/05", 409, "/excavators/17", 23, Decimal("8.800000000000000710542735760100185871124267578125"), None, False, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.643Z"), Decimal("1"), Decimal("66"), Decimal("0.008000000000000000166533453693773481063544750213623046875")),
    ("89b8d73f-2ce7-4593-83a5-d51d6568ea8d", "Imperium Extirpater v1", 5641, "/excavators/26", 19, Decimal("6.79999999999999982236431605997495353221893310546875"), None, False, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.650Z"), Decimal("1"), Decimal("2.20000000000000017763568394002504646778106689453125"), Decimal("0.00340000000000000024424906541753443889319896697998046875")),
    ("fd6948b0-4aa2-45d4-bf45-932761c7a816", "Island Earth Excavator ME/01", 409, "/excavators/28", 19, Decimal("6.79999999999999982236431605997495353221893310546875"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.651Z"), Decimal("2"), Decimal("2.399999999999999911182158029987476766109466552734375"), Decimal("0.003000000000000000062450045135165055398829281330108642578125")),
    ("070f5fe8-ba95-4aa3-888d-08c1699adf8d", "Punk Digger (L)", 410, "/excavators/32", 19, Decimal("6.79999999999999982236431605997495353221893310546875"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.652Z"), Decimal("2"), Decimal("3"), Decimal("0.003000000000000000062450045135165055398829281330108642578125")),
    ("6f509fcd-0c88-4c87-bbd6-9279ba57925f", "Genesis Star Excavator, Adjusted", 409, "/excavators/19", 23, Decimal("12.800000000000000710542735760100185871124267578125"), None, True, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.646Z"), Decimal("2"), Decimal("18"), Decimal("0.005000000000000000104083408558608425664715468883514404296875")),
    ("de13f136-93e9-4299-9b8c-1859ecaa3b4c", "Genesis Star Excavator, Adjusted, TWEN Edition", 409, "/excavators/20", 23, Decimal("16.800000000000000710542735760100185871124267578125"), None, True, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.646Z"), Decimal("1"), Decimal("100"), Decimal("0.005000000000000000104083408558608425664715468883514404296875")),
    ("7676251a-cab9-4387-971c-fbf4a4a97740", "Genesis Star Excavator, Improved, TWEN Edition", 409, "/excavators/22", 24, Decimal("19.199999999999999289457264239899814128875732421875"), None, True, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.647Z"), Decimal("1"), Decimal("200"), Decimal("0.005000000000000000104083408558608425664715468883514404296875")),
    ("156e9b4d-b204-41fc-95d1-1d79e41aa31c", "Genesis Star Excavator, Modified", 409, "/excavators/23", 27, Decimal("20.800000000000000710542735760100185871124267578125"), None, True, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.648Z"), Decimal("0.8000000000000000444089209850062616169452667236328125"), Decimal("4362"), Decimal("0.032120000000000002715605518233132897876203060150146484375")),
    ("a8e5806a-5033-4ae0-aa52-ab2c9d2ed1fc", "Genesis Star Excavator, Modified, TWEN Edition", None, "/excavators/24", 27, Decimal("24.800000000000000710542735760100185871124267578125"), None, True, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.649Z"), Decimal("0.8000000000000000444089209850062616169452667236328125"), Decimal("400"), Decimal("0.032120000000000002715605518233132897876203060150146484375")),
    ("2943a6db-c9c8-4ac7-b22b-d36a105b072f", "Resource Extractor RE-101", 407, "/excavators/33", 20, Decimal("7.20000000000000017763568394002504646778106689453125"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.653Z"), Decimal("2"), Decimal("5.5"), Decimal("0.00600000000000000012490009027033011079765856266021728515625")),
    ("d0ddf859-c366-4720-b659-2e1c3b53320c", "Resource Extractor RE-204 (L)", 407, "/excavators/41", 26, Decimal("12.800000000000000710542735760100185871124267578125"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.653Z"), Decimal("1.5"), Decimal("195"), Decimal("0.0233100000000000008582023980352460057474672794342041015625")),
    ("c2cdbf6b-2447-40d7-9973-1d3a18e9160e", "Resource Extractor RE-204 Adapted (L)", None, "/excavators/42", 34, Decimal("12.800000000000000710542735760100185871124267578125"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.654Z"), Decimal("1.5"), Decimal("195"), Decimal("0.0233100000000000008582023980352460057474672794342041015625")),
    ("d01d5798-1396-471b-a98a-2a0fdc053f77", "Resource Extractor RE-301 (L)", 407, "/excavators/44", 24, Decimal("14"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.655Z"), Decimal("3.899999999999999911182158029987476766109466552734375"), Decimal("83"), Decimal("0.0250300000000000001654232306691483245231211185455322265625")),
    ("87c06b0f-2d8c-4732-935b-86c12839caf2", "Rock Ripper 1 (L)", 4703, "/excavators/45", 22, Decimal("6.5999999999999996447286321199499070644378662109375"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.656Z"), Decimal("1.399999999999999911182158029987476766109466552734375"), Decimal("2"), Decimal("0.0028000000000000004052314039881821372546255588531494140625")),
    ("a2ad06ea-cfd1-446e-b09d-39c1625a73e1", "Rock Ripper 2 (L)", 4703, "/excavators/46", 24, Decimal("7.70000000000000017763568394002504646778106689453125"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.656Z"), Decimal("1.399999999999999911182158029987476766109466552734375"), Decimal("22"), Decimal("0.01128999999999999968858244159264359041117131710052490234375")),
    ("1abc1324-d298-44b1-abf4-03b88e17b628", "Rock Ripper 3 (L)", 4703, "/excavators/47", 24, Decimal("8.800000000000000710542735760100185871124267578125"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.657Z"), Decimal("1.399999999999999911182158029987476766109466552734375"), Decimal("44"), Decimal("0.01453999999999999910571535366443640668876469135284423828125")),
    ("3116dd3b-1378-4c7f-bac4-de59587e975c", "Rock Ripper Trainer (L)", 4703, "/excavators/50", 17, Decimal("6"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.659Z"), Decimal("1.399999999999999911182158029987476766109466552734375"), Decimal("0.200000000000000011102230246251565404236316680908203125"), Decimal("0.002740000000000000247857290247566197649575769901275634765625")),
    ("6a606293-7bef-4bec-927e-c4099cf38d88", "Rock Ripper TT (L)", None, "/excavators/51", 19, Decimal("6.79999999999999982236431605997495353221893310546875"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.660Z"), Decimal("2"), Decimal("3"), Decimal("0.003000000000000000062450045135165055398829281330108642578125")),
    ("9d69f801-b536-498c-9e7e-b30d9b7b0f87", "Exhumer Mk1", None, "/excavators/11", 19, Decimal("6.79999999999999982236431605997495353221893310546875"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.663Z"), Decimal("2"), Decimal("2.399999999999999911182158029987476766109466552734375"), Decimal("0.003000000000000000062450045135165055398829281330108642578125")),
    ("d8619cd7-5539-4f2e-afad-600025c9b036", "ARD Excavator A-100 (L)", None, "/excavators/1", 19, Decimal("6.79999999999999982236431605997495353221893310546875"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.664Z"), Decimal("2"), Decimal("3"), Decimal("0.003000000000000000062450045135165055398829281330108642578125")),
    ("274bd7c2-9c03-47a9-bf97-e610d4bd69fd", "ARD Excavator Beginner (L)", None, "/excavators/2", 17, Decimal("1.1999999999999999555910790149937383830547332763671875"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.665Z"), Decimal("1.399999999999999911182158029987476766109466552734375"), Decimal("0.05000000000000000277555756156289135105907917022705078125"), Decimal("0.0030999999999999998910593657086565144709311425685882568359375")),
    ("c27ce5e6-6585-461a-8255-8713cb018e0e", "Genesis Rookie Extractor (L)", None, "/excavators/12", 17, Decimal("1.1999999999999999555910790149937383830547332763671875"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.666Z"), Decimal("1.5"), Decimal("0.01000000000000000020816681711721685132943093776702880859375"), Decimal("0.003129999999999999969746422578964484273456037044525146484375")),
    ("69050f2e-5054-4267-8db2-9eabe731295d", "Genesis Star Earth Excavator ME/04", 409, "/excavators/16", 23, Decimal("8"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.667Z"), Decimal("1"), Decimal("55"), Decimal("0.00830000000000000008604228440844963188283145427703857421875")),
    ("13da1b59-7acf-4070-934a-113aeef4497a", "Genesis Star Rookie Extractor (L)", 409, "/excavators/25", 17, Decimal("1.1999999999999999555910790149937383830547332763671875"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.667Z"), Decimal("1.5"), Decimal("0.1000000000000000055511151231257827021181583404541015625"), Decimal("0.001000000000000000020816681711721685132943093776702880859375")),
    ("c60b129a-1cda-40ee-a8dc-251c2ae1f0c2", "Initiate's Excavator (L)", 5641, "/excavators/27", 19, Decimal("6.79999999999999982236431605997495353221893310546875"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.668Z"), Decimal("2"), Decimal("3"), Decimal("0.003000000000000000062450045135165055398829281330108642578125")),
    ("445b1b26-1fa0-4bb8-8f53-813ef59ea5a8", "Lost Soul Savior (L)", 410, "/excavators/29", 26, Decimal("19.199999999999999289457264239899814128875732421875"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.669Z"), Decimal("2.399999999999999911182158029987476766109466552734375"), Decimal("64"), Decimal("0.0120000000000000002498001805406602215953171253204345703125")),
    ("43ff32b9-e18c-4ba6-85fc-994fb5dcc14c", "NI Basic Excavator (L)", 409, "/excavators/30", 19, Decimal("6.79999999999999982236431605997495353221893310546875"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.670Z"), Decimal("2"), Decimal("3"), Decimal("0.003000000000000000062450045135165055398829281330108642578125")),
    ("50fcab3d-1b57-4bfc-a7a4-f28b16b3e9ce", "Resource Extractor RE-103", 407, "/excavators/35", 23, Decimal("8.4000000000000003552713678800500929355621337890625"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.671Z"), Decimal("2"), Decimal("50"), Decimal("0.01600000000000000033306690738754696212708950042724609375")),
    ("4ea6a61a-b3e9-409d-803f-a932fc8f555b", "Resource Extractor RE-104", 407, "/excavators/36", 24, Decimal("9.5999999999999996447286321199499070644378662109375"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.671Z"), Decimal("1.5"), Decimal("65"), Decimal("0.017200000000000000011102230246251565404236316680908203125")),
    ("e6d79b07-7287-44ce-8127-c69b4c4058e9", "Resource Extractor RE-105", 407, "/excavators/37", 26, Decimal("10.800000000000000710542735760100185871124267578125"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.672Z"), Decimal("1.3000000000000000444089209850062616169452667236328125"), Decimal("80"), Decimal("0.0221499999999999995503596750268116011284291744232177734375")),
    ("13f2679f-19f5-424e-96a0-d50ff7a909f6", "Genesis Star Excavator, Improved", 409, "/excavators/21", 24, Decimal("15.199999999999999289457264239899814128875732421875"), None, True, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.663Z"), Decimal("2"), Decimal("27"), Decimal("0.005000000000000000104083408558608425664715468883514404296875")),
    ("1609eb13-61ad-4122-935e-c0f3061d737d", "Resource Extractor RE-201 (L)", 407, "/excavators/38", 25, Decimal("9.199999999999999289457264239899814128875732421875"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.673Z"), Decimal("1.6999999999999999555910790149937383830547332763671875"), Decimal("89"), Decimal("0.0126299999999999988664622918577151722274720668792724609375")),
    ("a7002f5a-04a2-416a-a621-2fd9bbf1c077", "Resource Extractor RE-202 (L)", 407, "/excavators/39", 25, Decimal("10.4000000000000003552713678800500929355621337890625"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.674Z"), Decimal("1.5"), Decimal("110"), Decimal("0.01614000000000000156763491077072103507816791534423828125")),
    ("0fd6ea6c-56db-4464-9fcd-8f3e186aabc2", "Rock Ripper 4 (L)", 4703, "/excavators/49", None, None, None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.679Z"), Decimal("1.399999999999999911182158029987476766109466552734375"), Decimal("70"), Decimal("0.0173199999999999985911269817506763502024114131927490234375")),
    ("255d365e-9501-424f-93bd-a7638906e93f", "Genesis Star Earth Excavator ME/05, SGA Edition", None, "/excavators/18", 33, Decimal("8.800000000000000710542735760100185871124267578125"), None, True, False, _timestamp("2026-10-11T23:22:04.280Z"), _timestamp("2026-10-12T10:19:18.644Z"), Decimal("1"), Decimal("66"), Decimal("0.008000000000000000166533453693773481063544750213623046875")),
    ("91d65d8c-fa0b-434c-9db5-3795764920ec", "Rock Ripper 3 Gold Rush", None, "/excavators/48", 29, Decimal("8.5"), None, True, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.658Z"), Decimal("1.399999999999999911182158029987476766109466552734375"), Decimal("44"), Decimal("0.00832999999999999886368673429615228087641298770904541015625")),
    ("319fae35-93ac-475c-a41d-8646d3cd93f1", "Resource Extractor RE-203 (L)", 407, "/excavators/40", 25, Decimal("11.5999999999999996447286321199499070644378662109375"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.674Z"), Decimal("1.5"), Decimal("185"), Decimal("0.0206499999999999982180920454766237526200711727142333984375")),
    ("201464ea-6a0f-40a7-9c3d-be7b094a7a4d", "Resource Extractor RE-205 (L)", None, "/excavators/43", 24, Decimal("14"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.675Z"), Decimal("3.899999999999999911182158029987476766109466552734375"), Decimal("83"), Decimal("0.0250300000000000001654232306691483245231211185455322265625")),
    ("5c4be4b2-c56b-45fe-8959-d0299830191a", "Training Mineral Extractor (L)", 5641, "/excavators/53", 19, Decimal("6.79999999999999982236431605997495353221893310546875"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.676Z"), Decimal("1"), Decimal("0.1000000000000000055511151231257827021181583404541015625"), Decimal("0.00340000000000000024424906541753443889319896697998046875")),
    ("ddeda65c-1d3b-4daf-872f-1acf8993cec6", "Genesis Star Earth Excavator ME/03", 409, "/excavators/15", 22, Decimal("7.20000000000000017763568394002504646778106689453125"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.676Z"), Decimal("2"), Decimal("42"), Decimal("0.0086000000000000000055511151231257827021181583404541015625")),
    ("07791409-b0c5-47c2-9f8a-30bb05df11bf", "Resource Extractor RE-102", 407, "/excavators/34", 22, Decimal("8"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.677Z"), Decimal("2"), Decimal("15"), Decimal("0.0114999999999999998057109706905976054258644580841064453125")),
    ("8a5fb2a5-fded-4e08-a1a1-2c5eff009091", "ARD Excavator M3 (L)", None, "/excavators/5", None, None, None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.678Z"), Decimal("1.75"), Decimal("72"), Decimal("0.01614000000000000156763491077072103507816791534423828125")),
    ("77b2ad61-db89-4e04-9b6f-cb42e15bb161", "ARD Excavator M4 (L)", None, "/excavators/6", None, None, None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.678Z"), Decimal("1.899999999999999911182158029987476766109466552734375"), Decimal("98"), Decimal("0.0206800000000000004651834473179405904375016689300537109375")),
    ("360dd36b-10fa-4c96-b01c-ffb906eba576", "Rookie Rock Ripper", 5679, "/excavators/52", 17, Decimal("6"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.660Z"), Decimal("1.399999999999999911182158029987476766109466552734375"), Decimal("1"), Decimal("0.002740000000000000247857290247566197649575769901275634765625")),
    ("de19aa60-c87c-427e-aeed-e3cb912d2472", "Xtreme Excavator MK-I (L)", 410, "/excavators/54", 17, Decimal("7.5999999999999996447286321199499070644378662109375"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.661Z"), Decimal("1"), Decimal("5"), Decimal("0")),
    ("798db3c3-91de-42ef-882a-27205c5ed2c8", "NI Extractor New Settler Issue (L)", 409, "/excavators/31", 24, Decimal("1.1999999999999999555910790149937383830547332763671875"), None, False, False, _timestamp("2026-10-11T23:22:04.281Z"), _timestamp("2026-10-12T10:19:18.662Z"), Decimal("2"), Decimal("0.1000000000000000055511151231257827021181583404541015625"), Decimal("0.001000000000000000020816681711721685132943093776702880859375")),
]


def upgrade() -> None:
    op.create_table(
        "excavator",
        sa.Column("item_id", sa.Uuid(), nullable=False),
        sa.Column("use_per_minute", sa.Integer(), nullable=True),
        sa.Column("efficiency", sa.Numeric(), nullable=True),
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
        sa.column("type_id", sa.Uuid()),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    excavator_table = sa.table(
        "excavator",
        sa.column("item_id", sa.Uuid()),
        sa.column("use_per_minute", sa.Integer()),
        sa.column("efficiency", sa.Numeric()),
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
                "weight": row[11],
                "is_active": True,
                "nexus_url": row[3],
                "description": row[6],
                "is_rare": row[7],
                "is_untradeable": row[8],
                "type_id": EXCAVATOR_TYPE_ID,
                "created_at": row[9],
                "updated_at": row[10],
            }
            for row in EXCAVATORS
        ],
    )
    op.bulk_insert(
        excavator_table,
        [
            {
                "item_id": UUID(row[0]),
                "use_per_minute": row[4],
                "efficiency": row[5],
            }
            for row in EXCAVATORS
        ],
    )
    op.bulk_insert(
        economy_table,
        [
            {
                "item_id": UUID(row[0]),
                "tt": row[12],
                "decay": row[13],
            }
            for row in EXCAVATORS
        ],
    )


def downgrade() -> None:
    bind = op.get_bind()
    item_ids = [UUID(row[0]) for row in EXCAVATORS]

    economy_table = sa.table("economy", sa.column("item_id", sa.Uuid()))
    excavator_table = sa.table("excavator", sa.column("item_id", sa.Uuid()))
    item_table = sa.table("item", sa.column("id", sa.Uuid()))
    bind.execute(economy_table.delete().where(economy_table.c.item_id.in_(item_ids)))
    bind.execute(excavator_table.delete().where(excavator_table.c.item_id.in_(item_ids)))
    bind.execute(item_table.delete().where(item_table.c.id.in_(item_ids)))
    op.drop_table("excavator")
