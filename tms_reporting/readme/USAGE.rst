Every time the Transport Order report is printed from a task
(*Print > Transport Order*), the generated PDF is attached to the task's
chatter thread and its header carries a QR code that downloads that exact
PDF. Reprinting the order after later changes creates a new, independent
attachment with its own QR: earlier printouts keep pointing to the PDF they
were handed with, they are not overwritten.

The *Send Transport Order* button, next to *Assign to Me* on the task form,
sends that same PDF by email to the task's driver. The email itself is
logged in the chatter with the PDF attached; printing does not repeat that
log entry when the order is later emailed.

On the printed document, the former "Cliente"/"Transp." fields are now
labelled "Contractual shipper"/"Effective carrier" ("Cargador
contractual"/"Transportista efectivo" in the Spanish translation).
