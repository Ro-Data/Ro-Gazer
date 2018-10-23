import subprocess
from os import listdir
from os.path import isfile, join, getmtime, expanduser
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from collections import defaultdict

terminal_tables_installed = False
try:
    from terminaltables import AsciiTable
    terminal_tables_installed = True
except:
    print('terminaltables isn\'t installed. Install this package to see prettier results :)')

def test_connection(host):
    return subprocess.run(['gzr', 'user', 'me', '--host=' + host], stdout = subprocess.PIPE, stderr = subprocess.PIPE).returncode

def show_spaces(host):
    ## print all spaces in 'home' looker directory
    print(subprocess.run(['gzr', 'space', 'ls', '--host=' + host], stdout = subprocess.PIPE).stdout.decode('utf-8'))

def get_space_id_list(host):
    #contents of 'home' looker directory
    home_contents = subprocess.run(
                        ['gzr', 'space', 'ls', '--host=' + host, '--fields=id', '--plain']
                        , stdout = subprocess.PIPE)

    # return the list of all space_ids in the users home looker directory
    space_id_list = [space.split()[1] for space in home_contents.stdout.decode('utf-8').split('\n') if len(space.split()) > 1]

    return space_id_list

def get_entities(host, output_type = 'both', time_since_last_update = '99 years', space = []):
    '''
    In general, hosted Looker servers will utilize UTC, so date comparisons are done in that timezone.
    If your Looker server doesn't utilize UTC, time filter may be off by a few hours.
    '''

    entity_dict = defaultdict(dict).fromkeys(['looks', 'dashboards'])
    entity_dict['looks'] = defaultdict(dict)
    entity_dict['dashboards'] = defaultdict(dict)
    #space = [int(space_id) for space_id in space]

    time_unit = time_since_last_update.split()[1]
    num_time = int(time_since_last_update.split()[0])

    #loop through every space id
    for space_num in range(len(space)):
        #get info about that space
        space_info = subprocess.run(['gzr', 'space', 'cat', space[space_num], '--host=' + host], stdout=subprocess.PIPE)
        space_info = json.loads(space_info.stdout.decode('utf-8'))

        #get info about every look in that space
        for look in space_info['looks']:
            if output_type == 'both' or output_type == 'looks':
                look_dict = defaultdict(str)
                look_dict['space_id'] = look['space']['id']
                look_dict['space_name'] = look['space']['name']
                look_dict['name'] = look['title']
                look_dict['last_updated'] = datetime.strptime(look['updated_at'].split(' +')[0], '%Y-%m-%d %H:%M:%S')
                look_dict['created_at'] = datetime.strptime(look['created_at'].split(' +')[0], '%Y-%m-%d %H:%M:%S')
                if datetime.utcnow() - relativedelta(**{time_unit: num_time}) < look_dict['last_updated']:
                    #add to look dict inside entity dict, with look ID being the key
                    entity_dict['looks'][look['id']] = look_dict
            else:
                pass
        #get info about every dashboard in that space
        for dashboard in space_info['dashboards']:
            if output_type == 'both' or output_type == 'dashboards':
                dashboard_dict = defaultdict(str)
                dashboard_dict['space_id'] = dashboard['space']['id']
                dashboard_dict['space_name'] = dashboard['space']['name']
                dashboard_dict['name'] = dashboard['title']
                #add to dashboard dict inside entity dict, with dashboard ID being the key
                entity_dict['dashboards'][dashboard['id']] = dashboard_dict
            else:
                pass
        print('Got info from %s out of %s specified spaces ' % (int(space_num)+1, len(space)))

    return entity_dict

