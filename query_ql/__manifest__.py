# -*- coding: utf-8 -*-
{
    "name": "Query_Ql",
    "version": "16.0.1.0.0",
    "summary": """ Execute postgreSQL query into Odoo interface ref ==> PostgreSQL Query Deluxe' """,
    "author": "Tanathip Singhanon",
    "support": "boathh31@gmail.com",
    "website": "https://github.com/madara1150/query_ql",
    "depends": ["base", "web", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/query_table_views.xml",
        "datas/data.xml",
    ],
    "assets": {},
    "application": True,
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
    "images": ["static/description/query_ql.jpg"],
}
