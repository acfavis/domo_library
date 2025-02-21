---
title: Domo Distribution and Governance Strategy across Instances
---
This is a framework for managing data distribution within an organization that has several departments using standalone instances of domo.

domo-accounting.domo.com

domo-sales.domo.com

domo-marketing.domo.com

domo-engineering.domo.com

There are several highly bespoke datastores that provide high value data to different departments, they’ll have their own instances of domo too.

domo-aa.domo.com

domo-sfdc.domo.com

domo-snowflake.domo.com

We need a single place where users can find trusted dashboards builton a consistent and validated data pipeline that will consume input datasets from different departments or a chain of transformed datasets.

Ex. The executive dashboard gets prepared by domo-engineering but consumes data from accounting, sales, and marketing.

4 Types of Datasets and Which ones we Publish
---------------------------------------------

Non-publishable Datasets
------------------------

Avoid publishing datasets that require additional lookups or external data to understand.

1.  ### Raw Datasets
    

*   Come straight from the source system.  
*   Minimize ETL during Ingest.

2.  ### Staging Dataset (INT)
    

*   Exist exclusively in Department or Clearinghouse instances.
*   Represent intermediate steps required to transform a dataset into a usable shape.

*   This will include dimension tables that are not golden records

Publishable Datasets
--------------------

We promote the publishing of datasets that can stand on their own and do not require additional context to understand.

3.  ### Data Warehouse (DWH)
    

*   The building blocks (inputs) to DASH datasets

ither facts or dimensional tables that have NOT been shaped for a specific analytic use case.

*   Do not publish cards or dashboards built on DWH datasets.
*   Fact tables can take the form of transactional, accumulating snapshot, periodic balance.

*   Period and accumulating snapshots should be avoided unless there’s a tradeoff for data volume optimization OR rigid reporting requirements where taking snapshots make sense (ex. Financial reporting)

*   DWH datasets will be fact tables representing a single fact type (ex. Sales, Sales Forecast or Inventory), joined with the minimum dimensional attributes to be useful in a stand-alone setting.

*   Avoid subsetting similar datasets (ex. Inventory 2019 vs Inventory 2022)

*   DWH datasets includes conformed dimensional tables (like a Calendar Dimension with FY attributes or golden record customer master)

4.  ### Dashboard Dataset (DASH)
    

*   Represent stand-alone datasets that dashboards and cards are built against.
*     Publishable only to distribution centers.
*   Typically will combine multiple DWH fact tables and conformed dimensions.

*   Datasets shaped for analysis (PIVOT or UNPIVOT metrics, or POP (CY vs PY etc. are classified as DASH datasets).

*   Do not conduct ETL on DASH datasets

* * *

3 Types of Instances
====================

1.  Data Clearinghouse
    ------------------
    

A domo instance for a specific type of data or data from a highly bespoke functional area or dataset that must be managed very closely.  This data will tend to be high volume and require domain expertise to manage.

Clearinghouses are exclusively data prep and management focused, so should house RAW, INT or DWH datasets.

*   No project or data pipelines should be assembled here – and by extension no DASH datasets.  Those should be handled in a Department instance.

2.  Department
    ----------
    

An instance where projects are implemented.  

Datasources can be RAW or subscriptions of DWH datasets from another department.

*   We do not publish DASH datasets between departments

Every dataset should terminate as a DWH or DASH dataset.

*   Only DASH datasets can be published to a Distribution Center
*   Only DWH datasets can be published to other departments.

3.  Distribution Center
    -------------------
    

An instance that hosts certified dashboards and datasets (DASH)

There can be a public datacenter and a private datacenter for highly sensitive dashboards.

To prevent data manipulation in the distribution center, DataCenter along with any form of ETL access or content manipulation is disabled (no Participants or Editor rights).

*   The instance can only receive datasets shared via Publish / Subscriber.

### Responsibility for Governance

Public and private distribution centers are differentiated by who owns responsibility for governance – the publisher versus central BI.

### Public Distribution Center 

Subscriber jobs INTO the public DC must be managed by the departmental data owners

*   We only publish DASH datasets into the public DC

Content sharing is managed by the dashboard publisher (using groups).

*   By default PDP is NOT enabled on any dataset.

### Private Distribution Center

Subscriber jobs INTO the private DC must be managed by Central BI

All content sharing is managed by central BI – instance admins.

*   By default PDP is enabled on all datasets that enter the distribution center.

Sample Use Cases
================

1\. Engineering produces a dashboard
------------------------------------

Engineering owns “database\_monitoring” (dbm) and publishes a dashboard to the PDC (public distribution center)

*   DATASOURCE via raw - dbm\_RAW
*   ETL to produce dbm\_DWH and dbm\_DASH
*   DISTRIBUTE via publish to PDC (dbm\_DASH)

2\. Infosec augments Engineering’s dashboard
--------------------------------------------

Infosec wants to augment database\_monitoring (dbm) published by Engineering and publish it as a new asset in PDC (public distribution center)

*   DATASOURCES

*   via subscription from engineering (dbm\_DWH)

*   Because we do not do publish DASH between departmental instances

*   RAW data from internal sources

*   ETL produces infosec\_DWH and infosec\_DASH
*   DISTRIBUTE via publish to PDC (infosec\_DASH)

3\. SecOps chooses the most downstream branch
---------------------------------------------

Security Operations wants to augment the work from Infosec and publish it as a new asset in PDC.

*   This introduces a 3-step ETL chain (RAW, engineering (dbm\_DWH), or infosec (infosec\_DWH) that SecOps must choose where to branch from.

Publish / Subscriber requests should be configured from the most downstream certified data owner – in this case infosec.

*   If an update is made to how engineering handles database\_monitoring, this ensures the update is passed to infosec. If infosec updates their ornamentation, that update passes down to SecOps and anyone who has branched off of it.
