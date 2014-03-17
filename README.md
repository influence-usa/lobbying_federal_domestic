lobbying-domestic
=================

Public domain code that collects data about domestic lobbying at the Federal Level, as reported by the [Senate Office of Public Records](http://www.senate.gov/pagelayout/legislative/one_item_and_teasers/opr.htm) and the [House Office of the Clerk](http://clerk.house.gov/).

Includes utilities for downloading, scraping, and storing:

 - SOPR XML:
   - Registrations (Form LD-1)
   - Lobbying Reports (Form LD-2)
     - 1999-2007: Reported semiannually (mid-year and year-end)
     - 2008-present: Reported quarterly
   - Termination Reports (Form LD-2)
     - Distinguished from other reports by boolean field (checkbox)
   - Miscellaneous 
     - Documents: other requests, including corrections
     - Terminations: requests to terminate registration of lobbyist, entity or registrant
   - Amendments
     - Registration amendments
     - Termination Amden
 
Planned:

 - Scraper for LD1/2 [template forms](http://lobbyingdisclosure.house.gov/software.asp)
 - Scraper for [registrant/client list](http://www.senate.gov/pagelayout/legislative/one_item_and_teasers/clientlist_parent.htm)
 - 

Setting Up
----------

Scripts are tested with Python 2.7. On Ubuntu, you'll need these packages (the last three are required for the lxml python package):

    sudo apt-get install git python-virtualenv python-dev libxml2-dev libxslt1-dev libz-dev

It's recommended you first create and activate a virtualenv. You can use [virtualenvwrapper](https://bitbucket.org/dhellmann/virtualenvwrapper/) or add a virtualenv at the root of your working directory with:

    cd path/to/working/dir
    virtualenv .env
    source .env/bin/activate

You don't need to call it `.env`, but `.gitignore` is set up to ignore that path. Also useful if you're using [autoenv](https://github.com/kennethreitz/autoenv).

Collecting the data
-------------------

The general form to start the scraping process is:

    ./run <data-type> [--force] [--fast] [other options]

where `<data-type>` is one of:

  - sopr
  - template_forms
  - registrant_client_list

Common options
--------------

The scripts will cache all downloaded pages and zip files, and it will not re-fetch them from the network unless a force flag is passed:

    ./run bills --force

Debugging messages are hidden by default. To include them, run with --log=info or --debug. To hide even warnings, run with --log=error.

To get emailed with errors, copy config.yml.example to config.yml and fill in the SMTP options. The script will automatically use the details when a parsing or execution error occurs.

Output
------

Because lobbying disclosures are both incomplete and a bit awkwardly formatted, the scripts included here make various decisions about how to alter them. While these alterations serve our purposes, they may not be what you're lookign for. In any case, however, we'll always be interested in what the original source documents are. For that reason, each script has two kinds of output:

  - original data goes into the top-level `original` directory
  - transformed data goes into a top-level `data` directory 
  
Each top-level directory is then organized by data-type, and each data-type has its own subfolder organization. In the case of SOPR filings (the output of `./run sopr`), the file tree is organized by year, quarter, month, day and filing type. Two data output files will be generated for each filing: the original XML (original.xml) a JSON version (data.json) and an XML version (data.xml). The result is the following folder structure:

    .
    ├── cache 
    │   └── sopr 
    │       ├── 1999
    │       │   ├── 1999_1.zip *(downloaded zip)*
    │       │   ├── 1999_2.zip
    │       │   ├── 1999_3.zip
    │       │   └── 1999_4.zip
    │       ├ ...
    │       └── 2014
    │           ├── 2014_1.zip
    │           ├── 2014_2.zip
    │           ├── 2014_3.zip
    │           └── 2014_4.zip
    ├── original 
    │   └── sopr 
    │       ├── 1999 *(year)*
    │       │   ├── Q1 *(quarter)*
    │       │   │   ├── 1999_1_1_1.xml *(each XML file contains multiple filings)*
    │       │   │   ├── 1999_1_2_1.xml
    │       │   │   └── 1999_1_3_1.xml
    │       │   ├── Q2
    │       │   │   ├── 1999_2_4_1.xml
    │       │   │   ├ ...
    │       │   │   └── 1999_2_6_1.xml
    │       │   ├── Q3
    │       │   │   └── ...
    │       │   └── Q4
    │       │       └── ...
    │       ├ 2000
    │       │   ├── Q1
    │       │   │   └── ...
    │       │   ├── Q2
    │       │   │   └── ...
    │       │   ├── Q3
    │       │   │   └── ...
    │       │   └── Q4
    │       │       └── ...
    │       ├ ...
    │       └── 2014
    │           └── ...
    └── data
        └── sopr 
            ├── 1999 *(year)*
            │   ├── Q1 *(quarter)*
            │   │   ├── registration *(filing type)*
            │   │   │   ├── 04EA3DE2-694C-4492-BCC1-0B1F137684B6.csv *(tranformed filings)*
            │   │   │   ├── 04EA3DE2-694C-4492-BCC1-0B1F137684B6.json
            │   │   │   ├── 64F62652-7E13-4E7B-92B5-1836721C483A.csv
            │   │   │   ├── 64F62652-7E13-4E7B-92B5-1836721C483A.json
            │   │   │   ├ ...
            │   │   │   ├── C7808F4F-5EBE-4005-B5A6-28E22A1F8753.csv
            │   │   │   └── C7808F4F-5EBE-4005-B5A6-28E22A1F8753.json
            │   │   ├── registration_amendment
            │   │   │   └── ...
            │   │   ├── termination
            │   │   │   └── ...
            │   │   ├── termination_letter
            │   │   │   └── ...
            │   │   ├── termination_amendment
            │   │   │   └── ...
            │   │   ├── report
            │   │   │   └── ...
            │   │   ├── misc_document
            │   │   │   └── ...
            │   │   └── misc_termination
            │   │       └── ...
            │   ├── Q2 *(quarter)*
            │   │   ├── registration
            │   │   │   └── ...
            │   │   ├ ...
            │   │   └── misc_termination
            │   │       └── ...
            │   ├── Q3
            │   │   └── ...
            │   └── Q4
            │       └── ...
            ├── 2000
            │   └── ...
            ├ ...
            └── 2014
                └── ...

See the [project wiki](https://github.com/sunlightlabs/lobbying-domestic/wiki) for documentation on the output format.

Contributing
------------

Pull requests with patches are awesome. Unit tests are strongly encouraged ([example tests](https://github.com/sunlightlabs/lobbying-domestic/blob/master/test/test_sopr.py)).

The best way to file a bug is to [open a ticket](https://github.com/sunlightlabs/lobbying-domestic/issues).

Running tests
-------------

To run this project's unit tests:

    ./test/run

Who's Using This Data
---------------------

The [Sunlight Foundation](http://sunlightfoundation.com) is the principal maintainer of this project.

## Public domain

This project is [dedicated to the public domain](LICENSE). As spelled out in [CONTRIBUTING](CONTRIBUTING.md):

> The project is in the public domain within the United States, and copyright and related rights in the work worldwide are waived through the [CC0 1.0 Universal public domain dedication](http://creativecommons.org/publicdomain/zero/1.0/).

> All contributions to this project will be released under the CC0 dedication. By submitting a pull request, you are agreeing to comply with this waiver of copyright interest.
