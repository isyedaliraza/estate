{
    'name': 'Real Estate',
    'version': '0.0.1',
    'description': 'A module to manage real estate advertisements.',
    'author': 'Baramej',
    'website': 'https://baramej.io',
    'license': 'LGPL-3',
    'category': 'Uncategorized',
    'depends': ['base'],
    'data': [
        'views/doctor_views.xml',
        'views/property_tag_views.xml',
        'views/property_offer_views.xml',
        'views/property_type_views.xml',
        'views/property_views.xml',
        'views/res_users_views.xml',
        'views/menus.xml',
        'security/ir.model.access.csv',
    ],
    'application': True
}
