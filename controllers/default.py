# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################
def index():
  return dict(form=auth())
  
def groups():
    db(db.Groups.id==db.Groups(request.args[0]))
    group = db.Groups(request.args[0]) or redirect(URL('index'))
    #mem = db(db.auth_user.id==db.Comments.member).select(db.auth_user.username)
    admin = db(db.Group_Members.member==db.auth_user.id).select(db.Group_Members.administrator)
    event = db(db.Events.group_id==group.id).select()
    return dict(group=group, event=event, admin=admin)
 
#@auth.requires_login() 
def createAGroup():
    form=SQLFORM(db.Groups)
    if form.process().accepted:
        response.flash="Your group has been added"
        redirect(URL('listGroups'))
    elif form.errors:
        response.flash="Please correct any errors"
    else:
        response.flash="Please enter the information for your group"
    return dict(form=form)
    
def listGroups():
    groups = db().select(db.Groups.ALL)
    return dict(groups=groups)

def displayEvent():
    db(db.Events.id==db.Events(request.args[0]))
    event = db.Events(request.args[0]) or redirect(URL('index'))
    c = db(db.Comments.event==event.id).select()
    mem = db(db.auth_user.id==db.Comments.member).select(db.auth_user.username)
    return dict(event=event, c=c, mem=mem)

@auth.requires_login()
def delete():
    note = db.notes(request.args[0]) or redirect(URL('index'))
    form = SQLFORM.factory(Field('Confirm_deletion', 'boolean', default=False))
    if form.process().accepted:
        db(db.notes.id == request.args[0]).delete()
        db.commit()
        session.flash = T('The note has been deleted')
        redirect(URL('index'))
    return dict(form=form, note=note, user=auth.user)
    


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
