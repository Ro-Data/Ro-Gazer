# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import re
import gzr_core_functions
import sys
from collections import defaultdict

from pprint import pprint
from PyInquirer import style_from_dict, Token, prompt
from PyInquirer import Validator, ValidationError


style = style_from_dict({
    Token.QuestionMark: '#E91E63 bold',
    Token.Selected: '#673AB7 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#2196f3 bold',
    Token.Question: '',
})

class ListValidator(Validator):
    def validate(self, document):
        try:
            comma_list = document.text.split(',') if len(document.text) > 0 else list(document.text)
            [int(number) for number in comma_list]
        except ValueError:
            raise ValidationError(
                message='Please enter a comma delimited list of integers (e.g. \'1,3,5,7\')',
                cursor_position=len(document.text))  # Move cursor to end

class TimeValidator(Validator):
    def validate(self, document):
        units_of_time = ['years', 'months', 'weeks', 'days', 'hours', 'minutes', 'seconds', 'microseconds']
        try:
            int(document.text.split()[0])
            document.text.split()[1] in units_of_time
        except ValueError:
            raise ValidationError(
                message='Please enter a valid number, and unit of time (e.g. \'3 days\', or \'45 minutes\').',
                cursor_position=len(document.text))  # Move cursor to end

print('\033[35m {}\033[00m' .format('\nHi, welcome to Ro-Gazer\n'))

# Initial Connection
def connect():
    instance = {
            'type': 'input',
            'name': 'host',
            'message': 'What Looker instance would you like to connect to? \n(If you connect at https://looker.example.com then looker.example.com is the instance name)\n',
            }
    host = prompt(instance, style = style)['host']
    return host

# Main Menu
def main_menu():
    main_menu_questions = {
            'type': 'list',
            'name': 'top_options',
            'message': 'What do you want to do?',
            'choices': ['View spaces',
                        'View looks and/or dashboards (option to filter by parameters)',
                        'Download looks/dashboards from a Looker instance (creating local files on your computer)',
                        'Upload looks/dashboards into a Looker instance (using local files on your computer)',
                        'Exit']
            }

    main_menu_answers = prompt(main_menu_questions, style=style)
    return main_menu_answers['top_options']

# Viewing looks/dashboards
def view_menu():
    view_menu_questions = {
            'type': 'list',
            'name': 'view_options',
            'message': 'You have chosen to view looks and dashboards. Would you like to:',
            'choices': ['View all looks and dashboards',
                        'Filter what you see',
                        'Go back'],
            }
    view_menu_answers = prompt(view_menu_questions, style=style)
    return view_menu_answers['view_options']

# Filtering before Viewing looks/dashboards
def filter_menu():
    filter_menu_questions = {
            'type': 'list',
            'name': 'filter_options',
            'message': 'You have chosen to filter looks and dashboards. Filter by:',
            'choices': ['Type (looks, dashboards, or both)',
                        'Last Updated (only applicable for looks)',
                        'Space ID',
                        'View filtered entities',
                        'Go back'],
            }
    filter_menu_answers = prompt(filter_menu_questions, style = style)
    return filter_menu_answers['filter_options']

def filter_menu_type():
    filter_menu_type_questions = {
            'type': 'list',
            'name': 'type',
            'message': 'You have chosen to filter by type. Only view:',
            'choices': ['Looks',
                        'Dashboards',
                        'Both'],
            'default': 'Both',
            'filter': lambda val: val.lower()
            }
    filter_menu_type_answers = prompt(filter_menu_type_questions, style = style)
    return filter_menu_type_answers['type']

def filter_menu_last_updated():
    filter_menu_last_updated_questions = {
            'type': 'input',
            'name': 'last_updated',
            'message': 'You have chosen to filter by when a look was last updated. Enter in the format \'number unit_of_time\' (e.g. \'3 hours\' or \'5 weeks\')',
            'filter': lambda val: val.lower(),
            'validate': TimeValidator
            }
    filter_menu_last_updated_answers = prompt(filter_menu_last_updated_questions, style = style)
    return filter_menu_last_updated_answers['last_updated']

