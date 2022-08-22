# -*- coding: utf-8 -*-
{
    'name': "refunds",

    'summary': """
       Refunds 
       """,

    'author': "Hafssa",

    'version': '15.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/package_order.xml',
        'views/res_partner.xml',
        'views/delivery_man.xml',
        'views/voyage.xml',
        'views/remboures_view.xml',
        'views/caisse.xml',
        'data/ir_sequence.xml',
    ],

}
