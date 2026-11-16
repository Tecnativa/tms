Analytic for the Transport Management System (TMS):

- Vehicles have an analytic distribution. Setting the tractor or the trailer
  on a sale order line or its task (form, planning kanban, timeline...), a
  purchase order line or a journal item (vendor bills, journal entries) adds it
  to the analytic distribution of that line, replacing the one of the previous
  vehicles and keeping the rest of the distribution. It also applies when the
  vehicle is written without the screens (imports, RPC), and removing the
  vehicle removes its distribution.
- The analytic plan of the vehicles is set in the Accounting settings. The
  account of that plan in the analytic distribution of a vehicle represents
  it: the analytic lines of that account get the vehicle as tractor or
  trailer, as for a cost shared between several vehicles (fuel, leasing...).
- The tractor, trailer, driver and division are available in the invoices
  analysis.
