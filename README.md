# ansible-samba_user

Manage samba user accounts with ansible.

## Installation

Requirements:

- `pdbedit`
- `smbpasswd`

Put the module in the `library` directory where your playbook is. You can do this with `curl`: `curl https://raw.githubusercontent.com/xsteadfastx/ansible-samba_user/master/samba_user.py -O library/samba_user.py`

## Examples

```
# Remove user
- samba_user: name=bob state=absent
  become: yes

# Be sure there is a user 'bob' with password '12345'
- samba_user: name=bob password=12345 state=present
  become: yes
```
