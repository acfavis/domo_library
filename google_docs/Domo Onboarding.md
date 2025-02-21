---
title: "\U0001F5C2️ Introduction "
---
This document describes the best practices for beginner Domo users. There are different personas use cases covered in this document:

*   Data Engineer
*   Product Stakeholder
*   Data Consumer
*   Visualization engineer
*   Support engineer

🖊️ this is a working document (ish).  Leave comments if specific content doesn’t make sense or you need more information.

Motivation
----------

This document contains a set of recommendations which will help end users:

*   Optimize the development process
*   Reduce development efforts
*   Be integrated into SIE process
*   Understand how to improve the content searchability and accessibility
*   Understand Domo tooling that can lead to improved customer satisfaction and engagement.

Relevant Links
--------------

[New Features](https://www.domo.com/product/new-features#/)

[Current Release Notes](https://domohelp.domo.com/hc/en-us/articles/360042936114-Current-Release-Notes)

🧵 Domo Training [Slack Channel](https://sie.slack.com/archives/C03QE172D33)

* * *

🗂️Basic Terms from Immersion Training
======================================

Core Domo Terms
---------------

*   DataSet: In Domo, a DataSet is a single flat table of data consisting of columns and rows.

*   Datasets are stored as flat files in “Vault” (Amazon S3) before getting loaded into “Adrenaline” (parallel distributed database layer)

*   DataFlow: a job in the Domo Data Center that makes transformations (e.g. joins, edits, calculations, etc.) to existing DataSets inside of Domo.

*   The output of a DataFlow is a new dataset (flat file) stored in Vault.

*   Analyzer: we design a Card in the Analyzer. The Analyzer is where we create and edit the card.  
    ﻿

*   Card: synonymous with “chart”, “graph”, or “plot”

*   Understanding Cards [KB link](https://domohelp.domo.com/hc/en-us/articles/360043428573-Understanding-Cards)
*   Each card gets reduced to a SQL Query against the underlying dataset  
    ﻿

*   Dashboard/Page: a group of cards ﻿

*   Managing Cards and Dashboards [KB Link](https://domohelp.domo.com/hc/en-us/sections/360007295674-Card-and-Dashboard-Management)

Unofficial Terms / “Scott’s Terms”
----------------------------------

*   Wall: a term to represent Pages in Domo (e.g. "I can see a bunch of different walls in Domo")

*   Pretty Picture: a term to represent Cards in Domo (e.g. I can see a bunch of pretty pictures hanging on a wall in Domo")

*   Shell: A Card is like a Shell - we design the Shell in the Analyzer and the data from the chosen DataSet flows in the Shell and is displayed according to the Shell parameters (i.e. filters, time frame, etc.)

"Business" Terms
----------------

*   Charts, graphs: Any sort of graphic to visualize data

*   Dashboards: A collection of key business indicators organized and arranged on a single page

🗂️ Working with Datasets
=========================

Jae Recommendations
-------------------

### Recommended naming conventions for datasets/dataflows

Use snake\_case as it is easier to read.

Ex. MYPROJ\_01\_historisation\_v1\_PROD

<PROJECT CODE>\_<STAGE\_ 1/2/X>\_<Description>\_<Version 1/2/X>\_<DEV/UAT/PROD>

Naming conventions allow the DSO team to track your utilization as well as facilitate data categorization.

*   The status of this dataset/dataflow. Also if you would like to create a copy and work on parallel development you just need to change the prefix to DEV and work on it.
*   Project Code should be unique and will help us to monitor the rows allocation per project per instance
*   Stage allows you better to define the data lineage and identify dependencies
*   Description provides more information about the nature of transformation or business logic
*   Versioning allows you to better manage the versioning (you might have PROD\_\_\_\_ V1 and then you create DEV\_\_\_\_ V2 to work on in the new version). This approach allows you to better control and separate different versions of dataflow.

### Account Creation and Dataset Continuity

#### Managing Accounts / Dataset Credentials when individuals go on PTO or leave the Company

Domo KB [Link](https://domohelp.domo.com/hc/en-us/articles/360042926054-Managing-User-Accounts-for-Connectors)

“I'd like to know what is the current way we use the service account to manage connectors / credentials in Domo so that the management of those connectors can be spread across a few individuals.  Currently, our team members are creating those connectors in their own account causing maintenance issues when those individual is on PTO or left the company.”

Datasets will continue executing using the stored credentials in an account object as long as the credentials are valid.  If a user is removed from Domo, the account is not automatically assigned, admins will need the Manage All Accounts role Grant to administer accounts that have not explicitly been shared with them.

Assign Account ownership to a service account OR a Domo Group (beta)

Take note that there are different account sharing levels, Read, Edit, Owner etc.

#### Creating Accounts

Accounts are created when users enter credentials for a datasource (Adobe Analytics, Salesforce, Snowflake etc). These credentials cannot be seen in plain text anywhere in Domo but are exchanged when a connector requests access from the source system.

Accounts are owned by a user(s) or group.

*   Owners can rename accounts and update the stored credentials (cycling credentials).  
*   Users who have Read access to an account can impersonate the stored credentials and create new data extracts from the source system.

### Recommended naming conventions for dataset columns

We recommend using snake case ([article](https://betterprogramming.pub/string-case-styles-camel-pascal-snake-and-kebab-case-981407998841)) for column names.

### Recommended tagging structure

To facilitate dataset classification, Jae requires the use of tags.  

Tags can be applied to datasets AND dataflows but they do not transfer automatically from a parent object to a child object.

#### Prefix Breakdown

cl\_

Content lifecycle

cl\_PROD

cl\_DEV

cl\_UAT

cl\_ARCHIVE

cl\_DELETE

pj\_

Project

pj\_MONIT

#### Known Project Prefixes

pj\_MONIT

For instance monitoring datasets (Domo\_Governance, Domo\_Stats etc).

### ETL and Data Pipeline Development

[How to Structure your DataCenter - video](https://www.youtube.com/watch?v=rS2e2_fv5yk)

*   Always comment you code (for MySQL/Redshift/Adrenaline flows) Each temporary table should be commented on purpose and what is the output
*   Try to use clear names for Magic tiles (instead of generated one like Select Columns 1/2/3 or Remove duplicates)
*   Use a bus matrix to organize and play your pipeline

*   Categorize datasets as Fact or Dimension (and wait till the late steps to JOIN them
*   Always apply GROUP BY or DEDUPLICATION before JOIN’ing in ETL
*   Try to UNION facts.  Do Not JOIN facts together.
*   Use the ALTER COLUMNS tile to standardize data types
*   UNION columns with an Activity\_Type and Activity\_Date for standard Filtering
*   Using WebForms you can join in descriptive information to augment datasets
*   Don’t filter your output datasets in ETL. Filter in Cards or a DSV used as a Semantic Layer.
*   Rationalize when it’s appropriate to write business logic into Magic (Formula tiles), webform\_lookups, vs. Beast Modes.
*   Do not leverage DSVs for data transformation if you’re also using Magic. Try to keep all your transformation logic in the same place.
*   If you are writing the same code multiple times, find a different implementation strategy
*   during this stage of adoption (and given the small data) JUST do Magic & Beast Modes. Don’t use DSVs until Users demand an intermediate semantic layer.

### Use Change Log and Versioning

Domo allows you to keep track of changes in the dataflow (all types).

### Archiving and Deleting Content

🚀 Deleting a dataflow does not automatically delete connected datasets.

To properly decommission dataflows:

1.  Relabel the output datasets, DELETE\_<dataset\_name>
2.  Relabel the dataflow, DELETE\_<dataflow\_name>
3.  Delete dataflows and datasets

There is no archive feature built into Domo.  As a surrogate for archiving, users can

1.  Disable execution of dataflows, workbench jobs, or connector datasources
2.  Use Lineage to confirm datasets are not part of an operational pipeline
3.  Relabel and retag assets.
4.  Cards and Pages can be moved from production pages and relabeled as appropriate.

Supporting Features from Domo
-----------------------------

*   Adrenaline Dataflows
*   Magic 2.0
*   CLI
*   Dataset Views
*   Publish
*   Certification
*   Advanced tools (Stacker, Data Assembler)

Which tool is the best for which use case
-----------------------------------------

Upsert and Partitioning tools
-----------------------------

* * *

🗂️ Visualize
=============

Understanding Pages and Dashboards
----------------------------------

In addition to default system dashboards (Overview, Favorites, Shared), as well as company-defined default dashboards, users can display content and cards on dashboards.

Page owners and users with manage pages rights can lock a page to prevent alterations to a page.  Consider the use of Certification workflows for ‘official’ content that should not be altered.

Change Card Interactions to control what happens when Users click on a Dashboard
--------------------------------------------------------------------------------

Default behavior is to apply filters on click, but dashboard designers change interaction behavior on a card by card basis.

Ex. Can have drilldown in place, or click to open a link to another Domo Page or external link.

Interactions [KB Link](https://domohelp.domo.com/hc/en-us/articles/360043428433-Creating-Domo-Stories#7.)

URL Links to pages can include predefined column filters using PFilters.  [KB Link](https://domohelp.domo.com/hc/en-us/articles/360042933114-Using-Pfilters-to-Apply-Filters-from-URL-Query-Parameters-to-Embedded-Dashboards)

### Additional Resources

*   Design better Dashboards / Tell Better Data Stories (📹 [YouTube Video](https://www.youtube.com/watch?v=Cpz2ecelaow))
*   Understanding Pages (System Defaults - Overview, Favorites, Shared – [KB Link](https://domohelp.domo.com/hc/en-us/articles/360043428553-Understanding-Pages))

Understanding Cards
-------------------

Cards are the Domo equivalent of charts, plots, or graphs.

Filtering, Sorting, cards in the Details view

### Sharing Cards to Pages vs Save As (creating a copy)

Sharing and Removing Access to Cards and Pages [Link to KB](https://domohelp.domo.com/hc/en-us/articles/360042932994-Sharing-and-Removing-Access-to-Cards-and-Pages)

### Lock your Cards and Pages to prevent users from editing the content.

### Chart Colors

Color Rules (“conditional formatting”) [Link to KB](https://domohelp.domo.com/hc/en-us/articles/360043428813-Setting-Color-Rules-for-a-Chart)

Changing Default Colors in different Chart Types [Link to KB](https://domohelp.domo.com/hc/en-us/articles/360043429653-Changing-the-Default-Colors-in-Your-Chart)

🚀 Only one Default Theme (color palette) can exist per instance in the form of the Brand Kit feature.   [Link to KB](https://domohelp.domo.com/hc/en-us/articles/5428851518999-Brand-Kit)

❓ “In Tableau when you select a field to color, it automatically assigns each distinct value a color. This is useful for say Department separation. We can then manually change it if needed.  How do you do it in Domo?”

*   Either set color rules (for metrics) OR if you have a chart type that allows you to add a Series (ex. Grouped bar chart) it will assign a color to each unique value

### Aggregation across Categories / Window Functions / Cumulative Sum

There are 3 ways to compare aggregates outside of the window of data you’re currently in

Segments

[KB Link](https://domohelp.domo.com/hc/en-us/articles/4403089503383-Creating-Segments-in-Analyzer)

Window Functions & Fixed Functions

Ultimate 2020 Window Function Tutorial 📹 [YouTube Video](https://www.youtube.com/watch?v=eifSYZIcPzg)

3 Month Average Lag 📹 [YouTube Video](https://www.youtube.com/watch?v=cnc6gMKZ9R8)

Certain Card Types allow cross category aggregation

Period over Period

Running Total

### Beast Modes are formulas defined in Analyzer / Cards

Beast Mode calculations will frequently use MySQL (and sometimes Redshift) syntax.

🚀 Beast Modes can be applied before aggregation (at the row level) or after aggregation

In most cases, any CASE statement should occur INSIDE a beast mode.

CASE statements and date-specific transforms that exist independently of aggregate functions should often move upstream and persist in the dataset itself.

### Understanding Card Sharing and Data Security

Card and Page sharing versus data security are two very different functions with different implications.  

⚠️ If you share a card or dashboard, you are implicitly giving READ access to the underlying dataset(s) represented in the entity.

⚠️ If there is content that needs to be filtered on a per-user basis consider using PDP (Personalized Data Permissions) to apply row-level security to limit the rows of data in a dataset a user has access to.

Jae Recommendations
-------------------

### Card Design

🚀 Naming Convention Tip:  Update the card title to indicate cards with a drill path.

*   Consider an asterisk, \*,  or ALT  + 16, ►, to indicate cards with a drill path.

🚀 There is a toggle to prevent users from drilling down to raw data

### Beast Mode Management

*   Use Beast Mode Manager and DomoGovernance\_BeastModes dataset to monitor beast mode proliferation in your instance
*   Card performance is directly correlated SQL commands issued in beast modes where possible to avoid COUNT(DISTINCT) and text-based operations (REGEX or LIKE).
*   When reasonable, materialize row-based transforms (date conversions) onto the dataset.
*   Sharing beast modes to datasets will improve card performance but will slow dataset indexing.
*   There is a difference between sharing a card versus making a copy of a card.  Cards can be shared (linked) to multiple pages making it easy to have one object to maintain.

### Card and Dashboard Management

*   Each card has its own URN.  You can either create a copy / duplicate of a card and embed it on a page (it will have its own URN) OR simply move or share a card to a page (it retains the original URN).

Card FAQ
--------

Is there a difference between “Save As” / “Duplicating” vs “Sharing” a card?

*   Save As or Duplicate will create a new object in Domo that is separate from the original entity.  
*   Changes made to the duplicated card or the original card will not impact the other.  
*   [Duplicating Cards KB](https://domohelp.domo.com/hc/en-us/articles/360042923274-Duplicating-Cards-Save-As-)

Can I prevent users from altering my card or page?

*   Yes, lock your content.  [KB Link](https://domohelp.domo.com/hc/en-us/articles/360042923814-Locking-or-Unlocking-Page-Content)
*   Consider a certification flow for ‘official content’.  [KB Link](https://domohelp.domo.com/hc/en-us/articles/360043430613-Certifying-Cards-and-DataSets)

How can I alias data (fix values) or create a custom calculated metric in a card?

*   Create a Beast Mode [Link KB](https://domohelp.domo.com/hc/en-us/sections/360007295754-Beast-Mode) using MySQL syntax functions

*   Ex. CASE WHEN END or SUM(CASE WHEN …  END)

* * *

🗂️ Interacting with Domo Content
=================================

Card Features for Participants (non-editors)
--------------------------------------------

### Use Annotations to share insights

Create card annotations and find or document interesting insights using annotations

*   [Annotation KB](https://domohelp.domo.com/hc/en-us/articles/360042923974-Adding-Chart-Annotations)

### Use Alerts to update users with changes in Domo

*   [Alerts KB](https://domohelp.domo.com/hc/en-us/sections/360007334393-Notifications-and-Alerts)

Alerts can be configured for cards and metrics represented in cards as well as datasets.

Card Features for Editors
-------------------------

### Use Quick Filters to encourage data exploration

*   [Quick Filters KB](https://domohelp.domo.com/hc/en-us/articles/360042924074-Adding-Filters-to-Your-Chart) 

### Use Page-level Filter Views to create preset combinations of filters for a guided user experience

*   [Filter Views KB](https://domohelp.domo.com/hc/en-us/articles/360042923914-Applying-Page-Level-Filters-with-Filter-Views)

### Add Drill Paths to Cards to control the exploration experience

*   [Drill Paths KB](https://domohelp.domo.com/hc/en-us/articles/360042924094-Adding-a-Drill-Path-to-Your-Chart)

* * *

🗂️ Project Handover / Moving into Production
=============================================

Documentation
-------------

*   High Level Design / Solution overview
*   New Users’ guide
*   Data Dictionary (see section below)

Data Quality
------------

Domo Momentum - Certification
-----------------------------

Dev / Prod & Maintenance
------------------------

### Use Domo Sandbox for managing same instance and cross-instance dev/prod content

*   By default SIE Domo instances will not have a second Domo instance to separate Dev from Prod.  Within the same instance however, Domo Sandbox can help manage the promotion of development assets to production and back. [Sandbox KB](https://domohelp.domo.com/hc/en-us/articles/4403367344023-Domo-Sandbox) 

*   Do not make full copies of production datasets into Dev; instead, consider developing against randomized samples of data.  This will both help manage developer experience (faster execution times) and instance rowcount.

### Transfer Assets to Appropriate Stakeholders

* * *

🗂️ Governance Themes
=====================

KB Domo Enterprise Toolkit - [https://domohelp.domo.com/hc/en-us/articles/5299662679447-Domo-Enterprise-Toolkit](https://domohelp.domo.com/hc/en-us/articles/5299662679447-Domo-Enterprise-Toolkit)

Single Sign On (SSO) and OKTA Authentication
--------------------------------------------

[User and Group Management KB](https://domohelp.domo.com/hc/en-us/sections/360007334573-User-and-Group-Management) link

Users can be aJaed to Domo at will.  The SIE Domo contract does not charge licensing fees on a per user basis.

See [Adding Users to Domo KB](https://domohelp.domo.com/hc/en-us/articles/360042934274-Adding-Users-to-Domo) link

Out of the box, Domo user authentication is handled with email and login.  User provisioning and authentication can be handled via SSO ([SSO using SAML KB](https://domohelp.domo.com/hc/en-us/articles/360042934374-Understanding-and-Configuring-Domo-Single-Sign-On-Using-SAML) link)

### Logging into Domo via Direct Sign On in an environment with SSO

To bypass SSO Authentication, users must first be added to the [Direct Sign On (DSO) List](https://domohelp.domo.com/hc/en-us/articles/360042934374-Understanding-and-Configuring-Domo-Single-Sign-On-Using-SAML#4.).  

Once aJaed to DSO, users can bypass SSO by adding /auth/index?domoManualLogin=true to the url.

Users, Groups, Roles
--------------------

### ⚖️ SIE Standard Roles

Roles are comprised of Grants which determine actions users can take in Domo.

Jae will create standard roles and groups to which instance members will be assigned by default.  Instance admins can create their own custom roles for departmental users as necessary.

*   SIE\_Admin
*   SIE\_Reset
*   SIE\_Priviliged

*   Privileged + ADR Flows

*   SIE\_Test

To monitor role & Grant configuration:

*   Go To Admin > Governance > Roles > Grid

### Define Custom Roles

*   [https://knowledge.domo.com/Administer/Controlling\_Access\_in\_Domo/Managing\_Custom\_Roles](https://knowledge.domo.com/Administer/Controlling_Access_in_Domo/Managing_Custom_Roles)
*   [https://knowledge.domo.com/Administer/Controlling\_Access\_in\_Domo/04Security\_Role\_Reference](https://knowledge.domo.com/Administer/Controlling_Access_in_Domo/04Security_Role_Reference)

### ⚖️ SIE Default Groups

*   SIE Admin
*   SIE User

### Defining Groups

Where Roles and Grants define what users can do, Group membership should be used to either:

*   Manage content ownership
*   Share content

Avoid the temptation to manage content by individuals, instead try to adopt the practice of sharing content with groups.

*   [https://domohelp.domo.com/hc/en-us/articles/360042934294-Creating-and-Managing-User-Groups](https://domohelp.domo.com/hc/en-us/articles/360042934294-Creating-and-Managing-User-Groups)

### Implement Row-Level Security with Personalized Data Permissions (PDP)  Policies

🚀 Monitoring card sharing is NOT a replacement for applying PDP policies.  Jae strongly recommends applying PDP policies to all sensitive data in Domo.

🚀 A card gets reduced to a SQL query against a dataset which is executed at runtime (i.e. when Michelle tries to view the card).  AND PDP creates row-level security to the dataset which limits what gets returned by the query.

ex. Michelle can create a card against any dataset that has been shared with her, but she will only see the rows the pdp policy allows her to see.

ex. SELECT Product, sum(amount) GROUP BY Product.

🚀 PDP policies are additive (each policy you’re a part of adds an OR clause for the data you can see).

#### PDP Links

*   Personalized Data Permissions - [KB Link](https://domohelp.domo.com/hc/en-us/sections/360007334593-Personalized-Data-Permissions-PDP-)
*   [https://domohelp.domo.com/hc/en-us/articles/4415800746391-Governance-Toolkit-PDP-Automation](https://domohelp.domo.com/hc/en-us/articles/4415800746391-Governance-Toolkit-PDP-Automation)
*   [https://domohelp.domo.com/hc/en-us/articles/360043439353-PDP-Policy-Autocreation](https://domohelp.domo.com/hc/en-us/articles/360043439353-PDP-Policy-Autocreation)

Datacenter Audits
-----------------

*   Create a schedule with your technology & business users to clean up on a regular basis and monitor the results through governance and activity logs
*   Set cleaning campaigns to a theme to make it fun
*   Check to make sure your instance objects are in security compliance with other parts of the business
*   Set alerts on ETL jobs to monitor failure – can set up as SMS message
*   Check schedules for ETL jobs and make sure they are available when needed for the business dashboard users

### Security

⚠️ By default, most users will not see all the data available in the datacenter; however, sharing a card automatically shares the underlying dataset.  Therefore PDP ([personalized data permissions KB](https://domohelp.domo.com/hc/en-us/sections/360007334593-Personalized-Data-Permissions-PDP-)) is the only way to implement proper data security.  

Manage Data using Metadata
--------------------------

*   Use Tags facilitate dataset audits and provide additional dataset metadata ([KB](https://domohelp.domo.com/hc/en-us/articles/4415839139863-Governance-Toolkit-DataSet-Tagging))

*   Utilize the Governance Connectors [(KB)](https://domohelp.domo.com/hc/en-us/articles/360056318074-Domo-Governance-Datasets-Connector) to access data schemas, beastmodes, access rights to dataset, and tags
*   Create a data dictionary dashboard

Monitor Domo Instance and Projects
----------------------------------

* * *

🗂️ Domo Pipeline Optimization
==============================

Domo Architecture Review
------------------------

🗂️ Domo Features
=================

Data Science Toolkit
--------------------

### Jupyter Notebook

[KB](https://domohelp.domo.com/hc/en-us/articles/360047400753-Jupyter-Workspaces) link

Primary Advantages

*   Notebooks can be scheduled to run as a dataflow
*   Datasets can be read in or updated using the domo jupyter package
*   During development, the performance of the notebooks will feel much faster than Magic 2.0 Scripting Tiles

Disadvantages

*   No built-in version control (no access to private GitHub)
*   No easy way to “download all files”

Extending Domo with APIs
------------------------

📚 Jae [Private API documentation](https://documenter.getpostman.com/view/5049119/UyxbppB2)
