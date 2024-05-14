import os
import click
from diffusion_wrapper.config import Project, NoProjectError, get_context, get_project


@click.group()
def project_group():
    pass


@project_group.command()
@click.option('--project-dir', type=str, required=True)
def open_project(project_dir):
    project_dir = os.path.abspath(project_dir)
    if not os.path.exists(project_dir):
        os.makedirs(project_dir, exist_ok=True)
    project = Project(project_dir)
    project.save()
    context = get_context()
    context.project_dir = project_dir
    context.save()


@project_group.command()
def show_current():
    try:
        prj = get_project()
        click.echo(f'Current project: {prj.cfg_path}')        
    except NoProjectError as ex:
        click.echo('No project was set')
