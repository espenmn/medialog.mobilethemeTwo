from zope import schema
from zope.interface import Interface
from z3c.form import interfaces
from zope.interface import alsoProvides
from plone.directives import form
from plone.autoform.interfaces import IFormFieldProvider
from medialog.controlpanel.interfaces import IMedialogControlpanelSettingsProvider

from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow

from zope.i18nmessageid import MessageFactory

_ = MessageFactory('medialog.mobilethemeTwo')


class IMobilethemeTwoLayer(Interface):
    """A layer specific to medialog.mobilethemeTwo
        """
#url class/id pair
class IUrlPair(form.Schema):
    scrape_base_url = schema.URI(
        title=_(u'scrape_base_url'), 
        description=_(u'help_base_scrape_url'),
        default='http://plone.org',
    )
    scrape_selector = schema.ASCIILine(
        title=_(u'scrape_selector'),
        description=_(u'scrape_selector',
        'This has to correspond to the url.'),
        default='#content',
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
                    'scrape_javascript',
                    'scrape_style'
            ],
    )
    
    form.widget(scrape_url_pair=DataGridFieldFactory)
    scrape_url_pair = schema.List(
        title = _(u"Url Pair Fields"),
        description = _(u"The combination of urls and css class / id"),
        value_type=DictRow(title=_(u"Field"), schema=IUrlPair),
                     required=True,
    )
                  
    scrape_url = schema.URI(
                title=_(u'scrape_url', 'default url'),
                description=_('scrape_url',
                            u'Base url if none is given'),
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

alsoProvides(IMobilethemeTwoSettings, IMedialogControlpanelSettingsProvider)
