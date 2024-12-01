# mclass_manager/config/fonts.py
import os
from django.conf import settings

FONTS_DIR = os.path.join(settings.BASE_DIR, 'static', 'fonts')

FONT_CONFIGS = {
    'nanum': {
        'name': 'NanumGothic',
        'path': os.path.join(FONTS_DIR, 'NanumGothic', 'NanumGothic.ttf'),
    },
    'noto_sans': {
        'name': 'NotoSansKR',
        'variants': {
            'regular': {
                'name': 'NotoSansKR',
                'path': os.path.join(FONTS_DIR, 'Noto_Sans_KR', 'NotoSansKR-Regular.ttf'),
            },
            'bold': {
                'name': 'NotoSansKR-Bold',
                'path': os.path.join(FONTS_DIR, 'Noto_Sans_KR', 'NotoSansKR-Bold.ttf'),
            },
            'thin': {
                'name': 'NotoSansKR-Thin',
                'path': os.path.join(FONTS_DIR, 'Noto_Sans_KR', 'NotoSansKR-Thin.ttf'),
            }
        }
    },
    'ubuntu': {
        'name': 'Ubuntu-Regular',
        'path': os.path.join(FONTS_DIR, 'Ubuntu', 'Ubuntu-Regular.ttf'),
    }
}