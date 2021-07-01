# coding: utf-8
import typer

from eu_state_aids import bg, it

app = typer.Typer()
app.add_typer(bg.app, name="bg")
app.add_typer(it.app, name="it")
