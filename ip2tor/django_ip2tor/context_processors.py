import os 

def export_vars(request):
    data = {}
    data['SOCIAL_GITHUB'] = os.environ['SOCIAL_GITHUB']
    data['SOCIAL_TWITTER'] = os.environ['SOCIAL_TWITTER']
    data['SOCIAL_INSTAGRAM'] = os.environ['SOCIAL_INSTAGRAM']
    data['SOCIAL_FACEBOOK'] = os.environ['SOCIAL_FACEBOOK']
    data['SOCIAL_LINKEDIN'] = os.environ['SOCIAL_LINKEDIN']
    data['SHOP_SITE_NAME'] = os.environ['SHOP_SITE_NAME']
    data['SHOP_SITE_DOMAIN'] = os.environ['SHOP_SITE_DOMAIN']

    return data
