"""
Excel export service.

Builds a formatted .xlsx workbook (in-memory) listing every participant,
for the admin dashboard's "Export Excel" button.
"""

from io import BytesIO
from typing import List

import pandas as pd

from app.models import Participant

# Column width is derived from content length; this caps it so a single
# very long value can't blow out the sheet.
MAX_COLUMN_WIDTH = 60


def export_participants_to_excel(participants: List[Participant]) -> BytesIO:
    rows = []
    for p in participants:
        rows.append(
            {
                "Name": p.name,
                "Age": p.age,
                "Weight (kg)": p.weight,
                "City": p.city,
                "Phone": p.phone,
                "Email": p.email,
                "Registration ID": p.reg_id,
                "Check-In Status": "Checked In" if p.checked_in else "Not Checked In",
                "Check-In Time": p.check_in_time.strftime("%Y-%m-%d %H:%M:%S") if p.check_in_time else "",
                "Lucky Draw Winner": "Yes" if p.is_winner else "No",
            }
        )

    columns = [
        "Name",
        "Age",
        "Weight (kg)",
        "City",
        "Phone",
        "Email",
        "Registration ID",
        "Check-In Status",
        "Check-In Time",
        "Lucky Draw Winner",
    ]
    df = pd.DataFrame(rows, columns=columns)

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Participants")
        worksheet = writer.sheets["Participants"]

        # Auto-fit column widths based on content.
        for col_index, column_name in enumerate(df.columns, start=1):
            if df.empty:
                content_len = 0
            else:
                content_len = df[column_name].astype(str).map(len).max()
            width = min(max(content_len, len(column_name)) + 4, MAX_COLUMN_WIDTH)
            col_letter = worksheet.cell(row=1, column=col_index).column_letter
            worksheet.column_dimensions[col_letter].width = width

    output.seek(0)
    return output
