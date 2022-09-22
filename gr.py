#!/usr/bin/python3
import json
import os
import subprocess
import sys
import getopt
from pathlib import Path

RED = '\033[1;31m'
BLUE = '\033[1;36m'
GREEN = '\033[1;32m'
YELL = '\033[1;33m'
PURPLE = '\033[1;35m'
NC = '\033[0m' # No Color
YES_LIST = ["y","yes","Yes","yEs","yeS","YES","yES","YeS","YEs"]

def find_paths_by_tag(tag,tags_data):
    result = []
    if tag in tags_data :
      for folder in tags_data[tag]:
        if folder in tags_data :
          # print("Find " + folder + " in tags list ")
          if not result == "":
            result += find_paths_by_tag(folder,tags_data)
          else:
            result = find_paths_by_tag(folder,tags_data)
        else :
          if not folder == "" :
            result.append(folder)
    if result == [] :
      sys.exit(RED + "ERROR: Folders for tag " + tag + " not found !!!\n" + NC)

    return result

def if_branch_exist(branch):
    local = ""
    remote = ""
    result = ""
    local = subprocess.run(["/usr/bin/git","show-ref","refs/heads/" + branch.replace("\n", "") ],capture_output=True)
    if local.stdout.decode('utf-8') == "" :
        remote = subprocess.run(["/usr/bin/git","ls-remote","--heads","origin",branch.replace("\n", "") ], check=True,capture_output=True)
        if remote.stdout.decode('utf-8') != "":
            result = branch
    else:
        result = branch

    return result

def print_no_git_folders(foders_list):
    if foders_list != []:
        print("")
        print(YELL + "\n############## WARNING ############# \n" + NC)
        for no_git_path in foders_list:
            print(YELL + "Repo: " + NC + no_git_path.replace("\n", "") + YELL + " haven't " + GREEN + "'.git'" + YELL + " folder !!!" + NC )
        print(YELL + "\n#################################### \n" + NC)

def clone_multi_repo(folders_paths):
    pass

def get_status(paths):
    status_result = {'have_updates':[],'no_git_folder':[]}
    for path in paths:
        # Convert all bash env in path to string
        path = subprocess.check_output(['bash','-c','echo ' + path ])
        path = path.decode('utf-8')
        print(GREEN + "Check " + path.replace("\n", "") + NC)
        os.chdir(path.replace("\n", ""))
        if os.path.exists(path.replace("\n", "")+"/.git") :
            status = subprocess.run(['/usr/bin/git','status','-s'], check=True, capture_output=True)
            if status.stdout.decode('utf-8') != "":
                status_result['have_updates'].append(path)
        else:
            status_result['no_git_folder'].append(path)

    # Output updates
    if status_result['have_updates'] != [] :
        print(PURPLE + "\n#################################### \n" + NC)
        for path in status_result['have_updates'] :
            print(YELL + "Repo: " + NC + path.replace("\n", "") + YELL + " have next updates.\n" + NC)
            os.chdir(path.replace("\n", ""))
            subprocess.check_call(['/usr/bin/git','status','-s'])
            print(PURPLE + "\n#################################### \n" + NC)

    # Output directoryes without .git folder
    print_no_git_folders(status_result['no_git_folder'])