def filter_menu_space():
    filter_menu_space_questions = {
            'type': 'input',
            'name': 'space',
            'message': 'You have chosen to filter by space ID. Please enter a comma delimited list of space IDs (e.g. \'1,3,5,7\')',
            'filter': lambda val: [num.strip() for num in val.split(',')] if len(val) > 0 else list(val),
            'validate': ListValidator
            }
    filter_menu_space_answers = prompt(filter_menu_space_questions, style = style)
    return filter_menu_space_answers['space']

# Downloading looks/dashboards
def download_menu():
    download_menu_questions = {
            'type': 'list',
            'name': 'download_options',
            'message': 'You have chosen to download looks and dashboards. Would you like to:',
            'choices': ['Provide a specific comma delimited list of look/dashboard IDs to download',
                        'Download based on your most recent filtered view (if you have one)',
                        'Download all looks/dashboards',
                        'Go back'],
            }

    download_menu_answers = prompt(download_menu_questions, style = style)
    return download_menu_answers['download_options']

def download_dir(host):
    hostname = host.split('.')[0]
    download_dir_questions = {
            'type': 'input',
            'name': 'dir',
            'message': 'Where do you want to download to? '
'Provide a directory path, and a folder will be created called %s, with two sub folders (Looks and Dashboards).\n'
'(E.g. If you input \'~/Looker_Files/\', ~/Looker_Files/%s/Looks/ and ~/Looker_Files/%s/Dashboards/ will be created to store look and dashboard json files)\n' % (hostname, hostname, hostname),
            'filter': lambda val: ' '.join(val.split())
            }

    download_dir_answers = prompt(download_dir_questions, style=style)
    return download_dir_answers['dir']

def download_menu_list():
    download_menu_list_questions = {
            'type': 'list',
            'name': 'comma_list',
            'message': 'Provide a comma delimited list of:',
            'choices': ['Look IDs',
                        'Dashboard IDs',
                        'Download provided list of entities',
                        'Go back'],
            }
    download_menu_list_answers = prompt(download_menu_list_questions, style = style)
    return download_menu_list_answers['comma_list']

def download_menu_list_looks():
    download_menu_list_looks_questions = {
            'type': 'input',
            'name': 'comma_list_looks',
            'message': 'Please enter a comma delimited list of look IDs (e.g. \'1,3,5,7\')',
            'filter': lambda val: [num.strip() for num in val.split(',')] if len(val) > 0 else list(val),
            'validate': ListValidator
            }
    download_menu_list_looks_answers = prompt(download_menu_list_looks_questions, style = style)
    return download_menu_list_looks_answers['comma_list_looks']

def download_menu_list_dboards():
    download_menu_list_dboards_questions = {
            'type': 'input',
            'name': 'comma_list_dashboards',
            'message': 'Please enter a comma delimited list of dashboard IDs (e.g. \'1,3,5,7\')',
            'filter': lambda val: [num.strip() for num in val.split(',')] if len(val) > 0 else list(val),
            'validate': ListValidator
            }
    download_menu_list_dboards_answers = prompt(download_menu_list_dboards_questions, style = style)
    return download_menu_list_dboards_answers['comma_list_dashboards']


# Uploading looks/dashboards
def upload_menu():
    upload_menu_questions = {
            'type': 'list',
            'name': 'upload_options',
            'message': 'You have chosen to upload looks and dashboards. Would you like to:',
            'choices': ['Provide a specific comma delimited list of look/dashboard IDs to upload',
                        'Upload everything in a particular folder',
                        'Go back'],
            }
    upload_menu_answers = prompt(upload_menu_questions, style = style)
    return upload_menu_answers['upload_options']

