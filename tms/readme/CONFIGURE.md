To estimate the distance and duration of a task route with the *Estimate
route* button, the task checkpoints need geolocated places and a route
service key:

- **Google Maps**: when a key is set for the *Google Place Map*
  geolocation API, routes are estimated with Google Maps.
- **Open Route Service**: otherwise routes are estimated with Open Route
  Service, which needs a key per company. Create a token in the
  [Open Route Service dashboard](https://openrouteservice.org/) and:

  1.  Switch to the company in the company selector.
  2.  Go to *Settings \> General Settings \> Integrations \>
      Geolocation*.
  3.  Select *Open Route Service* as API, fill in the *Key* and save.
  4.  Select again the geolocation API used for the contacts (e.g.
      *Open Street Map*) and save. The key is kept on the company.
      *Open Route Service* can't geolocate contacts, so leaving it
      selected makes their geolocation fail.

  Repeat it for each company that estimates routes.
