import click


@click.group()
def main():
    pass


@main.command(name='annotator', context_settings=dict(
    ignore_unknown_options=True,
    help_option_names=[],
))
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def annotator_cmd(args):
    from diffusion_wrapper.annotator import annotator_group
    annotator_group(args)


@main.command(name='project', context_settings=dict(
    ignore_unknown_options=True,
    help_option_names=[],
))
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def project_cmd(args):
    from diffusion_wrapper.project import project_group
    project_group(args)


@main.command(name='dataset', context_settings=dict(
    ignore_unknown_options=True,
    help_option_names=[],
))
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def project_cmd(args):
    from diffusion_wrapper.dataset import dataset_group
    dataset_group(args)


@main.command(name='vae', context_settings=dict(
    ignore_unknown_options=True,
    help_option_names=[],
))
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def vae_cmd(args):
    from diffusion_wrapper.pvae import vae_group
    vae_group(args)




main()