def git_multi_checkout(paths,branch):
    # check if branch name not empty
    if len(branch) == 0 :
        sys.exit(RED + "ERORR: Branch name is empty !!! " + NC)
    foders_list = {'exist_path':[],'not_exist_path':[],'have_branch':[],'havent_branch':[],'no_git_folder':[]}
    ans = ""
    checkout_b_ans = ""
    push_b_ans = ""
    checkout_cmd = ""

    for path in paths:
        # Convert all bash env in path to string
        path = subprocess.check_output(['bash','-c','echo ' + path ])
        path = path.decode('utf-8')
        check_branch = ""
        print(GREEN + "Check " + path.replace("\n", "") + NC)
        # check if folder exist
        if os.path.exists(path.replace("\n", "")) :
            foders_list['exist_path'].append(path)
            # cd to path directory
            os.chdir(path.replace("\n", ""))
            # check if .git exist
            if not os.path.exists(path.replace("\n", "")+"/.git") :
                foders_list['no_git_folder'].append(path)
                check_branch = "no_git"
            else:
                # check if branch exist on local and remoute
                check_branch = if_branch_exist(branch)
            if check_branch == "":
                foders_list['havent_branch'].append(path)
                if checkout_b_ans == "":
                    print(YELL + "WARNING: Branch " + NC + branch + YELL + " not exist for repo " + NC + path.replace("\n", "") + YELL + " !!! \n" + NC + "Do you wanna to create a new one ? [y/n]")
                    ans = input()
                    # check if u wanna checkout to the new branch
                    if ans in YES_LIST :
                        checkout_b_ans = "yes"
                        ans = ""
                        print("\nDo you wanna a push branch on remote after creating ? [y/n]")
                        ans = input()
                        if ans in YES_LIST :
                            push_b_ans = "yes"
                    else:
                        checkout_b_ans = "no"
            else:
                foders_list['have_branch'].append(path)
        else:
            foders_list['not_exist_path'].append(path)
        if path in foders_list['exist_path'] and path not in foders_list['no_git_folder'] :
            if path in foders_list['have_branch'] :
                print(YELL + "Checkout: " + NC + path)
                subprocess.check_call(['bash','-c', ' /usr/bin/git fetch ' ]);
                subprocess.check_call(['bash','-c', ' /usr/bin/git checkout ' + branch.replace("\n", "") ]);

            if path in foders_list['havent_branch'] and  checkout_b_ans == "yes":
                print(YELL + "Create new branch " + NC + branch.replace("\n", "") + YELL + " for " + NC + path.replace("\n", ""))
                subprocess.check_call(['bash','-c', ' /usr/bin/git fetch ' ]);
                subprocess.check_call(['bash','-c', ' /usr/bin/git checkout -b ' + branch.replace("\n", "") ]);
                if push_b_ans == "yes" :
                    subprocess.check_call(['bash','-c', ' /usr/bin/git push -u origin ' + branch.replace("\n", "") ]);

    # Output not exists directoryes
    if foders_list['not_exist_path'] != []:
        print(BLUE + "\n################ Info ############## \n" + NC)
        for no_path in foders_list['not_exist_path']:
            print("Folder: " + no_path.replace("\n", "")  + YELL + " not found !!!" + NC )
        print(BLUE + "\n#################################### \n" + NC)

    # Output directoryes without .git folder
    print_no_git_folders(foders_list['no_git_folder'])

    # Output directoryes where branch wasn't founded
    if foders_list['havent_branch'] != [] and checkout_b_ans == "no" :
        ans = ""
        branch_ans = ""
        print(BLUE + "\n################ Info ############## \n" + NC)
        for no_branch_path in foders_list['havent_branch']:
            print(YELL + "Repo: " + NC + no_branch_path.replace("\n", "") + YELL + " wasn't checkout to " + NC + branch + YELL+ " branch !!!" + NC )
        print(BLUE + "\n#################################### \n" + NC)
        print("Do you wanna create or choose other branch for this repo ? [y/n]")
        ans = input()
        print("")
        if ans in YES_LIST :
            print(GREEN + "Please choose branch name (" + branch + "):" + NC)
            branch_ans = input()
            if branch_ans == "" :
                branch_ans = branch
            git_multi_checkout(foders_list['havent_branch'],branch_ans)

