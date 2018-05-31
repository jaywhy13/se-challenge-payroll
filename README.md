# Wave Software Development Challenge

## Setup Instructions

The project is based on Docker. It can be built with the following steps:

```bash
docker-compose build
docker-compose up
```

This runs a web container that's accessible via http://localhost:8000


## Implementation

The implementation relies on a few important models in the **Payroll** module:

- Partner - a partner is a company / person we manage employee times for. 
- Partner Profile - each partner can have a profile that allows them to have territory specific settings. One example setting used is the date format. Other settings could be added like currency, pay period settings (bi-weekly vs monthly)
- EmployeeGroup - employees can be placed in groups as a way to dictate the rate they are paid at. This is tied to a PartnerProfile, allowing for different employee groups in different territories.
- EmployeeTimesheet - this model manages keeps a record of the hours employees have worked via attached EmployeeTime records.
- EmployeeTime - this holds the date, and quantity of work done. The abstraction of quantity was used here to allow further extension and representation of different units of time. Perhaps some partners don't go by hours?

In order to get data from the CSV file, an **Importer** module was built. The importer module is an abstract implementation that only cares about importing some data from somewhere. It allows a specification of fields and data types and therefore lends well to validation. A CSV implementation is built atop the Importer to allow importing data from the CSV. 

The **Payroll** module uses the importer to load data from the CSV file. It tells the importer the fields that should be in the file and leaves the validation to the importer. 


## Todo

- Started writing tests but need to fix some errors with them.
