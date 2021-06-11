# coding: utf-8
import typer

from op_state_aids import bg

app = typer.Typer()
app.add_typer(bg.app, name="bg")