def upload_dir(host):
    hostname = host.split('.')[0]
    upload_dir_questions = {
            'type': 'input',
            'name': 'dir',
            'message': 'Where do you want to upload from? '
'Provide a directory path to a folder that contains two sub folders (Looks and Dashboards) with json files.\n '
'(E.g. If you input \'~/Looker_Files/%s\', json files from ~/Looker_Files/%s/Looks/ and ~/Looker_Files/%s/Dashboards/ will be uploaded)\n' % (hostname, hostname, hostname),
            }

    upload_dir_answers = prompt(upload_dir_questions, style=style)
    return upload_dir_answers['dir']

def dest():
    instance = {
            'type': 'input',
            'name': 'dest',
            'message': 'What Looker instance would you like to upload these local files to? \n(If you connect at https://looker.example.com then looker.example.com is the instance name)\n',
            }
    dest = prompt(instance, style = style)['dest']
    return dest

def upload_menu_list():
    upload_menu_list_questions = {
            'type': 'list',
            'name': 'comma_list',
            'message': 'Provide a comma delimited list of:',
            'choices': ['Look IDs',
                        'Dashboard IDs',
                        'Upload provided list of entities',
                        'Go back'],
            }
    upload_menu_list_answers = prompt(upload_menu_list_questions, style = style)
    return upload_menu_list_answers['comma_list']

def upload_menu_list_looks():
    upload_menu_list_looks_questions = {
            'type': 'input',
            'name': 'comma_list_looks',
            'message': 'Please enter a comma delimited list of look IDs (e.g. \'1,3,5,7\')',
            'filter': lambda val: [num.strip() for num in val.split(',')] if len(val) > 0 else list(val),
            'validate': ListValidator
            }
    upload_menu_list_looks_answers = prompt(upload_menu_list_looks_questions, style = style)
    return upload_menu_list_looks_answers['comma_list_looks']

def upload_menu_list_dboards():
    upload_menu_list_dboards_questions = {
            'type': 'input',
            'name': 'comma_list_dashboards',
            'message': 'Please enter a comma delimited list of dashboard IDs (e.g. \'1,3,5,7\')',
            'filter': lambda val: [num.strip() for num in val.split(',')] if len(val) > 0 else list(val),
            'validate': ListValidator
            }
    upload_menu_list_dboards_answers = prompt(upload_menu_list_dboards_questions, style = style)
    return upload_menu_list_dboards_answers['comma_list_dashboards']

