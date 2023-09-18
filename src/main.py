import subprocess

from flet import Column, ElevatedButton, icons, FilePicker, Page, Ref, FilePickerResultEvent, Row, \
    app, Container, padding, border_radius, \
    CrossAxisAlignment, ScrollMode, RadioGroup, Radio, Markdown, \
    MarkdownExtensionSet, AlertDialog, Text, TextButton, TextField, MainAxisAlignment
from pdfannots.cli import main_igor


def main(page: Page):
    page.title = "PDFannots App"
    page.scroll = "adaptive"
    page.window_width = 190
    page.window_height = 210
    page.window_min_width = 190
    page.window_min_height = 210

    def request_preview(e):
        # markdown = subprocess.run(["pdfannots", radio_group.value], capture_output=True)
        # preview.current.value = str(markdown.stdout, 'UTF-8')
        preview.current.value = main_igor(radio_group.value)
        markdown_pane.width = 600
        markdown_pane.visible = True
        page.window_width = 1100
        page.window_height = 600
        page.update()

    path_export = Ref[TextField]()

    def save_markdown(e):
        with open(path_export.current.value, 'w') as markdown_file:
            markdown_file.write(preview.current.value)
        dlg_modal.open = False
        page.update()

    def close_modal(e):
        dlg_modal.open = False
        page.update()

    dlg_modal = AlertDialog(
        modal=True,
        title=Text("Exporting annotations"),
        content=Column([
            Text("Do you want to save exported PDF annotations as markdown?"),
            TextField(ref=path_export)]
        ),
        actions=[
            TextButton("Save", on_click=save_markdown),
            TextButton("Close", on_click=close_modal)
        ],
        actions_alignment=MainAxisAlignment.END,
    )

    def export_markdown(e):
        path_export.current.value = radio_group.value.replace(".pdf", ".md")
        path_export.current.label = "Path Markdown File"
        page.dialog = dlg_modal
        dlg_modal.open = True
        page.update()

    preview_button = Ref[ElevatedButton]()
    export_button = Ref[ElevatedButton]()
    menu = Container(
        bgcolor="#E8EFF8",
        border_radius=border_radius.all(10),
        padding=padding.all(10),
        content=Column(
            spacing=10,
            controls=[
                ElevatedButton(
                    "Select files...",
                    icon=icons.FOLDER_OPEN,
                    on_click=lambda _: file_picker.pick_files(allow_multiple=True, allowed_extensions=['pdf']),
                ),
                ElevatedButton(
                    "Preview",
                    icon=icons.PREVIEW,
                    ref=preview_button,
                    on_click=request_preview,
                    disabled=True,
                ),
                ElevatedButton(
                    "Export",
                    icon=icons.IMPORT_EXPORT,
                    ref=export_button,
                    on_click=export_markdown,
                    disabled=True,
                ),
            ]
        )
    )

    files = Ref[Column]()
    radio_group = RadioGroup(content=Column(ref=files))
    preview = Ref[Markdown]()

    pdf_list = Container(
        visible=True,
        width=None,
        content=Row(
            scroll=ScrollMode.ADAPTIVE,
            controls=[radio_group]
        )
    )

    markdown_pane = Container(
        visible=False,
        width=None,
        padding=15,
        content=Row(
            wrap=True,
            controls=[Markdown(
                ref=preview,
                selectable=True,
                extension_set=MarkdownExtensionSet.GITHUB_WEB,
                on_tap_link=lambda e: page.launch_url(e.data)
            )]
        )
    )

    def file_picker_result(e: FilePickerResultEvent):
        pdf_list.visible = False if e.files is None else True
        preview_button.current.disabled = True if e.files is None else False
        export_button.current.disabled = True if e.files is None else False
        if e.files is not None:
            pdf_list.width = 300

            if page.window_width < 500:
                page.window_width = 500
            if page.window_height < 500:
                page.window_height = 500

            for f in e.files:
                files.current.controls.append(
                    Radio(value=f.path, label=f.name)
                )

        page.update()

    file_picker = FilePicker(on_result=file_picker_result)
    page.overlay.append(file_picker)

    page.add(
        Row(
            vertical_alignment=CrossAxisAlignment.START,
            scroll=ScrollMode.HIDDEN,
            controls=[
                menu,
                pdf_list,
                markdown_pane
            ]
        )
    )


if __name__ == "__main__":
    app(target=main)
