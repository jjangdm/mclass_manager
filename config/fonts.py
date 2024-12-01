# mclass_manager/config/fonts.py
import os
from django.conf import settings

FONTS_DIR = os.path.join(settings.BASE_DIR, 'static', 'fonts')

FONT_CONFIGS = {
    'nanum': {
        'name': 'NanumGothic',
        'variants': {
            'regular': {
                'name': 'NanumGothic',
                'path': os.path.join(FONTS_DIR, 'NanumGothic', 'NanumGothic.ttf'),
            },
            'bold': {
                'name': 'NanumGothicBold',
                'path': os.path.join(FONTS_DIR, 'NanumGothic', 'NanumGothicBold.ttf'),
            },
            'extra_bold': {
                'name': 'NanumGothicExtraBold',
                'path': os.path.join(FONTS_DIR, 'NanumGothic', 'NanumGothicExtraBold.ttf'),
            },
            'light': {
                'name': 'NanumGothicLight',
                'path': os.path.join(FONTS_DIR, 'NanumGothic', 'NanumGothicLight.ttf'),
            },
        },
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
            },
            'light': {
                'name': 'NotoSansKR-Light',
                'path': os.path.join(FONTS_DIR, 'Noto_Sans_KR', 'NotoSansKR-Light.ttf'),
            },
            'medium': {
                'name': 'NotoSansKR-Medium',
                'path': os.path.join(FONTS_DIR, 'Noto_Sans_KR', 'NotoSansKR-Medium.ttf'),
            },
            'semi_bold': {
                'name': 'NotoSansKR-SemiBold',
                'path': os.path.join(FONTS_DIR, 'Noto_Sans_KR', 'NotoSansKR-SemiBold.ttf'),
            },
        }
    },
    'ubuntu': {
        'name': 'Ubuntu-Regular',
        'variants': {
            'regular': {
                'name': 'Ubuntu-Regular',
                'path': os.path.join(FONTS_DIR, 'Ubuntu', 'Ubuntu-Regular.ttf'),
            },
            'bold': {
                'name': 'Ubuntu-Bold',
                'path': os.path.join(FONTS_DIR, 'Ubuntu', 'Ubuntu-Bold.ttf'),
            },
            'light': {
                'name': 'Ubuntu-Light',
                'path': os.path.join(FONTS_DIR, 'Ubuntu', 'Ubuntu-Light.ttf'),
            },
            'medium': {
                'name': 'Ubuntu-Medium',
                'path': os.path.join(FONTS_DIR, 'Ubuntu', 'Ubuntu-Medium.ttf'),
            },
        },
    },
}