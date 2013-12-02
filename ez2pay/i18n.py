from __future__ import unicode_literals

from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('ez2pay')

default_domain = 'ez2pay'


def normalize_locale_name(locale_name):
    """Normalize locale name, for example, zh_tw will be normalized as
    zh_TW
    
    """
    import locale
    normalized = locale.normalize(locale_name)
    if normalized == locale_name:
        return normalized
    parts = normalized.split('.')
    result = parts[0]
    return result


class LocalizerFactory(object):
    """Localize string
    
    """
    
    def __init__(self, domain=default_domain):
        self.domain = domain
        
    def __call__(self, request):
        return self.get_localizer(request)
    
    def get_localizer(self, request):
        from pyramid.i18n import get_localizer
        localizer = get_localizer(request)
        return Localizer(localizer, self.domain)


class Localizer(object):
    """A proxy for localizer, bound with domain argument
    
    """
    
    def __init__(self, localizer, domain):
        self.localizer = localizer
        self.domain = domain
        
    def __call__(self, *args, **kwargs):
        return self.translate(*args, **kwargs)
    
    def translate(self, tstring, mapping=None):
        result = self.localizer.translate(tstring, 
                                          domain=self.domain, 
                                          mapping=mapping)
        return result
    
    def pluralize(self, singular, plural, n, mapping=None):
        result = self.localizer.pluralize(singular, plural, n,
                                          domain=self.domain, 
                                          mapping=mapping)
        return result
