"""Script is used to remove all Python packages
EXCEPT the ones defined in an input file.

All the packges to be removed must be supported by pip.

By default, this script uses PIP3. Alternatively it can use
any pip version by passing parameter when exeucting script.

Usage:
    python3 remove_not_in.py <path_to_packages_file> [pip_version]
    
    [pip_version] is optional, can be just a command like 'pip'
    for pip2 or a full path for a custom python install or virtual env.
"""


import os
import sys
import subprocess as proc


# Default pip command to be used.
# This assumes location of pip is already in PATH.
# If this is not correct, script can use a different pip
# or a full path to a pip command via script argument
PIP_COMMAND = 'pip3'


def main():
    # REQUIRED: We must have a file define the input
    # which defines a list of packages to keep.
    if len(sys.argv) == 1:
        raise Exception('Did not provide an input file')
    path_to_file = os.path.expanduser(sys.argv[1])

    # Optional: If want to use a different pip command
    # this can be used. It can be a full path if needed.
    if (len.sys.argv) >= 3:
        PIP_COMMAND = sys.argv[2]

    packages_to_keep = get_user_packages(path_to_file)
    print('\nPackage(s) to keep ({0}):\n'.format(len(packages_to_keep)),
          packages_to_keep)

    packages_installed = get_installed_packages()
    print('\nPackage(s) installed ({0}):\n'.format(len(packages_installed)),
          packages_installed)

    packages = list(set(packages_installed).difference(packages_to_keep))
    packages = sorted(packages, key=lambda s: s.lower())
    print('\nPackage(s) to remove ({0}):\n'.format(len(packages)), packages)

    if len(packages) > 0:
        print("\n Removing packages...")
        count = remove_packages(packages)
    else:
        print('\nDONE... nothing to remove!')


def write_output(packages):
    with open('packges_to_uninstall', 'w+') as f:
        for pkg in packages:
            f.write('{0}\n'.format(pkg))
        print('\nExported packages to uninstall:', os.path.realpath(f.name))
        print('\n\nRun the following command to finish unstalling:')
        print('   $> pip3 uninstall --yes -r packages_to_uninstall')


def get_user_packages(path):
    print('\nReading file:\n', '-->', path)
    with open(path, 'r') as f:
        data = f.readlines()

    packages = split(data, '==')
    return sorted(packages, key=lambda s: s.lower())


def get_installed_packages():
    print('\nGetting package(s) from pip...')
    result = proc.run([PIP_COMMAND, 'freeze'],
                      stdout=proc.PIPE,
                      stderr=proc.PIPE)
    error = result.stderr.decode('utf-8')

    if error != '':
        raise Exception('ERROR getting result from PIP:\n' + error)

    output = result.stdout.decode('utf-8').splitlines()
    packages = split(output, '==')
    return sorted(packages, key=lambda s: s.lower())


def split(data, separator):
    li = []
    for line in data:
        line = str(line).split(separator)[0].strip()
        if line != '':
            li.append(line)

    return li


def remove_packages(packages):
    cnt = 0
    for pkg in packages:
        result = proc.run([PIP_COMMAND, 'uninstall', '--yes', pkg],
                          stdout=proc.DEVNULL,
                          stderr=proc.PIPE)
        status = result.stderr.decode('utf-8').strip()
        if status == '':
            status = 'Success'
            cnt += 1
        else:
            status = 'Fail:' + status

        print('--> ({0}) {1}...{2}'.format(cnt, pkg, status))

    if cnt >= len(packages):
        print('\nDONE... removed ALL', count, 'package(s)')
    elif count==0:
        print('\nERROR... did NOT remove anything')
    else:
        print('\nWARNING... removed SOME', count, 'package(s)')


if __name__ == '__main__':
    main()

