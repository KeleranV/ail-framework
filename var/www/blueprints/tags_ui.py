#!/usr/bin/env python3
# -*-coding:UTF-8 -*

'''
    Blueprint Flask: crawler splash endpoints: dashboard, onion crawler ...
'''

import os
import sys
import json
import random

from flask import Flask, render_template, jsonify, request, Blueprint, redirect, url_for, Response
from flask_login import login_required, current_user, login_user, logout_user

sys.path.append('modules')
import Flask_config

# Import Role_Manager
from Role_Manager import create_user_db, check_password_strength, check_user_role_integrity
from Role_Manager import login_admin, login_analyst, login_read_only

sys.path.append(os.path.join(os.environ['AIL_BIN'], 'packages'))
import Date
import Tag

sys.path.append(os.path.join(os.environ['AIL_BIN'], 'lib'))
import Correlate_object

r_cache = Flask_config.r_cache
r_serv_db = Flask_config.r_serv_db
r_serv_tags = Flask_config.r_serv_tags
bootstrap_label = Flask_config.bootstrap_label

# ============ BLUEPRINT ============
tags_ui = Blueprint('tags_ui', __name__, template_folder=os.path.join(os.environ['AIL_FLASK'], 'templates/tags'))

# ============ VARIABLES ============



# ============ FUNCTIONS ============


# ============= ROUTES ==============
@tags_ui.route('/tag/add_tags')
@login_required
@login_analyst
def add_tags():

    tags = request.args.get('tags')
    tagsgalaxies = request.args.get('tagsgalaxies')
    object_id = request.args.get('object_id')
    object_type = request.args.get('object_type')

    list_tag = tags.split(',')
    list_tag_galaxies = tagsgalaxies.split(',')

    res = Tag.api_add_obj_tags(tags=list_tag, galaxy_tags=list_tag_galaxies, object_id=object_id, object_type=object_type)
    # error
    if res[1] != 200:
        return str(res[0])

    return redirect(Correlate_object.get_item_url(object_type, object_id))

@tags_ui.route('/tag/delete_tag')
@login_required
@login_analyst
def delete_tag():

    object_type = request.args.get('object_type')
    object_id = request.args.get('object_id')
    tag = request.args.get('tag')

    res = Tag.api_delete_obj_tags(tags=[tag], object_id=object_id, object_type=object_type)
    if res[1] != 200:
        return str(res[0])
    return redirect(Correlate_object.get_item_url(object_type, object_id))


@tags_ui.route('/tag/get_all_tags')
@login_required
@login_read_only
def get_all_tags():
    return jsonify(Tag.get_all_tags())

@tags_ui.route('/tag/get_all_obj_tags')
@login_required
@login_read_only
def get_all_obj_tags():
    object_type = request.args.get('object_type')
    res = Correlate_object.sanitize_object_type(object_type)
    if res:
        return jsonify(res)
    return jsonify(Tag.get_all_obj_tags(object_type))

@tags_ui.route('/tag/search/get_obj_by_tags')
@login_required
@login_read_only
def get_obj_by_tags():

    # # TODO: sanityze all
    object_type = request.args.get('object_type')
    ltags = request.args.get('ltags')
    page = request.args.get('ltags')
    date_from = request.args.get('ltags')
    date_to = request.args.get('ltags')

    # unpack tags
    list_tags = ltags.split(',')
    list_tag = []
    for tag in list_tags:
        list_tag.append(tag.replace('"','\"'))

    res = Correlate_object.sanitize_object_type(object_type)
    if res:
        return jsonify(res)

    dict_obj = Tag.get_obj_by_tags(object_type, list_tag)

    if dict_obj['tagged_obj']:
        dict_tagged = {"object_type":object_type, "page":dict_obj['page'] ,"nb_pages":dict_obj['nb_pages'], "tagged_obj":[]}
        for obj_id in dict_obj['tagged_obj']:
            obj_metadata = Correlate_object.get_object_metadata(object_type, obj_id)
            obj_metadata['id'] = obj_id
            dict_tagged["tagged_obj"].append(obj_metadata)

        dict_tagged['tab_keys'] = Correlate_object.get_obj_tag_table_keys(object_type)

        if len(list_tag) == 1:
            dict_tagged['current_tags'] = ltags.replace('"', '').replace('=', '').replace(':', '')
        else:
            dict_tagged['current_tags'] = list_tag

        #return jsonify(dict_tagged)
        return render_template("tags/search_obj_by_tags.html", bootstrap_label=bootstrap_label, dict_tagged=dict_tagged)

# # add route : /crawlers/show_domain
# @tags_ui.route('/tags/search/domain')
# @login_required
# @login_analyst
# def showDomain():
#     date_from = request.args.get('date_from')
#     date_to = request.args.get('date_to')
#     tags = request.args.get('ltags')
#
#     print(date_from)
#     print(date_to)
#
#     dates = Date.sanitise_date_range(date_from, date_to)
#
#     if tags is None:
#         return 'tags_none'
#         #return render_template("Tags.html", date_from=dates['date_from'], date_to=dates['date_to'])
#     else:
#         tags = Tag.unpack_str_tags_list(tags)
#
#
#
#
#     return render_template("showDomain.html", dict_domain=dict_domain, bootstrap_label=bootstrap_label,
#                                 tag_type="domain"))