def execute_command(paths,command,branch):
    if  command == "" :
        sys.exit(RED + "ERORR: Command is empty !!!" + NC + "\n")
    if len(branch) == 0 :
        print(YELL + "WARNING: Branch name is empty !!! " + NC + "\n")

    if command == "pull" or command == "push" or command == "fetch" or command == "diff":

        errors_msg = []
        for path in paths:
            try:
                r = ""
                folder_path = subprocess.check_output(['bash','-c','echo ' + path ], encoding="utf8")
                print(GREEN + command + ": " + NC + folder_path )
                cmd = ['bash','-c', 'cd ' + folder_path + ' /usr/bin/git ' + command ]
                r = subprocess.run(cmd, check=True, capture_output=True, encoding="utf8")
            except subprocess.CalledProcessError as e:
                print(RED + "error: " + NC + folder_path )
                errors_msg.append("Repo: " + RED + folder_path + NC)
                errors_msg.append(e.stderr)

        if not errors_msg == []:
            print(RED + "\n############### ERROR ############## \n" + NC)
            for error in errors_msg:
                print(error)
            print(RED + "\n#################################### \n" + NC)

    elif command == "status" :
        get_status(paths)
    elif command == "checkout":
        git_multi_checkout(paths,branch);
    #
    # elif command =="clone":
    #     clone_multi_repo(tag)
    else:
        errors_msg = []
        for path in paths:
            try:
                r = ""
                folder_path = subprocess.check_output(['bash','-c','echo ' + path ], encoding="utf8")
                print(GREEN + command + ": " + NC + folder_path )
                cmd = ['bash','-c', 'cd ' + folder_path + command ]
                r = subprocess.run(cmd, check=True, capture_output=True, encoding="utf8")
                print(r.stdout)
            except subprocess.CalledProcessError as e:
                print(RED + "error: " + NC + folder_path )
                errors_msg.append("Repo: " + RED + folder_path + NC)
                errors_msg.append(e.stderr)

        if not errors_msg == []:
            print(RED + "\n############### ERROR ############## \n" + NC)
            for error in errors_msg:
                print(error)
            print(RED + "\n#################################### \n" + NC)

# def gets_json()
def main(argv):
   tag_name = ''
   cmd = 'list'
   grconfig_path = ''
   git_branch = ''
   res = ''
   info_begin = BLUE + "\n################ Info ############## \n" + NC
   info_end = BLUE + "\n#################################### \n" + NC
   help_msg = info_begin + '\n gr.py -t <tag> -f <config file> -c "<command>" -b <branch> \n' + info_end
   try:
      opts, args = getopt.getopt(argv,"hlt:c:f:b:",["help","list","tag=","command=","config-path=","branch="])
   except getopt.GetoptError:
      print(help_msg)
      sys.exit()
   for opt, arg in opts:
      if opt == ("-h", "--help"):
         print(help_msg)
         sys.exit()
      elif opt in ("-l", "--list"):
          cmd = "list"
      elif opt in ("-t", "--tag"):
         tag_name = arg
      elif opt in ("-c", "--command"):
         cmd = arg
      elif opt in ("-f", "--config-path"):
         grconfig_path = arg
      elif opt in ("-b", "--branch"):
         git_branch = arg

# update gr confige file

# Check gr config file
   if grconfig_path == '':
     grconfig_path = os.environ["HOME"] + "/.grconfig.json"
   if not Path(grconfig_path).is_file() :
     sys.exit(RED + "File " + grconfig_path + " not found or it's not a file !!!" + NC)

# Check tag
   if tag_name == '':
     print(help_msg)
     sys.exit(RED + "ERORR: Tag name not found !!! " + NC)

# Open json
   grconfig = open(grconfig_path)
   data = json.load(grconfig)
   tags_list = data['tags']
   # Closing file
   grconfig.close()

   print(info_begin)
   print("Config file is: ", grconfig_path)
   print('Tag name is: ', tag_name)
   print('Command is: ', cmd)
   print('Branch is: ', git_branch)
   print(info_end)

   if tag_name not in tags_list:
       print(YELL + 'WARNING: Tag name not in tag list !!! ' + NC )

   folders_paths = sorted(set(find_paths_by_tag(tag_name,tags_list)))


   if cmd == 'list':
       for folder in folders_paths :
           print(folder)
   elif cmd == 'help':
       print(help_msg)
   else:
       print("")
       execute_command(folders_paths,cmd,git_branch)


if __name__ == "__main__":
   main(sys.argv[1:])
