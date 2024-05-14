import click


@click.group()
def annotator_group():
    pass


@annotator_group.command()
def gui():
    pass