#!/usr/bin/python


DOCUMENTATION = '''
---
module: samba_user
short_description: Manager samba user accounts.
author: "Marvin Steadfast (@xsteadfastx)"
requirements:
    - pdbedit
    - smbpasswd
options:
    name:
        description:
             - Name of the user, to create, remove or modify.
        required: true
    password:
        description:
            - Set the user's password.
        required: false
    state:
        description:
            - Whether the account should exist or not,
              taking action if the state is different from what is stated.
        default: present
        choices: ["absent", "present"]
        required: false
'''


EXAMPLES = '''
# Remove user
- samba_user: name=bob state=absent
  become: yes

# Be sure there is a user 'bob' with password '12345'
- samba_user: name=bob password=12345 state=present
  become: yes
'''


def get_user(pdbedit, name, module):
    '''Extract user information from pdbedit.

    :param pdbedit: Path of pdbedit
    :param name: Username
    :param module: AnsibleModule object
    :type pdbedit: str
    :type name: str
    :type module: ansible.module_utils.basic.AnsibleModule
    :returns: User data dictionary
    :rtype: dict
    '''
    output = module.run_command('{} -L -w'.format(pdbedit))

    if output[0] != 0:
        module.fail_json(msg=output[2])

    for line in output[1].splitlines():
        splitted_line = line.split(':')
        if splitted_line[0] == name:
            return {
                'name': splitted_line[0],
                'password': splitted_line[3]
            }

    return {}


def add_user(smbpasswd, name, password, module):
    '''Add samba user.

    :param smbpasswd: Path of smbpasswd
    :param name: Username
    :param password: Password
    :param module: AnsibleModule object
    :type smbpasswd: str
    :type name: str
    :type password: str
    :type module: ansible.module_utils.basic.AnsibleModule
    '''
    command = (
        'sh -c "(echo {password}; echo {password})" '
        '| {smbpasswd} -a -s {name}'
    ).format(password=password, smbpasswd=smbpasswd, name=name)

    output = module.run_command(command, use_unsafe_shell=True)

    if output[0] != 0:
        module.fail_json(msg=output[2])

    else:
        module.exit_json(changed=True)


def change_password(smbpasswd, pdbedit, user, password, module):
    '''Change samba user password.

    It runs sambpasswd anyway. Just the changed state changes. It will just
    check if the password changed or not.

    :param smbpasswd: Path of smbpasswd
    :param pdbedit: Path of pdbedit
    :param user: Username
    :param password: Password
    :param module: AnsibleModule object
    :type smbpasswd: str
    :type pdbedit: str
    :type user: str
    :type password: str
    :type module: ansible.module_utils.basic.AnsibleModule
    '''
    old_password = user['password']

    command = (
        'sh -c "(echo {password}; echo {password})" '
        '| {smbpasswd} -a -s {name}'
    ).format(password=password, smbpasswd=smbpasswd, name=user['name'])

    output = module.run_command(command, use_unsafe_shell=True)

    if output[0] != 0:
        module.fail_json(msg=output[2])

    new_password = get_user(pdbedit, user['name'], module)['password']

    if old_password == new_password:
        module.exit_json(changed=False)

    elif old_password != new_password:
        module.exit_json(changed=True)


def delete_user(pdbedit, name, module):
    ''' Delete samba user.

    :param pdbedit: Path of pdbedit
    :param name: Username
    :param module: AnsibleModule object
    :type pdbedit: str
    :type name: str
    :type module: ansible.module_utils.basic.AnsibleModule
    '''
    output = module.run_command(
        '{pdbedit} -x {name}'.format(pdbedit=pdbedit, name=name)
    )

    if output[0] != 0:
        module.fail_json(msg=output[2])

    else:
        module.exit_json(changed=True)


def main():
    '''Main function.
    '''
    module = AnsibleModule(
        argument_spec={
            'name': {
                'required': True
            },
            'password': {
                'no_log': True
            },
            'state': {
                'default': 'present',
                'choices': [
                    'absent',
                    'present'
                ]
            }
        }
    )

    name = module.params['name']
    password = module.params['password']
    state = module.params['state']

    smbpasswd = module.get_bin_path('smbpasswd', True)
    pdbedit = module.get_bin_path('pdbedit', True)

    user = get_user(pdbedit, name, module)

    if state == 'absent':
        if not user:
            module.exit_json(changed=False)

        else:
            delete_user(pdbedit, name, module)

    elif state == 'present':
        if user:
            change_password(smbpasswd, pdbedit, user, password, module)

        elif not user:
            add_user(smbpasswd, name, password, module)


from ansible.module_utils.basic import *
main()