def print_entities(entity_dict):
    #ugly printing
    if terminal_tables_installed == False:
        print('-------------\nLooks\n-------------\n')
        for k,v in entity_dict['looks'].items():
            print('ID: %s | Name: %s | Space ID: %s | Space Name: %s | Last Updated: %s' %
                 (k, v['name'], v['space_id'], v['space_name'], v['last_updated']))
        print('\n-------------\nDashboards\n-------------\n')
        for k,v in entity_dict['dashboards'].items():
            print('ID: %s | Name: %s | Space ID: %s | Space Name: %s' %
                 (k, v['name'], v['space_id'], v['space_name']))

    #pretty printing!
    else:
        look_table = [['ID', 'Name', 'Space ID', 'Space Name', 'Last Updated']]
        for k,v in entity_dict['looks'].items():
            look_table.append([k, v['name'], v['space_id'], v['space_name'], v['last_updated']])
        print(AsciiTable(look_table, title = 'Looks').table)

        dashboard_table = [['ID', 'Name', 'Space ID', 'Space Name']]
        for k,v in entity_dict['dashboards'].items():
            dashboard_table.append([k, v['name'], v['space_id'], v['space_name']])
        print(AsciiTable(dashboard_table, title = 'Dashboards').table)

def download_entities(host, dir, look_list, dboard_list):

    #create directories to store backups
    dir = expanduser(dir)
    hostname = host.split('.')[0]
    filepath = dir + '/' + hostname
    subprocess.run(['mkdir', '-p', filepath +'/Looks'])
    subprocess.run(['mkdir', '-p', filepath +'/Dashboards'])
    skip_warnings = False
    looks_downloaded = 0
    dboards_downloaded = 0
    #download creating a .json file for each
    #Looks
    for looknum in range(len(look_list)):
        filename = filepath + '/Looks/look_' + str(look_list[looknum]) + '.json'
        raw_json = subprocess.run(['gzr', 'look', 'cat', str(look_list[looknum]), '--host=' + host], stdout = subprocess.PIPE).stdout.decode('utf-8')
        look_exists = 'ERROR: Not found' not in raw_json
        if look_exists == True:
            json_file = json.loads(raw_json)
        else:
            print('Look with ID %s does not exist on your Looker server. File for this look was not created.' % (str(look_list[looknum])))
            continue
        if skip_warnings == True or not isfile(filename):
            with open(filename, 'w') as outfile:
                json.dump(json_file, outfile, indent=4)
                looks_downloaded += 1
                if looknum % 5 == 0:
                    print('Downloaded %s out of %s total looks' % (looks_downloaded, len(look_list)))
        elif isfile(filename):
            while True:
                overwrite = input('look_%s.json already exists in that folder. Overwrite? Y = Yes, N = No, S = Skip overwrite warnings ' % (str(look_list[looknum]))).lower()
                if overwrite == 'y' or overwrite == 's':
                    if overwrite == 's':
                        skip_warnings = True
                    with open(filename, 'w') as outfile:
                        json.dump(json_file, outfile, indent=4)
                        looks_downloaded +=1
                        if looknum % 5 == 0:
                            print('Downloaded %s out of %s total looks' % (looks_downloaded, len(look_list)))
                        break
                elif overwrite == 'n':
                    break
        print('%s/%s Looks downloaded to %s/Looks/' % (looks_downloaded, len(look_list), filepath))


    #Dashboards
    for dboardnum in range(len(dboard_list)):
        filename = filepath + '/Dashboards/dboard_' + str(dboard_list[dboardnum]) + '.json'
        raw_json = subprocess.run(['gzr', 'dashboard', 'cat', str(dboard_list[dboardnum]), '--host=' + host], stdout = subprocess.PIPE).stdout.decode('utf-8')
        dboard_exists = 'ERROR: Not found' not in raw_json
        if dboard_exists == True:
            json_file = json.loads(raw_json)
        else:
            print('Dashboard with ID %s does not exist on your Looker server. File for this dashboard was not created.' % (str(dboard_list[dboardnum])))
            continue
        if skip_warnings == True or not isfile(filename):
            with open(filename, 'w') as outfile:
                json.dump(json_file, outfile, indent=4)
                dboards_downloaded += 1
                if dboardnum % 5 == 0:
                    print('Downloaded %s out of %s total dashboards' % (dboards_downloaded, len(dboard_list)))
        elif isfile(filename):
            while True:
                overwrite = input('dboard_%s.json already exists in that folder. Overwrite? Y = Yes, N = No, S = Skip overwrite warnings' % (str(dboard_list[dboardnum]))).lower()
                if overwrite == 'y' or overwrite == 's':
                    if overwrite == 's':
                        skip_warnings = True
                    with open(filename, 'w') as outfile:
                        json.dump(json_file, outfile, indent=4)
                        dboards_downloaded +=1
                        if dboardnum % 5 == 0:
                            print('Downloaded %s out of %s total dashboards' % (dboards_downloaded, len(dboard_list)))
                        break
                elif overwrite == 'n':
                    break
        print('%s/%s Dashboards downloaded to %s/Dashboards/' % (dboards_downloaded, len(dboard_list), filepath))

    return None

