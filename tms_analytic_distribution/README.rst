.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================
TMS Analytic Distribution
=========================

Adds analytic fields in analytic distribution

Configuration
=============

To configure your analytic distributions go to:

#. *Invoicing > Configuration > Settings* and activate checkbox **Analytic
   accounting** in *Accounting & Finance*.
#. Now you see the menu *Invoicing > Configuration > Analytic Accounting >
   Analytic Distributions*
#. Create a new analytic distribution and enter its name
#. Add some distribution rules: you must specify the analytic account and
   percentage of total move line amount you want to distribute.
#. Save distribution.
#. You can set if sum of total percent of analytic accounts must be 100% or
   not by company. If you go to your company settings, you can find a checkbox
   **Force percent** in *General Information* tab.


Usage
=====

After installation, you'll see a new 'Analytic Distribution' column in
Journal Entry form (in Journal Items tab), in order to select the
analytic distribution you want when creating journal entries manually. You
can do the same in account invoice form and select your analytic distribution
in invoice lines.

Multiple analytic lines are created when the invoice or the entries are
confirmed.

You can continue using 'Analityc Account' field, but 'Analytic Distribution'
has precedence if defined.


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/87/12.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/account-analytic/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* `Odoo Community Association: Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Carlos Dauden <carlos.dauden@tecnativa.com>
* Sergio Teruel <sergio.teruel@tecnativa.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
