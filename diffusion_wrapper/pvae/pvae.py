import click
from diffusion_wrapper.config import get_context, get_project


@click.group()
def vae_group():
    pass


@vae_group.command()
def train():
    pass

