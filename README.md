lobbying-domestic
=================

Public domain code that collects data about domestic lobbying at the Federal Level, as reported by the [Senate Office of Public Records](http://www.senate.gov/pagelayout/legislative/one_item_and_teasers/opr.htm) and the [House Office of the Clerk](http://clerk.house.gov/).

Includes utilities for downloading, scraping, and storing:

 - SOPR XML and House XML:
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

    ./run.py <action> <data-type> [--force] [--fast] [other options]

where 

`<action>` is one of:
  - download
  - extract
  - transform
  - ~~load~~ (not implemented)

`<data-type>` is one of:
  - sopr
  - house_xml (no transform step, yet)
  - ~~template_forms~~
  - ~~registrant_client_list~~

Common  options
--------------

The scripts will cache all downloaded pages and zip files, and it will not re-fetch them from the network unless a force flag is passed:

    ./run.py download sopr_html --force

Debugging messages are shown by default. To ignore them, run with --loglevel=warn. To hide even warnings, run with --loglevel=error.

To get emailed with errors, copy config.yml.example to config.yml and fill in the SMTP options. The script will automatically use the details when a parsing or execution error occurs.

Output 
------

Because lobbying disclosures are both incomplete and a bit awkwardly formatted, the scripts included here make various decisions about how to alter them. While these alterations serve our purposes, they may not be what you're lookign for. In any case, however, we'll always be interested in what the original source documents are. For that reason, the top-level `data` directory has several subdirectories.

  - downloaded data goes into the `data/cache` directory
  - original extracted data goes into the `data/original` directory
  - transformed data goes into the `data/transformed` directory
  
Each top-level directory is then organized by data-type, and each data-type has its own subfolder organization. In the case of SOPR filings (the output of `./run sopr`), the file tree is organized by year, quarter, month, day and filing type. Two data output files will be generated for each filing: the original XML (original.xml) a JSON version (data.json) and an XML version (data.xml). The result is the following folder structure:

    .
    data
    ├── cache
    │   ├── house_clerk
    │   │   ├── 2004_MidYear_XML.zip
    │   │   ├── 2004_Registrations_XML.zip
    │   │   ├── 2004_YearEnd_XML.zip
    │   │   ├── 2005_MidYear_XML(2).zip
    │   │   ├..
    │   │   ├── 2013_4thQuarter_XML.zip
    │   │   ├── 2013_Registrations_XML.zip
    │   │   ├── 2014_1stQuarter_XML.zip
    │   │   └── 2014_Registrations_XML.zip
    │   └── sopr
    │       ├── 1999
    │       │   ├── Q1
    │       │   │   └── 1999_1.zip
    │       │   ├── Q2
    │       │   │   └── 1999_2.zip
    │       │   ├── Q3
    │       │   │   └── 1999_3.zip
    │       │   └── Q4
    │       │       └── 1999_4.zip
    │       ├ ...
    │       └── 2014
    │           ├── Q1
    │           │   └── 2014_1.zip
    │           ├── Q2
    │           ├── Q3
    │           └── Q4
    ├── original
    │   └── sopr
    │       ├── 1999
    │       │   ├── Q1
    │       │   │   ├── 1999_1_1_1.xml
    │       │   │   ├── 1999_1_2_1.xml
    │       │   │   └── 1999_1_3_1.xml
    │       │   ├── Q2
    │       │   │   ├── 1999_2_4_1.xml
    │       │   │   ├── 1999_2_5_1.xml
    │       │   │   └── 1999_2_6_1.xml
    │       │   ├── Q3
    │       │   │   ├── 1999_3_7_1.xml
    │       │   │   ├── 1999_3_7_2.xml
    │       │   │   ├── 1999_3_8_10.xml
    │       │   │   ├── 1999_3_8_11.xml
    │       │   │   ├── 1999_3_8_12.xml
    │       │   │   ├── 1999_3_8_1.xml
    │       │   │   ├── 1999_3_8_2.xml
    │       │   │   ├── 1999_3_8_3.xml
    │       │   │   ├── 1999_3_8_4.xml
    │       │   │   ├── 1999_3_8_5.xml
    │       │   │   ├── 1999_3_8_6.xml
    │       │   │   ├── 1999_3_8_7.xml
    │       │   │   ├── 1999_3_8_8.xml
    │       │   │   ├── 1999_3_8_9.xml
    │       │   │   └── 1999_3_9_1.xml
    │       │   └── Q4
    │       │       ├── 1999_4_10_1.xml
    │       │       ├── 1999_4_11_1.xml
    │       │       └── 1999_4_12_1.xml
    │       ├ ...
    │       └── 2014
    │           └── Q1
    │               ├── 2014_1_1_10.xml
    │               ├── 2014_1_1_11.xml
    │               ├ ...
    │               ├── 2014_1_2_2.xml
    │               └── 2014_1_3_1.xml
    └── transformed
        └── sopr
            ├── 1999
            │   ├── Q1
            │   │   ├── 00EA7DAA-6E3B-464A-856A-C5AB20F2A0DE.json
            │   │   ├── 01443BC7-AF38-4461-91D7-343630397195.json
            │   │   ├── 01B3DC8C-940E-4C85-9CBD-CB4326DA8AAE.json
            │   │   ├ ...
            │   │   ├── FF2C94D2-AF6D-4F63-8629-61255EC45E6A.json
            │   │   ├── FF640844-6133-4908-AB11-501E2161333D.json
            │   │   └── FFF29969-FDEC-4125-809E-0D8D2D8E73FC.json
            │   ├── Q2
            │   │   ├── 002EC404-D74D-4549-96B3-C6B5315D3148.json
            │   │   ├── 00387A4B-E159-4985-BDC0-70D14CA45974.json
            │   │   ├── 007F8718-0BDA-4AC7-8398-063BC1BC8ACA.json
            │   │   ├ ...
            │   │   ├── FFA276F6-D085-4DF7-B37E-5553D08EB16C.json
            │   │   ├── FFCD9060-BE89-4BC3-AF80-8B10F051064C.json
            │   │   └── FFCF95F8-C398-4163-AE62-76F3AD1D7BE8.json
            │   ├── Q3
            │   │   ├── 000D9EB3-8C23-4C6D-9F2C-BB367972902C.json
            │   │   ├── 000E52A8-1C79-47E2-9271-24407622FA56.json
            │   │   ├── 001120FC-38E4-44E8-8BD2-E75DA83AA13D.json
            │   │   ├ ...
            │   │   ├── FFF2C2C2-BAB6-4D98-99D8-2C22A06F2F6B.json
            │   │   ├── FFF31AA5-A208-4483-A245-10748DC79244.json
            │   │   └── FFFA13F7-1604-4B69-84E5-755B0DC55CE6.json
            │   └── Q4
            │       ├── 00952398-BC53-4710-9187-418B310B77B3.json
            │       ├── 00B3D9E2-2F76-4DF8-ABF7-B8200786FD3A.json
            │       ├── 00ED3EE5-EB83-4831-9B38-B0EF12F8B5FE.json
            │       ├ ...
            │       ├── FFD100FF-1102-446B-B930-23E505CCD759.json
            │       ├── FFE3B80C-F96E-4C2F-AE01-5D9415D252B7.json
            │       └── FFE4894E-5977-40E3-9084-E77D1F39794C.json
            ├── ...
            └── 2014
                └── Q1
                

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
