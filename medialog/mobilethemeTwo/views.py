    # -*- coding: utf-8 -*-

import logging
from Acquisition import aq_inner
from zope.component import getMultiAdapter
from zope.i18nmessageid import MessageFactory
from Products.Five import BrowserView
from zope.component import getUtility

import lxml.html
from lxml.cssselect import CSSSelector

import requests

class Scrape(BrowserView):
    """   lxml    """

    def repl(html, link):
        if link.startswith('https://www.bergen.kommune.no/omkommunen'):
            link = 'http://localhost:8080/Plone/scrape?url=' + link 
            return link
        if link.startswith('/'):
            link = 'https://www.bergen.kommune.no' + link 
        return link
        
    @property
    def scraped(self, selector=None, url=None):
        import pdb; pdb.set_trace()
        if url==None:
            url='https://www.bergen.kommune.no/omkommunen/avdelinger/bergenhus-og-arstad-kulturkontor/9353/9356'
        if selector==None:
            selector = '#rg7726'
        r = requests.get(url)
        tree = lxml.html.fromstring(r.text)
        
        tree.make_links_absolute('https://www.bergen.kommune.no', resolve_base_href=True)
        tree.rewrite_links(self.repl)
        
        #the parsed DOM Tree
        lxml.html.tostring(tree)

        # construct a CSS Selector
        sel = CSSSelector(selector)
        
        # Apply the selector to the DOM tree.
        results = sel(tree)
        
        # the HTML for the first result.
        match = results[0]
        
        return lxml.html.tostring(match)

        