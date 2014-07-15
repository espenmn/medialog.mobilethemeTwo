from zope import schema
from zope.interface import Interface
from z3c.form import interfaces
from zope.interface import alsoProvides
from plone.directives import form
from plone.autoform.interfaces import IFormFieldProvider
from medialog.controlpanel.interfaces import IMedialogControlpanelSettingsProvider

from collective.z3cform.datagridfield import DataGridFieldFactory 
from collective.z3cform.datagridfield.registry import DictRow

from zope.i18nmessageid import MessageFactory

_ = MessageFactory('medialog.mobilethemeTwo')


class IMobilethemeTwoLayer(Interface):
    """A layer specific to medialog.mobilethemeTwo
        """

#url class/id pair
class IUrlPair(form.Schema):
    scrape_base_url = schema.URI(
        title=_(u'scrape_base_url', 'URL that will embed'), 
        required=False
    )
    scrape_selector = schema.ASCIILine(
        title=_(u'scrape_selector', 'CSS selector to filter on'),
        required=False
    )

class IMobilethemeTwoSettings(form.Schema):
    """Adds settings to medialog.controlpanel
        """
    
    form.fieldset(
        'mobilethemeTwo',
        label=_(u'MobilethemeTwo settings'),
            fields=[
                    'scrape_url',
                    'scrape_url_pair',
                    'scrape_safe_attrs_only',
                    'scrape_javascript',
                    'scrape_style',
                    'scrape_whitelist',
            ],
    )
    
    form.widget(scrape_url_pair=DataGridFieldFactory)
    scrape_url_pair = schema.List(
        title = _(u"scrape_url_pair", default=u"URL selector pairs"),
        value_type=DictRow(schema=IUrlPair),
    )
                  
    scrape_url = schema.URI(
                title=_(u"scrape_url", default=u"Default URL"),
    )
                      
    scrape_safe_attrs_only = schema.Bool(
                 title=_(u"scrape_safe_attrs_only", default=u"Security:Only permit safe attr"),
                 description=_(u"help_safe_attrs_only",
                  default="")
    )
    
    scrape_javascript = schema.Bool(
                 title=_(u"scrape_javascript", default=u"Security: Filter out javascript"),
                 description=_(u"help_scrape_javascript",
                  default="")
    )

    scrape_style = schema.Bool(
                 title=_(u"scrape_style", default=u"Security: Filter out CSS styles"),
                 description=_(u"help_scrape_style",
                  default="")
    )
    
    scrape_whitelist = schema.Tuple(
                title=_(u"scrape_whitelist", default=u"Only permit these URLs"),
                value_type=schema.URI(),
    )

alsoProvides(IMobilethemeTwoSettings, IMedialogControlpanelSettingsProvider)
