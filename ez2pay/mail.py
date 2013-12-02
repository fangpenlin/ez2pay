from __future__ import unicode_literals
import logging

from pyramid.renderers import render
from pyramid.settings import asbool
from boto.ses import SESConnection


class SESService(object):
    
    def __init__(self, config, logger=None):
        self.logger = logger
        if self.logger is None:
            self.logger = logging.getLogger(__name__)
        self.config = config
        self._conn = None
        
    @property
    def conn(self):
        if not self._conn:
            self._conn = SESConnection(
                aws_access_key_id=self.config['access_key'],
                aws_secret_access_key=self.config['secret_key'],
            )
        return self._conn
    
    def get_usage(self):
        """Get and return (sent mail, total quota) tuple
        
        """
        res = self.conn.get_send_quota()
        res = res['GetSendQuotaResponse']
        result = res['GetSendQuotaResult']
        quota = float(result['Max24HourSend'])
        sent = float(result['SentLast24Hours'])
        return sent, quota
    
    def get_send_statistics(self):
        """Get send stats
        
        """
        res = self.conn.get_send_statistics()
        res = res['GetSendStatisticsResponse']
        result = res['GetSendStatisticsResult']
        return result['SendDataPoints']
    
    def send_mail(self, **kwargs):
        """Send email by Amazon SES service
        
        """
        if kwargs.get('source') is None:
            kwargs['source'] = self.config['default_source']
        self.conn.send_email(**kwargs)


def send_by_mailer(
    request,
    subject, 
    body, 
    to_addresses,
    cc_addresses=None, 
    bcc_addresses=None,
    reply_addresses=None,
    return_path=None,
    source=None,
    format='text'
):
    """Send a mail by our SMTP server
    
    """
    import types
    from pyramid_mailer import get_mailer
    from pyramid_mailer.message import Message
    
    assert '\r' not in subject
    assert '\n' not in subject

    def force_to_list(input):
        if isinstance(input, types.StringTypes):
            return [input]
        return input
    
    extra_args = {}
    
    if format == 'text':
        extra_args['body'] = body
    else:
        extra_args['html'] = body
        
    if source is None:
        settings = request.registry.settings
        source = settings.get('mail.default_sender', 'noreply@now.in')
    
    to_addresses = force_to_list(to_addresses)
    cc_addresses = force_to_list(cc_addresses)
    bcc_addresses = force_to_list(bcc_addresses)
    reply_addresses = force_to_list(reply_addresses)
    
    if reply_addresses:
        extra_args['extra_headers'] = {'Reply-To': ';'.join(reply_addresses)}
    
    message = Message(
        sender=source,
        subject=subject,
        recipients=to_addresses,
        cc=cc_addresses,
        bcc=bcc_addresses,
        **extra_args
    )
    
    mailer = get_mailer(request) 
    mailer.send(message)
    

def send_mail(**kwargs):
    """Send a mail, please reference to 
    
    http://boto.cloudhackers.com/ref/ses.html#boto.ses.connection.SESConnection.send_email
    
    """
    logger = logging.getLogger(__name__)
    settings = kwargs['request'].registry.settings
    use_ses = asbool(settings.get('use_amazon_ses', False))
    if use_ses:
        ses_cfg = settings['amazon.ses']
        ses = SESService(ses_cfg)
        ses_args = kwargs.copy()
        del ses_args['request']
        try:
            sent, quota = ses.get_usage()
            if quota and quota > sent:
                logger.info('Sending mail by Amazon SES ...')
                ses.send_mail(**ses_args)
                return
            else:
                logger.warn('Out of Amazon SES quota (%s/%s)', sent, quota)
        except:
            logger.error('Failed to send mail by Amazon SES', exc_info=True)
    logger.info('Sending mail by Mailer ...')
    send_by_mailer(**kwargs)


def render_mail(request, template, params, insert_template_vars=True, method='html'):
    """Render mail with template and parameters
    
    """
    result = render(template, params, request=request)
    return unicode(result, 'utf8')
