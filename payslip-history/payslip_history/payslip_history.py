"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import json

import fitz
import reflex as rx
from rxconfig import config


class UploadState(rx.State):
    _uploading: bool = False
    _progress: int = 0
    _total_bytes: int = 0
    _json_data: str = ""

    async def handle_upload(self, files: list[rx.UploadFile]):
        for file in files:
            file_data = await file.read()
            self._total_bytes += len(file_data)
            doc = fitz.open(stream=file_data, filetype="pdf")

            page = doc[0]
            tabs = page.find_tables()

            print(f"{len(tabs.tables)}個のテーブルが{page}上に見つかりました")

            if not tabs.tables:
                rx.window_alert("No tables found in the document")

            work_state = tabs[0].extract()
            print("就業状況")
            print(work_state)

            payslip = tabs[1].extract()
            print("給与")
            rows = len(payslip)

            res = {}
            for i in range(0, rows, 2):
                p = payslip[i : i + 2]
                keys = p[0]
                values = p[1]
                r = {k: v for k, v in zip(keys, values)}
                res |= r

            res_int = dict([(k, func(v)) for k, v in res.items() if k != ""])

            self._json_data = json.dumps(res_int, ensure_ascii=False, indent=2)

    def handle_upload_progress(self, progress: dict):
        self._uploading = True
        self._progress = round(progress["progress"] * 100)
        if self._progress >= 100:
            self._uploading = False

    def cancel_upload(self):
        self._uploading = False
        return rx.cancel_upload("upload3")


def func(v: str) -> int:
    if v == "":
        return 0

    return int(v.replace(",", "").replace(" ", ""))


def index() -> rx.Component:
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("Welcome to Reflex!", size="9"),
            rx.text(
                "Get started by editing ",
                rx.code(f"{config.app_name}/{config.app_name}.py"),
                size="5",
            ),
            rx.link(
                rx.button("Check out our docs!"),
                href="https://reflex.dev/docs/getting-started/introduction/",
                is_external=True,
            ),
            spacing="5",
            justify="center",
            min_height="85vh",
        ),
        upload_form(),
        rx.logo(),
    )


def upload_form():
    return rx.vstack(
        rx.upload(
            rx.text("Drag and drop files here or click to select files"),
            id="upload3",
            border="1px dotted rgb(107,99,246)",
            padding="5em",
        ),
        rx.vstack(
            rx.foreach(
                rx.selected_files("upload3"),
                rx.text,
            ),
        ),
        rx.progress(
            value=UploadState._progress,
            max=100,
        ),
        rx.cond(
            ~UploadState._uploading,
            rx.button(
                "Upload",
                on_click=UploadState.handle_upload(
                    rx.upload_files(
                        upload_id="upload3",
                        on_upload_progress=UploadState.handle_upload_progress,
                    ),
                ),
            ),
            rx.button(
                "Cancel",
                on_click=UploadState.cancel_upload,
            ),
        ),
        rx.text(
            "Total bytes uploaded: ",
            UploadState._total_bytes,
        ),
        rx.text(UploadState._json_data),
        align="center",
    )


app = rx.App()
app.add_page(index)
