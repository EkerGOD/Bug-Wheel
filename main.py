import toml
from dns.e164 import query
from pygments.lexer import default
import config

from core import start_crawl
import click

from file import SiteController
from utils import is_connected


@click.group()
def cli():
    pass

@cli.group()
def crawl():
    pass

@crawl.command()
def start():
    click.echo('start crawl')
    start_crawl()

@cli.group()
def query():
    pass

@query.command()
def mode():
    click.echo("Current mode: " + config.settings.MODE)

@query.command()
def link():
    click.echo("URL Testing...")
    siteController = SiteController(config.SITE_PATH)
    sites = siteController.get()['sites']
    for site in sites:
        if is_connected(site['url']):
            click.echo(site['name'] + ' connect successful!')
        else:
            click.echo(site['name'] + ' connect failed!')

@cli.group()
def update():
    pass

@update.group()
def setting():
    pass

@setting.command()
@click.argument('mode_type', type=click.Choice(config.settings.MODE_TYPES))
def mode(mode_type):
    with open('settings.toml', 'r') as f:
        settings = toml.load(f)
    settings['mode'] = mode_type
    with open('settings.toml', 'w') as f:
        toml.dump(settings, f)

if __name__ == "__main__":
    # systemStore = initialize()
    # app = systemStore.get('app')
    # app.run()
    cli()

'''
项目要如何组织

不需要：
    
    CrawlPool

爬虫执行完就把数据输入数据库

定时任务，每隔多少秒就通过主入口调用一次
'''