def user_flow(host):
    host = host
    filtered_entities = defaultdict(dict).fromkeys(['looks', 'dashboards'])
    filtered_entities['looks'] = defaultdict(dict)
    filtered_entities['dashboards'] = defaultdict(dict)
    space_id_list = gzr_core_functions.get_space_id_list(host)

    while True:
        main_menu_choice = main_menu()
        #Views
        if (main_menu_choice == 'View looks and/or dashboards (option to filter by parameters)'):
            while True:
                view_menu_choice = view_menu()
                if view_menu_choice == 'View all looks and dashboards':
                    gzr_core_functions.print_entities(gzr_core_functions.get_entities(host, space = space_id_list))
                elif view_menu_choice == 'Filter what you see':
                    type = 'both'
                    last_updated = '99 years'
                    spaces = space_id_list
                    while True:
                        filter_menu_choice = filter_menu()
                        if filter_menu_choice == 'Type (looks, dashboards, or both)':
                            type = filter_menu_type()
                        elif filter_menu_choice == 'Last Updated (Only applicable for looks)':
                            last_updated = filter_menu_last_updated()
                        elif filter_menu_choice == 'Space ID':
                            spaces = filter_menu_space()
                            if spaces == []:
                                spaces = space_id_list
                        elif filter_menu_choice == 'View filtered entities':
                            filtered_entities = gzr_core_functions.get_entities(host, type, last_updated, spaces)
                            gzr_core_functions.print_entities(filtered_entities)
                        elif filter_menu_choice == 'Go back':
                            break
                elif view_menu_choice == 'Go back':
                    break

        #Downloading
        elif (main_menu_choice == 'Download looks/dashboards from a Looker instance (creating local files on your computer)'):
                dir = download_dir(host)
                print(dir)
                while True:
                    download_menu_choice = download_menu()
                    if download_menu_choice == 'Provide a specific comma delimited list of look/dashboard IDs to download':
                        look_list = []
                        dboard_list = []
                        while True:
                            download_menu_list_choice = download_menu_list()
                            if download_menu_list_choice == 'Look IDs':
                                look_list = download_menu_list_looks()
                            if download_menu_list_choice == 'Dashboard IDs':
                                dboard_list = download_menu_list_dboards()
                            if download_menu_list_choice == 'Download provided list of entities':
                                gzr_core_functions.download_entities(host, dir, look_list, dboard_list)
                            if download_menu_list_choice == 'Go back':
                                break
                    elif download_menu_choice == 'Download based on your most recent filtered view (if you have one)':
                        gzr_core_functions.download_entities(host, dir, list(filtered_entities['looks'].keys()), list(filtered_entities['dashboards'].keys()))
                    elif download_menu_choice == 'Download all looks/dashboards':
                        all_entities = gzr_core_functions.get_entities(host, space = space_id_list)
                        gzr_core_functions.download_entities(host, dir, list(all_entities['looks'].keys()), list(all_entities['dashboards'].keys()))
                    elif download_menu_choice == 'Go back':
                        break

        #Uploading
        elif (main_menu_choice == 'Upload looks/dashboards into a Looker instance (using local files on your computer)'):
                dir = upload_dir(host)
                dest_instance = dest()
                return_code = gzr_core_functions.test_connection(dest_instance)
                if return_code == 0:
                    while True:
                        upload_menu_choice = upload_menu()
                        if upload_menu_choice == 'Provide a specific comma delimited list of look/dashboard IDs to upload':
                            upload_look_list = []
                            upload_dboard_list = []
                            while True:
                                upload_menu_list_choice = upload_menu_list()
                                if upload_menu_list_choice == 'Look IDs':
                                    upload_look_list = upload_menu_list_looks()
                                if upload_menu_list_choice == 'Dashboard IDs':
                                    upload_dboard_list = upload_menu_list_dboards()
                                if upload_menu_list_choice == 'Upload provided list of entities':
                                    gzr_core_functions.upload_entities(dest_instance, dir, look_list = upload_look_list, dboard_list = upload_dboard_list)
                                if upload_menu_list_choice == 'Go back':
                                    break
                        elif upload_menu_choice == 'Upload everything in a particular folder':
                            gzr_core_functions.upload_entities(dest_instance, dir, look_list = ['all'], dboard_list = ['all'])
                        elif upload_menu_choice == 'Go back':
                            break
                else:
                    print('\033[31m {}\033[00m'.format('\nConnection ERROR: ') + 'Please check your credentials in your ~/.netrc file in your home directory.'
                    'Look to' + '\033[34m {}\033[00m'.format('https://github.com/deangelo-llooker/gzr ') + 'under \'Storing Credentials\' for additional information on setting that up.\n')
        #spaces
        elif (main_menu_choice == 'View spaces'):
            gzr_core_functions.show_spaces(host)
        #Exit
        elif (main_menu_choice == 'Exit'):
            print('\033[35m {}\033[00m' .format('\nBye! Thanks for using Ro-Gazer!'))
            sys.exit()

host = connect()
return_code = gzr_core_functions.test_connection(host)
if return_code == 0:
    user_flow(host)
else:
    print('\033[31m {}\033[00m'.format('\nConnection ERROR: ') + 'Please check your credentials in your ~/.netrc file in your home directory.'
'Look to' + '\033[34m {}\033[00m'.format('https://github.com/deangelo-llooker/gzr ') + 'under \'Storing Credentials\' for additional information on setting that up.')
