# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 12:44:23 2020

@author: qchat
"""

from git import Repo
from . import paths

url = 'https://github.com/qcha41/autolab-drivers.git'
path = paths.DRIVERS_OFFICIAL

def clone() :
    Repo.clone_from(url,path)

def sync() :
    print('Syncing drivers repository...')
    # Try to clone repository if it is not already done
    try : clone()
    except : pass
    # load local repository
    repository = Repo(path)
    # discard any current changes (mandatory)
    repository.git.reset('--hard')
    # pull in the changes from from the remote repository
    repository.remotes.origin.pull()
    print('Drivers repository up-to-date!')
