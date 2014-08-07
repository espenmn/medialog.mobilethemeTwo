# -*- coding: utf-8 -*-

#import logging
#from Acquisition import aq_inner
from zope.i18nmessageid import MessageFactory
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone import api
from medialog.mobilethemeTwo.interfaces import IMobilethemeTwoSettings

import requests
import lxml.html
import urllib 
from lxml.cssselect import CSSSelector
from lxml.html.clean import Cleaner

from DateTime import DateTime
 

class Scrape(BrowserView):
    """   A View that uses lxml to embed external content    """
    
    def scraped(self):
        selector = '#container' #default value
        #get settings from control panel / registry
        scrape_add_nofollow = api.portal.get_registry_record('medialog.mobilethemeTwo.interfaces.IMobilethemeTwoSettings.scrape_add_nofollow')
        scrape_allow_tags = api.portal.get_registry_record('medialog.mobilethemeTwo.interfaces.IMobilethemeTwoSettings.scrape_allow_tags')
        scrape_annoying_tags = api.portal.get_registry_record('medialog.mobilethemeTwo.interfaces.IMobilethemeTwoSettings.scrape_annoying_tags')
        scrape_comments = api.portal.get_registry_record('medialog.mobilethemeTwo.interfaces.IMobilethemeTwoSettings.scrape_comments')
        scrape_embedded = api.portal.get_registry_record('medialog.mobilethemeTwo.interfaces.IMobilethemeTwoSettings.scrape_embedded')
        scrape_forms = api.portal.get_registry_record('medialog.mobilethemeTwo.interfaces.IMobilethemeTwoSettings.scrape_forms')
        scrape_frames = api.portal.get_registry_record('medialog.mobilethemeTwo.interfaces.IMobilethemeTwoSettings.scrape_frames')
        scrape_javascript = api.portal.get_registry_record('medialog.mobilethemeTwo.interfaces.IMobilethemeTwoSettings.scrape_javascript')
        scrape_kill_tags = api.portal.get_registry_record('medialog.mobilethemeTwo.interfaces.IMobilethemeTwoSettings.scrape_kill_tags')
        scrape_links = api.portal.get_registry_record('medialog.mobilethemeTwo.interfaces.IMobilethemeTwoSettings.scrape_links')
        scrape_meta = api.portal.get_registry_record('medialog.mobilethemeTwo.interfaces.IMobilethemeTwoSettings.scrape_meta')
        scrape_page_structure = api.portal.get_registry_record('medialog.mobilethemeTwo.interfaces.IMobilethemeTwoSettings.scrape_page_structure')
        scrape_processing_instructions = api.portal.get_registry_record('medialog.mobilethemeTwo.interfaces.IMobilethemeTwoSettings.scrape_processing_instructions')
        scrape_remove_tags = api.portal.get_registry_record('medialog.mobilethemeTwo.interfaces.IMobilethemeTwoSettings.scrape_remove_tags')
        scrape_remove_unknown_tags = api.portal.get_registry_record('medialog.mobilethemeTwo.interfaces.IMobilethemeTwoSettings.scrape_remove_unknown_tags')
        scrape_safe_attrs_only = api.portal.get_registry_record('medialog.mobilethemeTwo.interfaces.IMobilethemeTwoSettings.scrape_safe_attrs_only')
        scrape_scripts = api.portal.get_registry_record('medialog.mobilethemeTwo.interfaces.IMobilethemeTwoSettings.scrape_scripts')
        scrape_style = api.portal.get_registry_record('medialog.mobilethemeTwo.interfaces.IMobilethemeTwoSettings.scrape_style')
        scrape_url_pair = api.portal.get_registry_record('medialog.mobilethemeTwo.interfaces.IMobilethemeTwoSettings.scrape_url_pair')
        scrape_whitelist = api.portal.get_registry_record('medialog.mobilethemeTwo.interfaces.IMobilethemeTwoSettings.scrape_host_whitelist')
        scrape_whitelist_tags = api.portal.get_registry_record('medialog.mobilethemeTwo.interfaces.IMobilethemeTwoSettings.scrape_whitelist_tags')
        url = api.portal.get_registry_record('medialog.mobilethemeTwo.interfaces.IMobilethemeTwoSettings.scrape_url')
        
        #get url if it was set in the request
        if hasattr(self.request, 'url'):
            url = str(urllib.unquote((self.request.url).decode('utf8')))
            
        #get base url, 
        #if the url is taken from request
        parts = url.split('//', 1)
        this_base_url = parts[0]+'//'+parts[1].split('/', 1)[0]
        
        if this_base_url not in scrape_whitelist:
            return "URL domain is not in whitelist"
            
        #get html from the requested url
        r = requests.get(url)
        tree = lxml.html.fromstring(r.text)
             
        #clean evil stuff
        cleaner = Cleaner(
            add_nofollow = scrape_add_nofollow,
            allow_tags = scrape_allow_tags,
            annoying_tags =  scrape_annoying_tags,
            comments = scrape_comments,
            embedded = scrape_embedded,
            forms = scrape_forms,
            frames =  scrape_frames,
            host_whitelist = scrape_whitelist,
            javascript = scrape_javascript , 
            kill_tags = scrape_kill_tags,
            links = scrape_links ,
            meta = scrape_meta,
            page_structure = scrape_page_structure ,
            processing_instructions = scrape_processing_instructions,
            remove_tags = scrape_remove_tags,
            remove_unknown_tags = scrape_remove_unknown_tags,
            safe_attrs_only = scrape_safe_attrs_only,
            scripts =  scrape_scripts ,
            style = scrape_style, 
            whitelist_tags = scrape_whitelist_tags
        )
        cleaner(tree)
        
        #the parsed DOM Tree
        lxml.html.tostring(tree)

        #relink
        tree.make_links_absolute(this_base_url, resolve_base_href=True)
        tree.rewrite_links(self.repl)
        
        # construct a CSS Selector
        #it the request defines one, use that
        if hasattr(self.request, 'selector'):
            selector = str(urllib.unquote((self.request.selector).decode('utf8')))
        
        #if not, use settings from control panel
        else:
            for pair in scrape_url_pair:
                if pair['scrape_base_url'] in url:
                    selector = pair['scrape_selector']
                    break
                   
        sel = CSSSelector(selector)
                
        # Apply the selector to the DOM tree.
        results = sel(tree)

        # the HTML for the first result.
        if results:
            match = results[0]
            return lxml.html.tostring(match)

        #"Content can not be filtered, returning whole page"
        return lxml.html.tostring(tree)
        
    
    def repl(html, link):
        scrape_url_pair = api.portal.get_registry_record('medialog.mobilethemeTwo.interfaces.IMobilethemeTwoSettings.scrape_url_pair')
        root_url = api.portal.get().absolute_url()
        
        #dont modyfy image links
        if '/image' in link  or link.endswith('.jpg') or link.endswith('.png') or link.endswith('.gif') or link.endswith('.js') or link.endswith('.jpeg') or link.endswith('.pdf'):
            return link
        
        #point pages for sites enabled in  control panel to embedded view
        for pair in scrape_url_pair:
            if link.startswith(pair['scrape_base_url']):
                return root_url + '/scrape?url=' + link
        
        #for all other links
        return link


