# Ro-Gazer

ro_gzr_wrapper was built to provide an easy to use interface to view and manage Spaces, Looks, and Dashboards on a Looker Server. Its main use case so far has been to bulk view, download, and upload Looks and Dashboards between [two Looker servers](https://discourse.looker.com/t/git-workflow-for-lookml-promotion-across-development-staging-and-production-instances/7999).

Base functions (for developer use) can be found in the gzr_core_functions.py file. These are built on top of the [gzr](https://github.com/deangelo-llooker/gzr/) command line tool. Further documentation around these core functions can be found [here.](https://github.com/ro-data/core_functions_documentation.md)

## Getting Started

To start, you should have [gzr](https://github.com/deangelo-llooker/gzr/) installed on your local machine. You can install this gem by simply typing:

    $ gem install gazer

Find more information about gzr commands at https://github.com/deangelo-llooker/gzr/

#### Prerequisites

* [AsciiTable](https://github.com/Robpol86/terminaltables) - Used to pretty print output
* [PyInquirer](https://github.com/CITGuru/PyInquirer) - Used to support the command line interface

## Connecting to a Looker server

Once you have installed gzr and the prerequisites, you can use ro_gzr_wrapper by running it as a python script:

    $ python ro_gzr_wrapper.py

You will be first be prompted for a Looker server to connect to. (If you connect at https://looker.example.com then looker.example.com is the server name)

Make sure you have set up your credentials in a ~/.netrc file as outlined at https://github.com/deangelo-llooker/gzr under 'Storing Credentials'.

Once you have connected to a Looker server, you will see the Main Menu.

![Main Menu](Screenshots/main_menu.png?raw=true "Main Menu")

You can navigate the command line interface using arrow keys and the enter key.

## Using ro_gzr_wrapper to transfer Looks/Dashboards between two Looker servers

1. [Viewing spaces in your home Looker directory](#viewing-spaces)

2. [Viewing information about a Look or Dashboard](#viewing-information-about-a-look-or-dashboard)

3. [Making a backup from server 1](#making-a-backup-from-server-1)

4. [Making a backup from server 2](##making-a-backup-from-server-1)

5. [Uploading local files to a Looker server](#uploading-local-files-to-a-looker-server)

#### Viewing Spaces

This uses the gzr command ```gzr space ls``` to list the contents of all spaces and their respective IDs in your home Looker directory.

#### Viewing information about a Look or Dashboard

To view information about Looks or Dashboards, select the ```View Looks and/or Dashboards``` option. The information that is displayed is ID, Name, Space ID, Space Name, and date it was last updated (only for Looks).

In general, information from looker will be stored in a dictionary of dictionaries, with a structure like below:
```
Home Looker Directory
├── Looks
│   └── Look IDs
│       └── Look Info (Name, Space ID, Space Name, Date Last Updated)
└── Dashboards
    └── Dashboard IDs
        └── Dashboard Info (Name, Space ID, Space Name)
```

- View all Looks and Dashboards

    This displays all Looks and Dashboards that were gathered from your home Looker directory. In general, this command will take a few minutes, and the output from this will be quite long. This will be formatted using AsciiTable.

- Filter what you see

    You can filter by the below three parameters. You can choose to filter by just one parameter, or you can combine multiple. When you are ready to view based on your filters, select ```View filtered entities```. **This is useful because you can download based on your latest filtered view.** If you exit the ```Filter what you see``` section, the latest filtered view will be saved, but the filter parameters will disappear.

    - Type (Looks, Dashboards, or Both)

    - Last Updated. This is only applicable for Looks, as Dashboards don't have a last_updated field when retrieving their information using gzr. This supports the same units of time as dateutil.relativedate, which are _years, months, weeks, days, hours, minutes, and microseconds._ Enter in an integer followed by a unit of time (e.g. '24 hours', '50000 microseconds').

    - Space ID. Enter a comma-deleted list of Space IDs (e.g. 3,4,5,73)

    - View filtered entities (This may take a few minutes, depending on how many Looks or Dashboards you have filtered to)

#### Making a backup from server 1

To download Looks and Dashboards from Looker to your local files, select the ```Download Looks/Dashboards from a Looker server``` option. You will be prompted for a directory path, and within that path, a folder will be created with the host name of the server you are currently connected to (If you connect at https://testcompany.looker.com, the folder will be 'testcompany'). Within that folder, subfolders will be created for Looks and Dashboards. If the path you specify doesn't exist, it will be created.

Within their respective folders, a json file will be created that contains all information about that Look or Dashboard. These json files contain much more information than is shown in the ```View Looks and/or Dashboards``` option. **These files can be uploaded into another Looker server**. One common use case for this is to move Looks and Dashboards from a production environment to a staging environment, or vice versa. The folder structure is like below:

```
Directory path you give
└── hostname
    ├── Looks
    │   ├── look_1.json
    │   ├── look_2.json
    │   └── look_n.json
    └── Dashboards
        ├── dashboard_1.json
        ├── dashboard_2.json
        └── dashboard_n.json
```

You can download Looks and Dashboards in the following ways:
- Provide a specific comma delimited list of Look/Dashboard IDs to download (e.g. 3,4,5,73)

- Download based on your most recent filtered view (if you have one). If you created a filter view in the ```View Looks/and or Dashboards``` section, the latest filtered view will have been saved, and you can download the Looks/Dashboards in that filtered view.

- Download all Looks/Dashboards. This will download all Looks and Dashboards that were gathered from your home Looker directory.

For every json file that you download, it will check the directory you are downloading into, and if a Look/Dashboard exists with the same id, it will prompt you whether you would like to overwrite that existing Look/Dashboard. You can choose to skip all future warnings if you do not want to be prompted for each download.

#### Making a backup from server 2

Close the script, reconnect using the name of your second Looker server, and follow the steps above.

#### Uploading local files to a Looker server

To upload local files to a Looker server, select the ```Upload Looks/Dashboards into a Looker server``` option. You will be prompted for a directory path that contains two subfolders called Looks and Dashboards, which contain json files to be uploaded (these json files should have been previously downloaded from a Looker server). This follows the same folder structure that was created if you exported using the ```Download Looks and/or Dashboards``` option.

Note: the directory path you enter here is one level deeper than the path you provide when you use the ```Download Look and/or Dashboards``` option.

You will be then be prompted for a Looker server that you wish to upload to (if you connect at https://looker.example.com then looker.example.com is the server name). If you are moving files between two Looker servers, you must have set up credentials for both servers in your ~/.netrc file.

You can upload Looks and Dashboards in the following ways:

- Provide a specific comma delimited list of Look/Dashboard IDs to upload (e.g. 3,4,5,73)

- Upload everything in a particular folder on your computer

For every json file that you upload, it will check the space you are uploading into, and if a Look/Dashboard exists with the same name, it will prompt you whether you would like to overwrite that existing Look/Dashboard. You can choose to skip all future warnings if you do not want to be prompted for each upload.

## Planned Updates / Known Issues

- Doesn't load Looks and Dashboards in users private spaces, so you can't view/download them unless you already know the ID or the Space ID for them.

- No function to create a Space on a Looker server. This makes it hard to upload looks onto an empty Looker server.

- Considering also writing the name of the Look/Dashboard when downloading, so that everything can be done on a _name_ basis, removing the discrepancy of gzr using IDs and Looker using names.

## Authors

* [**Kevin Stern**](https://github.com/kstern31)

## Acknowledgments

* [gzr](https://github.com/deangelo-llooker/gzr/) - Command line tool used to navigate and manage Spaces, Looks, and Dashboards on a Looker Server
