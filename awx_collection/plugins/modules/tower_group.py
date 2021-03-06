#!/usr/bin/python
# coding: utf-8 -*-

# (c) 2017, Wayne Witzel III <wayne@riotousliving.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: tower_group
author: "Wayne Witzel III (@wwitzel3)"
version_added: "2.3"
short_description: create, update, or destroy Ansible Tower group.
description:
    - Create, update, or destroy Ansible Tower groups. See
      U(https://www.ansible.com/tower) for an overview.
options:
    name:
      description:
        - The name to use for the group.
      required: True
      type: str
    description:
      description:
        - The description to use for the group.
      type: str
    inventory:
      description:
        - Inventory the group should be made a member of.
      required: True
      type: str
    variables:
      description:
        - Variables to use for the group.
      type: dict
    state:
      description:
        - Desired state of the resource.
      default: "present"
      choices: ["present", "absent"]
      type: str
    new_name:
      description:
        - A new name for this group (for renaming)
      required: False
      type: str
      version_added: "3.7"
    tower_oauthtoken:
      description:
        - The Tower OAuth token to use.
      required: False
      type: str
      version_added: "3.7"
extends_documentation_fragment: awx.awx.auth
'''


EXAMPLES = '''
- name: Add tower group
  tower_group:
    name: localhost
    description: "Local Host Group"
    inventory: "Local Inventory"
    state: present
    tower_config_file: "~/tower_cli.cfg"
'''

from ..module_utils.tower_api import TowerModule
import json


def main():
    # Any additional arguments that are not fields of the item can be added here
    argument_spec = dict(
        name=dict(required=True),
        new_name=dict(required=False),
        description=dict(required=False),
        inventory=dict(required=True),
        variables=dict(type='dict', required=False),
        state=dict(choices=['present', 'absent'], default='present'),
    )

    # Create a module for ourselves
    module = TowerModule(argument_spec=argument_spec, supports_check_mode=True)

    # Extract our parameters
    name = module.params.get('name')
    new_name = module.params.get('new_name')
    inventory = module.params.get('inventory')
    description = module.params.get('description')
    state = module.params.pop('state')
    variables = module.params.get('variables')

    # Attempt to look up the related items the user specified (these will fail the module if not found)
    inventory_id = module.resolve_name_to_id('inventories', inventory)

    # Attempt to look up the object based on the provided name and inventory ID
    group = module.get_one('groups', **{
        'data': {
            'name': name,
            'inventory': inventory_id
        }
    })

    # Create the data that gets sent for create and update
    group_fields = {
        'name': new_name if new_name else name,
        'inventory': inventory_id,
    }
    if description is not None:
        group_fields['description'] = description
    if variables is not None:
        group_fields['variables'] = json.dumps(variables)

    if state == 'absent':
        # If the state was absent we can let the module delete it if needed, the module will handle exiting from this
        module.delete_if_needed(group)
    elif state == 'present':
        # If the state was present we can let the module build or update the existing group, this will return on its own
        module.create_or_update_if_needed(group, group_fields, endpoint='groups', item_type='group')


if __name__ == '__main__':
    main()
