# Ro-Gazer

Ro-Gazer was built to provide an easy to use interface for programmatically managing _spaces_, _looks_, and _dashboards_ on a [Looker instance.](https://looker.com/) Its main use case so far has been
- to bulk transfer looks and dashboards between two Looker instances [(one for production, one for staging.)](https://discourse.looker.com/t/git-workflow-for-lookml-promotion-across-development-staging-and-production-instances/7999)
- to bulk modify looks and dashboards on a Looker instance.

Base functions (for Python developer use) can be found in the gzr_core_functions.py file. These are built on top of the [gzr](https://github.com/deangelo-llooker/gzr/) command line tool.

## Getting Started

To start, you should have [gzr](https://github.com/deangelo-llooker/gzr/) installed on your local machine. You can install this gem by simply typing:

    $ gem install gazer

Find more information about gzr commands at https://github.com/deangelo-llooker/gzr/

#### Prerequisites

* [AsciiTable](https://github.com/Robpol86/terminaltables) - Used to pretty print output
* [PyInquirer](https://github.com/CITGuru/PyInquirer) - Used to support the command line interface

## Connecting to a Looker instance

Once you have installed gzr and the prerequisites, you can use ro_gzr_wrapper by running it as a python script:

    $ python ro-gazer.py

You will be first be prompted for a Looker instance to connect to. (If you connect at https://looker.example.com then looker.example.com is the instance name)

Make sure you have set up your credentials in a ~/.netrc file as outlined at https://github.com/deangelo-llooker/gzr under 'Storing Credentials'.

Once you have connected to a Looker instance, you will see the Main Menu.

![Main Menu](Screenshots/main_menu.png?raw=true "Main Menu")

You can navigate the command line interface using arrow keys and the enter key.

## Using Ro-Gazer to transfer looks/dashboards between two Looker instances

1. [Viewing spaces in your home Looker directory](#viewing-spaces)

2. [Viewing information about a look or dashboard](#viewing-information-about-a-look-or-dashboard)

3. [Making a backup from instance 1](#making-a-backup-from-instance-1)

4. [Making a backup from instance 2](##making-a-backup-from-instance-1)

5. [Uploading local files to a Looker instance](#uploading-local-files-to-a-looker-instance)

#### Viewing spaces

Select the ```View spaces``` option. This uses the gzr command ```gzr space ls``` to list the contents of all spaces and their respective IDs in your home Looker directory.

#### Viewing information about a look or dashboard

To view information about looks or dashboards, select the ```View looks and/or dashboards``` option. The information that is displayed is ID, name, space ID, space name, and date it was last updated (only for looks).

In general, information from looker will be stored in a dictionary of dictionaries, with a structure like below:
```
Home Looker Directory
├── looks
│   └── look IDs
│       └── look info (name, space ID, space name, date last updated)
└── dashboards
    └── dashboard IDs
        └── dashboard info (name, space ID, space name)
```

- View all looks and dashboards

    This displays all looks and dashboards that were gathered from your home Looker directory. In general, this command will take a few minutes, and the output from this will be quite long. This will be formatted using AsciiTable.

- Filter what you see

    You can filter by the below three parameters. You can choose to filter by just one parameter, or you can combine multiple. When you are ready to view based on your filters, select ```View filtered entities```. **This is useful because you can download based on your latest filtered view.** If you exit the ```Filter what you see``` section, the latest filtered view will be saved, but the filter parameters will disappear.

    - Type (looks, dashboards, or both)

    - Last Updated. This is only applicable for looks, as dashboards don't have a last_updated field when retrieving their information using gzr. This supports the same units of time as dateutil.relativedate, which are _years, months, weeks, days, hours, minutes, and microseconds._ Enter in an integer followed by a unit of time (e.g. '24 hours', '50000 microseconds').

    - Space ID. Enter a comma-deleted list of space IDs (e.g. 3,4,5,73)

    - View filtered entities (This may take a few minutes, depending on how many looks or dashboards you have filtered to)

#### Making a backup from instance 1

To download looks and dashboards from Looker to your local files, select the ```Download looks/dashboards from a Looker instance``` option. You will be prompted for a directory path, and within that path, a folder will be created with the host name of the instance you are currently connected to (if you connect at https://testcompany.looker.com, the folder will be 'testcompany'). Within that folder, subfolders will be created for looks and dashboards. If the path you specify doesn't exist, it will be created.

Within their respective folders, a json file will be created that contains all information about that look or dashboard. These json files contain much more information than is shown in the ```View looks and/or dashboards``` option. **These files can be uploaded into another Looker instance**. One common use case for this is to move looks and dashboards from a production environment to a staging environment, or vice versa. The folder structure is like below:

```
Directory path you give
└── hostname
    ├── looks
    │   ├── look_1.json
    │   ├── look_2.json
    │   └── look_n.json
    └── dashboards
        ├── dashboard_1.json
        ├── dashboard_2.json
        └── dashboard_n.json
```

You can download looks and dashboards in the following ways:
- Provide a specific comma delimited list of look/dashboard IDs to download (e.g. 3,4,5,73)

- Download based on your most recent filtered view (if you have one). If you created a filter view in the ```View looks/and or dashboards``` section, the latest filtered view will have been saved, and you can download the looks/dashboards in that filtered view.

- Download all looks/dashboards. This will download all looks and dashboards that were gathered from your home Looker directory.

For every json file that you download, it will check the directory you are downloading into, and if a look/dashboard exists with the same id, it will prompt you whether you would like to overwrite that existing look/dashboard. You can choose to skip all future warnings if you do not want to be prompted for each download.

#### Making a backup from instance 2

Close the script, reconnect using the name of your second Looker instance, and follow the steps above.

#### Uploading local files to a Looker instance

To upload local files to a Looker instance, select the ```Upload looks/dashboards into a Looker instance``` option. You will be prompted for a directory path that contains two subfolders called looks and dashboards, which contain json files to be uploaded (these json files should have been previously downloaded from a Looker instance). This follows the same folder structure that was created if you exported using the ```Download looks/dashboards from a Looker instance``` option.

Note: the directory path you enter here is one level deeper than the path you provide when you use the ```Download looks/dashboards from a Looker instance``` option.

You will be then be prompted for a Looker instance that you wish to upload to (if you connect at https://looker.example.com then looker.example.com is the instance name). If you are moving files between two Looker instances, you must have set up credentials for both instances in your ~/.netrc file.

You can upload looks and dashboards in the following ways:

- Provide a specific comma delimited list of look/dashboard IDs to upload (e.g. 3,4,5,73)

- Upload everything in a particular folder on your computer

For every json file that you upload, it will check the space you are uploading into, and if a look/dashboard exists with the same name, it will prompt you whether you would like to overwrite that existing look/dashboard. You can choose to skip all future warnings if you do not want to be prompted for each upload.

## Planned Updates / Known Issues

- Doesn't load looks and dashboards in users private spaces, so you can't view/download them unless you already know the ID or the space ID for them.

- No function to create a space on a Looker instance. This makes it hard to upload looks onto an empty Looker instance.

- Considering also writing the name of the look/dashboard when downloading, so that everything can be done on a _name_ basis, removing the discrepancy of gzr using IDs and Looker using names.

## Authors

* [**Kevin Stern**](https://github.com/kstern31)

## Acknowledgments

* [gzr](https://github.com/deangelo-llooker/gzr/) - Command line tool used to navigate and manage spaces, looks, and dashboards on a Looker instance
