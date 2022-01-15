{
    'name': "Novobi Sales B2B",
    'summary': "Addons feature for B2B Sales",
    'description': """
Manage Sales
==============
Description related to Sales.
    """,
    'author': "Alan Pham",
    'website': "http://www.example.com",
    'category': 'Sales',
    'version': '14.0.1',
    'depends': ['base', 'sale', 'crm'],
    'data': [
        # security
        'security/ir.model.access.csv',
        'security/salesperson_security.xml',
        # data
        'data/mail_template.xml',
        'data/delivery_order_sent_email.xml',
        # wizard
        'wizard/sale_request_wizard_view.xml',
        # view
        'views/sale_request.xml'
    ],
}