class ScrapeView(Scrape):
    """   A Dexterity Content View that uses the scrape view """
            
    def __init__(self, context, request):
          self.context = context
          self.request = request
          #looks ugly, but works
          self.request.selector    =   urllib.quote(context.scrape_selector).decode('utf8') 
          self.request.url         =   urllib.quote(context.scrape_url).decode('utf8')
    
        
        
class Manifest(BrowserView):
    """List of urls to cache"""
    
    def __call__(self):
        urls = '#Cached urls, date:' + (str(DateTime()))[0:16] +'\n'
        catalog = api.portal.get_tool(name='portal_catalog')
        all_brains = catalog.searchResults()
        for brain in all_brains:
            urls += (brain.getURL())
            urls +="\n"
             
        return """CACHE MANIFEST
# Explicitly cached entries
/++theme++medialog.mobilethemeTwo/assets/invisibles.css
/++theme++medialog.mobilethemeTwo/assets/mobiletwo.css 
/++theme++medialog.mobilethemeTwo/assets/navigation.css 
/++theme++medialog.mobilethemeTwo/assets/reset.css 
/++theme++medialog.mobilethemeTwo/assets/authoring.css 
/++theme++medialog.mobilethemeTwo/assets/IcoMoon/Icons/png/32px/mail4.png
/++theme++medialog.mobilethemeTwo/assets/IcoMoon/Icons/png/32px/newspaper.png
/++theme++medialog.mobilethemeTwo/assets/IcoMoon/Icons/png/32px/phone.png
/++theme++medialog.mobilethemeTwo/assets/images/add.png
/++theme++medialog.mobilethemeTwo/assets/images/addbutton.png
/++theme++medialog.mobilethemeTwo/assets/images/bubble.png
/++theme++medialog.mobilethemeTwo/assets/images/call.png
/++theme++medialog.mobilethemeTwo/assets/images/gear.png
/++theme++medialog.mobilethemeTwo/assets/images/home.png
/++theme++medialog.mobilethemeTwo/assets/images/info.png
/++theme++medialog.mobilethemeTwo/assets/images/mail.png
/++theme++medialog.mobilethemeTwo/assets/images/navigation.png
/sitemap
/contact-info
%s

# offline.html will be displayed if the user is offline
#FALLBACK:
#/ /++theme++medialog.mobilethemeTwo/offline.html

# All other resources (e.g. sites) require the user to be online. 
NETWORK:
*

# Additional resources to cache
#CACHE:
#get sitemap here, maybe
""" %(urls)


        return printed