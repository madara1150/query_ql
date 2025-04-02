# -*- coding: utf-8 -*-
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class QueryTable(models.Model):
    """Most of the code is from https://apps.odoo.com/apps/modules/16.0/query_deluxe"""

    _name = "query_table"
    _description = "Query Table"

    rowcount = fields.Text(string="Rowcount")
    html = fields.Html(string="HTML")
    display_name = fields.Char(string="Display Name")
    name = fields.Text(string="Query")
    query_type = fields.Selection(
        selection=[
            ("select", "SELECT"),
            ("insert", "INSERT"),
            ("update", "UPDATE"),
            ("delete", "DELETE"),
        ],
        string="Query Type",
        required=True,
        default="select",
    )
    valid_query_name = fields.Text()

    tips = fields.Many2one("tipsqueries", string="Examples")
    tips_description = fields.Text(related="tips.description")

    table = fields.Many2one(
        "ir.model",
        string="Table",
        required=True,
        ondelete="cascade",
    )

    selected_fields = fields.Many2many(
        "ir.model.fields",
        "query_table_fields_rel",
        "query_table_id",
        "field_id",
        string="Fields",
        domain="[('model_id', '=', table)]",
    )

    show_raw_output = fields.Boolean(string="Show the raw output of the query")
    raw_output = fields.Text(string="Raw output")

    @api.model
    def _get_model_tables(self):
        models = self.env["ir.model"].search([])
        return [(model.model, model.name) for model in models]

    def execute(self):
        self = self.sudo()
        self.ensure_one()

        self.show_raw_output = False
        self.raw_output = ""

        self.rowcount = ""
        self.html = "<br></br>"

        self.valid_query_name = ""

        if self.name:

            headers = []
            datas = []

            try:
                self.env.cr.execute(self.name)
            except Exception as e:
                raise UserError(e)

            try:
                if self.env.cr.description:
                    headers = [d[0] for d in self.env.cr.description]
                    datas = self.env.cr.fetchall()
            except Exception as e:
                raise UserError(e)

            rowcount = self.env.cr.rowcount
            self.rowcount = _("{0} row{1} processed").format(
                rowcount, "s" if 1 < rowcount else ""
            )

            if headers and datas:
                self.valid_query_name = self.name
                self.raw_output = datas

                header_html = "<tr style='background-color: #9fdbed; padding: 3px;'> <th style='background-color:white;padding: 3px;'>count</th>"
                header_html += "".join(
                    [
                        "<th style='padding:3px;'>" + str(header) + "</th>"
                        for header in headers
                    ],
                )
                header_html += "</tr>"

                body_html = ""
                i = 0
                for data in datas:
                    i += 1
                    body_line = "<tr style='background-color: {0}'> <td style='background-color: #4681e0;color:white;border-right: 3px solid;'>{1}</td>".format(
                        "#f5c014" if i % 2 == 0 else "white", i
                    )
                    for value in data:
                        display_value = ""
                        if value is not None:
                            display_value = (
                                str(value)
                                .replace("&", "&amp;")
                                .replace("<", "&lt;")
                                .replace(">", "&gt;")
                            )
                        body_line += (
                            "<td style='border-right: 3px solid;'>{0}</td>".format(
                                display_value
                            )
                        )
                    body_line += "</tr>"
                    body_html += body_line

                self.html = """
<table style="text-align: center;border-collapse: collapse;width: 100%;">
  <thead">
    {0}
  </thead>

  <tbody>
    {1}
  </tbody>
</table>
""".format(
                    header_html, body_html
                )

    @api.onchange("query_type", "table", "selected_fields")
    def _onchange_generate_query(self):
        if not self.table:
            self.name = ""
            return

        table_name = self.table.model.replace(".", "_")

        if self.query_type == "select":
            if not self.selected_fields:
                self.name = f"SELECT * FROM {table_name};"
            else:
                field_names = ", ".join(self.selected_fields.mapped("name"))
                self.name = f"SELECT {field_names} FROM {table_name};"

        elif self.query_type == "insert":
            if self.selected_fields:
                field_names = ", ".join(self.selected_fields.mapped("name"))
                values = ", ".join(["%s"] * len(self.selected_fields))
                self.name = (
                    f"INSERT INTO {table_name} ({field_names})\nVALUES ({values});"
                )
            else:
                self.name = f"INSERT INTO {table_name} VALUES (...);"

        elif self.query_type == "update":
            if self.selected_fields:
                field_assignments = ", ".join(
                    [f"{field.name} = %s" for field in self.selected_fields]
                )
                self.name = (
                    f"UPDATE {table_name}\nSET {field_assignments}\nWHERE condition;"
                )
            else:
                self.name = (
                    f"UPDATE {table_name}\nSET column1 = value1\nWHERE condition;"
                )

        elif self.query_type == "delete":
            self.name = f"DELETE FROM {table_name}\nWHERE condition;"

    def copy_query(self):
        """Copy to Query"""
        self.ensure_one()

        if self.tips:
            self.name = self.tips.name


class TipsQueries(models.Model):
    _name = "tipsqueries"
    _description = "Tips for queries"

    name = fields.Text(string="Query", required=True)
    description = fields.Text(string="Description", translate=True)