def upload_entities(dest, dir, time = 'none', look_list = [], dboard_list = []):
    dir = expanduser(dir)
    skip_warnings = False
    looks_uploaded = 0
    dboards_uploaded = 0

    looks_in_local = [f for f in listdir(dir + '/Looks/') if isfile(join(dir + '/Looks/', f))]
    dboards_in_local = [f for f in listdir(dir + '/Dashboards/') if isfile(join(dir + '/Dashboards/', f))]

    looks_to_upload = ['look_%s.json' % (num) for num in look_list]
    dboards_to_upload = ['dboard_%s.json' % (num) for num in dboard_list]
    if look_list == ['all']:
        looks_to_upload = looks_in_local
    if dboard_list == ['all']:
        dboards_to_upload = dboards_in_local

    #to upload looks
    for filenum in range(len(looks_to_upload)):
        local_look_dict = defaultdict(str)
        filepath = dir + '/Looks/' + looks_to_upload[filenum]
        #need to check if file exists
        if isfile(filepath):
            local_file_mod_time = datetime.utcfromtimestamp(getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
            local_look_dict['last_updated'] = local_file_mod_time
            with open(filepath) as file:
                json_file = json.load(file)
                local_look_dict['id'] = json_file['id']
                local_look_dict['name'] = json_file['title']
                local_look_dict['space_id'] = json_file['space']['id']
                local_look_dict['space_name'] = json_file['space']['name']
                file.close()

            #get info on the looks on the server with the same space id as the local file
            remote_look_info = subprocess.run(['gzr', 'space', 'ls', str(local_look_dict['space_id']), '--host=' + dest], stdout=subprocess.PIPE)
            remote_look_info = remote_look_info.stdout.decode('utf-8')
            # for some reason the gzr space ls command doesn't let you filter by title field, so this is a workaround. It's hacky but should work consistently.
            existing_look_names = [look.split('|')[2].strip() for look in remote_look_info.split('\n')[3:-2] if look.split('|')[1].strip() == 'looks.title' and len(look.split('|')[2].strip()) >= 1]
            existing_look_ids = [look.split('|')[2].strip() for look in remote_look_info.split('\n')[3:-2] if look.split('|')[1].strip() == 'looks.id' and len(look.split('|')[2].strip()) >= 1]

            if skip_warnings == True or local_look_dict['name'] not in existing_look_names:
                subprocess.run(['gzr', 'look', 'import', filepath, str(local_look_dict['space_id']), '--host=' + dest, '--force'])
                looks_uploaded += 1
                if looks_uploaded % 5 == 0:
                    print('Uploaded %s out of %s total Looks' % (looks_uploaded, len(looks_to_upload)))
            elif local_look_dict['name'] in existing_look_names:
                while True:
                    # This is necessary because I want to get the last_updated on the server for the look with the same name.
                    # In some rare cases, the IDs may differ between looks with the same name, so can't use the ID of the local look to find that info.
                    # It may seem counterintuitive, but its mainly because gzr works with IDs, but Looker works with names to identify things.
                    id_of_existing_look = existing_look_ids[existing_look_names.index(local_look_dict['name'])]
                    existing_look_updated = json.loads(subprocess.run(['gzr', 'look', 'cat', id_of_existing_look, '--host=' + dest], stdout = subprocess.PIPE).stdout.decode('utf-8'))['updated_at']
                    existing_look_updated = datetime.strptime(existing_look_updated.split(' +')[0], '%Y-%m-%d %H:%M:%S')

                    overwrite = input('A Look with the name %s already exists in Space %s on %s. Your local file for this look was created at %s, '
                    'while the look on the Looker server was last updated at %s. (UTC Time) '
                    'Overwrite? Y = Yes, N = No, S = Skip overwrite warnings' % (local_look_dict['name'], local_look_dict['space_id'], dest, str(local_look_dict['last_updated']), str(existing_look_updated))).lower()
                    if overwrite == 'y' or overwrite == 's':
                        if overwrite == 's':
                            skip_warnings = True
                        subprocess.run(['gzr', 'look', 'import', filepath, str(local_look_dict['space_id']), '--host=' + dest, '--force'])
                        looks_uploaded +=1
                        if looks_uploaded % 5 == 0:
                            print('Uploaded %s out of %s total Looks' % (looks_uploaded, len(looks_to_upload)))
                        break
                    elif overwrite == 'n':
                        break
        else:
            print('%s does not exist in the specified directory. Skipping this file.' % (looks_to_upload[filenum]))
            continue

    print('%s/%s Looks uploaded to %s' % (looks_uploaded, len(looks_to_upload), dest))

    #to upload dashboards
    for filenum in range(len(dboards_to_upload)):
        local_dboard_dict = defaultdict(str)
        filepath = dir + '/Dashboards/' + dboards_to_upload[filenum]
        #need to check if file exists
        if isfile(filepath):
            local_file_mod_time = datetime.utcfromtimestamp(getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
            local_dboard_dict['last_updated'] = local_file_mod_time
            with open(filepath) as file:
                json_file = json.load(file)
                local_dboard_dict['id'] = json_file['id']
                local_dboard_dict['name'] = json_file['title']
                local_dboard_dict['space_id'] = json_file['space']['id']
                local_dboard_dict['space_name'] = json_file['space']['name']
                file.close()

            #get info on the dboard on the server with the same id as the local file
            remote_dboard_info = subprocess.run(['gzr', 'space', 'ls', str(local_dboard_dict['space_id']), '--host=' + dest], stdout=subprocess.PIPE)
            remote_dboard_info = remote_dboard_info.stdout.decode('utf-8')
            # for some reason the gzr space ls command doesn't let you filter by title field, so this is a workaround. It's hacky but should work consistently.
            existing_dboard_names = [dboard.split('|')[2].strip() for dboard in remote_dboard_info.split('\n')[3:-2] if dboard.split('|')[1].strip() == 'dashboards.title' and len(dboard.split('|')[2].strip()) >= 1]

            if skip_warnings == True or local_dboard_dict['name'] not in existing_dboard_names:
                subprocess.run(['gzr', 'dashboard', 'import', filepath, str(local_dboard_dict['space_id']), '--host=' + dest, '--force'])
                dboards_uploaded += 1
                if dboards_uploaded % 5 == 0:
                    print('Uploaded %s out of %s total Dashboards' % (dboards_uploaded, len(dboards_to_upload)))
            elif local_dboard_dict['name'] in existing_dboard_names:
                #########
                while True:
                    overwrite = input('A Dashboard with the name %s already exists in Space %s on %s.'
                    'Overwrite? Y = Yes, N = No, S = Skip overwrite warnings' % (local_dboard_dict['name'], local_dboard_dict['space_id'], dest)).lower()
                    if overwrite == 'y' or overwrite == 's':
                        if overwrite == 's':
                            skip_warnings = True
                        subprocess.run(['gzr', 'dashboard', 'import', filepath, str(local_dboard_dict['space_id']), '--host=' + dest, '--force'])
                        dboards_uploaded +=1
                        if dboards_uploaded % 5 == 0:
                            print('Uploaded %s out of %s total Dashboards' % (dboards_uploaded, len(dboards_to_upload)))
                        break
                    elif overwrite == 'n':
                        break
        else:
            print('%s does not exist in the specified directory. Skipping this file.' % (dboards_to_upload[filenum]))
            continue

    print('%s/%s Dashboards uploaded to %s' % (dboards_uploaded, len(dboards_to_upload), dest))
